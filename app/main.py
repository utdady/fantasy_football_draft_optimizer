from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from draftopt.autopsy import DISAGREE_CATEGORIES, autopsy_analyze, dump_case, format_analyze_markdown, log_disagreement
from draftopt import db
from draftopt.config import N_TEAMS, PICK_CLOCK_SECONDS, ROSTER_PRESETS, get_roster_preset
from draftopt.draft.cpu import cpu_pick
from draftopt.draft.grade import grade_draft
from draftopt.draft.state import (
    DraftError,
    create_draft,
    record_human_pick,
    resolve_player,
    search_remaining,
    snapshot,
    undo_pick,
)
from draftopt.recommend import recommend
from draftopt.strategies import get_strategy

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Draft Optimizer V1")


def get_conn():
    conn = db.connect()
    db.init(conn)
    return conn


def payload(conn, draft_id: str, strategy: str = "marginal") -> dict:
    state = snapshot(conn, draft_id)
    out = {
        "state": state,
        "recommend": recommend(conn, draft_id, strategy=strategy),
        "strategy": strategy,
    }
    if state.get("complete"):
        out["grade"] = grade_draft(conn, draft_id)
    return out


class CreateDraftBody(BaseModel):
    user_slot: int = Field(default=1, ge=1, le=N_TEAMS)
    user_name: str = Field(default="You", min_length=1, max_length=40)
    roster_preset: str = Field(default="league_default")
    order_mode: str = Field(default="pick_slot")
    opponent_names: list[str] = Field(default_factory=list)
    team_names: dict[str, str] | None = None
    pick_mode: str = Field(default="user_only")


class PickBody(BaseModel):
    player_id: str | None = None
    query: str | None = None


class DisagreeBody(BaseModel):
    recommended_player_id: str | None = None
    recommended_query: str | None = None
    chosen_player_id: str | None = None
    chosen_query: str | None = None
    category: str = "other"
    reason: str = ""


class AnalyzeBody(BaseModel):
    players: list[str] = Field(default_factory=list)
    n: int = Field(default=5, ge=1, le=20)


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/status")
def status():
    conn = get_conn()
    try:
        n = conn.execute("SELECT COUNT(*) AS n FROM players").fetchone()["n"]
        last = conn.execute(
            "SELECT source, pulled_at, n_rows FROM ingest_runs ORDER BY id DESC LIMIT 4"
        ).fetchall()
        presets = [get_roster_preset(pid) for pid in ROSTER_PRESETS]
        return {
            "players": n,
            "ingest": [dict(r) for r in last],
            "roster_presets": presets,
            "n_teams": N_TEAMS,
            "pick_clock_seconds": PICK_CLOCK_SECONDS,
        }
    finally:
        conn.close()


@app.post("/api/drafts")
def api_create_draft(body: CreateDraftBody):
    conn = get_conn()
    try:
        n = conn.execute("SELECT COUNT(*) AS n FROM players").fetchone()["n"]
        if n == 0:
            raise HTTPException(400, "No players loaded. Run: python -m draftopt.ingest")
        if body.roster_preset not in ROSTER_PRESETS:
            raise HTTPException(400, f"unknown roster preset: {body.roster_preset}")
        draft_id = create_draft(
            conn,
            user_slot=body.user_slot,
            user_name=body.user_name,
            roster_preset=body.roster_preset,
            order_mode=body.order_mode,
            opponent_names=body.opponent_names,
            team_names=body.team_names,
            pick_mode=body.pick_mode,
        )
        return payload(conn, draft_id)
    except DraftError as e:
        raise HTTPException(400, str(e)) from e
    finally:
        conn.close()


@app.get("/api/drafts/{draft_id}")
def api_get_draft(draft_id: str, strategy: str = Query(default="marginal")):
    conn = get_conn()
    try:
        get_strategy(strategy)  # validate
        return payload(conn, draft_id, strategy=strategy)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except DraftError as e:
        raise HTTPException(404, str(e)) from e
    finally:
        conn.close()


@app.get("/api/drafts/{draft_id}/search")
def api_search(
    draft_id: str,
    q: str = Query(default=""),
    position: str = Query(default="ALL"),
    team: str = Query(default=""),
    sort: str = Query(default="adp"),
    limit: int = Query(default=50, ge=1, le=200),
):
    conn = get_conn()
    try:
        return {
            "results": search_remaining(
                conn,
                draft_id,
                query=q,
                position=position,
                team=team or None,
                sort=sort,
                limit=limit,
            )
        }
    except DraftError as e:
        raise HTTPException(404, str(e)) from e
    finally:
        conn.close()


@app.get("/api/drafts/{draft_id}/grade")
def api_grade(draft_id: str):
    conn = get_conn()
    try:
        return grade_draft(conn, draft_id)
    except DraftError as e:
        raise HTTPException(404, str(e)) from e
    finally:
        conn.close()


@app.post("/api/drafts/{draft_id}/picks")
def api_pick(draft_id: str, body: PickBody):
    conn = get_conn()
    try:
        player_id = body.player_id
        if not player_id:
            if not body.query:
                raise HTTPException(400, "player_id or query required")
            player_id = resolve_player(conn, draft_id, body.query)
        record_human_pick(conn, draft_id, player_id, made_by=None)
        return payload(conn, draft_id)
    except DraftError as e:
        raise HTTPException(400, str(e)) from e
    finally:
        conn.close()


@app.post("/api/drafts/{draft_id}/cpu")
def api_cpu(draft_id: str):
    conn = get_conn()
    try:
        cpu_pick(conn, draft_id)
        return payload(conn, draft_id)
    except DraftError as e:
        raise HTTPException(400, str(e)) from e
    finally:
        conn.close()


@app.post("/api/drafts/{draft_id}/autopick")
def api_autopick(draft_id: str, strategy: str = Query(default="marginal")):
    conn = get_conn()
    try:
        get_strategy(strategy)
        recs = recommend(conn, draft_id, n=1, strategy=strategy)
        if not recs:
            raise HTTPException(400, "no players remaining")
        record_human_pick(conn, draft_id, recs[0]["player_id"], made_by="timeout")
        return payload(conn, draft_id, strategy=strategy)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except DraftError as e:
        raise HTTPException(400, str(e)) from e
    finally:
        conn.close()


@app.post("/api/drafts/{draft_id}/undo")
def api_undo(draft_id: str):
    conn = get_conn()
    try:
        undo_pick(conn, draft_id)
        return payload(conn, draft_id)
    except DraftError as e:
        raise HTTPException(400, str(e)) from e
    finally:
        conn.close()


@app.post("/api/drafts/{draft_id}/autopsy/case")
def api_autopsy_case(draft_id: str, n: int = Query(default=10, ge=1, le=30)):
    """Dump board + top-N M recommendations (does not change TAKE)."""
    conn = get_conn()
    try:
        return dump_case(conn, draft_id, n_recs=n)
    except DraftError as e:
        raise HTTPException(404, str(e)) from e
    finally:
        conn.close()


@app.post("/api/drafts/{draft_id}/autopsy/analyze")
def api_autopsy_analyze(draft_id: str, body: AnalyzeBody):
    """Diagnostic M + survival + next-pick stub table (does not change TAKE)."""
    conn = get_conn()
    try:
        report = autopsy_analyze(
            conn,
            draft_id,
            queries=body.players or None,
            n_top=body.n,
        )
        report["markdown"] = format_analyze_markdown(report)
        return report
    except DraftError as e:
        raise HTTPException(400, str(e)) from e
    finally:
        conn.close()


@app.post("/api/drafts/{draft_id}/autopsy/disagree")
def api_autopsy_disagree(draft_id: str, body: DisagreeBody):
    """Append Gate-3 disagreement to results/autopsy_disagreements.jsonl."""
    conn = get_conn()
    try:
        rec = body.recommended_player_id
        ch = body.chosen_player_id
        if not rec:
            if not body.recommended_query:
                raise HTTPException(400, "recommended_player_id or recommended_query required")
            rec = resolve_player(conn, draft_id, body.recommended_query)
        if not ch:
            if not body.chosen_query:
                raise HTTPException(400, "chosen_player_id or chosen_query required")
            ch = resolve_player(conn, draft_id, body.chosen_query)
        if body.category not in DISAGREE_CATEGORIES:
            raise HTTPException(400, f"category must be one of {sorted(DISAGREE_CATEGORIES)}")
        return log_disagreement(
            conn,
            draft_id,
            recommended_player_id=rec,
            chosen_player_id=ch,
            reason=body.reason,
            category=body.category,
        )
    except DraftError as e:
        raise HTTPException(400, str(e)) from e
    finally:
        conn.close()


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
