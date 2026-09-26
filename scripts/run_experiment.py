from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tekclipse.config import load_config
from tekclipse.data.generator import generate_synthetic_dataset
from tekclipse.data.injection import get_scenario
from tekclipse.evaluation.runner import evaluate_scenario


def parse_args():
    parser = argparse.ArgumentParser(description="Run TekClipse experiment scenarios")
    parser.add_argument("--scenario", choices=["E1", "E2", "E3", "E4", "E5", "E6"], default="E1")
    return parser.parse_args()


def run_selected():
    args = parse_args()
    cfg = load_config()
    data = generate_synthetic_dataset(hours=cfg["simulation"]["hours"])
    scenario_data = data.copy()
    if args.scenario != "E1":
        scenario_data = get_scenario(args.scenario)(scenario_data)[0]
    result = evaluate_scenario(args.scenario, scenario_data)
    print(f"Scenario: {result['scenario']}")
    print(f"Metrics: {result['metrics']}")
    print(f"Alerts: {len(result['alerts'])}")


if __name__ == "__main__":
    run_selected()
