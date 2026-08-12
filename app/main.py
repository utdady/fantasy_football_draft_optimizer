from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from draftopt import db
from draftopt.config import ROSTER_PRESETS, get_roster_preset
from draftopt.draft.cpu import cpu_pick
from draftopt.draft.grade import grade_draft
from draftopt.draft.state import (
    DraftError,
    create_draft,
    record_user_pick,
    resolve_player,
    search_remaining,
    snapshot,
    undo_pick,
)
from draftopt.recommend import recommend

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Draft Optimizer V0")


def get_conn():
    conn = db.connect()
    db.init(conn)
    return conn


def payload(conn, draft_id: str) -> dict:
    state = snapshot(conn, draft_id)
    out = {"state": state, "recommend": recommend(conn, draft_id)}
    if state.get("complete"):
        out["grade"] = grade_draft(conn, draft_id)
    return out


class CreateDraftBody(BaseModel):
    user_slot: int = Field(default=1, ge=1, le=10)
    user_name: str = Field(default="You", min_length=1, max_length=40)
    roster_preset: str = Field(default="league_default")


class PickBody(BaseModel):
    player_id: str | None = None
    query: str | None = None


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
        return {"players": n, "ingest": [dict(r) for r in last], "roster_presets": presets}
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
        )
        return payload(conn, draft_id)
    except DraftError as e:
        raise HTTPException(400, str(e)) from e
    finally:
        conn.close()


@app.get("/api/drafts/{draft_id}")
def api_get_draft(draft_id: str):
    conn = get_conn()
    try:
        return payload(conn, draft_id)
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
        record_user_pick(conn, draft_id, player_id, made_by="user")
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
def api_autopick(draft_id: str):
    conn = get_conn()
    try:
        recs = recommend(conn, draft_id, n=1)
        if not recs:
            raise HTTPException(400, "no players remaining")
        record_user_pick(conn, draft_id, recs[0]["player_id"], made_by="timeout")
        return payload(conn, draft_id)
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


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
