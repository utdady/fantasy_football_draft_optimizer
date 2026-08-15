"""Load key=value pairs from a local .env into os.environ (no dependency).

Does not override variables already set in the process environment.
Never commit real secrets — keep `.env` gitignored; use `.env.example` as template.
"""

from __future__ import annotations

import os
from pathlib import Path

from draftopt.config import ROOT


def load_dotenv(path: Path | None = None) -> Path | None:
    """
    Load `.env` from repo root (or given path).

    Returns the path loaded, or None if missing.
    """
    env_path = path or (ROOT / ".env")
    if not env_path.is_file():
        return None
    text = env_path.read_text(encoding="utf-8-sig")
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        if not key:
            continue
        # Do not clobber an explicitly set shell env var.
        if key in os.environ and os.environ[key] != "":
            continue
        os.environ[key] = val
    return env_path
