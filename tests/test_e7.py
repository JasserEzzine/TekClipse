import pandas as pd
import pytest

from tekclipse.data.generator import generate_synthetic_dataset
from tekclipse.data.injection import get_scenario
from tekclipse.data.coordinated import ONSET, ground_truth_intervals
from tekclipse.pipeline.rules import detect_rule_alerts


def test_e7_reproducible_non_mutating_and_all_stages():
    nominal = generate_synthetic_dataset(13, persist=False)
    original = {k: v.copy() for k, v in nominal.items()}
    first, truth = get_scenario("E7")(nominal)
    second, other_truth = get_scenario("E7")(nominal)
    assert truth == other_truth
    assert len(truth) == 5
    for key in nominal:
        pd.testing.assert_frame_equal(first[key], second[key])
        pd.testing.assert_frame_equal(nominal[key], original[key])
    tel = first["telemetry"]
    alerts = detect_rule_alerts(first["commands"], tel[tel.timestamp >= ONSET])
    assert {a["source"] for a in alerts} == {"R1", "R2", "R3"}
    assert {"watchdog_reset", "subsystem_degraded"} <= set(
        first["system_events"].event_type
    )
    assert len(ground_truth_intervals("E7")) == 2
    with pytest.raises(ValueError):
        get_scenario("E7")(generate_synthetic_dataset(1, persist=False))
