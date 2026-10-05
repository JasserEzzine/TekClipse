from tekclipse.dashboard.security_charts import attack_timeline, trust_history
from tekclipse.pipeline.response import recommended_responses
from tekclipse.pipeline.subsystems import subsystem_statuses


def test_empty_and_populated_timeline_and_trust_are_serializable():
    assert attack_timeline([], []).to_json()
    evidence = [
        dict(
            source="R1",
            observed_at="2026-01-01T12:00:20Z",
            description="Unauthorized source",
        )
    ]
    assert "Unauthorized source" in attack_timeline(evidence, []).to_json()
    assert trust_history([dict(at="2026-01-01T12:00:20Z", score=80)]).data[0].y == (80,)


def test_responses_are_display_only_and_evidence_based():
    assert recommended_responses(dict(active_alerts=[], incidents=[])) == []
    guidance = recommended_responses(
        dict(active_alerts=[dict(source="R1", severity="CRITICAL")], incidents=[])
    )
    assert any("ground-station" in text for text in guidance)
    assert all(isinstance(text, str) for text in guidance)


def test_subsystem_status_requires_mapped_evidence():
    snapshot = dict(
        active_alerts=[
            dict(id="a", source="R3", severity="WARNING", subsystems=["Thermal"])
        ],
        incidents=[],
    )
    states = {r["subsystem"]: r["status"] for r in subsystem_statuses(snapshot)}
    assert states["Thermal"] == "WARNING"
    assert states["Power"] == "NORMAL"
    snapshot["incidents"] = [dict(severity="CRITICAL", contributing_alerts=["a"])]
    assert (
        next(r for r in subsystem_statuses(snapshot) if r["subsystem"] == "Thermal")[
            "status"
        ]
        == "CRITICAL"
    )
