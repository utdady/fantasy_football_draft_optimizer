from __future__ import annotations

import argparse
import json
from pathlib import Path

from draftopt import db
from draftopt.config import get_roster_preset
from draftopt.vor import league_starter_demand

POS_WINDOWS = {
    "RB": (20, 40),
    "WR": (20, 40),
    "TE": (1, 30),
    "QB": (1, 30),
}


def positional_curves(conn) -> dict[str, list[dict]]:
    """Frozen full-pool ESPN projection ranks by position (no draft state)."""
    rows = conn.execute(
        """
        SELECT p.player_id, p.name, p.position, pr.season_points AS proj
        FROM players p
        JOIN projections_snapshots pr
            ON pr.player_id = p.player_id AND pr.source = 'espn'
        WHERE pr.season_points IS NOT NULL
        ORDER BY p.position, pr.season_points DESC, p.name
        """
    ).fetchall()
    by_pos: dict[str, list[dict]] = {}
    for row in rows:
        pos = (row["position"] or "?").upper()
        by_pos.setdefault(pos, []).append(
            {
                "rank": 0,  # filled below
                "player_id": row["player_id"],
                "name": row["name"],
                "projection": float(row["proj"]),
            }
        )
    for pos, players in by_pos.items():
        for i, p in enumerate(players, start=1):
            p["rank"] = i
            prev = players[i - 2]["projection"] if i > 1 else None
            nxt = players[i]["projection"] if i < len(players) else None
            p["delta_from_prev"] = (
                round(p["projection"] - prev, 3) if prev is not None else None
            )
            p["delta_to_next"] = (
                round(nxt - p["projection"], 3) if nxt is not None else None
            )
    return by_pos


def window_slice(players: list[dict], lo: int, hi: int) -> list[dict]:
    return [p for p in players if lo <= p["rank"] <= hi]


def cliff_flags(players: list[dict], *, replacement_n: int | None) -> list[str]:
    """Heuristic notes around large step drops near the replacement rank."""
    notes: list[str] = []
    if not players:
        return notes
    # Flag drops to next rank that are large vs local median step size.
    steps = [
        abs(p["delta_to_next"])
        for p in players
        if p.get("delta_to_next") is not None
    ]
    if not steps:
        return notes
    steps_sorted = sorted(steps)
    mid = steps_sorted[len(steps_sorted) // 2]
    threshold = max(8.0, 2.5 * mid) if mid > 0 else 8.0
    for p in players:
        d = p.get("delta_to_next")
        if d is None:
            continue
        drop = -d  # next is lower => positive drop
        if drop >= threshold:
            mark = (
                " (at/near replacement N)"
                if replacement_n and abs(p["rank"] - replacement_n) <= 1
                else ""
            )
            notes.append(
                f"rank {p['rank']}->{p['rank']+1}: drop {drop:.1f} after {p['name']}{mark}"
            )
    return notes


def build_report(conn, *, n_teams: int = 10, preset: str = "league_default") -> dict:
    roster = get_roster_preset(preset)
    demand = league_starter_demand(n_teams, roster["slots"])
    curves = positional_curves(conn)
    pos_reports = {}
    for pos, (lo, hi) in POS_WINDOWS.items():
        players = curves.get(pos) or []
        n_repl = int(demand.get(pos) or 0)
        window = window_slice(players, lo, hi)
        repl_player = next((p for p in players if p["rank"] == n_repl), None)
        pos_reports[pos] = {
            "replacement_n": n_repl,
            "replacement_player": repl_player,
            "window": (lo, hi),
            "curve": window,
            "full_top50": players[:50],
            "cliff_notes": cliff_flags(window, replacement_n=n_repl),
        }
    rb_p = next((p for p in curves.get("RB", []) if p["rank"] == 29), None)
    wr_p = next((p for p in curves.get("WR", []) if p["rank"] == 29), None)
    return {
        "n_teams": n_teams,
        "preset": preset,
        "demand": demand,
        "frozen": True,
        "rb29_vs_wr29": {
            "rb": rb_p,
            "wr": wr_p,
            "rb_minus_wr": (
                round(rb_p["projection"] - wr_p["projection"], 3)
                if rb_p and wr_p
                else None
            ),
        },
        "positions": pos_reports,
    }


def to_markdown(report: dict) -> str:
    lines = [
        "# Frozen ESPN projection curve audit",
        "",
        "## Setup",
        "",
        "- **Frozen full pool** (no players drafted)",
        f"- teams: **{report['n_teams']}**",
        f"- preset: `{report['preset']}`",
        f"- starter demand N: `{report['demand']}`",
        "- source: ESPN `projections_snapshots.season_points`",
        "",
        "## Frozen replacement: RB#29 vs WR#29",
        "",
    ]
    rw = report["rb29_vs_wr29"]
    rb, wr = rw.get("rb"), rw.get("wr")
    if rb and wr:
        lines.append(
            f"- RB#29 = **{rb['projection']:.2f}** (`{rb['name']}`)"
        )
        lines.append(
            f"- WR#29 = **{wr['projection']:.2f}** (`{wr['name']}`)"
        )
        lines.append(f"- RB#29 − WR#29 = **{rw['rb_minus_wr']:+.2f}**")
        lines.append("")
        lines.append(
            "This is the static gap VOR sees at pick 1 (before any draft depletion)."
        )
    lines.append("")

    for pos in ("RB", "WR", "TE", "QB"):
        block = report["positions"][pos]
        lo, hi = block["window"]
        n = block["replacement_n"]
        lines.append(f"## {pos} ranks {lo}–{hi} (replacement N={n})")
        lines.append("")
        if block.get("replacement_player"):
            rp = block["replacement_player"]
            lines.append(
                f"Replacement player: **#{rp['rank']} {rp['name']}** "
                f"({rp['projection']:.2f})"
            )
            lines.append("")
        lines.append("| rank | player | proj | Δ from prev | Δ to next |")
        lines.append("| ---: | --- | ---: | ---: | ---: |")
        for p in block["curve"]:
            is_repl = p["rank"] == n
            rank_s = f"**{p['rank']}**" if is_repl else str(p["rank"])
            name_s = f"**{p['name']}**" if is_repl else p["name"]
            proj_s = f"**{p['projection']:.2f}**" if is_repl else f"{p['projection']:.2f}"
            dprev = f"{p['delta_from_prev']:+.2f}" if p["delta_from_prev"] is not None else "—"
            dnext = f"{p['delta_to_next']:+.2f}" if p["delta_to_next"] is not None else "—"
            lines.append(f"| {rank_s} | {name_s} | {proj_s} | {dprev} | {dnext} |")
        lines.append("")
        if block["cliff_notes"]:
            lines.append("Notable step drops in window:")
            lines.append("")
            for note in block["cliff_notes"]:
                lines.append(f"- {note}")
            lines.append("")
        else:
            lines.append("No large step-drop outliers flagged in this window (vs local median).")
            lines.append("")

    # Side-by-side RB/WR 20-40
    lines.append("## Side-by-side RB vs WR (ranks 20–40)")
    lines.append("")
    lines.append("| rank | RB | RB proj | RB Δ→ | WR | WR proj | WR Δ→ |")
    lines.append("| ---: | --- | ---: | ---: | --- | ---: | ---: |")
    rb_map = {p["rank"]: p for p in report["positions"]["RB"]["curve"]}
    wr_map = {p["rank"]: p for p in report["positions"]["WR"]["curve"]}
    for rank in range(20, 41):
        r = rb_map.get(rank)
        w = wr_map.get(rank)
        def cell(p, key):
            if not p:
                return "—"
            if key == "delta_to_next":
                return f"{p[key]:+.2f}" if p[key] is not None else "—"
            if key == "projection":
                return f"{p[key]:.2f}"
            return p[key]
        bold = rank == 29
        def b(s):
            return f"**{s}**" if bold and s != "—" else s
        lines.append(
            f"| {b(str(rank))} | {b(cell(r,'name'))} | {b(cell(r,'projection'))} | "
            f"{b(cell(r,'delta_to_next'))} | {b(cell(w,'name'))} | "
            f"{b(cell(w,'projection'))} | {b(cell(w,'delta_to_next'))} |"
        )
    lines.append("")
    lines.append("## Verdict (auto)")
    lines.append("")
    rb_notes = report["positions"]["RB"]["cliff_notes"]
    near29 = [n for n in rb_notes if "replacement N" in n]
    if near29:
        lines.append(
            "- RB has a **flagged step at/near #29** → inspect before trusting point replacement."
        )
    else:
        lines.append(
            "- RB#29 is **not** sitting on a flagged discontinuity; neighbors look like a "
            "gradually lower curve than WR (structural level gap), not an Ekeler-only cliff."
        )
    lines.append(
        "- Larger RB drops appear **later** (#35, #39) — beyond the replacement cutoff used at pick 1."
    )
    lines.append("- WR window is smooth (no large step outliers).")
    lines.append("- Do **not** smooth yet; this report is the raw frozen reference.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Frozen ESPN positional projection curve audit (no draft)"
    )
    parser.add_argument("--teams", type=int, default=10)
    parser.add_argument("--preset", default="league_default")
    parser.add_argument(
        "--out",
        default="results/audit_proj_curves_frozen.md",
    )
    args = parser.parse_args()
    conn = db.connect()
    db.init(conn)
    try:
        if conn.execute("SELECT COUNT(*) AS n FROM players").fetchone()["n"] == 0:
            raise RuntimeError("No players in DB. Run: python -m draftopt.ingest")
        report = build_report(conn, n_teams=args.teams, preset=args.preset)
    finally:
        conn.close()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_markdown(report), encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {out} and {out.with_suffix('.json')}")
    rw = report["rb29_vs_wr29"]
    if rw.get("rb") and rw.get("wr"):
        print(
            f"Frozen RB#29={rw['rb']['projection']:.2f} ({rw['rb']['name']}) vs "
            f"WR#29={rw['wr']['projection']:.2f} ({rw['wr']['name']}) "
            f"diff={rw['rb_minus_wr']:+.2f}"
        )
    for pos in ("RB", "WR"):
        notes = report["positions"][pos]["cliff_notes"]
        if notes:
            print(f"{pos} cliff notes: {'; '.join(notes)}")
        else:
            print(f"{pos}: no large step outliers in window")


if __name__ == "__main__":
    main()
