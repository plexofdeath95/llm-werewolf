"""Reusable night-effect handlers: most roles are one of these with different numbers."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.modes.werewolf.roles.base import Handler

from aiplays.modes.werewolf.roles.effects_info import (  # noqa: F401  (re-exported)
    follow, inspect_role, inspect_team, lineup, watch_home)

if TYPE_CHECKING:  # runtime import would be circular (context -> roles -> effects)
    from aiplays.modes.werewolf.night.context import Act, Night

def kill(cause: str, unstoppable: bool = False) -> Handler:
    def handler(n: Night, a: Act) -> None:
        for t in a.targets:
            n.attack(t, a.actor, cause, unstoppable)
    return handler


def heal(n: Night, a: Act) -> None:
    for t in a.targets:
        n.heals[t.id].append(a.actor)


def guard(n: Night, a: Act) -> None:
    n.guards[a.targets[0].id].append(a.actor)


def block(n: Night, a: Act) -> None:
    n.block(a.targets[0])


def jail(n: Night, a: Act) -> None:
    n.block(a.targets[0])
    n.jailed.add(a.targets[0].id)


def kill_if_leaves(cause: str) -> Handler:
    """Crusader / Stalker / Crone: kill the target if they step out of their home."""
    def handler(n: Night, a: Act) -> None:
        t = a.targets[0]
        if t.id in n.left_home:
            n.attack(t, a.actor, cause)
    return handler


def kill_visitors(of_actor: bool, cause: str, travellers: bool = False) -> Handler:
    """Veteran (own home) / Sentry (target's home): kill everyone who comes there."""
    def handler(n: Night, a: Act) -> None:
        home = a.actor if of_actor else a.targets[0]
        for v in n.visitors(home):
            if v.actor is not a.actor and v.actor is not home and (
                    travellers or v.action.movement == "visit"):
                n.attack(v.actor, a.actor, cause)
    return handler


def flag(name: str, note: str = "") -> Handler:
    """Put a status flag on the target (doused, infected, framed...)."""
    def handler(n: Night, a: Act) -> None:
        for t in a.targets:
            n.st(t).flags.add(name)
            if note:
                n.note(t, note)
    return handler


def borrow(n: Night, actor, role_id: str) -> None:
    """Grant role_id's night abilities to actor for the next night only."""
    n.st(actor).marks["borrow"] = (n.n + 1, role_id)
