import json
import sqlite3
from pathlib import Path

import pytest

from draftopt import db
from draftopt.ingest import build_catalog
from draftopt.sources import dynastyprocess, espn, sleeper

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    db.init(c)
    return c


@pytest.fixture
def catalog(conn):
    sleeper_rows = sleeper.parse(json.loads((FIXTURES / "sleeper_players.json").read_text(encoding="utf-8")))
    dp_ids = dynastyprocess.parse_ids((FIXTURES / "db_playerids.csv").read_text(encoding="utf-8"))
    ecr_rows = dynastyprocess.parse_ecr((FIXTURES / "db_fpecr_latest.csv").read_text(encoding="utf-8"))
    espn_rows = espn.parse(json.loads((FIXTURES / "espn_players.json").read_text(encoding="utf-8")))
    return build_catalog(conn, sleeper_rows, dp_ids, ecr_rows, espn_rows, "2026-08-12T00:00:00Z")
