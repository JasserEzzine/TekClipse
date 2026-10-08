"""Validation-only feature/threshold selection. Never loads final test seeds."""
from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
import numpy as np
import pandas as pd
from time import perf_counter
from tekclipse.data.generator import generate_synthetic_dataset
from tekclipse.pipeline.model import build_model
from tekclipse.pipeline.research_features import fit_relationships, research_features, representative_nominal
from tekclipse.evaluation.phase_a2_data import make_a2_case
from tekclipse.evaluation.scientific import alerts_from_scores, write_json, digest
from tekclipse.evaluation.scientific_metrics import measure
from tekclipse.evaluation.study_data import fingerprint

ROOT = Path(__file__).resolve().parents[1]


def select():
    started = perf_counter()
    protocol = json.loads((ROOT/'docs/phase-a2/protocol.json').read_text())
    phase_a = json.loads((ROOT/'docs/phase-a/protocol.json').read_text())
    roles = [protocol['training_seed'], protocol['calibration_seed'], *protocol['validation_seeds'], *protocol['test_seeds'], *protocol['regression_test_seeds']]
    if len(roles) != len(set(roles)):
        raise ValueError('Run roles overlap')
    training = generate_synthetic_dataset(24, persist=False, seed=protocol['training_seed'])
    calibration = generate_synthetic_dataset(24, persist=False, seed=protocol['calibration_seed'])
    relationships = fit_relationships(training['telemetry'])
    candidates, fitted = [], {}
    for mode in protocol['feature_candidates']:
        features = research_features(representative_nominal(training['telemetry'], protocol['training_seed'], mode), mode, relationships)
        model, _ = build_model(features.select_dtypes(include='number'), random_state=protocol['model_seed'])
        cal = research_features(representative_nominal(calibration['telemetry'], protocol['calibration_seed'], mode), mode, relationships)
        scores = -model.decision_function(cal.select_dtypes(include='number'))
        fitted[mode] = model
        for quantile in protocol['quantile_candidates']:
            candidates.append(dict(mode=mode, quantile=quantile, threshold=float(np.quantile(scores, quantile)), cases=[]))
    for seed in protocol['validation_seeds']:
        nominal = generate_synthetic_dataset(24, persist=False, seed=seed)
        for name in protocol['validation_cases']:
            data, events, _ = make_a2_case(nominal, name, protocol, phase_a, seed)
            for mode, model in fitted.items():
                features = research_features(data['telemetry'], mode, relationships)
                scores = -model.decision_function(features.select_dtypes(include='number'))
                # Only telemetry-labeled events are relevant for ML acceptance.
                telemetry_events = [e for e in events if 'ML' in e['detectors']]
                for candidate in [c for c in candidates if c['mode'] == mode]:
                    alerts = alerts_from_scores(features, scores, candidate['threshold'])
                    candidate['cases'].append(dict(seed=seed, case=name, metrics=measure(pd.DatetimeIndex(features.timestamp), telemetry_events, alerts)))
            print(f'Validated seed={seed} case={name}', flush=True)
    benign = {'E1', 'benign_telemetry', 'nominal_thermal_regime', 'nominal_power_regime'}
    for candidate in candidates:
        cases = candidate['cases']
        candidate['eligible'] = all(c['metrics']['events']['detected'] == c['metrics']['events']['total'] for c in cases if c['case'] in {'E5', 'E7'})
        candidate['benign_fp_seconds'] = sum(c['metrics']['seconds']['fp'] for c in cases if c['case'] in benign)
        delays = [c['metrics']['events']['mean_detection_delay_seconds'] for c in cases if c['case'].startswith('operational_')]
        candidate['mean_operational_delay'] = float(np.mean(delays)) if all(d is not None for d in delays) else None
    reference = next(c for c in candidates if c['mode'] == 'all21' and c['quantile'] == .975)
    for candidate in candidates:
        candidate['eligible'] &= candidate['benign_fp_seconds'] < reference['benign_fp_seconds']
        candidate['operational_events_detected'] = sum(c['metrics']['events']['detected'] for c in candidate['cases'] if c['case'].startswith('operational_'))
    eligible = [c for c in candidates if c['eligible']]
    winner = min(eligible, key=lambda c: (c['benign_fp_seconds'], -c['operational_events_detected'], c['mode'], c['quantile'])) if eligible else None
    selected = {k: v for k, v in winner.items() if k != 'cases'} if winner else None
    result = dict(protocol_hash='sha256:'+digest(protocol), selected=selected, candidates=candidates,
                  training_fingerprint='sha256:'+fingerprint(training), calibration_fingerprint='sha256:'+fingerprint(calibration),
                  relationships=relationships, seconds=perf_counter()-started,
                  note='No test seeds loaded. All raw scores above threshold emit alerts; no persistence suppression.')
    write_json(ROOT/'docs/phase-a2/selection.json', result)
    print(json.dumps(selected), flush=True)


if __name__ == '__main__':
    select()
