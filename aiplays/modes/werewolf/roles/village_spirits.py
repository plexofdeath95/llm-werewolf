"""Village mediums who deal with the dead: the Druid and the Ghost Whisperer."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.agents.schemas import Choice
from aiplays.core.moderator import Moderator
from aiplays.modes.werewolf.roles import effects
from aiplays.modes.werewolf.roles.base import ROLES, VILLAGE, act, role

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Night


def _commune(n: Night, a: Act) -> None:
    t = a.targets[0]
    if "exhumed" in n.st(t).flags:
        n.note(a.actor, f"{t.name}'s body has already been used.")
        return
    n.st(t).flags.add("exhumed")
    n.note(a.actor, f"{t.name} was the {ROLES[t.role].label}. Tomorrow night you may use "
                    "their abilities.")
    effects.borrow(n, a.actor, t.role)


async def _seance(mod: Moderator, n: Night, a: Act) -> None:
    dead = [p for p in mod.state.players if not p.alive]
    if not dead:
        n.note(a.actor, "No spirits answer: nobody has died yet.")
        return
    q = a.option
    replies = await mod.ask_many(
        dead, lambda p: f'[spirit chat] The Ghost Whisperer asks the dead: "{q}". Put "yes" '
                        'or "no" in "target" (the dead may lie).', Choice,
        fallback=lambda p: Choice(target="no"), choices=lambda p: ["yes", "no"])
    yes = sum(c.target.strip().lower().startswith("y") for c in replies.values())
    no = len(replies) - yes
    verdict = "YES" if yes > no else "NO" if no > yes else "undecided"
    n.note(a.actor, f'The dead answer "{q}": {verdict}.')


role(id="druid", label="Druid", team=VILLAGE, emoji="🌿", classes=("information", "role_copy"),
     weight=4, summary="Communes with a corpse: learns its role and borrows its power.",
     card="Visit the graveyard and pick a dead player: you learn their role, and the next "
          "night only you may use their night abilities. Each body can be used once.",
     actions=(act("commune", "role_copy", "Commune with a dead player.", _commune,
                  pool="dead"),))
role(id="ghost_whisperer", label="Ghost Whisperer", team=VILLAGE, emoji="👻",
     classes=("information",), weight=3,
     summary="Asks the dead one yes/no question each night; the dead vote on the answer.",
     card="Each night ask the dead one yes/no question (put it in 'option'). The dead vote "
          "and you get the majority answer, or 'undecided' on a tie. The dead may lie.",
     actions=(act("ask_the_dead", "information", "Ask the dead a yes/no question.",
                  lambda n, a: None, movement="none", targets=0, options=("*",),
                  late=_seance),))
