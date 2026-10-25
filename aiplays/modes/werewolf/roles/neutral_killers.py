"""Neutral killers: Arsonist, Murderer, Crone, Vampire."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.modes.werewolf.roles import effects
from aiplays.modes.werewolf.roles import neutral_kit as kit
from aiplays.modes.werewolf.roles.base import PRIORITY, ROLES, TEAM_ORDER
from aiplays.modes.werewolf.status import role_of, status

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Attack, Night

IGNITED, MURDERED, DRAINED = "burned alive by the Arsonist", "murdered", "drained by a Vampire"
KILLER = ("killing",)
drain = effects.kill(DRAINED)


def douse(n: Night, a: Act) -> None:
    for t in a.targets:
        n.st(t).flags.add("doused")
        n.note(t, "You smell petrol: someone doused your home tonight.")


def ignite(n: Night, a: Act) -> None:
    for p in n.state.alive():
        if p is not a.actor and "doused" in n.st(p).flags:
            n.attack(p, a.actor, IGNITED, unstoppable=True)


def has_doused(state, p) -> bool:
    return any("doused" in status(state, q).flags for q in state.alive() if q is not p)


def murder(n: Night, a: Act) -> None:
    """A visitor to the Murderer's home dies instead of the intended target."""
    came = [v for v in n.visitors(a.actor) if v.actor is not a.actor
            and v.action.movement == "visit"]
    if not came:
        n.attack(a.targets[0], a.actor, MURDERED)
        return
    first = min(came, key=lambda v: (PRIORITY.index(v.action.cls) if v.action.cls in PRIORITY
                                     else -1, TEAM_ORDER.get(n.role(v.actor).team, 1), v.actor.seat))
    n.attack(first.actor, a.actor, MURDERED)
    n.note(a.actor, f"{first.actor.name} came to your home, so you killed them instead.")


def feed(n: Night, a: Act) -> None:  # after: a fresh victim lends the Vampire their powers
    t = a.targets[0]
    if n.deaths.get(t.id) == DRAINED:
        rid = role_of(n.state, t)
        effects.borrow(n, a.actor, rid)
        n.appear(a.actor, rid, until=n.n + 1)
        n.note(a.actor, f"You drained {t.name}, the {ROLES[rid].label}. Tomorrow night you can "
                        "use their powers, and investigators will see you as one.")


class Arsonist:
    @staticmethod
    def passive(n: Night, p) -> None:
        if kit.was_blocked(n, p):  # whoever blocks the Arsonist gets doused instead
            for b in kit.blockers(n, p):
                n.st(b).flags.add("doused")
                n.note(b, "You smell petrol: someone doused your home tonight.")

    @staticmethod
    def after_night(n: Night, p) -> None:
        kit.count(n.state, p, "ignited", sum(c == IGNITED for c in n.deaths.values()))

    win = kit.goal_win(lambda s: s.marks.get("ignited", 0))


class Murderer:
    win = kit.goal_win(lambda s: s.kills_by_team.get("village", 0))


class Crone:
    win = kit.goal_win(lambda s: s.kills)


class Vampire:
    @staticmethod
    def passive(n: Night, p) -> None:
        if kit.was_blocked(n, p):  # a blocker dies in place of the intended victim
            for b in kit.blockers(n, p):
                n.attack(b, p, DRAINED)

    @staticmethod
    def on_attacked(n: Night, atk: Attack) -> bool:
        draining = any(a.action.name == "drain" and not a.blocked for a in n.acts_by(atk.target))
        if draining:
            n.note(atk.target, "Someone attacked you while you hunted, but you shrugged it off.")
        return draining

    @staticmethod
    def after_night(n: Night, p) -> None:
        kit.count(n.state, p, "drained", sum(c == DRAINED for c in n.deaths.values()))

    win = kit.goal_win(lambda s: s.marks.get("drained", 0))
