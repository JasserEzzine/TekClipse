from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def build_model(train_features: pd.DataFrame, contamination: float = 0.05, random_state: int = 42) -> tuple[IsolationForest, np.ndarray]:
    model = IsolationForest(n_estimators=100, contamination=contamination, random_state=random_state)
    model.fit(train_features)
    score = -model.decision_function(train_features)
    threshold = float(np.quantile(score, 1 - contamination))
    return model, np.array(score)


def compute_ml_alerts(model: IsolationForest, df: pd.DataFrame, threshold: float):
    features = df.select_dtypes(include=["number"]).copy()
    if features.empty:
        return []
    scores = -model.decision_function(features)
    alerts = []
    for idx, score in enumerate(scores):
        if score > threshold:
            alerts.append({
                "timestamp": df.iloc[idx].get("timestamp"),
                "source": "ML",
                "severity": "WARNING",
                "description": "Isolation Forest deviation from nominal profile",
                "score": float(score),
            })
    return alerts
