from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from tekclipse.config import load_config
from tekclipse.data.generator import generate_synthetic_dataset
from tekclipse.data.injection import get_scenario
from tekclipse.evaluation.metrics import compute_metrics
from tekclipse.pipeline.features import telemetry_features
from tekclipse.pipeline.model import build_model, compute_ml_alerts
from tekclipse.pipeline.rules import detect_rule_alerts
from tekclipse.storage.db import save_json, save_summary

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results"


def prepare_nominal_split(data: dict):
    cfg = load_config()
    telemetry = data["telemetry"].copy()
    telemetry["timestamp"] = pd.to_datetime(telemetry["timestamp"], utc=True)
    split = int(len(telemetry) * cfg["simulation"]["nominal_train_fraction"])
    train = telemetry.iloc[:split].copy()
    test = telemetry.iloc[split:].copy()
    feat_cols = ["temperature_c", "cpu_percent", "ram_percent", "battery_percent", "voltage_v", "power_w", "signal_dbm"]
    return train, test, feat_cols


def _feature_matrix(df: pd.DataFrame, feat_cols: list[str]) -> pd.DataFrame:
    out = telemetry_features(df.copy())
    for c in feat_cols:
        for suffix in ["_rolling_mean_60s", "_rolling_std_60s"]:
            if c + suffix not in out.columns:
                if "mean" in suffix:
                    out[c + suffix] = out[c].rolling(window=60, min_periods=1).mean()
                else:
                    out[c + suffix] = out[c].rolling(window=60, min_periods=1).std(ddof=0)
    return out


def evaluate_scenario(scenario_name: str, data: dict):
    cfg = load_config()
    train_telemetry, test_telemetry, feat_cols = prepare_nominal_split(data)
    train_features = _feature_matrix(train_telemetry, feat_cols)
    test_features = _feature_matrix(test_telemetry, feat_cols)
    ml_cols = [c for c in train_features.columns if c.endswith("_rolling_mean_60s") or c.endswith("_rolling_std_60s") or c in feat_cols]

    model, train_scores = build_model(
        train_features[ml_cols],
        contamination=cfg["model"]["isolation_forest"]["contamination"],
        random_state=cfg["model"]["isolation_forest"]["random_state"],
    )
    threshold = float(np.quantile(train_scores, 1 - cfg["model"]["isolation_forest"]["contamination"]))

    rule_alerts = detect_rule_alerts(data["commands"], telemetry=data["telemetry"], network=data["network"], events=data["system_events"])
    ml_alerts = compute_ml_alerts(model, test_features[["timestamp", *ml_cols]].copy(), threshold)
    alerts = rule_alerts + ml_alerts

    # ground truth is encoded as a set of onset timestamps from the injection helper
    ground_truth = get_scenario(scenario_name)(data)[1]
    onset = pd.to_datetime(ground_truth[0][0], utc=True) if ground_truth else None
    valid_alert_times = []
    for alert in alerts:
        ts = pd.to_datetime(alert.get("timestamp"), utc=True, errors="coerce")
        if pd.notna(ts):
            valid_alert_times.append(ts)
    first_alert = min(valid_alert_times) if valid_alert_times else None

    # Preserve the legacy preview API, but do not publish onset-only counts as
    # measured performance. This path may receive already-injected training data.
    metrics = {name: float("nan") for name in (
        "precision", "recall", "f1", "fpr", "latency_ms", "cpu_percent", "ram_mb"
    )}
    return {"scenario": scenario_name, "alerts": alerts, "metrics": metrics,
            "ground_truth": ground_truth, "metrics_available": False,
            "evaluation_note": "Legacy preview has insufficient labels/split guarantees. Use evaluation.validated.evaluate_held_out with untouched nominal data."}


def run_all_scenarios():
    cfg = load_config()
    data = generate_synthetic_dataset(hours=cfg["simulation"]["hours"])
    results = []
    for scenario in ["E1", "E2", "E3", "E4", "E5", "E6"]:
        scenario_data = data.copy()
        if scenario != "E1":
            scenario_data = get_scenario(scenario)(scenario_data)[0]
        results.append(evaluate_scenario(scenario, scenario_data))
    return results


def print_results_table(results):
    print("| Scenario | Precision | Recall | F1 | FPR | Latency(ms) | CPU% | RAM(MB) |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|")
    for item in results:
        m = item["metrics"]
        lat = round(m["latency_ms"], 2) if pd.notna(m["latency_ms"]) else "[TO BE MEASURED]"
        print(
            f"| {item['scenario']} | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} | {m['fpr']:.3f} | {lat} | {m['cpu_percent']:.2f} | {m['ram_mb']:.2f} |"
        )


def main(scenario: str | None = None):
    cfg = load_config()
    data = generate_synthetic_dataset(hours=cfg["simulation"]["hours"])
    if scenario is None:
        scenarios = ["E1", "E2", "E3", "E4", "E5", "E6"]
    else:
        scenarios = [scenario]

    results = []
    for name in scenarios:
        scenario_data = data.copy()
        if name != "E1":
            scenario_data = get_scenario(name)(scenario_data)[0]
        results.append(evaluate_scenario(name, scenario_data))

    payload = {"scenarios": [{
        "scenario": item["scenario"],
        "metrics": item["metrics"],
        "alerts": item["alerts"],
        "ground_truth": item["ground_truth"],
    } for item in results]}
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    save_json(payload, "results.json", RESULTS_DIR)
    summary = "# TekClipse evaluation summary\n\n" + "\n".join([
        f"- {item['scenario']}: precision={item['metrics']['precision']:.3f}, recall={item['metrics']['recall']:.3f}, F1={item['metrics']['f1']:.3f}, FPR={item['metrics']['fpr']:.3f}" for item in results
    ]) + "\n"
    save_summary(summary, RESULTS_DIR)
    print_results_table(results)
    return results


if __name__ == "__main__":
    np.random.seed(42)
    main()
