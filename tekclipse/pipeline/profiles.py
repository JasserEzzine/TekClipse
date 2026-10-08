"""Shared, independently fitted scientific profiles for CLI and Streamlit.

The original dashboard preview remains implemented by data_service.detect.
Scientific profiles never fit on the data passed to infer_profile.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from tekclipse.data.generator import generate_synthetic_dataset
from tekclipse.pipeline.model import build_model
from tekclipse.pipeline.research_features import fit_relationships, research_features, representative_nominal
from tekclipse.pipeline.rules import detect_rule_alerts
from tekclipse.pipeline.network import fit_network_baseline, detect_network_alerts
from tekclipse.pipeline.explain import detect_system_alerts, explain_alerts
from tekclipse.pipeline.correlation import correlate_alerts

CONFIG_PATH = Path(__file__).with_name('detection_profiles.json')
PROFILE_LABELS = {
    'original': 'Original preview (default)',
    'phase_a': 'Phase A calibrated (experimental)',
    'phase_a2': 'Phase A.2 hardened (experimental)',
}


def profile_config(name):
    configs = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
    if name not in configs:
        raise ValueError('Unknown scientific detection profile')
    return configs[name]


def configuration_digest(config):
    return 'sha256:' + hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()


def fit_profile(name):
    config = profile_config(name)
    training = generate_synthetic_dataset(config['hours'], persist=False, seed=config['training_seed'])
    calibration = generate_synthetic_dataset(config['hours'], persist=False, seed=config['calibration_seed'])
    relationships = fit_relationships(training['telemetry'])
    features = research_features(representative_nominal(training['telemetry'], config['training_seed'], config['feature_mode']), config['feature_mode'], relationships)
    cal_features = research_features(representative_nominal(calibration['telemetry'], config['calibration_seed'], config['feature_mode']), config['feature_mode'], relationships)
    model, _ = build_model(features.select_dtypes(include='number'), random_state=config['model_seed'])
    cal_scores = -model.decision_function(cal_features.select_dtypes(include='number'))
    threshold = float(np.quantile(cal_scores, config['quantile']))
    # Keep the same independent network reference as Phase A for a fair comparison.
    net_training = generate_synthetic_dataset(24, persist=False, seed=config['network_training_seed'])
    network = fit_network_baseline(net_training['network'].iloc[:6*3600])
    metadata = dict(name=name, label=PROFILE_LABELS[name], config=config,
                    config_digest=configuration_digest(config), threshold=threshold,
                    train_samples=len(features), calibration_samples=len(cal_features),
                    feature_columns=list(features.select_dtypes(include='number').columns),
                    relationships=relationships,
                    raw_equals_emitted_ml=True, production_validated=False)
    return dict(model=model, threshold=threshold, nominal_features=features,
                relationships=relationships, network=network, metadata=metadata)


def infer_profile(bundle, data, *, explain=True):
    config = bundle['metadata']['config']
    features = research_features(data['telemetry'], config['feature_mode'], bundle['relationships'])
    scores = -bundle['model'].decision_function(features.select_dtypes(include='number'))
    ml = [dict(timestamp=features.timestamp.iloc[i], source='ML', severity='WARNING',
               description='Isolation Forest deviation from nominal profile', score=float(scores[i]))
          for i in np.flatnonzero(scores > bundle['threshold'])]
    rules = detect_rule_alerts(data['commands'], data['telemetry'], r2_mode=config['r2_mode'])
    network = detect_network_alerts(data['network'], bundle['network'], authorized_flows=config['authorized_flows'])
    system = detect_system_alerts(data['system_events'])
    raw = rules + ml + network + system
    if explain:
        evidence = explain_alerts(raw, data, bundle['nominal_features'], features)
    else:
        evidence = [dict(a, id=f'A-{i:06d}', observed_at=pd.Timestamp(a['timestamp']).isoformat()) for i, a in enumerate(raw)]
        if config['r2_mode'] == 'fixed':
            observed = {minute: frame.sort_values('timestamp').timestamp.iloc[10]
                        for minute, frame in data['commands'].groupby(pd.Grouper(key='timestamp', freq='min')) if len(frame)>10}
            for alert in evidence:
                if alert['source'] == 'R2':
                    alert['observed_at'] = observed[pd.Timestamp(alert['timestamp'])].isoformat()
    incidents = correlate_alerts(evidence, config['correlation_window_seconds'], policy=config['correlation_policy'])
    return dict(evidence=evidence, incidents=incidents, scores=scores, features=features,
                components={name: [a for a in evidence if a['source'] in sources]
                            for name, sources in [('rules', {'R1','R2','R3'}), ('ml', {'ML'}), ('network', {'NET'}), ('system', {'SYS'})]},
                window_seconds=config['correlation_window_seconds'], correlation_policy=config['correlation_policy'])
