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
    parser.add_argument('--profile', choices=['original', 'phase_a', 'phase_a2'], default='original',
                        help='Explicit detector profile; original preserves the historical evaluation')
    parser.add_argument("--scientific", action="store_true", help="Run the independent-run Phase A protocol instead of the historical single-scenario evaluation")
    parser.add_argument("--stage", choices=["all", "validation", "test"], default="all")
    parser.add_argument("--protocol", type=Path, default=ROOT / "docs/phase-a/protocol.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results/phase-a")
    return parser.parse_args()


def run_selected():
    args = parse_args()
    if args.scientific and args.profile != 'original':
        raise ValueError('--scientific is the archived Phase A protocol; use --profile alone or scripts/benchmark_phase_a2.py')
    if args.scientific:
        from tekclipse.evaluation.scientific import run_study

        path = run_study(args.output, args.protocol, args.stage)
        print(f"Scientific evaluation saved: {path}")
        return
    data = generate_synthetic_dataset(hours=args.hours, persist=False)
    if args.profile == 'original':
        result = evaluate_held_out(data, args.scenario)
        filename = f"{args.scenario}-held-out.json"
    else:
        from tekclipse.evaluation.profile_evaluation import evaluate_profile
        from tekclipse.pipeline.profiles import fit_profile
        result = evaluate_profile(data, args.scenario, fit_profile(args.profile))
        filename = f'{args.scenario}-{args.profile}-held-out.json'
    path = save_json(result, filename)
    if result["available"]:
        print(result["method"])
        for name, metrics in result["comparisons"].items():
            print(f"{name}: {metrics}")
    else:
        print("Evaluation unavailable: " + result["reason"])
    print(f"Saved: {path}")


if __name__ == "__main__":
    run_selected()
