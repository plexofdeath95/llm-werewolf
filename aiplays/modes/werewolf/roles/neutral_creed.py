"""The Creed: a sworn group of killers who must all strike the same victim together."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.modes.werewolf.roles import neutral_kit as kit
from aiplays.modes.werewolf.roles.base import NEUTRAL, act, role
from aiplays.modes.werewolf.roles.neutral_kit import GOAL_TEXT
from aiplays.modes.werewolf.status import role_of

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Night

SLAIN, CREED = "slain by the Creed", "creed"


def _crew(n: Night) -> list:
    return [p for p in n.state.alive() if role_of(n.state, p) == "creed"]


def _strikes(n: Night) -> list[Act]:
    ids = {p.id for p in _crew(n)}
    return [b for b in n.acts if b.actor.id in ids and b.action.name == "strike"]


def _lead(n: Night, a: Act) -> bool:
    """Only the first unblocked striker resolves the Creed's (single) kill."""
    live = [b for b in _strikes(n) if not b.blocked]
    return bool(live) and live[0] is a


def _strike(n: Night, a: Act) -> None:
    if not _lead(n, a):
        return
    crew, strikes = _crew(n), _strikes(n)
    victims = {b.targets[0].id for b in strikes if b.targets}
    united = (len(strikes) == len(crew) and len(victims) == 1
              and all(not b.blocked and not b.failed for b in strikes))
    t = a.targets[0]
    if not united or role_of(n.state, t) == "creed":
        for p in crew:
            n.note(p, "The Creed was not united tonight (a different choice, someone stopped, "
                      "or an absentee): nobody died by your hand.")
        return
    n.attack(t, a.actor, SLAIN)


def _tally(n: Night, a: Act) -> None:  # after: count the Creed's shared kills once
    if _lead(n, a) and n.deaths.get(a.targets[0].id) == SLAIN:
        n.state.memory["creed_kills"] = n.state.memory.get("creed_kills", 0) + 1


class Creed:
    @staticmethod
    def knowledge(state, p) -> str:
        others = [q for q in state.players if q.role == "creed" and q is not p]
        return f"Your fellow Creed members: {state.names(others)}."

    @staticmethod
    def win(state, p, result) -> bool:
        return state.memory.get("creed_kills", 0) >= kit.goal(state) or \
            kit.last_standing(state, p, result)


role(id="creed", label="Creed", team=NEUTRAL, emoji="🕯️", classes=("killing",), weight=-5,
     hostile=True, group=3, chats=(CREED,), hooks=Creed,
     summary="A sworn group of three killers who must all strike the same victim.",
     card="You are one of the Creed (usually three), who know each other and talk privately at "
          "night. Each night every living Creed member may STRIKE a player. The kill only "
          "happens if every living member strikes the SAME player and none of you is blocked or "
          "stopped; otherwise nobody dies. You are not immune at night. The Creed wins once it "
          f"has killed at least {GOAL_TEXT} players, or if you are the last threat standing. "
          "The Village cannot win while any of you live.",
     actions=(act("strike", "killing", "Join the Creed's strike on one player (all of you must "
                  "pick the same one).", _strike, after=_tally),))
