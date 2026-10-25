"""Neutrals defined by where people sleep: Detour (redirects) and Orphan (lodges, adopts)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.modes.werewolf.roles import neutral_kit as kit
from aiplays.modes.werewolf.roles.base import NEUTRAL, ROLES, act, role
from aiplays.modes.werewolf.status import role_of, status

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Night


def _unvisited(state, p) -> list:
    done = status(state, p).marks.get("detoured", [])
    return [q for q in state.alive() if q is not p and q.id not in done]


def _detour(n: Night, a: Act) -> None:
    """Early: send one visitor to this home, and the owner, somewhere random instead."""
    house, s = a.targets[0], n.st(a.actor)
    s.marks.setdefault("detoured", []).append(house.id)
    coming = [b for b in n.acts if b.moves and b.actor not in (a.actor, house)
              and any(t is house for t in b.targets)]
    leaving = [b for b in n.acts_by(house) if b.moves]
    s.marks["pending"] = []
    for b in coming[:1] + leaving[:1]:
        spots = [q for q in n.state.alive() if q not in (b.actor, house, a.actor)]
        if spots:
            n.redirect[b.actor.id] = n.rng.choice(spots).id
            s.marks["pending"].append(b.actor.id)


def _tally(n: Night, a: Act) -> None:  # after: count the players who really got moved
    s = n.st(a.actor)
    for pid in s.marks.pop("pending", []):
        if pid in n.left_home:
            p = n.state.by_id(pid)
            n.note(p, f"You lost your way tonight and ended up at "
                      f"{n.state.by_id(n.redirect[pid]).name}'s home.")
            s.marks.setdefault("moved", []).append(n.team(p))


class Detour:
    @staticmethod
    def after_night(n: Night, p) -> None:
        if not any(b.action.name == "detour" and not b.blocked for b in n.acts_by(p)):
            kit.count(n.state, p, "idle")

    @staticmethod
    def win(state, p, result) -> bool:
        m = status(state, p).marks
        moved = m.get("moved", [])
        return len(moved) >= 3 and {"village", "wolves"} <= set(moved) and m.get("idle", 0) < 3


def _lodge(n: Night, a: Act) -> None:  # early: away from home, sharing the host's fate
    n.hidden.add(a.actor.id)
    n.linked[a.targets[0].id].append(a.actor)


def _adopt(n: Night, a: Act) -> None:  # after: take the host's role if you survived the night
    if a.actor.id not in n.deaths:
        rid = role_of(n.state, a.targets[0])
        n.st(a.actor).acting_as = rid
        n.note(a.actor, f"You have been adopted into a new life: you are now the "
                        f"{ROLES[rid].label}, with their abilities and win condition.")


role(id="detour", label="Detour", team=NEUTRAL, emoji="🚧", classes=("manipulation",), weight=-1,
     hooks=Detour, summary="Sends travellers astray; wins by misleading both village and wolves.",
     card="Each night travel to one home (each player at most once per game). Before anything "
          "else happens, the first player heading to that home and the owner (if they go out) "
          "are sent to a random other home instead and told where they ended up. You win once "
          "you have redirected 3 players including at least one Village and one Werewolf "
          "player, but you lose if you spend 3 nights without detouring.",
     actions=(act("detour", "early", "Choose a home to divert traffic around tonight.", _detour,
                  movement="travel", pool=_unvisited, after=_tally),))

role(id="orphan", label="Orphan", team=NEUTRAL, emoji="🧒", classes=("role_copy",), weight=0,
     hooks=type("OrphanHooks", (), {"win": staticmethod(lambda s, p, r: False)}),
     summary="Lodges with others at night; from night 2 can adopt a host's role.",
     card="Each night you may LODGE at another player's home: nobody can visit you at your own "
          "home that night, but if your host's home is attacked you are attacked too. From "
          "night 2 you may ADOPT instead: lodge with them and, if you survive the night, become "
          "their role (abilities, team and win condition). As a plain Orphan you cannot win.",
     actions=(act("lodge", "early", "Spend the night at another player's home.", _lodge),
              act("adopt", "early", "Lodge with a player and become their role at dawn.",
                  _lodge, from_night=2, after=_adopt)))
