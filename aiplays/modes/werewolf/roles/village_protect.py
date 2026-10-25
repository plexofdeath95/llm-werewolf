"""Village protectors: doctor, bodyguard, martyr, jailor, smokescreener, coward, knight."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.core.moderator import Moderator
from aiplays.modes.werewolf.roles import effects
from aiplays.modes.werewolf.roles.base import VILLAGE, WOLVES, act, role
from aiplays.modes.werewolf.status import status

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Night

PROT = ("protection",)


def _martyr(n: Night, a: Act) -> None:
    n.martyrs[a.targets[0].id].append(a.actor)


def _smoke(n: Night, a: Act) -> None:
    n.shrouded[a.targets[0].id].add(WOLVES)


def _hide(n: Night, a: Act) -> None:
    n.hidden.add(a.actor.id)
    n.note(a.actor, "You hid all night. Nobody could visit you.")


class Knight:
    @staticmethod
    def on_start(state, p, rng) -> None:
        status(state, p).lives = 2

    @staticmethod
    async def on_lynched(mod: Moderator, p, voters) -> bool:
        s = status(mod.state, p)
        if s.lives > 1:
            s.lives -= 1
            await mod.announce(f"{p.name} is struck down... and gets back up! "
                               "The Knight survives, but the spare life is gone.")
            return True
        return False


role(id="doctor", label="Doctor", team=VILLAGE, emoji="🩺", classes=PROT, weight=6,
     summary="Heals one player a night from attacks (self allowed, not the same twice running).",
     card="Visit a player each night and heal them from any attack except unstoppable ones. "
          "You may heal yourself (you don't move then). You cannot heal the same player two "
          "nights in a row.",
     actions=(act("heal", "protection", "Heal a player tonight.", effects.heal,
                  pool="anyone"),))
role(id="bodyguard", label="Bodyguard", team=VILLAGE, emoji="🛡️", classes=PROT + ("killing",),
     weight=5, summary="Guards a player: if attacked, kills the attacker and dies too.",
     card="Travel to a player's home. If they are attacked, you kill the attacker but die "
          "in the fight. Not the same player two nights in a row.",
     actions=(act("guard", "protection", "Guard a player's home.", effects.guard,
                  movement="travel"),))
role(id="martyr", label="Martyr", team=VILLAGE, emoji="🕯️", classes=PROT, weight=4,
     summary="Stands in for a player: if they are attacked, the Martyr dies instead.",
     card="Travel to another player's home. If they are attacked tonight, you die in their "
          "place. Not the same player two nights in a row.",
     actions=(act("shield", "protection", "Die in a player's place if they are attacked.",
                  _martyr, movement="travel"),))
role(id="jailor", label="Jailor", team=VILLAGE, emoji="⛓️", classes=("role_block",) + PROT,
     weight=6, summary="Jails a player: they can't act and nobody can reach them.",
     card="Visit a player each night and jail them: they cannot use their ability, and no "
          "visitor can interact with them (attacks fail). You may jail yourself for safety "
          "(you don't move then). Not the same player two nights in a row.",
     actions=(act("jail", "role_block", "Jail a player for the night.", effects.jail,
                  pool="anyone"),))
role(id="smokescreener", label="Smokescreener", team=VILLAGE, emoji="🌫️", classes=PROT,
     weight=3, summary="Shrouds a home so wolf-side investigators learn nothing there.",
     card="Travel to a player's home. Werewolf-team information, influence, manipulation and "
          "role-copy abilities cannot read that home tonight.",
     actions=(act("smoke", "protection", "Shroud a player's home from the wolves.", _smoke,
                  movement="travel"),))
role(id="coward", label="Coward", team=VILLAGE, emoji="🙈", classes=("support",), weight=2,
     summary="Can hide twice per game: nobody can visit them that night.",
     card="Twice per game you may hide at night: nobody can visit you, including attackers "
          "and protectors.",
     actions=(act("hide", "early", "Hide tonight.", _hide, movement="none", targets=0,
                  uses=2),))
role(id="knight", label="Knight", team=VILLAGE, emoji="🗡️", classes=("support",), weight=3,
     hooks=Knight, summary="Has two lives, whether attacked at night or voted out.",
     card="You start with 2 lives. A night attack or being voted out costs one life; you die "
          "only when both are gone. Two attacks in one night kill you.")
