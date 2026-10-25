"""Players and the game-agnostic game state."""
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Player:
    id: str
    name: str
    seat: int
    model_id: str
    persona: str | None = None
    role: str = ""
    team: str = ""
    alive: bool = True
    died_round: int | None = None
    death_cause: str | None = None
    won: bool | None = None


@dataclass
class GameState:
    game_id: str
    mode: str
    seed: int
    players: list[Player]
    round: int = 0
    phase: str = "setup"
    winner: str | None = None
    memory: dict[str, Any] = field(default_factory=dict)  # mode-specific scratch

    def alive(self, exclude: Player | None = None) -> list[Player]:
        return [p for p in self.players if p.alive and p is not exclude]

    def by_id(self, pid: str) -> Player:
        return next(p for p in self.players if p.id == pid)

    def by_name(self, name: str | None, among: list[Player] | None = None) -> Player | None:
        if not name:
            return None
        key = name.strip().strip(".!\"'").lower()
        pool = among if among is not None else self.players
        return next((p for p in pool if p.name.lower() == key), None)

    def with_role(self, role: str, alive: bool = True) -> list[Player]:
        return [p for p in self.players if p.role == role and (p.alive or not alive)]

    def on_team(self, team: str, alive: bool = True) -> list[Player]:
        return [p for p in self.players if p.team == team and (p.alive or not alive)]

    def names(self, players: list[Player]) -> str:
        return ", ".join(p.name for p in players)

    def mentioned(self, text: str) -> set[str]:
        """Ids of players whose name appears in text as a whole word."""
        return {p.id for p in self.players
                if re.search(rf"\b{re.escape(p.name)}\b", text, re.IGNORECASE)}
