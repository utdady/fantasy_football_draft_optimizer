"""Phase 2 historical-eval schema (decision vs outcome separation).

Not wired into the live UI DB by default. Prefer a separate eval database
(e.g. data/draftopt_eval.db) when implementing P2.1+.

See results/PHASE2_HISTORICAL_EVAL.md and results/PHASE2_P22_SOURCES.md.
"""

from __future__ import annotations

import sqlite3

# Applied only via phase2.init_eval_db() — never mixed into draftopt.db.init
# without an explicit call site.

EVAL_SCHEMA = """
CREATE TABLE IF NOT EXISTS eval_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    season INTEGER NOT NULL,
    snapshot_date TEXT NOT NULL,
    label TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL,
    pipeline_proof INTEGER NOT NULL DEFAULT 0,
    evaluable INTEGER NOT NULL DEFAULT 0,
    outcome_season INTEGER,
    validation_status TEXT,
    validation_reason TEXT
);

CREATE TABLE IF NOT EXISTS eval_snapshot_players (
    snapshot_id TEXT NOT NULL,
    player_id TEXT NOT NULL,
    name TEXT,
    position TEXT,
    team TEXT,
    adp REAL,
    adp_source TEXT,
    adp_as_of TEXT NOT NULL,
    proj_ppr REAL,
    proj_source TEXT,
    proj_as_of TEXT NOT NULL,
    PRIMARY KEY (snapshot_id, player_id),
    FOREIGN KEY (snapshot_id) REFERENCES eval_snapshots(snapshot_id)
);

CREATE INDEX IF NOT EXISTS idx_eval_snap_players_adp
    ON eval_snapshot_players(snapshot_id, adp);

CREATE TABLE IF NOT EXISTS eval_outcomes (
    season INTEGER NOT NULL,
    player_id TEXT NOT NULL,
    actual_ppr_points REAL NOT NULL,
    games_played INTEGER,
    source TEXT NOT NULL,
    pulled_at TEXT NOT NULL,
    PRIMARY KEY (season, player_id, source)
);

CREATE TABLE IF NOT EXISTS eval_outcomes_weekly (
    season INTEGER NOT NULL,
    week INTEGER NOT NULL,
    season_type TEXT NOT NULL,
    player_id TEXT NOT NULL,
    gsis_id TEXT,
    position TEXT,
    team TEXT,
    actual_ppr_points REAL NOT NULL,
    source TEXT NOT NULL,
    pulled_at TEXT NOT NULL,
    PRIMARY KEY (season, week, season_type, player_id, source)
);

CREATE INDEX IF NOT EXISTS idx_eval_outcomes_weekly_player
    ON eval_outcomes_weekly(season, player_id);

CREATE TABLE IF NOT EXISTS eval_player_map (
    source TEXT NOT NULL,
    source_player_id TEXT NOT NULL,
    player_id TEXT NOT NULL,
    gsis_id TEXT,
    sleeper_id TEXT,
    espn_id TEXT,
    method TEXT NOT NULL,
    notes TEXT,
    PRIMARY KEY (source, source_player_id)
);

CREATE TABLE IF NOT EXISTS eval_player_unresolved (
    source TEXT NOT NULL,
    source_player_id TEXT NOT NULL,
    name TEXT,
    position TEXT,
    team TEXT,
    reason TEXT NOT NULL,
    PRIMARY KEY (source, source_player_id)
);

CREATE TABLE IF NOT EXISTS eval_drafts (
    eval_draft_id TEXT PRIMARY KEY,
    snapshot_id TEXT NOT NULL,
    strategy TEXT NOT NULL,
    user_slot INTEGER NOT NULL,
    seed INTEGER NOT NULL,
    n_teams INTEGER NOT NULL,
    n_rounds INTEGER NOT NULL,
    roster_json TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (snapshot_id) REFERENCES eval_snapshots(snapshot_id)
);

CREATE TABLE IF NOT EXISTS eval_picks (
    eval_draft_id TEXT NOT NULL,
    overall INTEGER NOT NULL,
    team_slot INTEGER NOT NULL,
    round INTEGER NOT NULL,
    player_id TEXT NOT NULL,
    made_by TEXT NOT NULL,
    PRIMARY KEY (eval_draft_id, overall),
    FOREIGN KEY (eval_draft_id) REFERENCES eval_drafts(eval_draft_id)
);

CREATE INDEX IF NOT EXISTS idx_eval_picks_player
    ON eval_picks(eval_draft_id, player_id);
"""

# Columns added after the first P2.1 freeze (CREATE IF NOT EXISTS does not alter).
_EVAL_SNAPSHOT_EXTRA_COLS: tuple[tuple[str, str], ...] = (
    ("pipeline_proof", "INTEGER NOT NULL DEFAULT 0"),
    ("evaluable", "INTEGER NOT NULL DEFAULT 0"),
    ("outcome_season", "INTEGER"),
    ("validation_status", "TEXT"),
    ("validation_reason", "TEXT"),
)

# Machine-readable refusal / validation reasons (spike + later gates).
VALIDATION_REASONS = (
    "adp_as_of_unverified",
    "adp_league_size_mismatch",
    "historical_projection_missing",
    "player_mapping_below_threshold",
    "outcome_coverage_below_threshold",
    "source_validation_pending",
)


def migrate_eval_schema(conn: sqlite3.Connection) -> None:
    """Create tables and add any missing eval_snapshots flag columns."""
    conn.executescript(EVAL_SCHEMA)
    existing = {
        row[1]
        for row in conn.execute("PRAGMA table_info(eval_snapshots)").fetchall()
    }
    for name, decl in _EVAL_SNAPSHOT_EXTRA_COLS:
        if name not in existing:
            conn.execute(f"ALTER TABLE eval_snapshots ADD COLUMN {name} {decl}")
    conn.commit()
