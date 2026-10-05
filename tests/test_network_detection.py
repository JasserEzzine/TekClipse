import pandas as pd
import pytest

from tekclipse.data.generator import generate_synthetic_dataset
from tekclipse.data.injection import get_scenario
from tekclipse.pipeline.network import fit_network_baseline, detect_network_alerts


def test_nominal_passes_and_existing_e4():
    data = generate_synthetic_dataset(24, persist=False)
    baseline = fit_network_baseline(data["network"].iloc[:21600])
    assert detect_network_alerts(data["network"], baseline) == []
    injected, _ = get_scenario("E4")(data)
    alerts = detect_network_alerts(injected["network"], baseline)
    assert len(alerts) == 120
    assert alerts[0]["source"] == "NET"
    assert "packets/sec" in alerts[0]["description"]
    assert "203.0.113.10" in alerts[0]["description"]
    assert len(injected["network"]) == len(data["network"]) + 120


def test_protocol_novelty_and_empty_input():
    data = generate_synthetic_dataset(1, persist=False)["network"]
    baseline = fit_network_baseline(data)
    changed = data.iloc[:1].copy()
    changed["protocol"] = "ICMP"
    assert (
        "protocol: ICMP" in detect_network_alerts(changed, baseline)[0]["description"]
    )
    assert detect_network_alerts(changed.iloc[:0], baseline) == []
    with pytest.raises(ValueError):
        fit_network_baseline(pd.DataFrame())
