from __future__ import annotations

import ipaddress
import sqlite3
import numpy as np
import pandas as pd
import pytest

from tekclipse.data.generator import generate_synthetic_dataset
from tekclipse.data.injection import get_scenario
from tekclipse.pipeline.rules import detect_rule_alerts
from tekclipse.dashboard import charts


def test_deterministic_patterns_and_persistence(tmp_path):
    first = generate_synthetic_dataset(3, tmp_path)
    second = generate_synthetic_dataset(3, persist=False)
    for name, df in first.items():
        pd.testing.assert_frame_equal(df, second[name])
        assert len(pd.read_csv(tmp_path / f"{name}.csv")) == len(df)
        with sqlite3.connect(tmp_path / "dataset.sqlite") as conn:
            assert conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0] == len(df)
    tel = first["telemetry"]
    assert len(tel) == 10800
    assert (tel.timestamp.diff().dropna() == pd.Timedelta(seconds=1)).all()
    # Charge/discharge directions in one orbit, away from phase boundaries.
    assert tel.battery_percent.iloc[3000] > tel.battery_percent.iloc[100]
    assert tel.battery_percent.iloc[5300] < tel.battery_percent.iloc[3400]
    assert np.corrcoef(tel.cpu_percent, first["network"].traffic_rate)[0, 1] > 0.8
    assert first["commands"].set_index("timestamp").resample("min").size().max() <= 3
    for value in first["network"].src_ip.unique():
        ipaddress.ip_address(value)
    assert (tmp_path / "manifest.json").exists()
    events = first["system_events"]
    acknowledgements = events[events.event_type == "command_ack"]
    assert len(acknowledgements) == len(first["commands"])
    assert set(acknowledgements.timestamp) == set(
        first["commands"].timestamp + pd.Timedelta(seconds=1)
    )
    assert {
        "contact_acquired",
        "contact_closed",
        "eclipse_entry",
        "sunlight_entry",
    } <= set(events.event_type)
    assert events.source.nunique() >= 6
    assert not events.details.eq("nominal simulation").any()


def test_duration_validation():
    for hours in [0, -1, 721, 1.5]:
        with pytest.raises(ValueError):
            generate_synthetic_dataset(hours, persist=False)


def test_existing_scenarios_and_rules_remain_compatible():
    data = generate_synthetic_dataset(24, persist=False)
    for scenario, expected in [
        ("E1", set()),
        ("E2", {"R1"}),
        ("E3", {"R2"}),
        ("E4", set()),
        ("E5", {"R3"}),
        ("E6", {"R1", "R3"}),
    ]:
        injected, truth = get_scenario(scenario)(data)
        # Full-resolution telemetry unchanged; use only the injection neighborhood
        # for this compatibility test of existing rule behavior.
        tel = injected["telemetry"]
        tel = tel[tel.timestamp.between("2026-01-01T11:59:00Z", "2026-01-01T12:04:00Z")]
        alerts = detect_rule_alerts(injected["commands"], telemetry=tel)
        assert {a["source"] for a in alerts} == expected
        assert bool(truth) == (scenario != "E1")
    assert data["telemetry"].temperature_c.max() < 85
    assert data["commands"].authorized.all()


def test_orbit_and_gauge_are_serializable():
    assert len(charts.orbit().data) > 20
    fig = charts.gauge(
        dict(score_min=-0.1, score_max=0.2, threshold=0.03, latest_score=-0.02)
    )
    assert fig.data[0].value == -0.02
    assert fig.data[0].gauge.threshold.value == 0.03
    assert fig.to_json()


def test_saved_preview_rejects_stale_data_and_preserves_timestamps(
    tmp_path, monkeypatch
):
    from tekclipse.dashboard import data_service

    monkeypatch.setattr(data_service, "DATA_DIR", tmp_path)
    timestamp = pd.Timestamp("2026-01-01T12:00:00Z")
    result = dict(
        scenario="E1",
        alerts=pd.DataFrame(
            [
                dict(
                    timestamp=timestamp,
                    source="ML",
                    severity="WARNING",
                    description="Unit test fixture",
                    score=0.02,
                )
            ]
        ),
        spans=[(timestamp, timestamp + pd.Timedelta(seconds=1))],
    )
    data_service.save_nominal_preview(168, "dataset-a", result)
    restored = data_service.load_nominal_preview(168, "dataset-a")
    assert restored["alerts"].timestamp.iloc[0] == timestamp
    assert restored["spans"] == result["spans"]
    assert data_service.load_nominal_preview(168, "dataset-b") is None
    assert data_service.load_nominal_preview(24, "dataset-a") is None
    with pytest.raises(ValueError):
        data_service.save_nominal_preview(168, "dataset-a", dict(result, scenario="E5"))
