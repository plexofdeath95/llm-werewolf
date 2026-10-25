"""Shared helpers for Neutral roles: win thresholds, who blocked whom, last-standing wins."""
from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from aiplays.core.state import GameState, Player
from aiplays.modes.werewolf.roles.base import NEUTRAL
from aiplays.modes.werewolf.status import Status, status

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Night

GOAL_TEXT = "3 (2 at tables of 8 or fewer players)"


def goal(state: GameState) -> int:
    """Kill / drain / ignite target for neutral killers (WikiWolf's 3, scaled for small games)."""
    return 2 if len(state.players) <= 8 else 3


def was_blocked(n: Night, p: Player) -> bool:
    return any(a.blocked for a in n.acts_by(p))


def blockers(n: Night, p: Player) -> list[Player]:
    """Players whose role-block (Escort, Consort, Jailor...) landed on p tonight."""
    return [a.actor for a in n.acts if a.action.cls == "role_block" and not a.blocked
            and any(t is p for t in a.targets)]


def last_standing(state: GameState, p: Player, result: str) -> bool:
    """Hostile neutrals also win when the game ends with them alive as the last threat."""
    return result == NEUTRAL and p.alive


def goal_win(score: Callable[[Status], int]) -> staticmethod:
    """A win hook: reach the neutral goal (see goal()), or be the last threat standing."""
    def win(state: GameState, p: Player, result: str) -> bool:
        return score(status(state, p)) >= goal(state) or last_standing(state, p, result)
    return staticmethod(win)


def count(state: GameState, p: Player, key: str, by: int = 1) -> int:
    marks = status(state, p).marks
    marks[key] = marks.get(key, 0) + by
    return marks[key]


def add_chat(state: GameState, p: Player, channel: str) -> None:
    chats = status(state, p).marks.setdefault("chats", [])
    if channel not in chats:
        chats.append(channel)
