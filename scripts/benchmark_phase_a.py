"""Measure complete E7 batch processing, separately from simulated detection delay."""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tekclipse.data.generator import generate_synthetic_dataset
from tekclipse.evaluation.study_data import fingerprint, make_case
from tekclipse.evaluation.scientific import MemorySample, score_alerts, write_json, source_digest
from tekclipse.pipeline.calibration import fit_profiles, feature_frame
from tekclipse.pipeline.rules import detect_rule_alerts
from tekclipse.pipeline.network import fit_network_baseline, detect_network_alerts
from tekclipse.pipeline.explain import detect_system_alerts, explain_alerts
from tekclipse.pipeline.correlation import correlate_alerts


def benchmark(study, repeats):
    frozen = json.loads((study/'frozen-validation.json').read_text())
    config = frozen['manifest']['protocol']
    if source_digest() != frozen['manifest']['source_hash']:
        raise ValueError('Benchmark requires unchanged frozen study source')
    training = generate_synthetic_dataset(config['hours'],persist=False,seed=config['training_seed'])
    calibration = generate_synthetic_dataset(config['hours'],persist=False,seed=config['calibration_seed'])
    profiles = fit_profiles(training['telemetry'],calibration['telemetry'],config)
    if profiles['thresholds'] != frozen['manifest']['thresholds']:
        raise ValueError('Benchmark model calibration differs from frozen study')
    network_baseline = fit_network_baseline(training['network'].iloc[:config['original_train_hours']*3600])
    seed = config['test_seeds'][-1]
    nominal = generate_synthetic_dataset(config['hours'],persist=False,seed=seed)
    data, _, _ = make_case(nominal,'E7',config,seed)
    rows = []
    with MemorySample(config['memory_sample_interval_seconds']) as memory:
        for iteration in range(repeats):
            for name,model,threshold in [
                ('Original hybrid',profiles['original'],profiles['thresholds']['original']),
                ('Improved hybrid',profiles['candidate'],profiles['thresholds']['calibrated']),
            ]:
                start = perf_counter()
                features = feature_frame(data['telemetry'])
                rules = detect_rule_alerts(data['commands'],data['telemetry'])
                _,ml = score_alerts(features,model,threshold)
                network = detect_network_alerts(data['network'],network_baseline)
                system = detect_system_alerts(data['system_events'])
                detector_end = perf_counter()
                evidence = explain_alerts(rules+ml+network+system,data,profiles['nominal_features'],features)
                incidents = correlate_alerts(evidence,config['correlation_window_seconds'])
                finish = perf_counter()
                rows.append(dict(iteration=iteration+1,method=name,
                                 detection_batch_seconds=detector_end-start,
                                 through_explanation_correlation_seconds=finish-start,
                                 alerts=len(evidence),incidents=len(incidents)))
                print(name,rows[-1],flush=True)
    summaries = {}
    for name in ('Original hybrid','Improved hybrid'):
        selected = [r for r in rows if r['method']==name]
        summaries[name] = {
            metric:dict(median=statistics.median(r[metric] for r in selected),
                        minimum=min(r[metric] for r in selected),maximum=max(r[metric] for r in selected))
            for metric in ('detection_batch_seconds','through_explanation_correlation_seconds')}
    return dict(seed=seed,scenario='E7',hours=config['hours'],repeats=repeats,
                dataset_fingerprint=fingerprint(data),summaries=summaries,measurements=rows,memory=memory.report(),
                note='Complete wall-clock batch processing from in-memory input through alerts, then evidence/correlation. Excludes generation, fitting, persistence, evaluation metrics and UI. Both profiles use output-equivalent optimized R3. Not streaming or spacecraft response latency; run on development hardware.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--study',type=Path,default=ROOT/'results/phase-a')
    parser.add_argument('--repeats',type=int,default=3)
    args=parser.parse_args()
    if not 1<=args.repeats<=20:
        parser.error('repeats must be between 1 and 20')
    write_json(args.study/'end-to-end-benchmark.json',benchmark(args.study,args.repeats))
