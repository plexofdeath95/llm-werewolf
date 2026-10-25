"""Per-player persistent status across nights: uses, cooldowns, flags, lives, kills."""
from dataclasses import dataclass, field
from typing import Any

from aiplays.core.state import GameState, Player


@dataclass
class Status:
    uses: dict[str, int] = field(default_factory=dict)        # action -> uses left (absent = unlimited)
    ready_on: dict[str, int] = field(default_factory=dict)    # action -> first night usable again
    last: dict[str, tuple[int, list[str]]] = field(default_factory=dict)  # action -> (night, target ids)
    flags: set[str] = field(default_factory=set)              # doused, infected, armor, hypnotized...
    marks: dict[str, Any] = field(default_factory=dict)       # role-specific memory
    lives: int = 1
    kills: int = 0
    kills_by_team: dict[str, int] = field(default_factory=dict)
    acting_as: str | None = None                              # copied role (amnesiac, orphan...)


def status(state: GameState, p: Player) -> Status:
    return state.memory.setdefault("status", {}).setdefault(p.id, Status())


def role_of(state: GameState, p: Player) -> str:
    """The role whose abilities the player currently has (copies override the dealt role)."""
    return status(state, p).acting_as or p.role
