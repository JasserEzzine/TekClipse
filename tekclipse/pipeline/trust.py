"""Deterministic policy indicator; neither probability nor certified spacecraft health."""

from __future__ import annotations

import pandas as pd

from tekclipse.pipeline.correlation import correlate_alerts

PENALTIES = {
    "R1": ("Unauthorized command", 20),
    "R2": ("Command burst", 12),
    "R3": ("Telemetry hard limit", 18),
    "NET": ("Network anomaly", 12),
    "SYS": ("Subsystem impact event", 12),
    "ML": ("Telemetry ML deviation", 3),
}


def trust_snapshot(evidence, at, window_seconds=180):
    at = pd.to_datetime(at, utc=True)
    start = at - pd.Timedelta(seconds=window_seconds)
    active = [a for a in evidence if start <= pd.Timestamp(a["observed_at"]) <= at]
    incidents = correlate_alerts(active, window_seconds)
    deductions = []
    for source, (label, cap) in PENALTIES.items():
        matching = [a for a in active if a["source"] == source]
        if matching:
            # Weight severity, cap each detector family to avoid sample-count bias.
            weight = max(
                {"INFO": 0, "WARNING": 0.75, "HIGH": 1, "CRITICAL": 1}.get(
                    a["severity"], 0.75
                )
                for a in matching
            )
            deductions.append(
                dict(
                    contributor=label,
                    penalty=round(cap * weight),
                    alerts=len(matching),
                    source=source,
                )
            )
    if incidents:
        penalty = 19 if any(i["severity"] == "CRITICAL" for i in incidents) else 10
        deductions.append(
            dict(
                contributor="Multi-source correlation",
                penalty=penalty,
                alerts=len(incidents),
                source="CORRELATION",
            )
        )
    score = max(0, 100 - sum(row["penalty"] for row in deductions))
    return dict(
        score=score,
        status="NORMAL" if score >= 80 else "SUSPICIOUS" if score >= 50 else "CRITICAL",
        label="Prototype Operational Trust Indicator",
        at=at.isoformat(),
        window_seconds=window_seconds,
        contributors=deductions,
        active_alerts=active,
        incidents=incidents,
    )
