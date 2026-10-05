"""Explicitly labeled, held-out synthetic evaluation with one-second units."""

from __future__ import annotations

import numpy as np
import pandas as pd

from tekclipse.data.coordinated import ground_truth_intervals
from tekclipse.data.injection import get_scenario
from tekclipse.evaluation.runner import _feature_matrix
from tekclipse.pipeline.model import build_model, compute_ml_alerts
from tekclipse.pipeline.rules import detect_rule_alerts
from tekclipse.pipeline.network import fit_network_baseline, detect_network_alerts
from tekclipse.pipeline.explain import detect_system_alerts

FEATURES = [
    "temperature_c",
    "cpu_percent",
    "ram_percent",
    "battery_percent",
    "voltage_v",
    "power_w",
    "signal_dbm",
]


def labeled_metrics(timeline, truth, alert_times, intervals):
    """No inferred labels: None/partial labels produce an unavailable result.

    Precision/recall/FPR classify seconds with any alert. Detection rate is the
    fraction of labeled intervals with an alert; latency is measured only within
    each detected interval, never from a preceding nominal alert.
    """
    timeline = pd.DatetimeIndex(timeline)
    if (
        truth is None
        or len(truth) != len(timeline)
        or len(timeline) == 0
        or pd.isna(truth).any()
        or timeline.has_duplicates
        or not timeline.is_monotonic_increasing
        or not all(isinstance(v, (bool, np.bool_)) for v in truth)
    ):
        return dict(
            available=False,
            reason="Complete explicit boolean ground-truth labels and an ordered unique timeline are required.",
        )
    truth = np.asarray(truth, dtype=bool)
    times = pd.DatetimeIndex(pd.to_datetime(list(alert_times), utc=True)).floor("s")
    predicted = timeline.isin(times)
    tp, fp = int((truth & predicted).sum()), int((~truth & predicted).sum())
    fn, tn = int((truth & ~predicted).sum()), int((~truth & ~predicted).sum())
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None
    latencies = []
    for start, end in intervals:
        hits = times[(times >= start) & (times <= end)]
        if len(hits):
            latencies.append((hits.min() - start).total_seconds())
    return dict(
        available=True,
        tp=tp,
        fp=fp,
        tn=tn,
        fn=fn,
        precision=precision,
        recall=recall,
        f1=f1,
        false_positive_rate=fp / (fp + tn) if fp + tn else None,
        detection_rate=len(latencies) / len(intervals) if intervals else None,
        detection_latency_seconds=float(np.mean(latencies)) if latencies else None,
        detected_intervals=len(latencies),
        total_intervals=len(intervals),
        evaluated_seconds=len(timeline),
    )


def evaluate_held_out(nominal, scenario, train_hours=6):
    """Caller supplies untouched nominal simulator data, never an injected frame."""
    intervals = ground_truth_intervals(scenario)
    if intervals is None:
        return dict(
            available=False, reason="No explicit ground truth for this scenario."
        )
    telemetry = nominal["telemetry"]
    split = telemetry.timestamp.min() + pd.Timedelta(hours=train_hours)
    finish = telemetry.timestamp.max()
    if (
        train_hours < 1
        or split >= finish
        or any(a < split or b > finish for a, b in intervals)
    ):
        return dict(
            available=False,
            reason="Insufficient held-out coverage: all injected intervals must follow training and fit in the test timeline.",
        )
    nominal_train = telemetry[telemetry.timestamp < split]
    injected, _ = get_scenario(scenario)(nominal)
    test = injected["telemetry"].loc[lambda d: d.timestamp >= split]
    timeline = pd.DatetimeIndex(test.timestamp)
    if (
        len(timeline) < 2
        or not (timeline[1:] - timeline[:-1] == pd.Timedelta(seconds=1)).all()
    ):
        return dict(
            available=False, reason="Evaluation requires a complete 1 Hz test timeline."
        )
    train_features = _feature_matrix(nominal_train, FEATURES)
    model, scores = build_model(train_features.select_dtypes(include="number"))
    threshold = float(np.quantile(scores, 0.95))
    test_features = _feature_matrix(test, FEATURES)
    ml = compute_ml_alerts(model, test_features, threshold)
    commands = injected["commands"].loc[lambda d: d.timestamp >= split]
    rules = detect_rule_alerts(commands, test)
    # Observe R2 at the 11th command, not the legacy minute-bin label.
    burst_times = {
        minute: frame.sort_values("timestamp").timestamp.iloc[10]
        for minute, frame in commands.groupby(pd.Grouper(key="timestamp", freq="min"))
        if len(frame) > 10
    }
    for alert in rules:
        if alert["source"] == "R2":
            alert["timestamp"] = burst_times[pd.Timestamp(alert["timestamp"])]
    baseline = fit_network_baseline(
        nominal["network"].loc[lambda d: d.timestamp < split]
    )
    network = detect_network_alerts(
        injected["network"].loc[lambda d: d.timestamp >= split], baseline
    )
    system = detect_system_alerts(
        injected["system_events"].loc[lambda d: d.timestamp >= split]
    )
    truth = np.zeros(len(timeline), dtype=bool)
    for a, b in intervals:
        truth |= (timeline >= a) & (timeline <= b)
    methods = {
        "Rules only": rules,
        "ML only": ml,
        "Hybrid": rules + ml + network + system,
    }
    comparisons = {
        name: labeled_metrics(
            timeline, truth, [a["timestamp"] for a in alerts], intervals
        )
        for name, alerts in methods.items()
    }
    return dict(
        available=True,
        scenario=scenario,
        train_end=(split - pd.Timedelta(seconds=1)).isoformat(),
        test_start=split.isoformat(),
        test_end=finish.isoformat(),
        comparisons=comparisons,
        method="Any-source alert per one-second bin. Rules=R1–R3; ML=telemetry IF; hybrid adds network statistics and explicit system-event checks. "
        "Detection rate/latency use labeled intervals. No overlapping training samples; test rolling features restart at the boundary. "
        "Synthetic labels only; temporal hits do not prove correct attribution. Feature aftereffects outside injected windows count as false positives.",
    )
