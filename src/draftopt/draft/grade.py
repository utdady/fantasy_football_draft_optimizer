from __future__ import annotations

from draftopt.draft.state import _draft_row, draft_roster


def grade_draft(conn, draft_id: str) -> dict:
    """Simple scorecard: projected points + ADP value vs pick number."""
    draft = _draft_row(conn, draft_id)
    roster = draft_roster(draft)
    n_teams = draft["n_teams"]
    user_slot = draft["user_slot"]
    user_name = draft["user_name"] or "You"

    rows = conn.execute(
        """
        SELECT pk.overall, pk.team_slot, pk.round, p.player_id, p.name, p.position, p.team,
               a.adp, pr.season_points, r.ecr
        FROM picks pk
        JOIN players p ON p.player_id = pk.player_id
        LEFT JOIN adp_snapshots a ON a.player_id = p.player_id AND a.source = 'espn'
        LEFT JOIN projections_snapshots pr ON pr.player_id = p.player_id AND pr.source = 'espn'
        LEFT JOIN rankings_snapshots r ON r.player_id = p.player_id AND r.source = 'fantasypros'
        WHERE pk.draft_id = ?
        ORDER BY pk.overall
        """,
        (draft_id,),
    ).fetchall()

    teams = {
        slot: {
            "team_slot": slot,
            "label": user_name if slot == user_slot else f"CPU {slot}",
            "is_user": slot == user_slot,
            "projected_points": 0.0,
            "adp_value": 0.0,
            "picks": 0,
            "players": [],
        }
        for slot in range(1, n_teams + 1)
    }

    for row in rows:
        slot = row["team_slot"]
        proj = float(row["season_points"] or 0.0)
        adp = row["adp"]
        overall = row["overall"]
        value = (float(adp) - float(overall)) if adp is not None else 0.0
        teams[slot]["projected_points"] += proj
        teams[slot]["adp_value"] += value
        teams[slot]["picks"] += 1
        teams[slot]["players"].append(
            {
                "overall": overall,
                "name": row["name"],
                "position": row["position"],
                "team": row["team"],
                "adp": adp,
                "season_points": row["season_points"],
                "ecr": row["ecr"],
                "adp_value": value if adp is not None else None,
            }
        )

    ranked = sorted(
        teams.values(),
        key=lambda t: (t["projected_points"], t["adp_value"]),
        reverse=True,
    )
    for i, team in enumerate(ranked, start=1):
        team["rank"] = i
        team["projected_points"] = round(team["projected_points"], 1)
        team["adp_value"] = round(team["adp_value"], 1)

    user = next(t for t in ranked if t["is_user"])
    return {
        "draft_id": draft_id,
        "roster": roster,
        "user": user,
        "teams": ranked,
        "method": "ESPN season projection sum + (ADP − pick#) value",
    }
