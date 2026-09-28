"""Populate mission data and save real nominal detector output for dashboard startup."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tekclipse.dashboard.data_service import (
    dataset_token,
    load_data,
    detect,
    save_nominal_preview,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hours", type=int, default=168)
    args = parser.parse_args()
    token = dataset_token(args.hours)
    data = load_data(args.hours, token)
    result = detect(args.hours, token, "E1")
    path = save_nominal_preview(args.hours, token, result)
    print({name: len(frame) for name, frame in data.items()})
    print(
        f"Saved {len(result['alerts']):,} actual nominal-preview alerts; detector time {result['seconds']:.2f}s"
    )
    print(path)


if __name__ == "__main__":
    main()
