from __future__ import annotations

from typing import Any

import pandas as pd


def detect_rule_alerts(commands, telemetry=None, network=None, events=None):
    alerts = []
    command_rows = [] if commands is None else commands
    if isinstance(command_rows, pd.DataFrame):
        command_rows = command_rows.to_dict(orient="records")
    for row in command_rows:
        ts = row.get("timestamp")
        source = row.get("source", "")
        typ = row.get("type", "")
        authorized = row.get("authorized", True)
        if source == "UNKNOWN_1" or not authorized:
            alerts.append({
                "timestamp": ts,
                "source": "R1",
                "severity": "CRITICAL",
                "description": f"Unauthorized command source {source} with type {typ}",
                "score": 0.99,
            })
    if command_rows:
        df = pd.DataFrame(command_rows)
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
            df["minute"] = df["timestamp"].dt.floor("min")
            counts = df.groupby("minute").size()
            for minute, count in counts.items():
                if count > 10:
                    alerts.append({
                        "timestamp": minute.isoformat(),
                        "source": "R2",
                        "severity": "CRITICAL",
                        "description": f"Command flood detected ({count} commands/min)",
                        "score": 0.95,
                    })
    if telemetry is not None:
        df = telemetry.copy()
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        # Format only violations; the thresholds and output order are unchanged.
        temp_values = df.get("temperature_c", pd.Series(0, index=df.index))
        voltage_values = df.get("voltage_v", pd.Series(0, index=df.index))
        violations = (temp_values > 85) | (voltage_values < 26) | (voltage_values > 30)
        for _, row in df.loc[violations].iterrows():
            temp = row.get("temperature_c", 0)
            voltage = row.get("voltage_v", 0)
            if temp > 85 or voltage < 26 or voltage > 30:
                alerts.append({
                    "timestamp": row.get("timestamp"),
                    "source": "R3",
                    "severity": "WARNING",
                    "description": f"Hard limit exceeded: temp={temp}C, voltage={voltage}V",
                    "score": 0.8,
                })
    return alerts
