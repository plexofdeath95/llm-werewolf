"""Assassin: a secret hit list, three bullets, and a vote that counts."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.modes.werewolf.roles import effects
from aiplays.modes.werewolf.roles.base import NEUTRAL, act, role
from aiplays.modes.werewolf.status import status

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Night

HIT = "assassinated"


def _listed(state, p) -> list:
    ids = status(state, p).marks.get("targets", [])
    return [q for q in state.alive() if q.id in ids]


def _confirm(n: Night, a: Act) -> None:  # after: a night kill on the list counts
    t = a.targets[0]
    if n.deaths.get(t.id) == HIT:
        status(n.state, a.actor).marks.setdefault("done", []).append(t.id)


class Assassin:
    @staticmethod
    def on_start(state, p, rng) -> None:
        others = [q for q in state.players if q is not p]
        k = min(len(others), 2 if len(state.players) <= 8 else 3)
        status(state, p).marks["targets"] = [q.id for q in rng.sample(others, k)]

    @staticmethod
    def knowledge(state, p) -> str:
        names = [state.by_id(i).name for i in status(state, p).marks.get("targets", [])]
        return f"Your targets: {', '.join(names)}."

    @staticmethod
    async def after_lynch(mod, q, lynched, voters) -> None:
        if lynched.id in status(mod.state, q).marks.get("targets", []) and \
                any(v is q for v in voters):
            status(mod.state, q).marks.setdefault("done", []).append(lynched.id)

    @staticmethod
    def win(state, p, result) -> bool:
        m = status(state, p).marks
        return bool(m.get("targets")) and set(m["targets"]) <= set(m.get("done", []))


role(id="assassin", label="Assassin", team=NEUTRAL, emoji="🗡️", classes=("killing",), weight=-2,
     hooks=Assassin, summary="Has a secret hit list; wins once everyone on it is dead by their hand.",
     card="At the start you are secretly given a list of targets (2, or 3 at tables of 9+). You "
          "have 3 night kills, usable only on players on your list. You win once every target "
          "has died by your hand: killed by you at night, or voted out on a day when you voted "
          "for them. Other sides can win alongside you.",
     actions=(act("assassinate", "killing", "Visit a player on your list and kill them.",
                  effects.kill(HIT), pool=_listed, uses=3, after=_confirm),))
