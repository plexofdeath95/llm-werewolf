"""Village crafters and mediums: armorer, artificer, druid, ghost whisperer."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.agents.schemas import Choice
from aiplays.core.moderator import Moderator
from aiplays.modes.werewolf.roles import effects
from aiplays.modes.werewolf.roles.base import ROLES, VILLAGE, act, role
from aiplays.modes.werewolf.status import status

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Night


def _forge(n: Night, a: Act) -> None:
    s = n.st(a.actor)
    s.marks["armor_stock"] = s.marks.get("armor_stock", 0) + 1
    n.note(a.actor, f"You forged armor. Pieces ready: {s.marks['armor_stock']}.")


def _give_armor(n: Night, a: Act) -> None:
    n.st(a.actor).marks["armor_stock"] -= 1
    n.st(a.targets[0]).flags.add("armor_on")
    n.note(a.targets[0], "You received a suit of armor: it will save you from one attack.")


USE_BINOCULARS = act("use_binoculars", "information", "One-time: watch a home like a Lookout "
                     "(uses your night action).", effects.watch_home, movement="travel", uses=1)
USE_FIRST_AID = act("use_first_aid", "protection", "One-time: heal a player like a Doctor "
                    "(uses your night action).", effects.heal, pool="anyone", uses=1)
ITEMS = {"binoculars": USE_BINOCULARS, "first aid kit": USE_FIRST_AID}


def _package(item: str):
    def handler(n: Night, a: Act) -> None:
        t, s = a.targets[0], n.st(a.targets[0])
        if item == "nail bomb":
            n.attack(t, a.actor, "killed by a nail bomb in a package")
            return
        if item == "steroid":
            s.flags.add("steroid")
        else:
            s.marks.setdefault("borrowed", []).append(ITEMS[item])
        n.note(t, f"You received a package containing a {item}. "
                  + ("It will save you from one attack." if item == "steroid"
                     else "You can use it on a later night instead of your normal action."))
    return handler


def _commune(n: Night, a: Act) -> None:
    t = a.targets[0]
    if "corpse_used" in n.st(t).flags:
        n.note(a.actor, f"{t.name}'s body has already been used.")
        return
    n.st(t).flags.add("corpse_used")
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


role(id="armorer", label="Armorer", team=VILLAGE, emoji="🛠️", classes=("support",), weight=3,
     summary="Forges armor and hands it out; armor saves its wearer from one attack.",
     card="Each night either forge a piece of armor or deliver a piece to a player. Armor "
          "is worn automatically and absorbs the next attack, then breaks.",
     actions=(act("forge", "support", "Forge a piece of armor.", _forge, movement="none",
                  targets=0),
              act("give_armor", "support", "Deliver armor to a player.", _give_armor,
                  ready=lambda st, p: status(st, p).marks.get("armor_stock", 0) > 0)))
role(id="artificer", label="Artificer", team=VILLAGE, emoji="📦", classes=("support", "killing"),
     weight=4, summary="Sends packages: binoculars, first aid, steroid, or a nail bomb.",
     card="Each night visit a player with a package: binoculars (one Lookout watch), a first "
          "aid kit (one Doctor heal), a steroid (survive one attack) or a nail bomb (kills "
          "them). Each item has a two-night cooldown. Using an item takes the holder's action.",
     actions=tuple(act(f"send_{k.split()[0]}", "support", f"Deliver a package with a {k}.",
                       _package(k), cooldown=2)
                   for k in ("binoculars", "first aid kit", "steroid", "nail bomb")))
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
