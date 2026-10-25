"""Disease: the Plague Bringer, and the infection model it shares with the Parasite."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.modes.werewolf.roles import neutral_kit as kit
from aiplays.modes.werewolf.roles.base import NEUTRAL, act, role
from aiplays.modes.werewolf.roles.neutral_kit import GOAL_TEXT

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Night

PLAGUE = "succumbed to the plague"


def infect(n: Night, p, by, contained: bool = False) -> None:
    s = n.st(p)
    if "infected" not in s.flags:
        s.flags.add("infected")
        s.marks.update(infected_on=n.n, infected_by=by.id)
        if contained:  # the Parasite's strain does not spread
            s.flags.add("contained")


def tick(n: Night) -> None:
    """Once per night: older infections kill (unstoppably); the plague spreads to visitors."""
    if n.state.memory.get("plague_tick") == n.n:
        return
    n.state.memory["plague_tick"] = n.n
    sick = [p for p in n.state.alive() if "infected" in n.st(p).flags]
    for p in sick:
        s = n.st(p)
        if s.marks["infected_on"] < n.n:
            n.attack(p, n.state.by_id(s.marks["infected_by"]), PLAGUE, unstoppable=True)
    bringers = [p for p in n.state.alive() if n.role(p).id == "plague_bringer"]
    for carrier in bringers + [p for p in sick if "contained" not in n.st(p).flags]:
        src = carrier if carrier in bringers else n.state.by_id(n.st(carrier).marks["infected_by"])
        for v in n.visitors(carrier):
            if v.actor not in (carrier, *bringers) and v.action.movement == "visit":
                infect(n, v.actor, src)


def _spread(n: Night, a: Act) -> None:
    infect(n, a.targets[0], a.actor)


class PlagueBringer:
    @staticmethod
    def passive(n: Night, p) -> None:
        if kit.was_blocked(n, p):  # whoever blocks the Plague Bringer catches it
            for b in kit.blockers(n, p):
                infect(n, b, p)
        tick(n)

    @staticmethod
    def after_night(n: Night, p) -> None:
        alive = n.state.alive()
        if sum("infected" in n.st(q).flags for q in alive) * 2 >= len(alive):
            n.st(p).flags.add("outbreak")

    win = kit.goal_win(lambda s: s.kills + (99 if "outbreak" in s.flags else 0))


role(id="plague_bringer", label="Plague Bringer", team=NEUTRAL, emoji="☣️", classes=("killing",),
     weight=-5, hostile=True, hooks=PlagueBringer,
     summary="Infects players; the infected die the following night and spread it to visitors.",
     card="Each night you may visit one player and infect them. An infected player dies at the "
          "end of the NEXT night, and nothing can save them. Anyone who visits you, or visits an "
          "infected player, also becomes infected; whoever role-blocks you catches it too. The "
          "plague only spreads and kills while you (or a Parasite) live. You win once the plague "
          f"has killed at least {GOAL_TEXT} players, or once half of the living are infected, "
          "or if you are the last threat standing. The Village cannot win while you live.",
     actions=(act("infect", "killing", "Visit a player and infect them.", _spread),))
