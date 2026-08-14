"""Phase 2 historical-eval schema stubs (decision vs outcome separation).

Not wired into the live UI DB by default. Prefer a separate eval database
(e.g. data/draftopt_eval.db) when implementing P2.1+.

See results/PHASE2_HISTORICAL_EVAL.md.
"""

from __future__ import annotations

# Applied only via phase2.init_eval_db() — never mixed into draftopt.db.init
# without an explicit call site.

EVAL_SCHEMA = """
CREATE TABLE IF NOT EXISTS eval_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    season INTEGER NOT NULL,
    snapshot_date TEXT NOT NULL,
    label TEXT NOT NULL,
    notes TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS eval_snapshot_players (
    snapshot_id TEXT NOT NULL,
    player_id TEXT NOT NULL,
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
