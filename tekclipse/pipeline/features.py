from __future__ import annotations

import pandas as pd


def telemetry_features(telemetry: pd.DataFrame) -> pd.DataFrame:
    out = telemetry.copy()
    for col in ["temperature_c", "cpu_percent", "ram_percent", "battery_percent", "voltage_v", "power_w", "signal_dbm"]:
        if col not in out.columns:
            continue
        out[f"{col}_rolling_mean_60s"] = out[col].rolling(window=60, min_periods=1).mean()
        out[f"{col}_rolling_std_60s"] = out[col].rolling(window=60, min_periods=1).std(ddof=0)
    return out


def command_features(commands: pd.DataFrame) -> pd.DataFrame:
    out = commands.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    if out.empty:
        return out
    out["cmd_count_5min"] = out.groupby(pd.Grouper(key="timestamp", freq="5min")).transform("size")
    return out


def network_features(network: pd.DataFrame) -> pd.DataFrame:
    out = network.copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    if out.empty:
        return out
    out["traffic_rate_1min"] = out.groupby(pd.Grouper(key="timestamp", freq="1min"))["traffic_rate"].transform("sum")
    return out


def event_features(events: pd.DataFrame) -> pd.DataFrame:
    out = events.copy()
    if out.empty:
        return out
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True)
    out["event_count_1min"] = out.groupby(pd.Grouper(key="timestamp", freq="1min")).transform("size")
    return out
