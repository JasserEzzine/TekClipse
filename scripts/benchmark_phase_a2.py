"""Frozen Phase A.2 test matrix. Model/threshold selection happens separately."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from tekclipse.data.generator import generate_synthetic_dataset
from tekclipse.evaluation.phase_a2_data import make_a2_case
from tekclipse.evaluation.scientific import write_json, digest, source_digest, MemorySample
from tekclipse.evaluation.scientific_metrics import measure, measure_incidents
from tekclipse.evaluation.study_data import fingerprint
from tekclipse.pipeline.profiles import fit_profile, infer_profile
from tekclipse.pipeline.trust import trust_snapshot
from tekclipse.pipeline.subsystems import subsystem_statuses

ROOT = Path(__file__).resolve().parents[1]


def study(output):
    started = perf_counter()
    protocol = json.loads((ROOT/'docs/phase-a2/protocol.json').read_text())
    phase_a = json.loads((ROOT/'docs/phase-a/protocol.json').read_text())
    selection = json.loads((ROOT/'docs/phase-a2/selection.json').read_text())
    if selection['protocol_hash'] != 'sha256:' + digest(protocol):
        raise ValueError('Selection protocol has changed; revalidate before test')
    before, after = fit_profile('phase_a'), fit_profile('phase_a2')
    chosen = selection['selected']
    config = after['metadata']['config']
    if chosen is None or config['feature_mode'] != chosen['mode'] or config['quantile'] != chosen['quantile'] or abs(after['threshold']-chosen['threshold']) > 1e-12:
        raise ValueError('Profile differs from the validation selection')
    archived = json.loads((ROOT/'docs/phase-a/results/test.json').read_text())
    lookup = {(c['seed'], c['case']): c for c in archived['cases']}
    manifest = dict(protocol=protocol, protocol_hash='sha256:'+digest(protocol),
                    source_hash='sha256:'+source_digest(),
                    selection_hash='sha256:'+digest(selection),
                    profiles={'Phase A':before['metadata'], 'Phase A.2':after['metadata']})
    output = Path(output)
    if (output/'test.json').exists():
        raise ValueError('Use a new output directory to preserve existing test evidence')
    # Freeze the selected state BEFORE generating any test run.
    write_json(output/'frozen.json', manifest)
    rows = []
    with MemorySample(.02) as memory:
        for seed in protocol['regression_test_seeds'] + protocol['test_seeds']:
            nominal = generate_synthetic_dataset(24, persist=False, seed=seed)
            names = phase_a['scenarios'] + phase_a['variants'] if seed in protocol['regression_test_seeds'] else ['E1', 'E7'] + protocol['novel_cases']
            nominal_ml_times = {}
            for name in names:
                case_started = perf_counter()
                data, events, coordinated = make_a2_case(nominal, name, protocol, phase_a, seed)
                data_hash = 'sha256:'+fingerprint(data)
                historical = lookup.get((seed, name))
                if historical and historical['dataset_fingerprint'] != data_hash:
                    raise ValueError(f'Frozen regression data changed: {seed}/{name}')
                old = infer_profile(before, data, explain=False)
                inference_started = perf_counter()
                new = infer_profile(after, data, explain=True)
                inference_seconds = perf_counter() - inference_started
                r, m, n, s = (new['components'][k] for k in ('rules','ml','network','system'))
                old_r, old_m, old_n, old_s = (old['components'][k] for k in ('rules','ml','network','system'))
                if name == 'E1':
                    nominal_ml_times = {label:{pd.Timestamp(a['observed_at']) for a in alerts}
                                        for label, alerts in [('Phase A',old_m), ('Phase A.2',m)]}
                incremental = {}
                if name.startswith('operational_'):
                    start, end = pd.Timestamp(events[0]['start']), pd.Timestamp(events[0]['end'])
                    for label, alerts in [('Phase A',old_m), ('Phase A.2',m)]:
                        hits = {pd.Timestamp(a['observed_at']) for a in alerts if start <= pd.Timestamp(a['observed_at']) <= end}
                        baseline_hits = {t for t in nominal_ml_times[label] if start <= t <= end}
                        new_hits = hits - baseline_hits
                        incremental[label] = dict(anomaly_alert_seconds_in_window=len(hits),
                            paired_nominal_alert_seconds_in_window=len(baseline_hits),
                            newly_flagged_seconds=len(new_hits), incremental_event_detected=bool(new_hits),
                            first_new_flag_delay_seconds=(min(new_hits)-start).total_seconds() if new_hits else None,
                            note='Paired nominal counterfactual; new flags support sensitivity to the change, not malicious intent or causal diagnosis.')
                methods = {
                    'Phase A hybrid': old['evidence'], 'Phase A ML': old_m,
                    'Phase A.2 hybrid': new['evidence'], 'Rules only': r, 'ML only': m,
                    'Network only': n, 'Without ML': r+n+s,
                    'Without network': r+m+s, 'Without rules': m+n+s,
                    'Phase A ML + rolling R2': r+old_m+old_n+s,
                    'Phase A ML + authorized network': old_r+old_m+n+s,
                    'Phase A.2 ML + legacy rules/network': old_r+m+old_n+s,
                }
                timeline = pd.DatetimeIndex(data['telemetry'].timestamp)
                comparisons = {method:measure(timeline, events, alerts) for method, alerts in methods.items()}
                if historical:
                    if comparisons['Phase A hybrid'] != historical['comparisons']['Improved hybrid']:
                        raise ValueError(f'Phase A baseline drift: {seed}/{name}')
                    comparisons['Historical original hybrid'] = historical['comparisons']['Original hybrid']
                security = {}
                for label, inferred, policy in [('Phase A hybrid', old, 'legacy'), ('Phase A.2 hybrid', new, 'supported')]:
                    incidents = measure_incidents(inferred['incidents'], inferred['evidence'], events, coordinated)
                    incidents['unmatched_groups_per_hour'] = incidents['unmatched_groups']/24
                    times = [pd.Timestamp('2026-01-01T12:00Z')+pd.Timedelta(seconds=s) for s in (0,20,45,86,100,120,160,180)] if name == 'E7' else [max(pd.Timestamp(e['end']) for e in events) if events else timeline[len(timeline)//2]]
                    reviews = []
                    for at in times:
                        snapshot = trust_snapshot(inferred['evidence'], at, correlation_policy=policy)
                        reviews.append(dict(at=at.isoformat(), score=snapshot['score'], contributors=snapshot['contributors'],
                                            incidents=len(snapshot['incidents']), **({'subsystems':subsystem_statuses(snapshot)} if label == 'Phase A.2 hybrid' else {})))
                    security[label] = dict(incidents=incidents, reviews=reviews)
                row = dict(seed=seed, case=name, kind='operational anomaly (not cyberattack)' if name.startswith('operational_') else 'nominal' if name.startswith(('nominal_', 'benign_')) or name=='E1' else 'known synthetic attack',
                           dataset_fingerprint=data_hash, nominal_fingerprint='sha256:'+fingerprint(nominal),
                           ground_truth=events, comparisons=comparisons, security=security, ml_incremental=incremental,
                           ml_raw_anomalous_observations=int((new['scores'] > after['threshold']).sum()),
                           ml_emitted_alerts=len(m), processing=dict(inference_explanation_correlation_seconds=inference_seconds, total_case_seconds=perf_counter()-case_started))
                rows.append(row)
                write_json(output/'checkpoint.json', dict(manifest=manifest, cases=rows))
                print(f"seed={seed} {name}: FP {comparisons['Phase A hybrid']['seconds']['fp']} -> {comparisons['Phase A.2 hybrid']['seconds']['fp']}; events {comparisons['Phase A.2 hybrid']['events']['detected']}/{len(events)}", flush=True)
    semantic = [{k:v for k,v in row.items() if k != 'processing'} for row in rows]
    write_json(output/'test.json', dict(manifest=manifest, cases=rows, results_digest='sha256:'+digest(semantic)))
    flat = []
    for row in rows:
        for method, values in row['comparisons'].items():
            flat.append(dict(seed=row['seed'], case=row['case'], kind=row['kind'], method=method,
                             **values['seconds'], source_matched_events=values['events']['detected'],
                             source_matched_event_total=values['events']['total'], source_matched_event_recall=values['events']['recall'],
                             mean_source_matched_delay_seconds=values['events']['mean_detection_delay_seconds']))
    pd.DataFrame(flat).to_csv(output/'metrics.csv', index=False)
    pd.DataFrame([dict(seed=r['seed'],case=r['case'],method=m,**s['incidents']) for r in rows for m,s in r['security'].items()]).to_csv(output/'incidents.csv', index=False)
    write_json(output/'runtime.json', dict(seconds=perf_counter()-started, memory=memory.report()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'results/phase-a2')
    study(parser.parse_args().output)
