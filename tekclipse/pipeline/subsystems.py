"""Evidence-derived subsystem flags; NORMAL means no mapped active evidence."""

SUBSYSTEMS = (
    "Communications",
    "Thermal",
    "Power",
    "On-board computer",
    "Command channel",
)


def subsystem_statuses(snapshot):
    rows = []
    critical_ids = {
        identifier
        for incident in snapshot["incidents"]
        if incident["severity"] == "CRITICAL"
        for identifier in incident["contributing_alerts"]
    }
    for name in SUBSYSTEMS:
        alerts = [
            a for a in snapshot["active_alerts"] if name in a.get("subsystems", [])
        ]
        status = "NORMAL"
        if alerts:
            status = (
                "CRITICAL"
                if any(
                    a["severity"] == "CRITICAL" or a["id"] in critical_ids
                    for a in alerts
                )
                else "WARNING"
            )
        rows.append(
            dict(
                subsystem=name,
                status=status,
                evidence_count=len(alerts),
                reason=(
                    "; ".join(sorted({a["source"] for a in alerts}))
                    if alerts
                    else "No mapped active evidence"
                ),
            )
        )
    return rows
