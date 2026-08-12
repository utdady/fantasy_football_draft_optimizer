from __future__ import annotations

from typing import Protocol


class DraftStrategy(Protocol):
    name: str

    def recommend(self, conn, draft_id: str, n: int = 3) -> list[dict]:
        """Return up to n ranked candidate dicts with at least player_id and why."""
