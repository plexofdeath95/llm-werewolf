"""Shared trap mechanics (village Mechanist, wolf Trapper): build, set/move, spring."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.modes.werewolf.roles.base import act
from aiplays.modes.werewolf.status import status

if TYPE_CHECKING:
    from aiplays.core.state import GameState, Player
    from aiplays.modes.werewolf.night.context import Act, Night


def _build(n: Night, a: Act) -> None:
    s = n.st(a.actor)
    s.marks["traps"] = s.marks.get("traps", 0) + 1
    n.note(a.actor, f"You built a trap. Traps in hand: {s.marks['traps']}.")


def _place(n: Night, a: Act) -> None:
    s, home = n.st(a.actor), a.targets[0]
    if "trap_at" not in s.marks:  # setting a new trap uses one from hand; moving doesn't
        s.marks["traps"] = s.marks.get("traps", 0) - 1
    s.marks["trap_at"] = home.id
    n.note(a.actor, f"Your trap is set at {home.name}'s home.")


def _has_trap(state: GameState, p: Player) -> bool:
    s = status(state, p)
    return s.marks.get("traps", 0) > 0 or "trap_at" in s.marks


build_trap = act("build", "support", "Build a trap and keep it in hand (no limit).",
                 _build, movement="none", targets=0)
place_trap = act("place", "support",
                 "Set a trap from your hand at a home, or move your laid trap there.",
                 _place, movement="travel", pool="anyone", ready=_has_trap)


def TRAP_PASSIVE(n: Night, owner: Player) -> None:
    """The first other player (by seat) to visit the trapped home springs it and dies."""
    s = n.st(owner)
    home_id = s.marks.get("trap_at")
    if not home_id:
        return
    home = n.state.by_id(home_id)
    comers = sorted((v for v in n.visitors(home) if v.actor is not owner
                     and v.actor is not home and v.action.movement == "visit"),
                    key=lambda v: v.actor.seat)
    if comers:
        n.attack(comers[0].actor, owner, "caught in a trap")
        del s.marks["trap_at"]
        n.note(owner, f"Your trap at {home.name}'s home was sprung.")


class TrapHooks:
    passive = staticmethod(TRAP_PASSIVE)


BUILD_TRAP, PLACE_TRAP = build_trap, place_trap  # names used by the village Mechanist
