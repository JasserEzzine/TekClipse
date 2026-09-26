from __future__ import annotations

import math
import random
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from tekclipse.config import load_config


SEED = 42


def _safe_resolve(path: str | Path | None = None) -> Path:
    root = Path(__file__).resolve().parents[2]
    if path is None:
        return root / "tekclipse" / "data" / "generated"
    return Path(path)


def generate_synthetic_dataset(hours: int = 24, output_dir: str | Path | None = None) -> Dict[str, pd.DataFrame]:
    cfg = load_config()
    rng = np.random.default_rng(SEED)
    sim_cfg = cfg["simulation"]
    hz = int(sim_cfg.get("hz", 1))
    total_seconds = int(hours * 3600)
    timestamps = pd.date_range("2026-01-01", periods=total_seconds, freq=f"{hz}s", tz="UTC")

    t = np.arange(total_seconds, dtype=float)
    temperature = 38 + 4 * np.sin(2 * np.pi * t / 86400) + rng.normal(0.0, 0.5, total_seconds)
    temperature = np.clip(temperature, 35.0, 45.0)

    cpu = np.empty(total_seconds, dtype=float)
    cpu[0] = 45.0
    for i in range(1, total_seconds):
        cpu[i] = np.clip(cpu[i - 1] + rng.normal(0.0, 1.0), 20.0, 60.0)

    ram = np.clip(55 + 6 * np.sin(2 * np.pi * t / 43200) + rng.normal(0.0, 2.0, total_seconds), 40.0, 70.0)
    battery = np.clip(70 + 20 * np.sin(2 * np.pi * t / 43200) + rng.normal(0.0, 1.2, total_seconds), 40.0, 100.0)
    voltage = 27.8 + 0.4 * np.sin(2 * np.pi * t / 43200) + 0.05 * (battery - 70) / 30 + rng.normal(0.0, 0.08, total_seconds)
    voltage = np.clip(voltage, 27.5, 28.5)
    power = np.clip(110 + 0.3 * cpu + 0.5 * (battery - 70) + rng.normal(0.0, 5.0, total_seconds), 80.0, 150.0)
    signal = np.clip(-82 + 5 * np.sin(2 * np.pi * t / 28800) + rng.normal(0.0, 2.0, total_seconds), -95.0, -75.0)

    telemetry = pd.DataFrame(
        {
            "timestamp": timestamps,
            "temperature_c": temperature,
            "cpu_percent": cpu,
            "ram_percent": ram,
            "battery_percent": battery,
            "voltage_v": voltage,
            "power_w": power,
            "signal_dbm": signal,
        }
    )

    command_interval = int(cfg["commands"]["interval_seconds"])
    command_types = cfg["commands"]["types"]
    command_sources = cfg["commands"]["sources"]
    rand = random.Random(SEED)
    commands = []
    start = pd.Timestamp("2026-01-01T00:00:00Z")
    for i in range(0, total_seconds, command_interval):
        ts = start + pd.Timedelta(seconds=i)
        cmd = {
            "timestamp": ts,
            "type": rand.choice(command_types),
            "source": rand.choice(command_sources),
            "authorized": True,
        }
        commands.append(cmd)

    commands_df = pd.DataFrame(commands)

    network_rows = []
    for i in range(total_seconds):
        rate = cfg["network"]["nominal_rate"] * (1 + 0.05 * math.sin(2 * math.pi * i / 1800))
        packets = max(1, int(cfg["network"]["packets_base"] + rng.normal(0, 8)))
        bytes_value = max(10, int(cfg["network"]["bytes_base"] + rng.normal(0, 200)))
        network_rows.append(
            {
                "timestamp": timestamps[i],
                "src_ip": f"10.0.0.{(i % 250) + 2}",
                "dst_ip": f"10.0.0.{(i % 250) + 10}",
                "protocol": "TCP" if i % 2 == 0 else "UDP",
                "packets": packets,
                "bytes": bytes_value,
                "connection_count": int(1 + (i % 5)),
                "traffic_rate": rate,
            }
        )
    network = pd.DataFrame(network_rows)

    event_types = ["auth_success", "auth_failure", "process_start", "process_stop", "config_change", "warning", "error"]
    events = []
    for i in range(total_seconds):
        if rng.random() < 0.02:
            events.append({
                "timestamp": timestamps[i],
                "event_type": rng.choice(event_types),
                "source": "system",
                "details": "nominal",
            })
        elif rng.random() < 0.005:
            events.append({
                "timestamp": timestamps[i],
                "event_type": "auth_failure",
                "source": "auth",
                "details": "nominal-ish",
            })
    events_df = pd.DataFrame(events)

    output = _safe_resolve(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    outputs = {
        "telemetry": telemetry,
        "commands": commands_df,
        "network": network,
        "system_events": events_df,
    }
    for name, df in outputs.items():
        path = output / f"{name}.csv"
        df.to_csv(path, index=False)
    return outputs
