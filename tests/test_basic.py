import os

from tekclipse.config import load_config


def test_config_loads():
    cfg = load_config()
    assert cfg["simulation"]["seed"] == 42
    assert cfg["rules"]["r2_critical_commands_per_minute"] == 10


def test_rule_detection_smoke():
    from tekclipse.pipeline.rules import detect_rule_alerts

    sample = [
        {"timestamp": "2026-01-01T00:00:00", "source": "UNKNOWN_1", "type": "REBOOT", "authorized": False},
        {"timestamp": "2026-01-01T00:05:00", "source": "GS_PRIMARY", "type": "REBOOT", "authorized": True},
    ]
    alerts = detect_rule_alerts(sample, telemetry=None, network=[], events=[])
    assert any(a["source"] == "R1" for a in alerts)
