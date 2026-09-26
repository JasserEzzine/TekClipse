from __future__ import annotations

from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.yaml"


def load_config(path: str | Path | None = None) -> dict:
    config_path = Path(path) if path is not None else CONFIG_PATH
    with open(config_path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}
