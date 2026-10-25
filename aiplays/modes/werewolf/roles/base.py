"""Declarative role + action definitions (WikiWolf ruleset) and the role registry."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from aiplays.core.role import Role

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Night

VILLAGE, WOLVES, NEUTRAL = "village", "wolves", "neutral"
# WikiWolf movement priority: night actions resolve in this class order.
PRIORITY = ("role_block", "protection", "manipulation", "information", "influence",
            "role_copy", "support", "killing")
TEAM_ORDER = {VILLAGE: 0, NEUTRAL: 1, WOLVES: 2}  # tie order within a class
WOLF_DEN = "wolf den"

Handler = Callable[["Night", "Act"], None]


@dataclass(frozen=True)
class ActionDef:
    name: str
    cls: str                     # priority class (see PRIORITY)
    help: str                    # what the player is told
    handler: Handler
    movement: str = "visit"      # none | visit | travel
    targets: int = 1             # players to pick (0 = no target)
    pool: str = "others"         # others | anyone | dead | non_wolves
    uses: int | None = None      # per game; None = unlimited
    cooldown: int = 0            # nights to wait after use
    no_repeat: bool = False      # can't pick the same target two nights running
    from_night: int = 1
    only_night: int | None = None
    unblockable: bool = False
    options: tuple[str, ...] = ()  # extra choice: listed values, or ("*",) for free text
    aim: Handler | None = None   # rewrites act.targets before movement (e.g. sleepwalker)
    ready: Callable[[Any, Any], bool] | None = None  # (state, player) -> usable tonight?
    uses_key: str | None = None  # share a uses pool between actions (inquisitor shot/alert)
    after: Handler | None = None  # runs after deaths are settled (preacher, vigilante guilt)
    late: Callable[..., Any] | None = None  # async (mod, night, act) after resolution

    @property
    def repeat_banned(self) -> bool:
        return self.no_repeat or self.cls in ("protection", "role_block")


@dataclass(frozen=True)
class RoleDef(Role):
    summary: str = ""
    card: str = ""
    classes: tuple[str, ...] = ()
    weight: int = 0              # balance: + helps village, - helps wolves
    actions: tuple[ActionDef, ...] = ()
    chats: tuple[str, ...] = ()  # private night channels (wolf den, masons, lovers...)
    hostile: bool = False        # neutral killer: village must eliminate it too
    night_immune: bool = False
    in_deck: bool = True         # eligible for random default decks
    group: int = 1               # copies that must be dealt together (masons, lovers, creed)
    hooks: Any = None            # optional object with on_start/on_death/on_lynched/win/...

    def hook(self, name: str) -> Callable | None:
        return getattr(self.hooks, name, None) if self.hooks else None


ROLES: dict[str, RoleDef] = {}


def role(**kw: Any) -> RoleDef:
    r = RoleDef(**kw)
    ROLES[r.id] = r
    return r


def act(name: str, cls: str, help: str, handler: Handler, **kw: Any) -> ActionDef:
    return ActionDef(name=name, cls=cls, help=help, handler=handler, **kw)
