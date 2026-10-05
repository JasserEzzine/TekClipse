"""E7's reproducible sequence and explicit synthetic ground-truth intervals."""

from __future__ import annotations

import pandas as pd

ONSET = pd.Timestamp("2026-01-01T12:00:00Z")
STAGES = [
    (0, "Nominal watch"),
    (20, "Unauthorized configuration command"),
    (45, "Unfamiliar network peer and traffic rise"),
    (86, "Repeated command activity"),
    (100, "Thermal deviation"),
    (120, "Subsystem impact"),
    (160, "Review coordinated incident"),
]


def scenario_e7(data):
    if data["telemetry"].timestamp.min() > ONSET or data[
        "telemetry"
    ].timestamp.max() < ONSET + pd.Timedelta(seconds=180):
        raise ValueError(
            "E7 requires data covering 1 January 2026, 12:00–12:03 UTC (use at least 13 hours)"
        )
    out = {name: frame.copy(deep=True) for name, frame in data.items()}
    commands = [
        dict(
            timestamp=ONSET + pd.Timedelta(seconds=20),
            type="CONFIG_UPDATE",
            source="UNKNOWN_1",
            authorized=False,
        )
    ]
    commands += [
        dict(
            timestamp=ONSET + pd.Timedelta(seconds=76 + i),
            type="UPLOAD",
            source="GS_BACKUP",
            authorized=True,
        )
        for i in range(12)
    ]
    out["commands"] = (
        pd.concat([out["commands"], pd.DataFrame(commands)], ignore_index=True)
        .sort_values("timestamp", kind="stable")
        .reset_index(drop=True)
    )
    seconds = pd.date_range(ONSET + pd.Timedelta(seconds=45), periods=116, freq="s")
    network = pd.DataFrame(
        dict(
            timestamp=seconds,
            src_ip="203.0.113.27",
            dst_ip="10.0.0.5",
            protocol="UDP",
            packets=110,
            bytes=8500,
            connection_count=5,
            traffic_rate=1700.0,
        )
    )
    out["network"] = (
        pd.concat([out["network"], network], ignore_index=True)
        .sort_values("timestamp", kind="stable")
        .reset_index(drop=True)
    )
    mask = out["telemetry"].timestamp.between(
        ONSET + pd.Timedelta(seconds=100), ONSET + pd.Timedelta(seconds=160)
    )
    out["telemetry"].loc[mask, "temperature_c"] = 88.0
    out["telemetry"].loc[mask, "cpu_percent"] = 68.0
    events = pd.DataFrame(
        [
            dict(
                timestamp=ONSET + pd.Timedelta(seconds=120),
                event_type="watchdog_reset",
                source="flight_computer",
                details="Simulated watchdog reset following delayed housekeeping; operator verification needed",
            ),
            dict(
                timestamp=ONSET + pd.Timedelta(seconds=135),
                event_type="subsystem_degraded",
                source="thermal_controller",
                details="Simulated thermal regulation degraded; no real safe-mode action performed",
            ),
        ]
    )
    out["system_events"] = (
        pd.concat([out["system_events"], events], ignore_index=True)
        .sort_values("timestamp", kind="stable")
        .reset_index(drop=True)
    )
    return out, [
        ((ONSET + pd.Timedelta(seconds=second)).isoformat(), "E7 " + label)
        for second, label in STAGES[1:-1]
    ]


def ground_truth_intervals(scenario):
    """Inclusive one-second injected windows. Empty means known nominal E1.

    These labels describe injected activity, not confirmed real-world attacks.
    Rolling-feature aftereffects outside these windows count as false positives.
    """
    offsets = {
        "E1": [],
        "E2": [(0, 0)],
        "E3": [(0, 58)],
        "E4": [(0, 119)],
        "E5": [(0, 180)],
        "E6": [(0, 180)],
        "E7": [(20, 20), (45, 160)],
    }
    if scenario not in offsets:
        return None
    return [
        (ONSET + pd.Timedelta(seconds=a), ONSET + pd.Timedelta(seconds=b))
        for a, b in offsets[scenario]
    ]
