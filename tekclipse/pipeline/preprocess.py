from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd


def clean_and_resample(data: dict, hz: int = 1) -> dict:
    out = {}
    for key, df in data.items():
        if isinstance(df, pd.DataFrame):
            if "timestamp" in df.columns:
                df = df.copy()
                df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
                df = df.sort_values("timestamp").drop_duplicates(subset=["timestamp"], keep="last")
                if hz != 1:
                    df = df.set_index("timestamp").resample(f"{hz}s").mean().reset_index()
            out[key] = df
        else:
            out[key] = df
    return out


def zscore_train_stats(data: pd.DataFrame, feature_cols: list[str]) -> dict:
    stats = {}
    for col in feature_cols:
        mean = float(data[col].mean())
        std = float(data[col].std(ddof=0))
        stats[col] = {"mean": mean, "std": max(std, 1e-6)}
    return stats


def normalized_features(data: pd.DataFrame, stats: dict, feature_cols: list[str]) -> pd.DataFrame:
    out = data.copy()
    for col in feature_cols:
        mean = stats[col]["mean"]
        std = stats[col]["std"]
        out[f"{col}_z"] = (out[col] - mean) / std
    return out
