"""Explainable potential consequences, not predictions of spacecraft failure.

This layer consumes an existing causal review snapshot. It never changes alerts,
severity, correlation, trust or recommendations. Every inference keeps evidence IDs.
"""

from __future__ import annotations

IMPACT_DISCLAIMER = "Mission impact represents simulated decision-support reasoning and does not predict physical spacecraft failure."

MAPPINGS = {
    "R1": (
        "Unauthorized command",
        "Command integrity at risk",
        "Command channel",
        "Potential interruption or unintended change to nominal operations",
    ),
    "R2": (
        "Command burst",
        "Command availability at risk",
        "Command channel",
        "Possible delays to legitimate operator commands",
    ),
    "NET": (
        "Abnormal communication activity",
        "Communication integrity / availability at risk",
        "Communications",
        "Potential degradation of ground-to-space communication",
    ),
    "THERMAL": (
        "Thermal limit exceeded",
        "Thermal operating margin at risk",
        "Thermal",
        "Possible interruption of temperature-sensitive payload operations",
    ),
    "POWER": (
        "Voltage limit exceeded",
        "Power operating margin at risk",
        "Power",
        "Potential disruption to power-dependent subsystem operation",
    ),
    "OBC": (
        "On-board computer event",
        "On-board processing continuity at risk",
        "On-board computer",
        "Possible interruption of onboard processing or scheduled tasks",
    ),
    "SYS_THERMAL": (
        "Thermal subsystem event",
        "Thermal regulation requires review",
        "Thermal",
        "Possible reduction in payload operating availability",
    ),
    "ML": (
        "Unusual telemetry pattern",
        "Operational state requires verification",
        "Telemetry",
        "Possible operational deviation; cause and mission effect remain unconfirmed",
    ),
}


def mission_impacts(snapshot):
    groups = {}
    for alert in snapshot["active_alerts"]:
        source = alert["source"]
        keys = [source] if source in {"R1", "R2", "NET", "ML"} else []
        if source == "R3":
            keys = [
                key
                for subsystem, key in [("Thermal", "THERMAL"), ("Power", "POWER")]
                if subsystem in alert.get("subsystems", [])
            ]
        elif source == "SYS":
            keys = [
                key
                for subsystem, key in [
                    ("On-board computer", "OBC"),
                    ("Thermal", "SYS_THERMAL"),
                ]
                if subsystem in alert.get("subsystems", [])
            ]
        for key in keys:
            groups.setdefault(key, []).append(alert)
    impacts = []
    rank = {"INFO": 0, "WARNING": 1, "HIGH": 2, "CRITICAL": 3}
    for key, alerts in groups.items():
        event, consequence, subsystem, mission = MAPPINGS[key]
        severity = max((a["severity"] for a in alerts), key=lambda s: rank.get(s, 0))
        impacts.append(
            dict(
                key=key,
                event=event,
                security_consequence=consequence,
                subsystem=subsystem,
                potential_consequence=mission,
                severity=severity,
                evidence_ids=[a["id"] for a in alerts],
                first_observed=min(a["observed_at"] for a in alerts),
                reasoning="Deterministic decision-support mapping from observed detector evidence; not proven physical impact.",
            )
        )
    return sorted(
        impacts,
        key=lambda r: (-rank.get(r["severity"], 0), r["first_observed"], r["key"]),
    )
