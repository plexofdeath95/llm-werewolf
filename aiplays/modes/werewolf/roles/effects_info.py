"""Reusable information handlers: role/side checks, lineups, watching and following."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.modes.werewolf.roles.base import ROLES

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Night

FOG = "A strange fog hid {name}'s home: you learned nothing."


def _learn(n: Night, a: Act) -> bool:
    if not n.can_learn(a, a.targets[0]):
        n.note(a.actor, FOG.format(name=a.targets[0].name))
        return False
    return True


def inspect_role(n: Night, a: Act) -> None:
    t = a.targets[0]
    if _learn(n, a):
        n.note(a.actor, f"Your investigation shows {t.name} is the {ROLES[n.seen_role(t)].label}.")


def inspect_team(n: Night, a: Act) -> None:
    t = a.targets[0]
    if _learn(n, a):
        n.note(a.actor, f"{t.name} belongs to the {n.seen_team(t).upper()} side.")


def lineup(n: Night, a: Act) -> None:
    """Three roles, one of which is the target's (seen) role."""
    t = a.targets[0]
    if not _learn(n, a):
        return
    true = n.seen_role(t)
    others = sorted({p.role for p in n.state.players} - {true}) or sorted(set(ROLES) - {true})
    picks = n.rng.sample(others, min(2, len(others))) + [true]
    n.rng.shuffle(picks)
    n.note(a.actor, f"{t.name} is one of: {', '.join(ROLES[r].label for r in picks)}.")


def watch_home(n: Night, a: Act) -> None:
    """Lookout-style: who came to the target's home, and whether the owner went out."""
    t = a.targets[0]
    seen = sorted({v.actor.name for v in n.visitors(t) if v.actor is not a.actor})
    left = " They left home tonight." if t.id in n.left_home else ""
    n.note(a.actor, f"At {t.name}'s home you saw: {', '.join(seen) or 'no visitors'}.{left}")


def follow(n: Night, a: Act) -> None:
    """Mystic/Spy-style: where the target went."""
    t = a.targets[0]
    went = sorted({x.name for b in n.acts_by(t) if b.moves and not b.blocked and not b.failed
                   for x in b.targets if x is not t})
    n.note(a.actor, f"{t.name} went to: {', '.join(went)}." if went
           else f"{t.name} did not leave home.")
