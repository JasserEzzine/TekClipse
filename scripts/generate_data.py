from __future__ import annotations

import argparse
import sys
from time import perf_counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tekclipse.data.generator import generate_synthetic_dataset


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic TekClipse satellite dataset"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=168,
        help="Duration: 1–720 hours; default 7 days at 1 Hz",
    )
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    started = perf_counter()
    data = generate_synthetic_dataset(hours=args.hours, output_dir=args.output_dir)
    print(
        f"Generated {args.hours} hours in {perf_counter() - started:.2f}s (including storage)."
    )
    print({name: len(df) for name, df in data.items()})


if __name__ == "__main__":
    main()
