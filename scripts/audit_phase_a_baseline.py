"""Reproduce the historical protocol and attribute its false-positive seconds."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
from tekclipse.data.generator import generate_synthetic_dataset
from tekclipse.data.injection import get_scenario
from tekclipse.data.coordinated import ground_truth_intervals
from tekclipse.evaluation.runner import _feature_matrix
from tekclipse.evaluation.validated import FEATURES, labeled_metrics
from tekclipse.pipeline.model import build_model, compute_ml_alerts
from tekclipse.pipeline.rules import detect_rule_alerts
from tekclipse.pipeline.network import fit_network_baseline, detect_network_alerts
from tekclipse.pipeline.explain import detect_system_alerts


def audit():
    started = perf_counter()
    nominal = generate_synthetic_dataset(24, persist=False)
    split = pd.Timestamp('2026-01-01T06:00Z')
    train = _feature_matrix(nominal['telemetry'].iloc[:21600], FEATURES)
    model, scores = build_model(train.select_dtypes(include='number'))
    threshold = float(np.quantile(scores, .95))
    baseline = fit_network_baseline(nominal['network'].iloc[:21600])
    results = {}
    nominal_ml = None
    for scenario in [f'E{i}' for i in range(1, 8)]:
        data, _ = get_scenario(scenario)(nominal)
        data = {k: v.loc[v.timestamp >= split].copy() for k, v in data.items()}
        timeline = pd.DatetimeIndex(data['telemetry'].timestamp)
        intervals = ground_truth_intervals(scenario)
        truth = np.zeros(len(timeline), bool)
        for a, b in intervals:
            truth |= (timeline >= a) & (timeline <= b)
        features = _feature_matrix(data['telemetry'], FEATURES)
        timings = {}
        t = perf_counter()
        rules = detect_rule_alerts(data['commands'], data['telemetry'])
        timings['rules_seconds'] = perf_counter() - t
        burst = {minute: frame.sort_values('timestamp').timestamp.iloc[10]
                 for minute, frame in data['commands'].groupby(pd.Grouper(key='timestamp', freq='min')) if len(frame) > 10}
        for alert in rules:
            if alert['source'] == 'R2':
                alert['timestamp'] = burst[pd.Timestamp(alert['timestamp'])]
        t = perf_counter()
        ml = compute_ml_alerts(model, features, threshold)
        timings['ml_seconds'] = perf_counter() - t
        t = perf_counter()
        network = detect_network_alerts(data['network'], baseline)
        timings['network_seconds'] = perf_counter() - t
        system = detect_system_alerts(data['system_events'])
        methods = {'Rules only': rules, 'ML only': ml, 'Network only': network,
                   'System only': system, 'Hybrid': rules + ml + network + system}
        metrics = {name: labeled_metrics(timeline, truth, [a['timestamp'] for a in rows], intervals)
                   for name, rows in methods.items()}
        flags = timeline.isin(pd.to_datetime([a['timestamp'] for a in ml], utc=True))
        if scenario == 'E1':
            nominal_ml = flags
        diagnostics = {
            'raw_alerts': {name: len(rows) for name, rows in methods.items()},
            'ml_false_positive_seconds_shared_with_nominal': int((flags & ~truth & nominal_ml).sum()),
            'ml_false_positive_seconds_not_in_nominal': int((flags & ~truth & ~nominal_ml).sum()),
            'ml_false_positive_seconds_by_hour': {str(hour): int((flags & ~truth & (timeline.hour == hour)).sum()) for hour in range(6, 24)},
            'duplicate_alerts_do_not_increase_second_counts': True,
        }
        results[scenario] = dict(comparisons=metrics, diagnostics=diagnostics, processing=timings)
        print(scenario, metrics['Hybrid'], flush=True)
    return dict(baseline_commit='git:2b25015378564206a84d50ace8e3d0e906c46d7e',
                protocol='Historical same-run temporal split: 24h seed42, first6h nominal train, remaining18h test; training-score quantile .95; model seed42; 21 telemetry features',
                python=platform.python_version(), threshold=threshold, scenarios=results,
                runtime_seconds=perf_counter()-started,
                source_hashes={str(p.relative_to(ROOT)): 'sha256:'+hashlib.sha256(p.read_bytes()).hexdigest()
                               for folder in ['tekclipse', 'tests'] for p in sorted((ROOT/folder).rglob('*.py'))})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'results/phase-a-baseline.json')
    args = parser.parse_args()
    result = audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False), encoding='utf-8')
