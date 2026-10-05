"""Explanations and observation times alongside unchanged R1–R3/IF outputs."""

from __future__ import annotations

import pandas as pd


def detect_system_alerts(events):
    recognized = {"watchdog_reset", "subsystem_degraded"}
    return [
        dict(
            timestamp=row.timestamp,
            source="SYS",
            severity="CRITICAL",
            description=f"{row.event_type} on {row.source}: {row.details}",
            score=1.0,
        )
        for row in events[events.event_type.isin(recognized)].itertuples()
    ]


def explain_alerts(alerts, data, nominal_features, features):
    """Return new records; never alter original detector results.

    ML feature deviations are descriptive z-scores, NOT causal feature attribution.
    R2's legacy minute timestamp is retained; observed_at is its 11th command.
    """
    numeric = nominal_features.select_dtypes(include="number")
    means, deviations = numeric.mean(), numeric.std(ddof=0).clip(lower=1e-6)
    values = features.set_index("timestamp")
    telemetry = data["telemetry"].set_index("timestamp")
    commands = data["commands"].sort_values("timestamp")
    command_times = {
        minute: frame.timestamp.iloc[10]
        for minute, frame in commands.groupby(pd.Grouper(key="timestamp", freq="min"))
        if len(frame) > 10
    }
    records = []
    for index, row in enumerate(alerts):
        item = dict(row)
        ts = pd.to_datetime(row["timestamp"], utc=True)
        item.update(
            id=f"A-{index:06d}", timestamp=ts.isoformat(), observed_at=ts.isoformat()
        )
        source = row["source"]
        subsystems = []
        if source in {"R1", "R2"}:
            subsystems = ["Command channel"]
        if source == "R2":
            item["observed_at"] = pd.Timestamp(
                command_times[ts.floor("min")]
            ).isoformat()
            item[
                "description"
            ] += "; threshold >10/min; first observable at the 11th command (original timestamp is bin start)"
        elif source == "R3" and ts in telemetry.index:
            sample = telemetry.loc[ts]
            why = []
            if sample.temperature_c > 85:
                why.append(
                    f"Temperature {sample.temperature_c:.1f} C exceeds 85 C by {sample.temperature_c - 85:.1f} C"
                )
                subsystems.append("Thermal")
            if sample.voltage_v < 26 or sample.voltage_v > 30:
                why.append(f"Voltage {sample.voltage_v:.2f} V outside 26–30 V")
                subsystems.append("Power")
            item["description"] = "; ".join(why)
        elif source == "ML" and ts in values.index:
            standardized = (
                ((values.loc[ts, numeric.columns] - means) / deviations)
                .abs()
                .nlargest(3)
            )
            item["description"] += (
                "; largest nominal standardized deviations: "
                + ", ".join(
                    f"{name}={value:.1f} SD" for name, value in standardized.items()
                )
                + ". Context only, not model attribution or probability."
            )
            for name in standardized.index:
                if name.startswith("temperature"):
                    subsystems.append("Thermal")
                elif name.startswith(("battery", "voltage", "power")):
                    subsystems.append("Power")
                elif name.startswith(("cpu", "ram")):
                    subsystems.append("On-board computer")
                elif name.startswith("signal"):
                    subsystems.append("Communications")
        elif source == "NET":
            subsystems = ["Communications"]
        elif source == "SYS":
            subsystems = (
                ["Thermal"]
                if "thermal_controller" in item["description"]
                else ["On-board computer"]
            )
        item["subsystems"] = sorted(set(subsystems))
        records.append(item)
    return sorted(records, key=lambda a: (a["observed_at"], a["id"]))
