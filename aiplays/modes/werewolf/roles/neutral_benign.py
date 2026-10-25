"""Benign neutrals that never need to kill: Survivor, Amnesiac, Executioner."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.core.events import Kind
from aiplays.modes.werewolf.roles import neutral_kit as kit
from aiplays.modes.werewolf.roles.base import NEUTRAL, ROLES, act, role
from aiplays.modes.werewolf.status import role_of, status

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Attack, Night


def _hide(n: Night, a: Act) -> None:
    n.linked[a.targets[0].id].append(a.actor)  # whatever hits that home hits you too


class Survivor:
    @staticmethod
    def on_attacked(n: Night, atk: Attack) -> bool:
        t = atk.target
        if atk.home and atk.home != t.id:  # caught in the home you hid in
            return atk.home not in n.deaths
        if kit.was_blocked(n, t):
            return False
        n.note(t, "Someone came for you tonight, but you were nowhere to be found.")
        return True

    win = staticmethod(lambda state, p, result: p.alive)


def _remember(n: Night, a: Act) -> None:
    rid = role_of(n.state, a.targets[0])
    if rid == "amnesiac":
        n.note(a.actor, "That body held no memories worth having.")
        return
    n.st(a.actor).acting_as = rid
    n.note(a.actor, f"You remember who you are: the {ROLES[rid].label}! You now have their "
                    "abilities and their win condition.")


def _choose(n: Night, a: Act) -> None:
    n.st(a.actor).marks["target"] = a.targets[0].id
    n.note(a.actor, f"Your target is {a.targets[0].name}. Get them voted out.")


def _needs_target(state, p) -> bool:
    t = status(state, p).marks.get("target")
    return not t or not state.by_id(t).alive


class Executioner:
    @staticmethod
    async def after_lynch(mod, q, lynched, voters) -> None:
        if status(mod.state, q).marks.get("target") == lynched.id:
            status(mod.state, q).flags.add("executed")
            await mod.emit(Kind.ACTION, f"{lynched.name} was hanged: you have won!", actor=q.id,
                           visible_to=[q.id], data={"action": "result"})

    win = staticmethod(lambda state, p, result: "executed" in status(state, p).flags)


role(id="survivor", label="Survivor", team=NEUTRAL, emoji="🏃", classes=("support",), weight=0,
     hooks=Survivor, summary="Hides from danger every night. Wins by being alive at the end.",
     card="Killing roles cannot harm you in your own home, unless you were role-blocked that "
          "night. Each night you may hide in another player's home instead: if that home's "
          "owner is killed there, you die with them. You win if you are alive when the game "
          "ends, whoever else wins.",
     actions=(act("hide", "support", "Spend the night hiding in another player's home.", _hide),))

role(id="amnesiac", label="Amnesiac", team=NEUTRAL, emoji="🌀", classes=("role_copy",), weight=0,
     hooks=type("AmnesiacHooks", (), {"win": staticmethod(lambda s, p, r: False)}),
     summary="Visits the graveyard once to take a dead player's role and win condition.",
     card="You have no goal of your own yet. Once per game, visit the graveyard and pick a dead "
          "player: you become their role, with its abilities, team and win condition, from the "
          "next night on. You learn which role you took. Until then you cannot win.",
     actions=(act("remember", "role_copy", "Become a dead player's role (once per game).",
                  _remember, pool="dead", uses=1),))

role(id="executioner", label="Executioner", team=NEUTRAL, emoji="🪓", classes=("influence",),
     weight=-1, hooks=Executioner,
     summary="Picks a target and wins if the village hangs them.",
     card="On a night when you have no living target, choose one other player as your target "
          "(no visit). You win if your target is eliminated by the day vote while you are "
          "alive. If your target dies any other way, you choose a new target the next night.",
     actions=(act("target", "influence", "Choose the player you want the village to hang.",
                  _choose, movement="none", ready=_needs_target),))
