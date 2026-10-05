import pandas as pd

from tekclipse.pipeline.explain import explain_alerts, detect_system_alerts
from tekclipse.pipeline.rules import detect_rule_alerts


def test_command_burst_is_not_observed_before_eleventh_command():
    stamps = pd.date_range("2026-01-01T12:01:16Z", periods=12, freq="s")
    commands = pd.DataFrame(
        dict(timestamp=stamps, type="UPLOAD", source="GS_BACKUP", authorized=True)
    )
    tel = pd.DataFrame(dict(timestamp=stamps, temperature_c=88.0, voltage_v=28.0))
    nominal = tel.assign(temperature_c=40.0)
    alerts = detect_rule_alerts(commands, tel)
    explained = explain_alerts(
        alerts, dict(commands=commands, telemetry=tel), nominal, tel
    )
    burst = next(a for a in explained if a["source"] == "R2")
    assert pd.Timestamp(burst["observed_at"]) == stamps[10]
    assert pd.Timestamp(burst["timestamp"]) == stamps[0].floor("min")
    thermal = next(a for a in explained if a["source"] == "R3")
    assert "by 3.0 C" in thermal["description"]
    assert thermal["subsystems"] == ["Thermal"]
    assert "subsystems" not in alerts[0]


def test_routine_events_do_not_become_security_incidents():
    events = pd.DataFrame(
        [
            dict(
                timestamp="2026-01-01T12:00Z",
                event_type="error",
                source="payload",
                details="retry",
            )
        ]
    )
    assert detect_system_alerts(events) == []
    events["event_type"] = "watchdog_reset"
    assert detect_system_alerts(events)[0]["source"] == "SYS"


def test_ml_explanation_is_feature_context_not_probability():
    stamps = pd.date_range("2026-01-01", periods=3, freq="s", tz="UTC")
    nominal = pd.DataFrame(
        dict(
            timestamp=stamps,
            temperature_c=[39.0, 40.0, 41.0],
            voltage_v=[27.0, 28.0, 29.0],
        )
    )
    test = nominal.copy()
    test.loc[1, "temperature_c"] = 90.0
    commands = pd.DataFrame(columns=["timestamp", "source", "type", "authorized"])
    commands["timestamp"] = pd.to_datetime(commands.timestamp, utc=True)
    rows = explain_alerts(
        [
            dict(
                timestamp=stamps[1],
                source="ML",
                severity="WARNING",
                description="IF deviation",
                score=0.1,
            )
        ],
        dict(commands=commands, telemetry=test),
        nominal,
        test,
    )
    assert "temperature_c=" in rows[0]["description"]
    assert "not model attribution or probability" in rows[0]["description"]
