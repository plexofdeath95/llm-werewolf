"""Village roles that learn from rumours, graves, confessions and study."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.core.moderator import Moderator
from aiplays.modes.werewolf.roles.base import NEUTRAL, ROLES, VILLAGE, WOLVES, act, role
from aiplays.modes.werewolf.status import role_of, status

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Night


def _bartend(n: Night, a: Act) -> None:
    pick = n.rng.choice(a.targets)
    n.note(a.actor, f"Over drinks you learned one of {n.state.names(a.targets)} is the "
                    f"{ROLES[role_of(n.state, pick)].label}.")


def _dig(n: Night, a: Act) -> None:
    t = a.targets[0]
    n.note(a.actor, f"The grave tells the truth: {t.name} was the {ROLES[t.role].label}.")


def _confess(n: Night, a: Act) -> None:  # runs after tonight's deaths are settled
    t = a.targets[0]
    has = "has killed" if "has_killed" in n.st(t).flags else "has NOT killed"
    n.note(a.actor, f"In confession you sense that {t.name} {has} anyone so far.")


def _tattle(n: Night, a: Act) -> None:
    n.st(a.actor).marks["tattled"] = a.targets[0].id


def _study(n: Night, a: Act) -> None:
    st, k = n.state, n.n
    alive = st.alive()
    wolves = [p for p in alive if ROLES[role_of(st, p)].team == WOLVES]
    if k == 1:
        text = f"There are {len(wolves)} Werewolf-team players alive."
    elif k == 2:
        text = f"There are {sum(ROLES[role_of(st, p)].team == NEUTRAL for p in alive)} " \
               "Neutral players alive."
    elif k == 3:
        safe = [p for p in alive if p not in wolves and p is not a.actor]
        text = f"{n.rng.choice(safe).name} is not a werewolf." if safe else "Nothing new."
    elif k == 4 and wolves:
        text = f"One living wolf is the {ROLES[role_of(st, n.rng.choice(wolves))].label}."
    else:
        text = f"{n.rng.choice(wolves).name} is on the Werewolf team!" if wolves else \
            "No werewolves remain."
    n.note(a.actor, f"Your studies reveal: {text}")


class TattleHooks:
    @staticmethod
    async def on_death(mod: Moderator, p) -> None:
        tid = status(mod.state, p).marks.get("tattled")
        if tid:
            t = mod.state.by_id(tid)
            await mod.announce(f"{p.name}'s diary is found: \"{t.name} is the "
                               f"{ROLES[t.role].label}.\"")


role(id="bartender", label="Bartender", team=VILLAGE, emoji="🍸", classes=("information",),
     weight=3, summary="Picks three players and learns the role of one of them (not which).",
     card="Each night choose three players. You learn the true role of one of them, picked "
          "at random, but not which of the three it belongs to. You don't move.",
     actions=(act("serve", "information", "Pick three players for a round of drinks.",
                  _bartend, movement="none", targets=3),))
role(id="gravedigger", label="Gravedigger", team=VILLAGE, emoji="⚰️", classes=("information",),
     weight=3, summary="Digs up a dead player each night to learn their true role.",
     card="Once there are dead players, visit the graveyard each night and learn a dead "
          "player's true role. This information cannot be faked.",
     actions=(act("dig", "information", "Learn a dead player's true role.", _dig,
                  pool="dead"),))
role(id="preacher", label="Preacher", team=VILLAGE, emoji="⛪", classes=("information",),
     weight=4, summary="Hears a confession: learns whether a player has ever killed.",
     card="Visit a player each night for confession. You learn whether they have killed "
          "anyone so far, including tonight, but not when.",
     actions=(act("confess", "information", "Learn whether a player has killed.",
                  lambda n, a: None, after=_confess),))
role(id="tattletale", label="Tattletale", team=VILLAGE, emoji="📔", classes=("information",),
     weight=3, hooks=TattleHooks,
     summary="Keeps a diary: when they die, the true role of their last visit is revealed.",
     card="Visit a player each night. When you die, the true role of the last player you "
          "visited is announced publicly from your diary.",
     actions=(act("visit", "information", "Note down a player in your diary.", _tattle),))
role(id="scholar", label="Scholar", team=VILLAGE, emoji="📚", classes=("information",),
     weight=4, summary="Learns stronger facts about the game every night. Unblockable.",
     card="Each night you study and learn a fact that grows stronger: night 1 the number of "
          "living wolves, night 2 living neutrals, night 3 a player who is not a wolf, night "
          "4 one living wolf's role, night 5+ the name of a living wolf.",
     actions=(act("study", "information", "Study the village's secrets.", _study,
                  movement="none", targets=0, unblockable=True),))
