"""Wolf information roles: Bloodhound, Clairvoyant, Spy, Graverobber, Necromancer."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.modes.werewolf.roles import effects
from aiplays.modes.werewolf.roles.base import ROLES, Handler, act
from aiplays.modes.werewolf.roles.wolves_kit import wolf_role
from aiplays.modes.werewolf.status import role_of

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Night

ONCE = " Each body can be used only once (by you or any other grave-visiting role)."


def exhume(learn: bool) -> Handler:
    """Graveyard visit: claim a body once; its night abilities are yours tomorrow night."""
    def handler(n: Night, a: Act) -> None:
        body = a.targets[0]
        if "exhumed" in n.st(body).flags:
            n.note(a.actor, f"{body.name}'s grave was already disturbed: the body is useless.")
            return
        n.st(body).flags.add("exhumed")
        rid = role_of(n.state, body)
        effects.borrow(n, a.actor, rid)
        known = f"{body.name} was the {ROLES[rid].label}. " if learn else ""
        n.note(a.actor, f"You dig up {body.name}'s body. {known}"
                        "Tomorrow night you may use their night abilities, if they had any.")
    return handler


wolf_role(id="bloodhound", label="Bloodhound", emoji="🐕", classes=("information",), weight=-4,
          summary="Sniffs out a non-wolf: learns three roles, one of them theirs.",
          card="Each night you may visit one non-wolf. You learn three roles, one of which is "
               "their role as it appears to investigators (framing and disguises fool you).",
          actions=(act("sniff", "information", "Visit a non-wolf; learn 3 roles, 1 is theirs.",
                       effects.lineup, pool="non_wolves"),))
wolf_role(id="clairvoyant", label="Clairvoyant", emoji="👁️", classes=("information",),
          weight=-5, summary="Travels to a non-wolf's home and learns their role.",
          card="Each night you may travel to one non-wolf's home (watching from outside, "
               "without interacting) and learn their role as it appears to investigators.",
          actions=(act("divine", "information", "Travel to a non-wolf and learn their role.",
                       effects.inspect_role, movement="travel", pool="non_wolves"),))
wolf_role(id="spy", label="Spy", emoji="🕵️", classes=("information",), weight=-4,
          summary="Tails a non-wolf: learns whether and where they went at night.",
          card="Each night you may travel to one non-wolf's home and learn whether they went "
               "out that night and, if so, whose home(s) they went to.",
          actions=(act("tail", "information", "Travel to a non-wolf; learn where they went.",
                       effects.follow, movement="travel", pool="non_wolves"),))
wolf_role(id="graverobber", label="Graverobber", emoji="⚰️",
          classes=("information", "role_copy"), weight=-4,
          summary="Robs a grave: learns the dead player's role and borrows their power.",
          card="Once someone has died, each night you may visit the graveyard and dig up one "
               "body: you learn that player's true role, and the following night you may use "
               "their night abilities." + ONCE,
          actions=(act("rob", "information", "Dig up a dead player: learn their role, use "
                       "their ability tomorrow night.", exhume(True), pool="dead"),))
wolf_role(id="necromancer", label="Necromancer", emoji="💀", classes=("role_copy",),
          weight=-4, summary="Raises a corpse to use its night ability the next night.",
          card="Once someone has died, each night you may visit the graveyard and exhume one "
               "body. The following night you can make the corpse use its night ability, "
               "getting the results as if you were that role." + ONCE,
          actions=(act("exhume", "role_copy", "Exhume a dead player; tomorrow night you may "
                       "use their night ability.", exhume(False), pool="dead"),))
