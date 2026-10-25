"""Village investigators who read roles, sides, or movement."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.modes.werewolf.roles import effects
from aiplays.modes.werewolf.roles.base import ROLES, VILLAGE, act, role

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Night

INFO = ("information",)


def _scry(n: Night, a: Act) -> None:
    t, s = a.targets[0], n.st(a.actor)
    prev = s.marks.get("scry_prev")
    s.marks["scry_prev"] = (t.name, n.seen_team(t))
    if prev:
        same = "MATCHES" if prev[1] == n.seen_team(t) else "does NOT match"
        n.note(a.actor, f"{t.name}'s alignment {same} {prev[0]}'s.")
    else:
        n.note(a.actor, f"You attune to {t.name}. Tomorrow night you can compare someone to them.")


def _shoes(n: Night, a: Act) -> None:
    t = a.targets[0]
    moves = any(x.movement != "none" for x in ROLES[n.seen_role(t)].actions)
    n.note(a.actor, f"{t.name} {'IS' if moves else 'is NOT'} capable of moving at night.")


def _voyeur(n: Night, a: Act) -> None:
    t = a.targets[0]
    kinds = sorted({v.action.cls for v in n.visitors(t) if v.actor is not a.actor})
    n.note(a.actor, f"Kinds of roles that came to {t.name}'s home: {', '.join(kinds) or 'none'}.")


role(id="seer", label="Seer", team=VILLAGE, emoji="🔮", classes=INFO, weight=7,
     summary="Each night learns one player's exact role. Cannot be role-blocked.",
     card="Each night pick a player; you learn their role. You don't move, so you cannot be "
          "role-blocked. Framed or disguised players show their false role.",
     actions=(act("inspect", "information", "Learn a player's role.", effects.inspect_role,
                  movement="none", unblockable=True),))
role(id="alignment_seer", label="Alignment Seer", team=VILLAGE, emoji="⚖️", classes=INFO,
     weight=6, summary="Each night visits a player to learn which side they are on.",
     card="Visit a player each night to learn their side: village, wolves or neutral.",
     actions=(act("inspect", "information", "Learn a player's side.", effects.inspect_team),))
role(id="lookout", label="Lookout", team=VILLAGE, emoji="👀", classes=INFO, weight=5,
     summary="Watches a home: sees who arrives and whether the owner goes out.",
     card="Travel to a home and watch it all night. You see every player who visits or "
          "travels there, and whether its owner leaves. You don't interact with anyone.",
     actions=(act("watch", "information", "Watch a player's home.", effects.watch_home,
                  movement="travel"),))
role(id="mystic", label="Mystic", team=VILLAGE, emoji="🌌", classes=INFO, weight=5,
     summary="Learns where a player went tonight. Cannot be role-blocked.",
     card="Each night pick a player and learn whose homes they went to. You don't move and "
          "cannot be role-blocked.",
     actions=(act("follow", "information", "See where a player goes.", effects.follow,
                  movement="none", unblockable=True),))
role(id="scryer", label="Scryer", team=VILLAGE, emoji="🪞", classes=INFO, weight=4,
     summary="Learns whether each new target's side matches the previous target's.",
     card="Visit a player each night (not yourself). From the second use on, you learn "
          "whether their side matches the side of the player you visited before.",
     actions=(act("scry", "information", "Compare this player's side with your last.",
                  _scry),))
role(id="shoe_shiner", label="Shoe Shiner", team=VILLAGE, emoji="👞", classes=INFO, weight=3,
     summary="Learns whether a player's role is able to move at night.",
     card="Travel to a player each night and learn whether their role can move at night "
          "(visit or travel), whether or not they actually moved tonight.",
     actions=(act("shine", "information", "Check whether a player can move at night.",
                  _shoes, movement="travel"),))
role(id="voyeur", label="Voyeur", team=VILLAGE, emoji="🔭", classes=INFO, weight=3,
     summary="Learns which kinds of roles came to a home (not who, not how many).",
     card="Travel to a home and learn the classes (killing, protection, information...) of "
          "every role that came there tonight. You learn neither names nor numbers.",
     actions=(act("peep", "information", "Spy on a home's visitors' classes.", _voyeur,
                  movement="travel"),))
role(id="drunkard", label="Drunkard", team=VILLAGE, emoji="🍺", classes=INFO, weight=3,
     summary="Visits a player and learns three roles, one of which is theirs.",
     card="Visit a player and get drunk with them: you learn three roles from this game's "
          "deck, one of which is their real (or disguised) role.",
     actions=(act("drink", "information", "Get three role guesses about a player.",
                  effects.lineup),))
