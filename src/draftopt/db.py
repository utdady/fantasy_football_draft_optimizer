from __future__ import annotations

import sqlite3
from pathlib import Path

from draftopt.config import DATA_DIR, DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
    player_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    position TEXT,
    team TEXT,
    bye INTEGER,
    status TEXT,
    injury_status TEXT,
    sleeper_id TEXT,
    espn_id TEXT,
    fantasypros_id TEXT,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS player_aliases (
    player_id TEXT NOT NULL,
    alias TEXT NOT NULL,
    PRIMARY KEY (player_id, alias),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

CREATE INDEX IF NOT EXISTS idx_aliases_alias ON player_aliases(alias);

CREATE TABLE IF NOT EXISTS adp_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id TEXT NOT NULL,
    source TEXT NOT NULL,
    adp REAL,
    pulled_at TEXT NOT NULL,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

CREATE TABLE IF NOT EXISTS projections_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id TEXT NOT NULL,
    source TEXT NOT NULL,
    season_points REAL,
    pulled_at TEXT NOT NULL,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

CREATE TABLE IF NOT EXISTS rankings_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_id TEXT NOT NULL,
    source TEXT NOT NULL,
    ecr REAL,
    sd REAL,
    best INTEGER,
    worst INTEGER,
    pulled_at TEXT NOT NULL,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

CREATE TABLE IF NOT EXISTS ingest_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    pulled_at TEXT NOT NULL,
    raw_path TEXT,
    n_rows INTEGER
);

CREATE TABLE IF NOT EXISTS drafts (
    draft_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    current_pick INTEGER NOT NULL DEFAULT 1,
    user_slot INTEGER NOT NULL DEFAULT 1,
    user_name TEXT NOT NULL DEFAULT 'You',
    n_teams INTEGER NOT NULL,
    n_rounds INTEGER NOT NULL,
    roster_json TEXT
);

CREATE TABLE IF NOT EXISTS picks (
    draft_id TEXT NOT NULL,
    overall INTEGER NOT NULL,
    team_slot INTEGER NOT NULL,
    round INTEGER NOT NULL,
    player_id TEXT NOT NULL,
    picked_at TEXT NOT NULL,
    made_by TEXT NOT NULL DEFAULT 'user',
    PRIMARY KEY (draft_id, overall),
    FOREIGN KEY (draft_id) REFERENCES drafts(draft_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

CREATE INDEX IF NOT EXISTS idx_picks_player ON picks(draft_id, player_id);
"""


def connect(path: Path | None = None) -> sqlite3.Connection:
    db_path = path or DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _add_column(conn: sqlite3.Connection, table: str, ddl: str) -> None:
    col = ddl.split()[0]
    existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    if col not in existing:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")


def init(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    _add_column(conn, "drafts", "user_name TEXT DEFAULT 'You'")
    _add_column(conn, "drafts", "roster_json TEXT")
    _add_column(conn, "picks", "made_by TEXT DEFAULT 'user'")
    conn.commit()
