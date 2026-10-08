"""Frozen independent-run study, opt-in through the existing experiment CLI."""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
import threading
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
import psutil

from tekclipse.data.generator import generate_synthetic_dataset
from tekclipse.evaluation.study_data import fingerprint, make_case, validate_roles
from tekclipse.evaluation.scientific_metrics import measure, measure_incidents
from tekclipse.pipeline.calibration import feature_frame, fit_profiles
from tekclipse.pipeline.rules import detect_rule_alerts
from tekclipse.pipeline.network import fit_network_baseline, detect_network_alerts
from tekclipse.pipeline.explain import detect_system_alerts, explain_alerts
from tekclipse.pipeline.correlation import correlate_alerts
from tekclipse.pipeline.trust import trust_snapshot
from tekclipse.pipeline.subsystems import subsystem_statuses

ROOT = Path(__file__).resolve().parents[2]


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, allow_nan=False), encoding='utf-8')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def source_digest():
    files = sorted((ROOT/'tekclipse').rglob('*.py')) + [ROOT/'config.yaml', ROOT/'requirements.txt']
    return digest({str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files})


class MemorySample:
    """Sample process RSS; includes interpreter/data, not just detector allocation."""
    def __init__(self, interval):
        self.interval = interval
        self.stop = threading.Event()
        self.process = psutil.Process()
        self.start = self.process.memory_info().rss
        self.peak = self.start

    def _sample(self):
        while not self.stop.wait(self.interval):
            self.peak = max(self.peak, self.process.memory_info().rss)

    def __enter__(self):
        self.thread = threading.Thread(target=self._sample, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.peak = max(self.peak, self.process.memory_info().rss)
        self.stop.set()
        self.thread.join()

    def report(self):
        return dict(start_rss_mb=self.start/2**20, sampled_peak_rss_mb=self.peak/2**20,
                    sampled_increment_mb=(self.peak-self.start)/2**20,
                    interval_seconds=self.interval,
                    note='Whole process RSS sampled, not an exact allocator peak; includes evaluation work.')


def score_alerts(features, model, threshold):
    scores = -model.decision_function(features.select_dtypes(include='number'))
    return scores, alerts_from_scores(features, scores, threshold)


def alerts_from_scores(features, scores, threshold):
    return [dict(timestamp=features.timestamp.iloc[i], source='ML', severity='WARNING',
                 description='Isolation Forest deviation from nominal profile', score=float(scores[i]))
            for i in np.flatnonzero(scores > threshold)]


def observe_rules(rules, commands):
    burst = {minute: frame.sort_values('timestamp').timestamp.iloc[10]
             for minute, frame in commands.groupby(pd.Grouper(key='timestamp', freq='min')) if len(frame)>10}
    return [dict(a, timestamp=burst[pd.Timestamp(a['timestamp'])]) if a['source']=='R2' else dict(a) for a in rules]


def run_case(data, events, coordinated, name, profiles, network_baseline, config):
    timings = {}

    def timed(label, function):
        started = perf_counter()
        value = function()
        timings[label] = perf_counter()-started
        return value

    features = timed('feature_seconds', lambda: feature_frame(data['telemetry']))
    raw_rules = timed('rules_seconds', lambda: detect_rule_alerts(data['commands'], data['telemetry']))
    rules = observe_rules(raw_rules, data['commands'])
    # Replay the original R1 bug only in the explicitly named historical comparator.
    original_rules = [a for a in rules if not (a['source']=='R1' and
                      a['description'].startswith('Unauthorized command source GS_PRIMARY '))]
    network = timed('network_seconds', lambda: detect_network_alerts(data['network'], network_baseline))
    system = timed('system_seconds', lambda: detect_system_alerts(data['system_events']))
    _, original_ml = timed('original_if_seconds', lambda: score_alerts(features, profiles['original'], profiles['thresholds']['original']))
    scores, calibrated_ml = timed('candidate_if_seconds', lambda: score_alerts(features, profiles['candidate'], profiles['thresholds']['calibrated']))
    full_day_ml = alerts_from_scores(features, scores, profiles['thresholds']['full_day_uncalibrated'])
    methods = {
        'Rules only': rules, 'ML original': original_ml, 'ML calibrated': calibrated_ml,
        'Network only': network, 'System only': system,
        'Original hybrid': original_rules + original_ml + network + system,
        'Full-day uncalibrated hybrid': rules + full_day_ml + network + system,
        'Improved hybrid': rules + calibrated_ml + network + system,
        'Without ML': rules + network + system,
        'Without network': rules + calibrated_ml + system,
        'Without rules': calibrated_ml + network + system,
    }
    timeline = pd.DatetimeIndex(data['telemetry'].timestamp)
    comparisons = {method: measure(timeline, events, alerts) for method, alerts in methods.items()}
    security = {}
    for method in ('Original hybrid', 'Improved hybrid'):
        # R2 explain_alerts expects its legacy bin time; restore that field just
        # for explanation, which supplies the causal observed_at used downstream.
        alerts = [dict(a, timestamp=pd.Timestamp(a['timestamp']).floor('min')) if a['source']=='R2' else a
                  for a in methods[method]]
        evidence = timed(method+'_explanation_seconds', lambda: explain_alerts(alerts, data, profiles['nominal_features'], features))
        incidents = timed(method+'_correlation_seconds', lambda: correlate_alerts(evidence, config['correlation_window_seconds']))
        incident_metrics = measure_incidents(incidents, evidence, events, coordinated)
        incident_metrics['unmatched_groups_per_hour'] = incident_metrics['unmatched_groups']/config['hours']
        if name == 'E7':
            anchor = pd.Timestamp('2026-01-01T12:00Z')
            review_times = [anchor+pd.Timedelta(seconds=s) for s in (0,20,45,86,100,120,160,180)]
        else:
            review_times = [max(pd.Timestamp(e['end']) for e in events) if events else timeline[len(timeline)//2]]
        reviews = []
        for timestamp in review_times:
            snapshot = trust_snapshot(evidence, timestamp, config['correlation_window_seconds'])
            reviews.append(dict(at=timestamp.isoformat(), score=snapshot['score'],
                                contributors=snapshot['contributors'],
                                subsystems=subsystem_statuses(snapshot), incidents=len(snapshot['incidents'])))
        security[method] = dict(incidents=incident_metrics, reviews=reviews)
    shared = sum(timings[k] for k in ('feature_seconds','rules_seconds','network_seconds','system_seconds'))
    timings['original_detection_processing_seconds'] = shared+timings['original_if_seconds']
    timings['candidate_detection_processing_seconds'] = shared+timings['candidate_if_seconds']
    return dict(case=name, ground_truth=events, comparisons=comparisons, security=security, processing=timings)


def acceptance(cases):
    standard = [c for c in cases if c['case'] in {f'E{i}' for i in range(1,8)}]
    original_fp = sum(c['comparisons']['Original hybrid']['seconds']['fp'] for c in standard)
    candidate_fp = sum(c['comparisons']['Improved hybrid']['seconds']['fp'] for c in standard)
    def preserves(before, after):
        return all({e['id'] for e in c['comparisons'][before]['events']['details'] if e['detected']}.issubset(
                   {e['id'] for e in c['comparisons'][after]['events']['details'] if e['detected']}) for c in standard)
    no_event_loss = preserves('Original hybrid', 'Improved hybrid')
    no_ml_event_loss = preserves('ML original', 'ML calibrated')
    return dict(accepted=candidate_fp < original_fp and no_event_loss and no_ml_event_loss,
                original_fp_seconds=original_fp, candidate_fp_seconds=candidate_fp,
                no_standard_event_coverage_loss=no_event_loss,
                no_standard_ml_event_coverage_loss=no_ml_event_loss)


def run_study(output, protocol_path, stage='all'):
    from tekclipse.evaluation.study_report import export_tables

    config = json.loads(Path(protocol_path).read_text(encoding='utf-8'))
    validate_roles(config)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    started = perf_counter()
    with MemorySample(config['memory_sample_interval_seconds']) as memory:
        training = generate_synthetic_dataset(config['hours'], persist=False, seed=config['training_seed'])
        calibration = generate_synthetic_dataset(config['hours'], persist=False, seed=config['calibration_seed'])
        fit_start = perf_counter()
        profiles = fit_profiles(training['telemetry'], calibration['telemetry'], config)
        fit_seconds = perf_counter()-fit_start
        network_baseline = fit_network_baseline(training['network'].iloc[:config['original_train_hours']*3600])
        manifest = dict(protocol=config, protocol_hash=digest(config), source_hash=source_digest(),
                        training_fingerprint=fingerprint(training), calibration_fingerprint=fingerprint(calibration),
                        thresholds=profiles['thresholds'], network_baseline=network_baseline)
        # All fitted state/choices are fixed before held-out runs are generated.
        freeze_path = output/'frozen-validation.json'
        if stage in ('all', 'validation'):
            from tekclipse.evaluation.calibration_study import calibration_grid

            selection = calibration_grid(config)
            write_json(output/'calibration-grid.json',selection)
            if selection['selected_quantile'] != config['calibration_quantile']:
                raise ValueError('Configured quantile does not match the validation-only selection rule')
            validation = run_seeds(config['validation_seeds'], config, profiles, network_baseline)
            decision = acceptance(validation)
            write_json(output/'validation.json', dict(manifest=manifest, decision=decision, cases=validation))
            write_json(freeze_path, dict(manifest=manifest, decision=decision))
            export_tables(validation, output/'validation')
            print('Validation decision:', decision, flush=True)
        if stage in ('all', 'test'):
            if not freeze_path.exists():
                raise ValueError('Run validation first; a frozen selection artifact is required')
            frozen = json.loads(freeze_path.read_text(encoding='utf-8'))
            if frozen['manifest'] != manifest:
                raise ValueError('Protocol, source, training or calibration changed since selection; revalidate before testing')
            # Failed candidates are retained as negative experimental evidence,
            # not silently promoted. This flag is carried into every report.
            test_cases = run_seeds(config['test_seeds'], config, profiles, network_baseline)
            stable = [{k:v for k,v in c.items() if k!='processing'} for c in test_cases]
            report = dict(manifest=manifest, validation_decision=frozen['decision'],
                          results_digest=digest(stable), cases=test_cases)
            write_json(output/'test.json', report)
            export_tables(test_cases, output/'test')
    environment = dict(python=platform.python_version(), platform=platform.platform(),
                       machine=platform.machine(), processor=platform.processor(),
                       logical_cpus=psutil.cpu_count(), physical_cpus=psutil.cpu_count(logical=False),
                       installed_ram_mb=psutil.virtual_memory().total/2**20,
                       packages={name:importlib.metadata.version(name) for name in ('numpy','pandas','scikit-learn','psutil','streamlit')})
    write_json(output/'runtime.json', dict(environment=environment, fit_and_calibration_seconds=fit_seconds,
                                         total_seconds=perf_counter()-started, memory=memory.report(),
                                         note='Batch detector processing excludes data generation, model fitting, explanation, correlation and metrics; each is labeled separately. Not stream ingestion latency.'))
    return output


def run_seeds(seeds, config, profiles, network_baseline):
    cases = []
    for seed in seeds:
        nominal = generate_synthetic_dataset(config['hours'], persist=False, seed=seed)
        nominal_fingerprint = fingerprint(nominal)
        for name in config['scenarios']+config['variants']:
            data, events, coordinated = make_case(nominal, name, config, seed)
            row = run_case(data, events, coordinated, name, profiles, network_baseline, config)
            row.update(seed=seed, nominal_fingerprint=nominal_fingerprint, dataset_fingerprint=fingerprint(data))
            cases.append(row)
            before = row['comparisons']['Original hybrid']['seconds']
            after = row['comparisons']['Improved hybrid']['seconds']
            print(f"seed={seed} {name}: FP seconds {before['fp']} -> {after['fp']}; TP {before['tp']} -> {after['tp']}", flush=True)
    return cases
