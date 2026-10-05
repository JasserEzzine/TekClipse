from copy import deepcopy

import pandas as pd

from tekclipse.pipeline.trust import trust_snapshot
from tekclipse.pipeline.mission_impact import mission_impacts
from tekclipse.dashboard.mission_state import mission_briefing, attack_chain
from tekclipse.dashboard.mission_visuals import satellite_svg, impact_reasoning_html

BASE = pd.Timestamp("2026-01-01T12:00Z")


def alert(source, second, subsystems=()):
    return dict(
        id=f"{source}-{second}",
        source=source,
        severity="CRITICAL",
        description="Observed fixture",
        observed_at=(BASE + pd.Timedelta(seconds=second)).isoformat(),
        subsystems=list(subsystems),
    )


def test_mission_impact_is_traceable_causal_and_does_not_mutate_trust():
    rows = [
        alert("R1", 20),
        alert("NET", 45, ["Communications"]),
        alert("R3", 100, ["Thermal"]),
        alert("SYS", 120, ["On-board computer"]),
    ]
    early = trust_snapshot(rows, BASE)
    assert mission_impacts(early) == []
    snapshot = trust_snapshot(rows, BASE + pd.Timedelta(seconds=120))
    original = deepcopy(snapshot)
    impacts = mission_impacts(snapshot)
    assert {i["key"] for i in impacts} == {"R1", "NET", "THERMAL", "OBC"}
    assert all(
        i["evidence_ids"]
        and i["potential_consequence"].startswith(("Possible", "Potential"))
        for i in impacts
    )
    assert snapshot == original
    assert "POWER" not in {i["key"] for i in impacts}


def test_chain_preserves_real_order_without_future_stages():
    rows = [alert("NET", 45), alert("R1", 20), alert("SYS", 120)]
    snapshot = trust_snapshot(rows, BASE + pd.Timedelta(seconds=45))
    chain = attack_chain(snapshot)
    assert chain[0]["kind"] == "R1"
    assert "SYS" not in {n["kind"] for n in chain}
    assert all(pd.Timestamp(n["at"]) <= BASE + pd.Timedelta(seconds=45) for n in chain)


def test_ground_link_uses_available_records_and_distinguishes_rf_contact():
    snapshot = trust_snapshot([], BASE)
    unavailable = mission_briefing(snapshot)
    assert not unavailable["telemetry_active"] and not unavailable["network_active"]
    view = dict(
        start=BASE - pd.Timedelta(hours=12),
        review_telemetry=pd.DataFrame(
            [
                dict(timestamp=BASE, temperature_c=40),
                dict(timestamp=BASE + pd.Timedelta(seconds=100), temperature_c=88),
            ]
        ),
        review_network=pd.DataFrame([dict(timestamp=BASE)]),
        events=pd.DataFrame(
            [
                dict(
                    timestamp=BASE - pd.Timedelta(minutes=60),
                    event_type="contact_closed",
                ),
                dict(
                    timestamp=BASE + pd.Timedelta(minutes=60),
                    event_type="contact_acquired",
                ),
            ]
        ),
    )
    briefing = mission_briefing(snapshot, view)
    assert briefing["telemetry_active"] and briefing["network_active"]
    assert briefing["scheduled_contact"] == "OUT OF PASS"
    assert briefing["sample"]["temperature_c"] == 40
    assert briefing["elapsed_seconds"] == 43200
    assert not any(row["evidence_ids"] for row in briefing["ground_space"])


def test_vector_asset_is_valid_and_mission_labels_are_escaped():
    import base64
    import re
    import xml.etree.ElementTree as ET

    briefing = mission_briefing(trust_snapshot([], BASE))
    image = satellite_svg(briefing)
    encoded = re.search(r"base64,([^\"]+)", image).group(1)
    svg = base64.b64decode(encoded)
    assert ET.fromstring(svg).tag.endswith("svg")
    assert b"SAT-01" in svg
    impact = dict(
        event="<script>alert(1)</script>",
        security_consequence="risk",
        subsystem="test",
        potential_consequence="Potential effect",
        evidence_ids=["a"],
    )
    assert "<script>" not in impact_reasoning_html([impact])
