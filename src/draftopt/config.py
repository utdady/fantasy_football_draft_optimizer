from __future__ import annotations

from pathlib import Path

MODE = "redraft"
SCORING = "PPR"
SEASON = 2026
N_TEAMS = 12
USER_SLOT_DEFAULT = 1
PICK_CLOCK_SECONDS = 60

# Default league: no K, IR is a roster slot but not drafted.
ROSTER_PRESETS = {
    "league_default": {
        "id": "league_default",
        "label": "Default (no K)",
        "description": "QB, 2 RB, 2 WR, TE, 2 FLEX, D/ST, 7 bench (+ IR, not drafted)",
        "slots": {
            "QB": 1,
            "RB": 2,
            "WR": 2,
            "TE": 1,
            "FLEX": 2,
            "DST": 1,
            "K": 0,
            "BENCH": 7,
            "IR": 1,
        },
        "draft_ir": False,
    },
    "espn_with_k": {
        "id": "espn_with_k",
        "label": "ESPN-style (with K)",
        "description": "QB, 2 RB, 2 WR, TE, 2 FLEX, D/ST, K, 6 bench",
        "slots": {
            "QB": 1,
            "RB": 2,
            "WR": 2,
            "TE": 1,
            "FLEX": 2,
            "DST": 1,
            "K": 1,
            "BENCH": 6,
            "IR": 0,
        },
        "draft_ir": False,
    },
}

DEFAULT_ROSTER_PRESET = "league_default"


def roster_draft_rounds(slots: dict[str, int], draft_ir: bool = False) -> int:
    """Starters + bench (+ IR only if drafted)."""
    total = 0
    for key, n in slots.items():
        if key == "IR" and not draft_ir:
            continue
        total += int(n or 0)
    return total


def get_roster_preset(preset_id: str | None = None) -> dict:
    key = preset_id or DEFAULT_ROSTER_PRESET
    if key not in ROSTER_PRESETS:
        key = DEFAULT_ROSTER_PRESET
    preset = ROSTER_PRESETS[key]
    slots = dict(preset["slots"])
    return {
        "id": preset["id"],
        "label": preset["label"],
        "description": preset["description"],
        "slots": slots,
        "draft_ir": bool(preset["draft_ir"]),
        "n_rounds": roster_draft_rounds(slots, preset["draft_ir"]),
    }


ROSTER_SLOTS = get_roster_preset()["slots"]
N_ROUNDS = get_roster_preset()["n_rounds"]
SKILL_POSITIONS = ("QB", "RB", "WR", "TE", "K", "DST")

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
DB_PATH = DATA_DIR / "draftopt.db"
EVAL_DB_PATH = DATA_DIR / "draftopt_eval.db"

SLEEPER_PLAYERS_URL = "https://api.sleeper.app/v1/players/nfl"
DP_IDS_URL = "https://raw.githubusercontent.com/dynastyprocess/data/master/files/db_playerids.csv"
DP_ECR_URL = "https://raw.githubusercontent.com/dynastyprocess/data/master/files/db_fpecr_latest.csv"
ESPN_PLAYERS_URL = (
    f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{SEASON}"
    "/segments/0/leaguedefaults/3?view=kona_player_info"
)
ESPN_PLAYER_LIMIT = 800

HTTP_HEADERS = {
    "User-Agent": "draftopt/0.1 (personal redraft tool)",
    "Accept": "application/json,text/csv,*/*",
}

PPR_ECR_PAGES = {
    "/nfl/rankings/ppr-cheatsheets.php",
    "/nfl/rankings/ppr-k-cheatsheets.php",
    "/nfl/rankings/ppr-dst-cheatsheets.php",
    "/nfl/rankings/k-cheatsheets.php",
    "/nfl/rankings/dst-cheatsheets.php",
}
