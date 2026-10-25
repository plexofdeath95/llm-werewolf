"""Village support: villager, mason, lovers, sleepwalker."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.core.state import GameState, Player
from aiplays.modes.werewolf.roles.base import VILLAGE, act, role
from aiplays.modes.werewolf.status import status

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Attack, Night


def partner(state: GameState, p: Player) -> Player | None:
    """The other living lover (Lovers role pair, or Cupid's 'lover' flag)."""
    mine = "lover" in status(state, p).flags
    return next((q for q in state.alive() if q is not p and (
        ("lover" in status(state, q).flags) if mine else q.role == "lovers")), None)


def _stay(n: Night, a: Act) -> None:
    other = partner(n.state, a.actor)
    if not other or other.id in n.hidden or a.actor.id in n.hidden:
        return  # no partner, or the pair already settled where to sleep tonight
    host, guest = (a.actor, other) if a.option == "my home" else (other, a.actor)
    n.linked[host.id].append(guest)
    n.hidden.add(guest.id)  # the empty home: anything aimed there fails
    for p in (host, guest):
        n.note(p, f"You and {(guest if p is host else host).name} spent the night at "
                  f"{host.name}'s home.")


LOVERS_STAY = act("stay", "early", "Choose where you and your lover sleep tonight; whatever "
                  "happens at that home happens to both of you, the other home stands empty.",
                  _stay, movement="none", targets=0, options=("my home", "partner's home"))


def _sleepwalk(n: Night, a: Act) -> None:
    avoid = {t.id for t in a.targets}
    pool = [p for p in n.state.alive() if p is not a.actor and p.id not in avoid]
    if pool:
        dest = n.rng.choice(pool)
        a.targets = [dest]
        n.linked[dest.id].append(a.actor)
        n.note(a.actor, f"You sleepwalked into {dest.name}'s home.")


class Lovers:
    @staticmethod
    def knowledge(state: GameState, p: Player) -> str:
        q = partner(state, p)
        return f"Your lover is {q.name}. You can talk privately at night." if q else ""


class Sleepwalker:
    @staticmethod
    def on_attacked(n: Night, atk: Attack) -> bool:
        """Immune at home unless a role-blocker kept them in."""
        home = atk.home == atk.target.id
        return home and not any(x.blocked for x in n.acts_by(atk.target))


role(id="villager", label="Villager", team=VILLAGE, emoji="🧑‍🌾", classes=("support",), weight=1,
     summary="No powers: only wits and a vote.",
     card="You have no ability. Find the wolves through discussion and your vote.")
role(id="mason", label="Mason", team=VILLAGE, emoji="🧱", classes=("support",), weight=2,
     group=2, chats=("masons",), summary="Masons know each other and talk privately at night.",
     card="You know who the other Masons are and can talk with them privately each night.",
     hooks=type("MasonHooks", (), {"knowledge": staticmethod(lambda st, p: "Fellow masons: "
                + st.names([q for q in st.players if q.role == "mason" and q is not p]) + ".")}))
role(id="lovers", label="Lovers", team=VILLAGE, emoji="💞", classes=("support",), weight=2,
     group=2, chats=("lovers",), hooks=Lovers, actions=(LOVERS_STAY,),
     summary="A pair who talk privately and choose each night whose home they share.",
     card="You and your lover talk privately at night and pick whose home you both sleep "
          "in: anything that happens there happens to both of you.")
role(id="sleepwalker", label="Sleepwalker", team=VILLAGE, emoji="😴", classes=("support",),
     weight=2, hooks=Sleepwalker, summary="Wanders into a random home at night; safe at home.",
     card="You cannot be attacked at your own home unless a role-blocker keeps you in. Each "
          "night name two players to avoid; you sleepwalk into a random other player's home "
          "and share whatever happens there (including attacks).",
     actions=(act("sleepwalk", "support", "Name two players to avoid tonight.",
                  lambda n, a: None, targets=2, aim=_sleepwalk),))
