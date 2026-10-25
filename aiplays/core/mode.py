"""GameMode base class and registry. Each game lives in aiplays/modes/<id>/."""
from __future__ import annotations

import random
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from aiplays.core.role import Role
from aiplays.core.state import GameState, Player

if TYPE_CHECKING:
    from aiplays.core.moderator import Moderator


class GameMode(ABC):
    id: ClassVar[str]
    name: ClassVar[str]
    min_players: ClassVar[int]
    max_players: ClassVar[int]
    prompts_dir: ClassVar[Path]
    roles: ClassVar[dict[str, Role]]

    def role_label(self, role_id: str) -> str:
        label = self.roles[role_id].label
        return f"an {label}" if label[0].lower() in "aeiou" else f"a {label}"

    @abstractmethod
    def assign_roles(self, state: GameState, rng: random.Random) -> None:
        """Set role/team on every player."""

    @abstractmethod
    def briefing(self, state: GameState, player: Player, reveal_models: bool) -> str:
        """System instruction for one player (rules, role card, private knowledge)."""

    @abstractmethod
    async def play(self, mod: Moderator) -> str:
        """Run the game to completion and return the winning team."""

    def describe(self) -> dict:
        return {"id": self.id, "name": self.name,
                "min_players": self.min_players, "max_players": self.max_players,
                "roles": {k: {"label": r.label, "team": r.team, "emoji": r.emoji}
                          for k, r in self.roles.items()}}


_REGISTRY: dict[str, type[GameMode]] = {}


def register(cls: type[GameMode]) -> type[GameMode]:
    _REGISTRY[cls.id] = cls
    return cls


def get_mode(mode_id: str) -> GameMode:
    import aiplays.modes  # noqa: F401  (registers built-in modes)
    return _REGISTRY[mode_id]()


def list_modes() -> list[dict]:
    import aiplays.modes  # noqa: F401
    return [cls().describe() for cls in _REGISTRY.values()]
