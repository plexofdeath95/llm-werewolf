"""The Warlock: brainwashes a villager into killing whoever they next visit."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.modes.werewolf.roles.base import act
from aiplays.modes.werewolf.roles.wolves_core import Succession
from aiplays.modes.werewolf.roles.wolves_kit import wolf_role

if TYPE_CHECKING:
    from aiplays.core.state import Player
    from aiplays.modes.werewolf.night.context import Act, Night


def _brainwash(n: Night, a: Act) -> None:
    n.st(a.targets[0]).marks.update(brainwashed_by=a.actor.id, brainwash_from=n.n + 1)
    n.note(a.actor, f"You brainwashed {a.targets[0].name}.")


class WarlockHooks(Succession):
    @staticmethod
    def passive(n: Night, warlock: Player) -> None:
        """A brainwashed player kills the first person they visit or travel to."""
        for q in n.state.alive():
            m = n.st(q).marks
            if m.get("brainwashed_by") != warlock.id or m.get("brainwash_from", 99) > n.n:
                continue
            hits = [t for b in n.acts_by(q) if b.moves and not b.blocked and not b.failed
                    for t in b.targets if t is not q and t.alive]
            if hits:
                n.attack(hits[0], q, "killed by a brainwashed visitor")
                n.note(q, "You wake up with a splitting headache.")
                m.pop("brainwashed_by")
                m.pop("brainwash_from")


wolf_role(id="warlock", label="Warlock", emoji="🧙", classes=("manipulation",), weight=-5,
          hooks=WarlockHooks,
          summary="Brainwashes a non-wolf, who later kills the first player they visit.",
          card="Each night you may visit one non-wolf and brainwash them. From the next night "
               "on, the first player they visit or travel to is killed by them; then they wake "
               "with a headache and the spell ends. It only works while you are alive.",
          actions=(act("brainwash", "manipulation", "Visit a non-wolf and brainwash them.",
                       _brainwash, pool="non_wolves"),))
