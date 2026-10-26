"""Stored games, loaded once for analysis: every seat plus the full event log."""
from dataclasses import dataclass

from aiplays.core.events import GameEvent
from aiplays.db.repo import Repo


@dataclass
class Seat:
    name: str
    model: str
    role: str
    team: str  # village | wolves | neutral
    won: bool | None


@dataclass
class Game:
    id: str
    status: str
    winner: str | None
    config: dict
    seats: dict[str, Seat]  # player_id -> seat
    events: list[GameEvent]

    @property
    def by_name(self) -> dict[str, str]:
        return {s.name: pid for pid, s in self.seats.items()}

    @property
    def wolves(self) -> set[str]:
        return {s.name for s in self.seats.values() if s.team == "wolves"}


async def load_games(repo: Repo, *, mode: str = "werewolf", finished_only: bool = False,
                     include_fake: bool = False, min_speeches: int = 8) -> list[Game]:
    """Games oldest first. Real games only unless include_fake; very short (aborted) games
    with fewer than min_speeches spoken lines are skipped."""
    games = []
    for g in reversed(await repo.list_games(limit=100_000)):
        if g["mode"] != mode or (g["config"].get("fake") and not include_fake):
            continue
        if finished_only and g["status"] != "finished":
            continue
        events = await repo.load_events(g["id"])
        if sum(e.kind == "speech" for e in events) < min_speeches:
            continue
        players = (await repo.get_game(g["id"]))["players"]
        seats = {p["player_id"]: Seat(p["name"], p["model_id"], p["role"], p["team"], p["won"])
                 for p in players}
        games.append(Game(g["id"], g["status"], g["winner"], g["config"], seats, events))
    return games
