from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "scoring.json"


@lru_cache(maxsize=1)
def load_scoring_config() -> dict:
    with _CONFIG_PATH.open() as f:
        return json.load(f)
