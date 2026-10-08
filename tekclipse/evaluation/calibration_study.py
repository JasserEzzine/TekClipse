"""Reproduce validation-only threshold selection; never generate test runs."""
from __future__ import annotations

import numpy as np
import pandas as pd

from tekclipse.data.generator import generate_synthetic_dataset
from tekclipse.data.injection import get_scenario
from tekclipse.evaluation.study_data import standard_events, validate_roles
from tekclipse.evaluation.scientific_metrics import truth_mask
from tekclipse.pipeline.calibration import feature_frame, fit_profiles


def calibration_grid(config):
    validate_roles(config)
    training = generate_synthetic_dataset(config['hours'],persist=False,seed=config['training_seed'])
    calibration = generate_synthetic_dataset(config['hours'],persist=False,seed=config['calibration_seed'])
    profiles = fit_profiles(training['telemetry'],calibration['telemetry'],config)
    calibration_features = feature_frame(calibration['telemetry']).select_dtypes(include='number')
    scores_cal = -profiles['candidate'].decision_function(calibration_features)
    candidates = {q:float(np.quantile(scores_cal,q)) for q in config['calibration_candidates']}
    rows = []
    for seed in config['validation_seeds']:
        nominal = generate_synthetic_dataset(config['hours'],persist=False,seed=seed)
        for scenario in config['scenarios']:
            data,_ = get_scenario(scenario)(nominal)
            features = feature_frame(data['telemetry']).select_dtypes(include='number')
            old = -profiles['original'].decision_function(features)
            new = -profiles['candidate'].decision_function(features)
            timeline = pd.DatetimeIndex(data['telemetry'].timestamp)
            events = standard_events(scenario)
            truth = truth_mask(timeline,events)

            def detected(scores, threshold):
                return [e['id'] for e in events if 'ML' in e['detectors'] and
                        ((scores>threshold) & (timeline>=pd.Timestamp(e['start'])) &
                         (timeline<=pd.Timestamp(e['end']))).any()]

            original_events = detected(old, profiles['thresholds']['original'])
            for q,threshold in candidates.items():
                candidate_events = detected(new,threshold)
                rows.append(dict(seed=seed,scenario=scenario,quantile=q,threshold=threshold,
                                 original_detected_events=original_events,candidate_detected_events=candidate_events,
                                 original_tp=int(((old>profiles['thresholds']['original'])&truth).sum()),
                                 candidate_tp=int(((new>threshold)&truth).sum()),
                                 original_fp=int(((old>profiles['thresholds']['original'])&~truth).sum()),
                                 candidate_fp=int(((new>threshold)&~truth).sum()),
                                 preserves_ml_events=set(original_events).issubset(candidate_events)))
    eligible = [q for q in candidates if all(r['preserves_ml_events'] for r in rows if r['quantile']==q)
                and sum(r['candidate_fp'] for r in rows if r['quantile']==q)<sum(r['original_fp'] for r in rows if r['quantile']==q)]
    return dict(selected_quantile=max(eligible) if eligible else None,
                selection='Largest tested quantile reducing FP while retaining every original source-matched ML event on validation runs. This does not preserve sample recall or detection delay.',
                rows=rows)
