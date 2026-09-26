from __future__ import annotations

import time
from typing import Dict, List

import numpy as np
import psutil


def precision_score(tp: int, fp: int) -> float:
    if tp + fp == 0:
        return 0.0
    return tp / (tp + fp)


def recall_score(tp: int, fn: int) -> float:
    if tp + fn == 0:
        return 0.0
    return tp / (tp + fn)


def f1_score(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def false_positive_rate(fp: int, tn: int) -> float:
    total = fp + tn
    if total == 0:
        return 0.0
    return fp / total


def latency_ms(first_alert_ts, onset_ts) -> float:
    if first_alert_ts is None or onset_ts is None:
        return float("nan")
    return (first_alert_ts - onset_ts).total_seconds() * 1000.0


def cpu_ram_overhead() -> Dict[str, float]:
    process = psutil.Process()
    mem = process.memory_info().rss / (1024 * 1024)
    cpu = process.cpu_percent(interval=None)
    return {"cpu_percent": float(cpu), "ram_mb": float(mem)}


def compute_metrics(tp: int, fp: int, tn: int, fn: int, first_alert_ts=None, onset_ts=None):
    p = precision_score(tp, fp)
    r = recall_score(tp, fn)
    f1 = f1_score(p, r)
    fpr = false_positive_rate(fp, tn)
    latency = latency_ms(first_alert_ts, onset_ts)
    overhead = cpu_ram_overhead()
    return {
        "precision": p,
        "recall": r,
        "f1": f1,
        "fpr": fpr,
        "latency_ms": latency,
        "cpu_percent": overhead["cpu_percent"],
        "ram_mb": overhead["ram_mb"],
    }
