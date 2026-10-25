"""Wolf blockers and killers: Amoeba, Consort, Potion Master, Stalker, Trapper."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.modes.werewolf.roles import effects
from aiplays.modes.werewolf.roles.base import ROLES, act
from aiplays.modes.werewolf.roles.traps import TRAP_PASSIVE, build_trap, place_trap
from aiplays.modes.werewolf.roles.wolves_core import Succession
from aiplays.modes.werewolf.roles.wolves_kit import find_role, wolf_role
from aiplays.modes.werewolf.status import role_of

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Night


def _absorb(n: Night, a: Act) -> None:
    t = a.targets[0]
    true = role_of(n.state, t)
    if find_role(a.option) != true:
        n.note(a.actor, f"{t.name} is not the {a.option}: your absorption failed.")
        return
    n.block(t)
    n.note(t, "You feel strangely drained.")
    effects.borrow(n, a.actor, true)
    n.note(a.actor, f"Correct: {t.name} is the {ROLES[true].label}. They are drained tonight, "
                    "and tomorrow night you may use their abilities.")


class TrapperHooks(Succession):
    passive = staticmethod(TRAP_PASSIVE)


POTIONS = " (each potion needs two nights to rebrew)"

wolf_role(id="amoeba", label="Amoeba", emoji="🦠", classes=("role_block", "role_copy"),
          weight=-4, summary="Guesses a non-wolf's role; if right, drains them and copies it.",
          card="Each night you may visit one non-wolf and guess their role (option = the role "
               "name). If you are right, their action fails tonight (they feel drained) and "
               "tomorrow night you may use their abilities. If wrong, nothing happens. You "
               "can't target the same player two nights in a row.",
          actions=(act("absorb", "role_block", "Visit a non-wolf; option = your guess of "
                       "their role.", _absorb, pool="non_wolves", options=("*",)),))
wolf_role(id="consort", label="Consort", emoji="💋", classes=("role_block",), weight=-5,
          summary="Keeps a non-wolf busy so their night action fails.",
          card="Each night you may visit one non-wolf and keep them busy: they can't leave home "
               "and their ability fails tonight (they are told so). A few roles, like the Seer, "
               "can't be blocked. You can't target the same player two nights in a row.",
          actions=(act("block", "role_block", "Visit a non-wolf; their action fails tonight.",
                       effects.block, pool="non_wolves"),))
wolf_role(id="potion_master", label="Potion Master", emoji="🧪",
          classes=("killing", "information", "role_block"), weight=-6,
          summary="Brews three potions: kill, learn a role, or block, each on a cooldown.",
          card="Each night you may use one of three potions on a non-wolf you visit. After "
               "use, a potion needs two nights to rebrew (used night 1, ready again night 4). "
               "Poison kills, Sight reveals their role, Sleep makes their action fail tonight.",
          actions=(act("poison", "killing", "Kill a non-wolf" + POTIONS + ".",
                       effects.kill("poisoned by the Potion Master"), pool="non_wolves",
                       cooldown=2),
                   act("sight", "information", "Learn a non-wolf's role" + POTIONS + ".",
                       effects.inspect_role, pool="non_wolves", cooldown=2),
                   act("sleep", "role_block", "Block a non-wolf tonight" + POTIONS + ".",
                       effects.block, pool="non_wolves", cooldown=2)))
wolf_role(id="stalker", label="Stalker", emoji="🔪", classes=("role_block", "killing"),
          weight=-5, summary="Lies in wait outside a non-wolf's home; kills them if they go out.",
          card="Three times per game you may travel to a non-wolf's home and lie in wait: if "
               "they leave home that night (visit or travel anywhere), you kill them outside "
               "their door. You can't target the same player two nights in a row.",
          actions=(act("stalk", "killing", "Travel to a non-wolf; kill them if they go out.",
                       effects.kill_if_leaves("killed by the Stalker"), movement="travel",
                       pool="non_wolves", uses=3, no_repeat=True),))
wolf_role(id="trapper", label="Trapper", emoji="🪤", classes=("killing",), weight=-5,
          hooks=TrapperHooks, summary="Builds and lays traps that kill the first visitor.",
          card="Each night you may either build a trap (kept in hand, no limit) or set your one "
               "laid trap at any home, a fellow wolf's included (setting it again moves it). "
               "The first other player to visit that home springs it and dies; the trap is "
               "then gone. Wolves are not spared.",
          actions=(build_trap, place_trap))
