"""Independent operational deviations, not new cyberattack capabilities."""
from __future__ import annotations

import numpy as np
import pandas as pd
from tekclipse.evaluation.study_data import make_case, event


def make_a2_case(nominal, name, protocol, phase_a, seed):
    if name not in protocol["novel_cases"]:
        return make_case(nominal, name, phase_a, seed)
    data = {k: v.copy(deep=True) for k, v in nominal.items()}
    telemetry = data["telemetry"]
    start = telemetry.timestamp.min() + pd.Timedelta(seconds=protocol["novel_start_seconds"])
    end = start + pd.Timedelta(seconds=protocol["novel_duration_seconds"] - 1)
    mask = telemetry.timestamp.between(start, end)
    if name == "operational_thermal_drift":
        offset = np.minimum(np.arange(mask.sum()) / protocol["thermal_ramp_seconds"], 1) * protocol["thermal_drift_c"]
        telemetry.loc[mask, "temperature_c"] += offset
    elif name == "operational_power_relationship":
        telemetry.loc[mask, "power_w"] += protocol["power_relationship_w"]
    elif name == "operational_voltage_relationship":
        telemetry.loc[mask, "voltage_v"] += protocol["voltage_relationship_v"]
    elif name == "nominal_thermal_regime":
        telemetry["temperature_c"] += protocol["nominal_temperature_offset_c"]
    elif name == "nominal_power_regime":
        telemetry["power_w"] += protocol["nominal_power_offset_w"]
    events = [] if name.startswith("nominal_") else [event(name, start, end, "Telemetry", ["R3", "ML"])]
    return data, events, False
