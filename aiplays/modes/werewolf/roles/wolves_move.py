"""Wolves that bend movement: Angler, Transporter, Scarecrow."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.modes.werewolf.roles.base import WOLVES, act
from aiplays.modes.werewolf.roles.wolves_core import Succession
from aiplays.modes.werewolf.roles.wolves_kit import wolf_role
from aiplays.modes.werewolf.status import status

if TYPE_CHECKING:
    from aiplays.core.moderator import Moderator
    from aiplays.core.state import Player
    from aiplays.modes.werewolf.night.context import Act, Night


def _hook(n: Night, a: Act) -> None:
    n.redirect[a.targets[0].id] = a.actor.id
    n.note(a.actor, f"You cast your line at {a.targets[0].name}.")


def _transport(n: Night, a: Act) -> None:
    x, y = a.targets
    if n.role(x).team == WOLVES and n.role(y).team == WOLVES:
        n.note(a.actor, "You can move at most one wolf per transport: nothing happened.")
        return
    n.resident[x.id], n.resident[y.id] = y.id, x.id
    n.note(x, "You woke up confused and out of place.")
    n.note(a.actor, f"You swapped {x.name} and {y.name} for the night.")


def _frighten(n: Night, a: Act) -> None:
    victim, fear = a.targets
    if n.role(victim).team == WOLVES:
        n.note(a.actor, "Your nightmares don't work on fellow wolves.")
        return
    n.st(victim).marks.update(nightmare=fear.id, nightmare_by=a.actor.id)
    n.note(victim, f"You had a nightmare about {fear.name}: you can't bring yourself to go "
                   "to their home.")


def _first_only(n: Night, a: Act) -> None:
    a.targets = a.targets[:1]  # the Scarecrow only visits the first player


class ScarecrowHooks(Succession):
    @staticmethod
    async def on_death(mod: Moderator, p: Player) -> None:
        for q in mod.state.players:  # nightmares fade when the Scarecrow dies
            m = status(mod.state, q).marks
            if m.get("nightmare_by") == p.id:
                m.pop("nightmare", None)
                m.pop("nightmare_by", None)


wolf_role(id="angler", label="Angler", emoji="🎣", classes=("manipulation",), weight=-4,
          summary="Hooks a player so their moving ability lands on the Angler instead.",
          card="Three times per game you may hook a player (you don't move). If they use an "
               "ability that visits or travels, they come to you and use it on you instead, "
               "without being told. Players who don't move are unaffected.",
          actions=(act("hook", "early", "Hook a player: their moving ability targets you "
                       "instead.", _hook, movement="none", uses=3),))
wolf_role(id="transporter", label="Transporter", emoji="🔀", classes=("manipulation",),
          weight=-4, summary="Swaps two players' homes for the night.",
          card="Three times per game you may pick two players (at most one wolf) to swap homes "
               "for the night: whoever targets one reaches the other. The swap happens before "
               "every other action and cannot be stopped. One of them wakes up confused.",
          actions=(act("transport", "early", "Pick two players to swap homes tonight.",
                       _transport, movement="travel", targets=2, pool="anyone", uses=3),))
wolf_role(id="scarecrow", label="Scarecrow", emoji="🎃", classes=("role_block",), weight=-3,
          hooks=ScarecrowHooks,
          summary="Gives a non-wolf a lasting nightmare: they can't move to a chosen player.",
          card="Each night you may visit a non-wolf (first name) and give them a nightmare about "
               "any second player (second name). From tonight on they cannot move to that "
               "player, until they get a new nightmare or you die. You only visit the first "
               "player, and can't target the same players two nights in a row.",
          actions=(act("frighten", "role_block", "Targets: victim, then who they will fear.",
                       _frighten, targets=2, aim=_first_only),))
