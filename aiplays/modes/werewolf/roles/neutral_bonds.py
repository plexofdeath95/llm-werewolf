"""Neutrals that bind others: Cult Leader (converts) and Cupid (makes lovers)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.modes.werewolf.roles import neutral_kit as kit
from aiplays.modes.werewolf.roles.base import NEUTRAL
from aiplays.modes.werewolf.status import status

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Night

CULT, LOVERS = "cult", "cupid's lovers"


def convert(n: Night, p, leader) -> bool:
    if "cult" in n.st(p).flags:
        return False
    n.st(p).flags.add("cult")
    kit.add_chat(n.state, p, CULT)
    n.note(p, f"You have been converted! You now serve {leader.name}'s cult: you keep your "
              "abilities, but you win only if the cult converts every living player.")
    return True


def _convert(n: Night, a: Act) -> None:
    t = a.targets[0]
    ok = convert(n, t, a.actor)
    n.note(a.actor, f"{t.name} {'has joined' if ok else 'already belongs to'} your cult.")


class CultLeader:
    on_start = staticmethod(lambda state, p, rng: status(state, p).flags.add("cult"))

    @staticmethod
    def passive(n: Night, p) -> None:
        if kit.was_blocked(n, p):  # whoever blocks the Cult Leader joins the cult
            for b in kit.blockers(n, p):
                convert(n, b, p)

    @staticmethod
    def decides(state, p) -> str | None:
        if all("cult" in status(state, q).flags for q in state.alive()):
            state.memory["cult_won"] = True
            return NEUTRAL
        return None

    @staticmethod
    async def on_death(mod, p) -> None:
        for q in mod.state.alive():
            if "cult" in status(mod.state, q).flags:
                await mod.kill(q, "died with their Cult Leader",
                               f"{q.name} collapses as the cult's power dies with its leader.")

    win = staticmethod(lambda state, p, result: bool(state.memory.get("cult_won")))


def _lovers_stay():
    try:  # reuse the village Lovers' "stay" ability when that module provides it
        from aiplays.modes.werewolf.roles.village_support import LOVERS_STAY
        return LOVERS_STAY
    except ImportError:
        return None


def _shoot(n: Night, a: Act) -> None:
    x, y = a.targets
    stay = _lovers_stay()
    for me, other in ((x, y), (y, x)):
        s = n.st(me)
        s.flags.add("lover")
        s.marks["beloved"] = other.id
        kit.add_chat(n.state, me, LOVERS)
        if stay and stay not in s.marks.setdefault("borrowed", []):
            s.marks["borrowed"].append(stay)
        n.note(me, f"Cupid's arrow strikes: you are in love with {other.name}! You keep your "
                   "role, but you two can now talk privately at night.")
    n.st(a.actor).marks["lovers"] = [x.id, y.id]
    n.note(a.actor, f"Your arrows struck true: {x.name} and {y.name} are in love.")


class Cupid:
    @staticmethod
    def win(state, p, result) -> bool:
        ids = status(state, p).marks.get("lovers", [])
        return bool(ids) and all(state.by_id(i).alive for i in ids)
