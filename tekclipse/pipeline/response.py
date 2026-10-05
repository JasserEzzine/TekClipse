"""Display-only operator guidance. No command execution or device integration."""

ACTIONS = {
    "R1": [
        "Verify ground-station identity with the operator",
        "Consider rejecting the unrecognized command source",
    ],
    "R2": [
        "Consider temporarily restricting the command channel pending operator verification"
    ],
    "R3": [
        "Increase telemetry monitoring",
        "Consider affected-subsystem safe-mode simulation after operator verification",
    ],
    "NET": [
        "Investigate the unfamiliar communication peer",
        "Consider isolating the suspicious communication source",
    ],
    "SYS": [
        "Inspect subsystem logs and watchdog state",
        "Request operator verification before any recovery action",
    ],
    "ML": ["Review the listed telemetry deviations against the operational schedule"],
}


def recommended_responses(snapshot):
    correlated = bool(snapshot["incidents"])
    sources = {
        a["source"]
        for a in snapshot["active_alerts"]
        if a["severity"] in {"HIGH", "CRITICAL"} or correlated
    }
    return sorted({action for source in sources for action in ACTIONS.get(source, [])})
