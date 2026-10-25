"""Shared helpers for the Werewolf-team role modules (wolves_*.py)."""
from typing import Any

from aiplays.modes.werewolf.roles.base import ROLES, WOLF_DEN, WOLVES, RoleDef, role
from aiplays.modes.werewolf.roles.wolves_core import Succession


def wolf_role(*, den: bool = True, hooks: Any = Succession, **kw: Any) -> RoleDef:
    """A Werewolf-team role. Den members plot in the wolf den; every wolf role carries the
    Succession hook so the pack always regains an Alpha (and its kill)."""
    return role(team=WOLVES, chats=(WOLF_DEN,) if den else (), hooks=hooks, **kw)


def find_role(text: str) -> str | None:
    """Role id from a player's free-text guess ('the Seer', 'seer', 'Alignment Seer')."""
    key = text.strip().lower().removeprefix("the ").strip()
    for rid, r in ROLES.items():
        if key in (rid, rid.replace("_", " "), r.label.lower()):
            return rid
    return None
