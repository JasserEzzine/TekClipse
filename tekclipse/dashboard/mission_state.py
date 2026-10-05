"""Small presentation models derived solely from already-observed evidence."""

from __future__ import annotations

import pandas as pd

from tekclipse.pipeline.mission_impact import mission_impacts
from tekclipse.pipeline.subsystems import subsystem_statuses
from tekclipse.pipeline.response import recommended_responses

SOURCE_NAMES = {
    "R1": "Unauthorized command",
    "NET": "Network anomaly",
    "R2": "Command burst",
    "R3": "Telemetry limit",
    "ML": "Telemetry deviation",
    "SYS": "Subsystem event",
}


def attack_chain(snapshot):
    """First observed evidence per family, sorted by actual observation time."""
    nodes = []
    for source, label in SOURCE_NAMES.items():
        alerts = [a for a in snapshot["active_alerts"] if a["source"] == source]
        if alerts:
            first = min(alerts, key=lambda a: pd.Timestamp(a["observed_at"]))
            nodes.append(
                dict(
                    kind=source,
                    label=label,
                    at=first["observed_at"],
                    severity=first["severity"],
                    evidence_ids=[a["id"] for a in alerts],
                    explanation=first["description"],
                )
            )
    for incident in snapshot["incidents"]:
        nodes.append(
            dict(
                kind="CORRELATION",
                label="Multi-source incident",
                at=incident["detected_at"],
                severity=incident["severity"],
                evidence_ids=incident["contributing_alerts"],
                explanation="Temporal association across "
                + ", ".join(incident["sources"])
                + "; severity assessed at current review time.",
            )
        )
    # At a shared timestamp, show the triggering observation before its association.
    return sorted(
        nodes,
        key=lambda n: (pd.Timestamp(n["at"]), n["kind"] == "CORRELATION", n["kind"]),
    )


def mission_briefing(snapshot, view=None):
    """Show actual data availability, not an invented physical ground contact.

    Raw bounded review samples avoid future data in the display's aggregated bins.
    Presence of network records is explicitly different from a scheduled RF pass.
    """
    view = view or {}
    at = pd.Timestamp(snapshot["at"])
    sample = None
    raw = view.get("review_telemetry")
    if raw is not None and not raw.empty:
        candidates = raw[raw.timestamp <= at]
        if not candidates.empty:
            latest = candidates.iloc[-1]
            if at - latest.timestamp <= pd.Timedelta(seconds=2):
                sample = latest.to_dict()
    packets = view.get("review_network")
    network_present = False
    if packets is not None and not packets.empty:
        network_present = bool(
            packets.timestamp.between(at - pd.Timedelta(seconds=2), at).any()
        )
    events = view.get("events")
    contact = "UNKNOWN"
    if events is not None and not events.empty:
        changes = events[
            (events.timestamp <= at)
            & events.event_type.isin(["contact_acquired", "contact_closed"])
        ].sort_values("timestamp")
        if not changes.empty:
            contact = (
                "IN PASS"
                if changes.iloc[-1].event_type == "contact_acquired"
                else "OUT OF PASS"
            )
    states = subsystem_statuses(snapshot)
    state_map = {s["subsystem"]: s["status"] for s in states}
    command_ids = [
        a["id"] for a in snapshot["active_alerts"] if a["source"] in {"R1", "R2"}
    ]
    network_ids = [a["id"] for a in snapshot["active_alerts"] if a["source"] == "NET"]
    return dict(
        satellite="SAT-01",
        identity_note="Simulated spacecraft",
        at=at.isoformat(),
        elapsed_seconds=max(
            0, int((at - pd.Timestamp(view.get("start", at))).total_seconds())
        ),
        telemetry_active=sample is not None,
        network_active=network_present,
        scheduled_contact=contact,
        sample=sample,
        states=states,
        link_status=state_map["Communications"],
        ground_space=[
            dict(segment="Ground segment / command origin", evidence_ids=command_ids),
            dict(segment="Communication link", evidence_ids=network_ids),
            dict(
                segment="Space segment / SAT-01",
                evidence_ids=[
                    a["id"]
                    for a in snapshot["active_alerts"]
                    if a["source"] in {"R3", "ML", "SYS"}
                ],
            ),
        ],
        chain=attack_chain(snapshot),
        impacts=mission_impacts(snapshot),
        recommendations=recommended_responses(snapshot),
    )
