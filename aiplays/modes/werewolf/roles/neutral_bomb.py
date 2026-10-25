"""Munitions Expert: bombs that kill visitors, and a grand finale at home."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.modes.werewolf.roles.base import NEUTRAL, act, role
from aiplays.modes.werewolf.status import status

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Night

BOOM = "blown up by a bomb"


def detonate(n: Night, expert, house) -> None:
    """Everyone who visits the bombed home dies; a bomb on your own home takes you too."""
    hit = [v.actor for v in n.visitors(house) if v.action.movement == "visit"
           and v.actor is not expert and v.actor is not house]
    for v in hit:
        n.attack(v, expert, BOOM)
    if hit:
        n.st(expert).marks.pop("bomb", None)
        if house is expert:
            n.attack(expert, None, "went out with a bang", unstoppable=True)
            n.st(expert).flags.add("finale")


def _plant(n: Night, a: Act) -> None:
    n.st(a.actor).marks["bomb"] = a.targets[0].id
    detonate(n, a.actor, a.targets[0])


def _bomb_sites(state, p) -> list:
    """Other players; your own home too once your bombs have killed 2."""
    return [q for q in state.alive() if q is not p or status(state, p).kills >= 2]


class Munitions:
    @staticmethod
    def passive(n: Night, p) -> None:  # a bomb from an earlier night is still primed
        bomb = n.st(p).marks.get("bomb")
        planting = any(b.action.name == "plant" and not b.blocked for b in n.acts_by(p))
        if bomb and not planting and n.state.by_id(bomb).alive:
            detonate(n, p, n.state.by_id(bomb))

    win = staticmethod(lambda state, p, result: "finale" in status(state, p).flags)


role(id="munitions_expert", label="Munitions Expert", team=NEUTRAL, emoji="💣",
     classes=("killing",), weight=-4, hostile=True, hooks=Munitions,
     summary="Bombs homes so visitors die; then must blow up their own home with a visitor.",
     card="Each night you may travel to a home and plant your bomb there (you only have one "
          "planted bomb; planting moves it). It stays primed until it goes off: everyone who "
          "VISITS that home dies (the owner and travellers are spared). Once your bombs have "
          "killed 2 players, you may plant on your own home: if anyone then visits you, you "
          "both die and you WIN. The Village cannot win while you live.",
     actions=(act("plant", "killing", "Travel to a home and plant your bomb there.", _plant,
                  movement="travel", pool=_bomb_sites),))
