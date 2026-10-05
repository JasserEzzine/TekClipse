from __future__ import annotations

import json
import hashlib
from functools import wraps
from tempfile import NamedTemporaryFile
from threading import Lock
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
import streamlit as st

from tekclipse.data.generator import (
    GENERATOR_VERSION,
    SOURCES,
    generate_synthetic_dataset,
)
from tekclipse.data.injection import get_scenario
from tekclipse.evaluation.runner import prepare_nominal_split, _feature_matrix
from tekclipse.pipeline.model import build_model, compute_ml_alerts
from tekclipse.pipeline.rules import detect_rule_alerts
from tekclipse.pipeline.network import fit_network_baseline, detect_network_alerts
from tekclipse.pipeline.explain import explain_alerts, detect_system_alerts
from tekclipse.pipeline.correlation import correlate_alerts
from tekclipse.config import load_config

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "generated"
ALERT_COLUMNS = ["timestamp", "source", "severity", "description", "score"]
_DETECTION_LOCK = Lock()
_PREVIEW_LOCK = Lock()


def serialized_detector(function):
    """Bound model-training memory: one uncached detector job per server process."""

    @wraps(function)
    def guarded(*args, **kwargs):
        with _DETECTION_LOCK:
            return function(*args, **kwargs)

    return guarded


def _detector_signature():
    root = Path(__file__).resolve().parents[2]
    paths = [
        root / "config.yaml",
        Path(__file__),
        root / "tekclipse/evaluation/runner.py",
    ]
    paths.extend(sorted((root / "tekclipse/pipeline").glob("*.py")))
    paths.extend(sorted((root / "tekclipse/data").glob("*.py")))
    return hashlib.sha256(b"".join(p.read_bytes() for p in paths)).hexdigest()


def save_nominal_preview(hours: int, token: str, result: dict):
    """Persist actual detector output for this exact dataset, never fabricated alerts."""
    if result["scenario"] != "E1":
        raise ValueError(
            "Only the nominal baseline can be saved as the default preview"
        )
    payload = dict(result)
    payload["alerts"] = result["alerts"].to_dict(orient="records")
    document = dict(
        hours=hours,
        token=token,
        detector_signature=_detector_signature(),
        generated_at=pd.Timestamp.now(tz="UTC").isoformat(),
        result=payload,
    )
    path = DATA_DIR / "nominal_preview.json"
    # Separate temporary files prevent two sessions from clobbering one writer.
    temporary = None
    try:
        with NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=DATA_DIR,
            prefix="nominal-preview-",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            json.dump(document, handle, default=str)
        with _PREVIEW_LOCK:
            temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return path


def load_nominal_preview(hours: int, token: str):
    path = DATA_DIR / "nominal_preview.json"
    try:
        with _PREVIEW_LOCK:
            document = json.loads(path.read_text(encoding="utf-8"))
        if (
            document["hours"] != hours
            or document["token"] != token
            or document["detector_signature"] != _detector_signature()
        ):
            return None
        result = document["result"]
        if result["scenario"] != "E1":
            return None
        result["alerts"] = pd.DataFrame(result["alerts"], columns=ALERT_COLUMNS)
        result["alerts"]["timestamp"] = pd.to_datetime(
            result["alerts"].timestamp, utc=True
        )
        result["spans"] = [
            (pd.Timestamp(a), pd.Timestamp(b)) for a, b in result["spans"]
        ]
        result["saved_at"] = document["generated_at"]
        return result
    except (OSError, ValueError, KeyError, TypeError):
        return None


def dataset_token(hours: int) -> str:
    """Validate completion/version/files before consulting Streamlit's data cache."""
    manifest_path = DATA_DIR / "manifest.json"
    try:
        m = json.loads(manifest_path.read_text(encoding="utf-8"))
        valid = (
            m["version"] == GENERATOR_VERSION
            and m["hours"] >= hours
            and m["seed"] == 42
            and m["counts"]["telemetry"] >= hours * 3600
            and m["counts"]["network"] >= hours * 3600
            and all((DATA_DIR / f"{name}.csv").exists() for name in SOURCES)
            and (DATA_DIR / "dataset.sqlite").exists()
        )
    except (OSError, ValueError, KeyError, TypeError):
        valid = False
    if not valid:
        with st.spinner(
            f"Generating {hours / 24:g} days of simulation and storing all four sources…"
        ):
            generate_synthetic_dataset(hours, DATA_DIR)
    paths = [manifest_path] + [
        DATA_DIR / f"{name}.{ext}"
        for name in SOURCES
        for ext in ("csv", "parquet")
        if (DATA_DIR / f"{name}.{ext}").exists()
    ]
    return "|".join(
        f"{p.name}:{p.stat().st_mtime_ns}:{p.stat().st_size}" for p in paths
    )


@st.cache_data(max_entries=2, show_spinner=False)
def load_data(hours: int, token: str) -> dict:
    m = json.loads((DATA_DIR / "manifest.json").read_text(encoding="utf-8"))
    end = pd.Timestamp(m["start"]) + pd.Timedelta(hours=hours)
    data = {}
    for name in SOURCES:
        pq = DATA_DIR / f"{name}.parquet"
        df = (
            pd.read_parquet(pq)
            if m["parquet"] and pq.exists()
            else pd.read_csv(DATA_DIR / f"{name}.csv")
        )
        df["timestamp"] = pd.to_datetime(df.timestamp, utc=True)
        data[name] = df.loc[df.timestamp < end].reset_index(drop=True)
    expected = hours * 3600
    if any(
        len(data[name]) != expected
        or data[name].timestamp.max() < end - pd.Timedelta(seconds=1)
        for name in ("telemetry", "network")
    ):
        with st.spinner("Repairing incomplete simulation data…"):
            return generate_synthetic_dataset(hours, DATA_DIR)
    return data


@st.cache_data(max_entries=16, show_spinner=False)
@serialized_detector
def detect(hours: int, token: str, scenario: str) -> dict:
    """Use unchanged public detectors; train only on the separate nominal baseline.

    Existing injections have fixed timestamps at noon on Jan 1. Score the entire
    scenario at full resolution for a demonstration, and disclose overlap with
    the nominal training timeline. This is not a held-out performance evaluation.
    """
    started = perf_counter()
    get_scenario(scenario)  # Reject invalid scenario names before any expensive work.
    nominal = load_data(hours, token)
    train, _, cols = prepare_nominal_split(nominal)
    train_features = _feature_matrix(train, cols).select_dtypes(include="number")
    model, train_scores = build_model(
        train_features, contamination=0.05, random_state=42
    )
    threshold = float(np.quantile(train_scores, 0.95))
    scenario_data, truth = get_scenario(scenario)(nominal)
    features = _feature_matrix(scenario_data["telemetry"], cols)
    numeric = features.select_dtypes(include="number")
    scores = -model.decision_function(numeric)
    # timestamp is nonnumeric, so the existing ML function retains it in alerts.
    ml = compute_ml_alerts(model, features, threshold)
    rules = detect_rule_alerts(
        scenario_data["commands"],
        telemetry=scenario_data["telemetry"],
        network=scenario_data["network"],
        events=scenario_data["system_events"],
    )
    network_baseline = fit_network_baseline(
        nominal["network"].loc[lambda d: d.timestamp <= train.timestamp.max()]
    )
    network = detect_network_alerts(scenario_data["network"], network_baseline)
    system = detect_system_alerts(scenario_data["system_events"])
    evidence = explain_alerts(
        rules + ml + network + system, scenario_data, train_features, features
    )
    window = int(
        load_config().get("security", {}).get("correlation_window_seconds", 180)
    )
    security = dict(
        evidence=evidence,
        incidents=correlate_alerts(evidence, window),
        window_seconds=window,
    )
    alerts = pd.DataFrame(evidence, columns=ALERT_COLUMNS)
    alerts["timestamp"] = pd.to_datetime(alerts.timestamp, utc=True)
    alerts = alerts.sort_values("timestamp").reset_index(drop=True)
    flagged = scores > threshold
    edges = np.diff(np.r_[False, flagged, False].astype(int))
    starts, ends = np.flatnonzero(edges == 1), np.flatnonzero(edges == -1) - 1
    ts = scenario_data["telemetry"].timestamp
    spans = [
        (ts.iloc[a], ts.iloc[b] + pd.Timedelta(seconds=1)) for a, b in zip(starts, ends)
    ]
    return dict(
        alerts=alerts,
        threshold=threshold,
        latest_score=float(scores[-1]),
        score_min=float(min(scores.min(), threshold)),
        score_max=float(max(scores.max(), threshold)),
        spans=spans,
        truth=truth,
        seconds=perf_counter() - started,
        scenario=scenario,
        train_samples=len(train),
        evaluated_samples=len(scores),
        security=security,
    )


@st.cache_data(max_entries=8, show_spinner=False)
@serialized_detector
def evaluate_preview(hours: int, token: str, scenario: str):
    from tekclipse.evaluation.validated import evaluate_held_out

    return evaluate_held_out(load_data(hours, token), scenario)


@st.cache_data(max_entries=4, show_spinner=False)
def chart_data(hours: int, token: str, scenario: str) -> dict:
    data, _ = get_scenario(scenario)(load_data(hours, token))
    telemetry = data["telemetry"]
    # Bounded time bins; means plus extrema retain spikes in long-range views.
    step = max(10, int(np.ceil(hours * 3600 / 1800)))
    freq = f"{step}s"
    tel = telemetry.set_index("timestamp").resample(freq).mean().reset_index()
    extrema = (
        telemetry.set_index("timestamp")
        .temperature_c.resample(freq)
        .agg(["min", "max"])
        .reset_index()
    )
    net = data["network"].copy(deep=False)
    area = (
        net.groupby([pd.Grouper(key="timestamp", freq=freq), "protocol"])
        .traffic_rate.sum()
        .reset_index()
    )
    area["traffic_rate"] /= step
    bubbles = (
        net.assign(day=net.timestamp.dt.strftime("%Y-%m-%d"))
        .groupby(["day", "src_ip", "dst_ip", "protocol"], observed=True)
        .agg(
            bytes=("bytes", "sum"),
            packets=("packets", "sum"),
            connections=("connection_count", "sum"),
        )
        .reset_index()
    )
    events = data["system_events"]
    days = pd.date_range(
        telemetry.timestamp.min().floor("D"),
        telemetry.timestamp.max().floor("D"),
        freq="D",
    ).strftime("%Y-%m-%d")
    event_grid = (
        events.assign(
            day=events.timestamp.dt.strftime("%Y-%m-%d"), hour=events.timestamp.dt.hour
        )
        .groupby(["day", "hour"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=days, columns=range(24), fill_value=0)
    )
    return dict(
        telemetry=tel,
        extrema=extrema,
        area=area,
        bubbles=bubbles,
        protocols=net.groupby("protocol").size().reset_index(name="rows"),
        correlation=telemetry.drop(columns="timestamp").corr(),
        commands=data["commands"],
        events=events,
        event_grid=event_grid,
        step=step,
        counts={name: len(frame) for name, frame in data.items()},
        latest=telemetry.iloc[-1].to_dict(),
        start=telemetry.timestamp.min(),
        end=telemetry.timestamp.max(),
        last_hour=telemetry.tail(3600).iloc[::60],
        hourly_alert_bins=pd.date_range(
            telemetry.timestamp.min().floor("h"),
            telemetry.timestamp.max().floor("h"),
            freq="h",
        ),
    )
