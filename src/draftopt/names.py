from __future__ import annotations

import re
import unicodedata

_PUNCT = re.compile(r"[^a-z0-9]+")

DST_NICKNAMES = {
    "ARI": ["cardinals", "arizona"],
    "ATL": ["falcons", "atlanta"],
    "BAL": ["ravens", "baltimore"],
    "BUF": ["bills", "buffalo"],
    "CAR": ["panthers", "carolina"],
    "CHI": ["bears", "chicago"],
    "CIN": ["bengals", "cincinnati"],
    "CLE": ["browns", "cleveland"],
    "DAL": ["cowboys", "dallas"],
    "DEN": ["broncos", "denver"],
    "DET": ["lions", "detroit"],
    "GB": ["packers", "green bay"],
    "HOU": ["texans", "houston"],
    "IND": ["colts", "indianapolis"],
    "JAX": ["jaguars", "jacksonville"],
    "KC": ["chiefs", "kansas city"],
    "LAC": ["chargers", "los angeles chargers"],
    "LAR": ["rams", "los angeles rams"],
    "LV": ["raiders", "las vegas"],
    "MIA": ["dolphins", "miami"],
    "MIN": ["vikings", "minnesota"],
    "NE": ["patriots", "new england"],
    "NO": ["saints", "new orleans"],
    "NYG": ["giants", "new york giants"],
    "NYJ": ["jets", "new york jets"],
    "PHI": ["eagles", "philadelphia"],
    "PIT": ["steelers", "pittsburgh"],
    "SEA": ["seahawks", "seattle"],
    "SF": ["49ers", "niners", "san francisco"],
    "TB": ["buccaneers", "bucs", "tampa bay"],
    "TEN": ["titans", "tennessee"],
    "WAS": ["commanders", "washington"],
}


def fold(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text or "")
    ascii_only = nfkd.encode("ascii", "ignore").decode("ascii")
    return _PUNCT.sub("", ascii_only.lower())


def display_name(first: str | None, last: str | None, fallback: str = "") -> str:
    parts = [p for p in (first or "", last or "") if p]
    return " ".join(parts) or fallback


def aliases_for(name: str, position: str | None, team: str | None) -> list[str]:
    aliases: set[str] = set()
    if name:
        aliases.add(fold(name))
        aliases.add(fold(name.replace("'", "").replace(".", "")))
        bits = name.replace(",", " ").split()
        if bits:
            aliases.add(fold(bits[-1]))
            if len(bits) >= 2:
                aliases.add(fold(f"{bits[-1]} {bits[0]}"))
    pos = (position or "").upper()
    team_code = (team or "").upper()
    if pos in {"DST", "DEF"} and team_code:
        aliases.add(fold(team_code))
        aliases.add(fold(f"{team_code} dst"))
        aliases.add(fold(f"{team_code} def"))
        for nick in DST_NICKNAMES.get(team_code, []):
            aliases.add(fold(nick))
            aliases.add(fold(f"{nick} dst"))
    return [a for a in aliases if a]
