"""Parasite: feeds on the dying, starves without blood, wins by surviving."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.modes.werewolf.roles import neutral_kit as kit
from aiplays.modes.werewolf.roles.base import NEUTRAL, act, role
from aiplays.modes.werewolf.roles.neutral_plague import infect, tick

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Night

STARVED = "starved without fresh blood"


def _feed(n: Night, a: Act) -> None:  # after: did the Parasite pick someone who died?
    t, s = a.targets[0], n.st(a.actor)
    if t.id in n.deaths:
        s.marks["fed"] = n.n
        kit.count(n.state, a.actor, "transfusions")
        n.note(a.actor, f"{t.name} died tonight: you fed on their blood.")
    elif s.marks.get("transfusions", 0) >= 2 and n.rng.random() < 0.5:
        infect(n, t, a.actor, contained=True)


def _lurk(n: Night, a: Act) -> None:  # early: moving roles cannot reach the Parasite's home
    n.hidden.add(a.actor.id)


class Parasite:
    passive = staticmethod(lambda n, p: tick(n))

    @staticmethod
    def after_night(n: Night, p) -> None:
        s = n.st(p)
        s.marks["misses"] = 0 if s.marks.get("fed") == n.n else s.marks.get("misses", 0) + 1
        if s.marks["misses"] >= 3:
            n.deaths[p.id] = STARVED
        elif s.marks["misses"]:
            n.note(p, f"You are weak with hunger ({s.marks['misses']}/3 nights without blood).")

    win = staticmethod(lambda state, p, result: p.alive)


role(id="parasite", label="Parasite", team=NEUTRAL, emoji="🩸", classes=("killing",), weight=-2,
     night_immune=True, hooks=Parasite,
     summary="Feeds on players who die; starves after 3 nights without blood. Wins by surviving.",
     card="You cannot be killed at night. Each night, visit a player you think will DIE that "
          "night: if they do, you feed. On any night you visit, moving roles cannot reach your "
          "home. After 3 nights in a row without feeding (skipping counts), you starve and die; "
          "nothing can prevent it. After your 2nd feeding, each visit to a survivor has a 50% "
          "chance to infect them: they die at the end of the next night (your strain does not "
          "spread). You win if you are alive when the game ends.",
     actions=(act("transfuse", "early", "Visit a player you expect to die tonight and feed "
                  "on them.", _lurk, after=_feed),))
