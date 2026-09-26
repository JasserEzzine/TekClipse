from __future__ import annotations

import csv
import sqlite3
from pathlib import Path


DEFAULT_RESULTS_DIR = Path(__file__).resolve().parents[2] / "results"


def ensure_results_dir(path: str | Path | None = None) -> Path:
    result_dir = Path(path) if path is not None else DEFAULT_RESULTS_DIR
    result_dir.mkdir(parents=True, exist_ok=True)
    return result_dir


def append_alerts_csv(alerts, output_dir: str | Path | None = None):
    result_dir = ensure_results_dir(output_dir)
    path = result_dir / "alerts.csv"
    fieldnames = ["timestamp", "source", "severity", "description", "score"]
    write_header = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        for row in alerts:
            writer.writerow(row)
    return path


def append_alerts_sqlite(alerts, output_dir: str | Path | None = None):
    result_dir = ensure_results_dir(output_dir)
    path = result_dir / "alerts.db"
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE IF NOT EXISTS alerts (timestamp TEXT, source TEXT, severity TEXT, description TEXT, score REAL)")
    conn.executemany(
        "INSERT INTO alerts (timestamp, source, severity, description, score) VALUES (?, ?, ?, ?, ?)",
        [(a["timestamp"], a["source"], a["severity"], a["description"], a["score"]) for a in alerts],
    )
    conn.commit()
    conn.close()
    return path


def save_json(data, filename: str, output_dir: str | Path | None = None):
    result_dir = ensure_results_dir(output_dir)
    path = result_dir / filename
    import json
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, default=str)
    return path


def save_summary(markdown, output_dir: str | Path | None = None):
    result_dir = ensure_results_dir(output_dir)
    path = result_dir / "summary.md"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(markdown)
    return path
