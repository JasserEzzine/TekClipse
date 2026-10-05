"""Bounded, explainable temporal correlation; association does not establish cause."""

from __future__ import annotations

import pandas as pd

DOMAINS = {
    "R1": "Commands",
    "R2": "Commands",
    "R3": "Telemetry",
    "ML": "Telemetry",
    "NET": "Network",
    "SYS": "System events",
}


def correlate_alerts(evidence, window_seconds=180):
    if not 1 <= window_seconds <= 3600:
        raise ValueError("Correlation window must be 1..3600 seconds")
    if not evidence:
        return []
    ordered = sorted(evidence, key=lambda a: (pd.Timestamp(a["observed_at"]), a["id"]))
    # Seed at actionable evidence, not background ML. Include subsequent evidence
    # only within the same bounded window; each alert belongs to at most one group.
    groups, consumed = [], set()
    delta = pd.Timedelta(seconds=window_seconds)
    for seed in ordered:
        if seed["id"] in consumed or seed["source"] == "ML":
            continue
        start = pd.Timestamp(seed["observed_at"])
        group = [
            a
            for a in ordered
            if a["id"] not in consumed
            and start <= pd.Timestamp(a["observed_at"]) <= start + delta
        ]
        consumed.update(a["id"] for a in group)
        sources = sorted({DOMAINS.get(a["source"], "Other") for a in group})
        if len(sources) < 2:
            continue
        detectors = sorted({a["source"] for a in group})
        # Independent domains, actionable detector families, and critical evidence.
        # ML and R3 count as one domain; repeated samples earn no extra confidence.
        score = min(
            100,
            20 * len(sources)
            + 5 * len(set(detectors) - {"ML"})
            + (10 if any(a["severity"] == "CRITICAL" for a in group) else 0),
        )
        severity = "CRITICAL" if len(sources) >= 3 and score >= 75 else "HIGH"
        first_by_domain = {}
        for a in group:
            first_by_domain.setdefault(
                DOMAINS.get(a["source"], "Other"), a["observed_at"]
            )
        detected_at = sorted(first_by_domain.values(), key=pd.Timestamp)[1]
        groups.append(
            dict(
                id=f"INC-{len(groups)+1:03d}",
                start=group[0]["observed_at"],
                end=group[-1]["observed_at"],
                detected_at=detected_at,
                sources=sources,
                contributing_alerts=[a["id"] for a in group],
                severity=severity,
                correlation_score=score,
                explanation=f"{', '.join(sources)} evidence within {window_seconds}s; "
                f"detectors {', '.join(detectors)}. Temporal association, not confirmed attack attribution.",
            )
        )
    return groups
