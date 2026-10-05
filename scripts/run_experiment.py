from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tekclipse.config import load_config
from tekclipse.data.generator import generate_synthetic_dataset
from tekclipse.evaluation.validated import evaluate_held_out
from tekclipse.storage.db import save_json


def parse_args():
    parser = argparse.ArgumentParser(description="Run TekClipse experiment scenarios")
    parser.add_argument(
        "--scenario", choices=["E1", "E2", "E3", "E4", "E5", "E6", "E7"], default="E1"
    )
    parser.add_argument("--hours", type=int, default=24)
    return parser.parse_args()


def run_selected():
    args = parse_args()
    data = generate_synthetic_dataset(hours=args.hours, persist=False)
    result = evaluate_held_out(data, args.scenario)
    path = save_json(result, f"{args.scenario}-held-out.json")
    if result["available"]:
        print(result["method"])
        for name, metrics in result["comparisons"].items():
            print(f"{name}: {metrics}")
    else:
        print("Evaluation unavailable: " + result["reason"])
    print(f"Saved: {path}")


if __name__ == "__main__":
    run_selected()
