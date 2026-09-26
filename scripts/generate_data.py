from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tekclipse.data.generator import generate_synthetic_dataset


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic TekClipse satellite dataset")
    parser.add_argument("--hours", type=int, default=24, help="Duration in hours")
    args = parser.parse_args()
    generate_synthetic_dataset(hours=args.hours)
    print(f"Generated synthetic dataset for {args.hours} hours.")


if __name__ == "__main__":
    main()
