from __future__ import annotations

import importlib.util
import json
import sqlite3
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd

from tekclipse.config import load_config

SEED = 42
GENERATOR_VERSION = 3
SOURCES = ("telemetry", "commands", "network", "system_events")


def _safe_resolve(path: str | Path | None = None) -> Path:
    return (
        Path(path)
        if path is not None
        else Path(__file__).resolve().parent / "generated"
    )


def generate_synthetic_dataset(
    hours: int = 168, output_dir: str | Path | None = None, *, persist: bool = True
) -> dict[str, pd.DataFrame]:
    """Vectorized synthetic operations, not a physical flight model.

    A 90-minute orbit has 60% sunlight. Station passes every three hours
    correlate resource use, network traffic and commands. Manifest written last.
    """
    started = perf_counter()
    if not isinstance(hours, int) or not 1 <= hours <= 720:
        raise ValueError("hours must be an integer between 1 and 720 (30 days)")
    cfg = load_config()
    if cfg["simulation"].get("hz", 1) != 1:
        raise ValueError("The generator and existing rolling features require 1 Hz")
    rng = np.random.default_rng(SEED)
    n = hours * 3600
    t = np.arange(n)
    timestamps = pd.date_range("2026-01-01", periods=n, freq="s", tz="UTC")
    phase = (t % 5400) / 5400
    daylight = phase < 0.6
    pass_distance = (t - 3600 + 5400) % 10800 - 5400
    passes = np.exp(-0.5 * (pass_distance / 420) ** 2)
    daily = 1 + 0.18 * np.sin(2 * np.pi * t / 86400)
    weekly = np.sin(2 * np.pi * t / (7 * 86400))
    temperature = (
        39
        + 3.8 * np.sin(2 * np.pi * phase - 0.8)
        + 0.035 * t / 86400
        + 0.4 * weekly
        + rng.normal(0, 0.35, n)
    )
    charge = np.where(daylight, phase / 0.6, (1 - phase) / 0.4)
    battery = np.clip(
        58 + 35 * charge - 0.025 * t / 86400 + 0.6 * weekly + rng.normal(0, 0.12, n),
        40,
        100,
    )
    cpu = np.clip(
        30
        + 22 * passes * daily
        + 3 * np.sin(2 * np.pi * t / 1200)
        + rng.normal(0, 1, n),
        20,
        60,
    )
    ram = np.clip(48 + 15 * passes + 2 * weekly + rng.normal(0, 0.7, n), 40, 70)
    voltage = np.clip(
        27.8 + 0.35 * (battery - 58) / 35 + rng.normal(0, 0.025, n), 27.5, 28.5
    )
    power = np.clip(95 + 0.6 * cpu + 8 * passes + rng.normal(0, 1, n), 80, 150)
    signal = np.clip(
        -79 - 5 * (~daylight) - 3 * passes + rng.normal(0, 0.6, n), -95, -75
    )
    telemetry = pd.DataFrame(
        dict(
            timestamp=timestamps,
            temperature_c=temperature,
            cpu_percent=cpu,
            ram_percent=ram,
            battery_percent=battery,
            voltage_v=voltage,
            power_w=power,
            signal_dbm=signal,
        )
    )
    # At most one nominal command per 20 seconds; clusters stay below R2.
    interval = int(cfg["commands"]["interval_seconds"])
    command_mask = (t % interval == 0) | (
        (t % 20 == 0) & (rng.random(n) < passes * 0.85)
    )
    indices = np.flatnonzero(command_mask)
    # Routine imaging and transfers dominate; reboot/firmware updates are rare.
    command_types = cfg["commands"]["types"]
    weights = np.array(
        [
            {
                "CAMERA_ON": 0.24,
                "CAMERA_OFF": 0.24,
                "REBOOT": 0.001,
                "DOWNLOAD": 0.26,
                "UPLOAD": 0.20,
                "CONFIG_UPDATE": 0.058,
                "FIRMWARE_UPDATE": 0.001,
            }.get(name, 0.01)
            for name in command_types
        ]
    )
    types = rng.choice(command_types, len(indices), p=weights / weights.sum())
    transfer = rng.random(len(indices)) < passes[indices] * 0.75
    types[transfer] = rng.choice(["DOWNLOAD", "UPLOAD"], transfer.sum())
    commands = pd.DataFrame(
        dict(
            timestamp=timestamps[indices],
            type=types,
            source=rng.choice(cfg["commands"]["sources"], len(indices)),
            authorized=True,
        )
    )
    rate = cfg["network"]["nominal_rate"] * (
        1 + 2.6 * passes * daily + 0.04 * np.sin(2 * np.pi * t / 1800)
    )
    hosts = np.array([f"10.0.0.{i}" for i in range(2, 34)])
    network = pd.DataFrame(
        dict(
            timestamp=timestamps,
            src_ip=hosts[t % 32],
            dst_ip=np.where(t % 2 == 0, "10.1.0.5", "10.1.0.6"),
            protocol=np.where(t % 2 == 0, "TCP", "UDP"),
            packets=np.maximum(
                1,
                (
                    cfg["network"]["packets_base"] * rate / 1000 + rng.normal(0, 4, n)
                ).astype(int),
            ),
            bytes=np.maximum(
                10,
                (
                    cfg["network"]["bytes_base"] * rate / 1000 + rng.normal(0, 80, n)
                ).astype(int),
            ),
            connection_count=1 + t % 3 + (passes * 4).astype(int),
            traffic_rate=rate,
        )
    )
    event_indices = np.flatnonzero(rng.random(n) < (0.012 + 0.07 * passes))
    event_types = [
        "auth_success",
        "auth_failure",
        "process_start",
        "process_stop",
        "config_change",
        "warning",
        "error",
    ]
    events = pd.DataFrame(
        dict(
            timestamp=timestamps[event_indices],
            event_type=rng.choice(
                event_types,
                len(event_indices),
                p=[0.38, 0.04, 0.23, 0.20, 0.07, 0.06, 0.02],
            ),
            source="system",
            details="nominal simulation",
        )
    )
    # Concrete synthetic operational records, correlated with the same timeline.
    messages = {
        "auth_success": (
            "access_gateway",
            "Ground-service session authenticated; scheduled access accepted",
        ),
        "auth_failure": (
            "access_gateway",
            "Expired simulator session rejected; fresh authentication required",
        ),
        "process_start": ("flight_computer", "Scheduled housekeeping worker started"),
        "process_stop": (
            "flight_computer",
            "Housekeeping worker completed and released its resources",
        ),
        "config_change": (
            "payload_controller",
            "Scheduled imaging profile loaded from the nominal operations plan",
        ),
        "warning": (
            "link_manager",
            "Transient link-quality warning; queued transfer retained for retry",
        ),
        "error": (
            "payload_controller",
            "Synthetic payload checksum mismatch; affected frame queued for retransmission",
        ),
    }
    events["source"] = events.event_type.map({k: v[0] for k, v in messages.items()})
    events["details"] = events.event_type.map({k: v[1] for k, v in messages.items()})

    def scheduled(seconds, kind, source, details):
        seconds = np.asarray(seconds)
        seconds = seconds[seconds < n]
        return pd.DataFrame(
            dict(
                timestamp=timestamps[seconds],
                event_type=kind,
                source=source,
                details=details,
            )
        )

    contacts = np.arange(3600, n, 10800)
    operational = [
        events,
        scheduled(
            contacts - 600,
            "contact_acquired",
            "ground_link",
            "Simulated ground-station contact acquired; queued uplink/downlink enabled",
        ),
        scheduled(
            contacts + 600,
            "contact_closed",
            "ground_link",
            "Scheduled ground-station contact closed; store-and-forward mode resumed",
        ),
        scheduled(
            np.arange(3240, n, 5400),
            "eclipse_entry",
            "power_controller",
            "Synthetic eclipse entry; battery discharge supplies spacecraft load",
        ),
        scheduled(
            np.arange(5400, n, 5400),
            "sunlight_entry",
            "power_controller",
            "Synthetic sunlight entry; solar charging cycle resumed",
        ),
    ]
    # Each acknowledgement corresponds to a real generated command, one second later.
    acknowledged = commands.loc[commands.timestamp < timestamps[-1]].copy()
    operational.append(
        pd.DataFrame(
            dict(
                timestamp=acknowledged.timestamp + pd.Timedelta(seconds=1),
                event_type="command_ack",
                source="command_dispatcher",
                details="Simulated "
                + acknowledged["type"]
                + " from "
                + acknowledged.source
                + " accepted by dispatcher (acknowledgement only)",
            )
        )
    )
    events = (
        pd.concat(operational, ignore_index=True)
        .sort_values("timestamp", kind="stable")
        .reset_index(drop=True)
    )
    outputs = dict(zip(SOURCES, [telemetry, commands, network, events]))
    if persist:
        output = _safe_resolve(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        manifest_path = output / "manifest.json"
        manifest_path.unlink(missing_ok=True)
        parquet = importlib.util.find_spec("pyarrow") is not None
        with sqlite3.connect(output / "dataset.sqlite") as conn:
            for name, df in outputs.items():
                serial = df.copy(deep=False).assign(
                    timestamp=df.timestamp.dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                )
                serial.to_csv(output / f"{name}.csv", index=False, float_format="%.6f")
                serial.to_sql(
                    name, conn, if_exists="replace", index=False, chunksize=10000
                )
                if parquet:
                    df.to_parquet(output / f"{name}.parquet", index=False)
        manifest = dict(
            version=GENERATOR_VERSION,
            hours=hours,
            hz=1,
            seed=SEED,
            start=timestamps[0].isoformat(),
            end=timestamps[-1].isoformat(),
            counts={name: len(df) for name, df in outputs.items()},
            parquet=parquet,
            generation_seconds=perf_counter() - started,
        )
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return outputs
