from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

from tekclipse.storage.db import append_alerts_csv, append_alerts_sqlite


def merge_alerts(alerts):
    rows = []
    for alert in alerts:
        rows.append({
            "timestamp": alert.get("timestamp"),
            "source": alert.get("source"),
            "severity": alert.get("severity", "INFO"),
            "description": alert.get("description", ""),
            "score": alert.get("score", 0.0),
        })
    return rows


def persist_alerts(alerts, output_dir: str | Path | None = None):
    rows = merge_alerts(alerts)
    if not rows:
        return []
    append_alerts_csv(rows, output_dir=output_dir)
    append_alerts_sqlite(rows, output_dir=output_dir)
    return rows
