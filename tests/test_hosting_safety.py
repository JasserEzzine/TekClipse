from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import threading
import time
import tomllib

import pandas as pd

from tekclipse.dashboard import data_service


def test_concurrent_preview_writes_are_atomic(tmp_path, monkeypatch):
    monkeypatch.setattr(data_service, "DATA_DIR", tmp_path)
    timestamp = pd.Timestamp("2026-01-01T00:00:00Z")
    result = dict(
        scenario="E1",
        alerts=pd.DataFrame(columns=data_service.ALERT_COLUMNS),
        spans=[(timestamp, timestamp + pd.Timedelta(seconds=1))],
    )
    with ThreadPoolExecutor(max_workers=8) as pool:
        paths = list(
            pool.map(
                lambda _: data_service.save_nominal_preview(24, "test-data", result),
                range(24),
            )
        )
    assert all(path.exists() for path in paths)
    assert json.loads(paths[0].read_text())["result"]["scenario"] == "E1"
    assert data_service.load_nominal_preview(24, "test-data") is not None
    assert not list(tmp_path.glob("*.tmp"))


def test_uncached_detector_jobs_do_not_overlap():
    state = {"active": 0, "peak": 0}
    lock = threading.Lock()

    @data_service.serialized_detector
    def task():
        with lock:
            state["active"] += 1
            state["peak"] = max(state["peak"], state["active"])
        time.sleep(0.01)
        with lock:
            state["active"] -= 1

    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(lambda _: task(), range(12)))
    assert state["peak"] == 1
    assert state["active"] == 0


def test_public_host_does_not_disable_browser_protections():
    path = Path(__file__).resolve().parents[1] / ".streamlit/config.toml"
    config = tomllib.loads(path.read_text(encoding="utf-8-sig"))
    assert config["server"]["enableCORS"] is True
    assert config["server"]["enableXsrfProtection"] is True
    assert config["server"]["enableStaticServing"] is False
    assert config["client"]["showErrorDetails"] == "none"


def test_evaluator_keeps_alert_times_and_accepts_utc_ground_truth():
    from tekclipse.data.generator import generate_synthetic_dataset
    from tekclipse.data.injection import get_scenario
    from tekclipse.evaluation.runner import evaluate_scenario

    data = generate_synthetic_dataset(24, persist=False)
    injected, _ = get_scenario("E2")(data)
    result = evaluate_scenario("E2", injected)
    assert result["ground_truth"]
    assert any(alert["source"] == "R1" for alert in result["alerts"])
    assert all(
        pd.notna(pd.to_datetime(alert["timestamp"], utc=True))
        for alert in result["alerts"]
    )
