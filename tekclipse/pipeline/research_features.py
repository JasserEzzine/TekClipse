"""Nominal-fitted feature candidates; all temporal statistics are trailing only."""
from __future__ import annotations

import numpy as np
import pandas as pd

from tekclipse.pipeline.calibration import feature_frame

RELATIONSHIPS = {
    "voltage_battery_residual": ("voltage_v", ["battery_percent"]),
    "power_cpu_ram_residual": ("power_w", ["cpu_percent", "ram_percent"]),
}


def representative_nominal(telemetry, seed, mode):
    """Explicit nominal noise augmentation, never used on inference data.

    Alternate 90-minute blocks cover both declared nominal sensor noise regimes.
    Seeded additional noise: temperature SD .5 C and CPU SD 1 percentage point.
    No anomaly, event label, or threshold-exceeding injection is fitted.
    """
    result = telemetry.copy()
    if mode == 'noise21':
        rng = np.random.default_rng(seed + 20000)
        noisy = (np.arange(len(result)) // 5400) % 2 == 1
        for column, sd in [('temperature_c', .5), ('cpu_percent', 1.0)]:
            result[column] += rng.normal(0, sd, len(result)) * noisy
    return result


def fit_relationships(nominal):
    """OLS coefficients fit nominal telemetry only; not scenario/label aware."""
    fitted = {name: np.linalg.lstsq(
        np.column_stack([np.ones(len(nominal)), nominal[predictors]]),
        nominal[target], rcond=None)[0].tolist()
        for name, (target, predictors) in RELATIONSHIPS.items()}
    fitted['temperature_context'] = np.linalg.lstsq(temperature_context(nominal.timestamp), nominal.temperature_c, rcond=None)[0].tolist()
    return fitted


def temperature_context(timestamps):
    # Simulator's declared 90-minute orbit; fitted amplitudes and secular trend.
    # No scenario input, attack labels, or future telemetry enters this basis.
    seconds = (timestamps - pd.Timestamp('2026-01-01T00:00:00Z')).dt.total_seconds().to_numpy()
    phase = 2 * np.pi * seconds / 5400
    return np.column_stack([np.ones(len(seconds)), np.sin(phase), np.cos(phase), seconds / 86400])


def research_features(telemetry, mode, relationships=None):
    full = feature_frame(telemetry)
    if mode in {"all21", "noise21"}:
        return full
    if mode not in {"means7", "relationships9", "context3"}:
        raise ValueError("Unknown research feature mode")
    features = full[["timestamp", *[c for c in full if c.endswith("_rolling_mean_60s")]]].copy()
    if mode in {"relationships9", "context3"}:
        if relationships is None:
            raise ValueError("Nominal-fitted relationship coefficients are required")
        for name, (target, predictors) in RELATIONSHIPS.items():
            prediction = np.column_stack([np.ones(len(telemetry)), telemetry[predictors]]) @ np.asarray(relationships[name])
            residual = telemetry[target].to_numpy() - prediction
            features[name + "_rolling_mean_60s"] = pd.Series(residual, index=features.index).rolling(60, min_periods=1).mean()
    if mode == 'context3':
        residual = telemetry.temperature_c.to_numpy() - temperature_context(telemetry.timestamp) @ np.asarray(relationships['temperature_context'])
        features['temperature_context_residual_rolling_mean_60s'] = pd.Series(residual, index=features.index).rolling(60, min_periods=1).mean()
        features = features[['timestamp', *[c for c in features if '_residual_' in c]]]
    return features
