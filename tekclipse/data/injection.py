from __future__ import annotations

from typing import Dict, List, Tuple

import pandas as pd


def scenario_e1(data: dict) -> tuple[dict, list[tuple[str, str]]]:
    return data, []


def scenario_e2(data: dict) -> tuple[dict, list[tuple[str, str]]]:
    cmd = data["commands"].copy()
    ts = pd.Timestamp("2026-01-01T12:00:00Z")
    cmd.loc[len(cmd)] = {"timestamp": ts, "type": "REBOOT", "source": "UNKNOWN_1", "authorized": False}
    out = data.copy()
    out["commands"] = cmd
    return out, [(ts.isoformat(), "E2 unauthorized source REBOOT")]


def scenario_e3(data: dict) -> tuple[dict, list[tuple[str, str]]]:
    cmd = data["commands"].copy()
    base = pd.Timestamp("2026-01-01T12:00:00Z")
    for i in range(30):
        ts = base + pd.Timedelta(seconds=i * 2)
        cmd.loc[len(cmd)] = {"timestamp": ts, "type": "UPLOAD", "source": "GS_PRIMARY", "authorized": True}
    out = data.copy()
    out["commands"] = cmd
    return out, [(base.isoformat(), "E3 command flood")]


def scenario_e4(data: dict) -> tuple[dict, list[tuple[str, str]]]:
    net = data["network"].copy()
    base = pd.Timestamp("2026-01-01T12:00:00Z")
    for i in range(120):
        ts = base + pd.Timedelta(seconds=i)
        row = {
            "timestamp": ts,
            "src_ip": "203.0.113.10",
            "dst_ip": "10.0.0.5",
            "protocol": "TCP",
            "packets": 500,
            "bytes": 60000,
            "connection_count": 20,
            "traffic_rate": 10000.0,
        }
        net.loc[len(net)] = row
    out = data.copy()
    out["network"] = net
    return out, [(base.isoformat(), "E4 network spike")]


def scenario_e5(data: dict) -> tuple[dict, list[tuple[str, str]]]:
    tel = data["telemetry"].copy()
    start = pd.Timestamp("2026-01-01T12:00:00Z")
    end = start + pd.Timedelta(minutes=3)
    mask = tel["timestamp"].between(start, end)
    tel.loc[mask, "temperature_c"] = 120.0
    out = data.copy()
    out["telemetry"] = tel
    return out, [(start.isoformat(), "E5 temperature step injection")]


def scenario_e6(data: dict) -> tuple[dict, list[tuple[str, str]]]:
    temp = scenario_e5(data)[0]
    net = scenario_e4(temp)[0]
    return scenario_e2(net)[0], [(pd.Timestamp("2026-01-01T12:00:00Z").isoformat(), "E6 combined injection")]


def get_scenario(name: str):
    from tekclipse.data.coordinated import scenario_e7

    mapping = {
        "E1": scenario_e1,
        "E2": scenario_e2,
        "E3": scenario_e3,
        "E4": scenario_e4,
        "E5": scenario_e5,
        "E6": scenario_e6,
        "E7": scenario_e7,
    }
    if name not in mapping:
        raise ValueError(f"Unknown scenario: {name}")
    return mapping[name]
