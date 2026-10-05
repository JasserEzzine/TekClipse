import pandas as pd
import pytest

from tekclipse.pipeline.correlation import correlate_alerts
from tekclipse.pipeline.trust import trust_snapshot


def evidence(source, second, number=0, severity="WARNING"):
    return dict(
        id=f"{source}-{second}-{number}",
        source=source,
        severity=severity,
        observed_at=(
            pd.Timestamp("2026-01-01T12:00Z") + pd.Timedelta(seconds=second)
        ).isoformat(),
        description="test evidence",
    )


def test_correlation_domains_bounded_window_and_no_inflation():
    assert not correlate_alerts([evidence("ML", 0), evidence("R3", 1)])
    assert not correlate_alerts([evidence("R1", 0), evidence("NET", 181)])
    pair = [evidence("R1", 0, severity="CRITICAL"), evidence("NET", 10)]
    first = correlate_alerts(pair)[0]
    assert first["sources"] == ["Commands", "Network"]
    assert (
        first["correlation_score"]
        == correlate_alerts(pair + [evidence("NET", 10, 1)])[0]["correlation_score"]
    )
    critical = correlate_alerts(pair + [evidence("R3", 30), evidence("SYS", 60)])[0]
    assert critical["severity"] == "CRITICAL"
    assert len(critical["contributing_alerts"]) == 4
    chain = correlate_alerts(
        [evidence("R1", 0), evidence("NET", 179), evidence("SYS", 358)]
    )
    assert len(chain) == 1 and chain[0]["sources"] == ["Commands", "Network"]
    with pytest.raises(ValueError):
        correlate_alerts(pair, 0)


def test_trust_is_causal_bounded_and_explainable():
    rows = [
        evidence("R1", 20, severity="CRITICAL"),
        evidence("NET", 45, severity="HIGH"),
        evidence("R3", 100),
        evidence("SYS", 120, severity="CRITICAL"),
    ]
    base = pd.Timestamp("2026-01-01T12:00Z")
    scores = [
        trust_snapshot(rows, base + pd.Timedelta(seconds=s))["score"]
        for s in [0, 20, 45, 100, 120]
    ]
    assert scores[0] == 100
    assert all(a > b for a, b in zip(scores, scores[1:]))
    final = trust_snapshot(rows, base + pd.Timedelta(seconds=120))
    assert final["status"] == "CRITICAL"
    assert final["score"] == 100 - sum(c["penalty"] for c in final["contributors"])
    assert trust_snapshot(rows, base + pd.Timedelta(seconds=400))["score"] == 100
    assert trust_snapshot([evidence("ML", 0)], base)["score"] >= 95
    assert (
        trust_snapshot(rows * 10, base + pd.Timedelta(seconds=120))["score"]
        == final["score"]
    )
