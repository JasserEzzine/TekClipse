"""Opt-in research calibration; established dashboard scoring stays unchanged."""
from __future__ import annotations

import numpy as np
import pandas as pd
from tekclipse.evaluation.validated import FEATURES
from tekclipse.evaluation.runner import _feature_matrix
from tekclipse.pipeline.model import build_model


def feature_frame(telemetry):
    """Reject incomplete data rather than silently imputing or scoring timestamps."""
    if telemetry.empty or not set(FEATURES).issubset(telemetry.columns):
        raise ValueError('Complete nonempty telemetry with all seven channels is required')
    times = telemetry.timestamp
    if times.dt.tz is None or not times.is_monotonic_increasing or times.duplicated().any():
        raise ValueError('Telemetry timestamps must be ordered, unique and timezone-aware')
    if len(times) > 1 and not times.diff().iloc[1:].eq(pd.Timedelta(seconds=1)).all():
        raise ValueError('Rolling features require a complete 1 Hz run')
    if not np.isfinite(telemetry[FEATURES].to_numpy(dtype=float)).all():
        raise ValueError('Missing or nonfinite telemetry must be resolved before research evaluation')
    return _feature_matrix(telemetry[['timestamp', *FEATURES]], FEATURES)


def fit_profiles(training, calibration, config):
    """Fitting and calibration accept nominal frames only; callers enforce run roles."""
    early = feature_frame(training.iloc[:config['original_train_hours']*3600])
    full = feature_frame(training)
    calibration_features = feature_frame(calibration)
    original, original_scores = build_model(early.select_dtypes(include='number'),
                                            random_state=config['model_seed'])
    candidate, candidate_scores = build_model(full.select_dtypes(include='number'),
                                              random_state=config['model_seed'])
    cal_scores = -candidate.decision_function(calibration_features.select_dtypes(include='number'))
    return dict(original=original, candidate=candidate, nominal_features=full,
                thresholds=dict(original=float(np.quantile(original_scores, config['original_quantile'])),
                                full_day_uncalibrated=float(np.quantile(candidate_scores, config['original_quantile'])),
                                calibrated=float(np.quantile(cal_scores, config['calibration_quantile']))))
