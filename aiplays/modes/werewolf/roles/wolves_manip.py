"""Wolf manipulators: Framer, Makeup Artist, Hypnotist, Mimic, Obscurist."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.modes.werewolf.roles.base import ROLES, VILLAGE, act
from aiplays.modes.werewolf.roles.wolves_kit import find_role, wolf_role

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Act, Night


def _frame(n: Night, a: Act) -> None:
    t = a.targets[0]
    n.appear(t, "wolf")
    n.st(t).marks["framed_until"] = n.n  # guilt-reading roles (e.g. Preacher) can honour this
    n.note(a.actor, f"You framed {t.name}: tonight they look like a Wolf to investigators.")


def _disguise(n: Night, a: Act) -> None:
    t, rid = a.targets[0], find_role(a.option)
    if not rid:
        n.note(a.actor, f'"{a.option}" is not a role, so your makeup came to nothing.')
        return
    n.appear(t, rid, n.n + 1)
    n.st(t).marks["framed_until"] = n.n + 1
    n.note(a.actor, f"You made {t.name} up as the {ROLES[rid].label} for tonight and tomorrow.")


def _hypnotize(n: Night, a: Act) -> None:
    t = a.targets[0]
    n.state.memory.setdefault("vote_copy", {})[t.id] = a.actor.id
    n.note(a.actor, f"{t.name} is hypnotized: tomorrow their vote will copy yours.")


def _mimic(n: Night, a: Act) -> None:
    rid = n.seen_role(a.targets[0])
    n.appear(a.actor, rid)
    n.note(a.actor, f"Tonight investigators see you as the {ROLES[rid].label}.")


def _obscure(n: Night, a: Act) -> None:
    n.shrouded[a.targets[0].id].add(VILLAGE)


wolf_role(id="framer", label="Framer", emoji="🖼️", classes=("manipulation",), weight=-4,
          summary="Frames a non-wolf so investigators see them as a Wolf tonight.",
          card="Each night you may visit one non-wolf and frame them: for the rest of that "
               "night, role checks on them show Wolf and side checks show the Werewolf side.",
          actions=(act("frame", "manipulation", "Visit a non-wolf; they look like a Wolf "
                       "tonight.", _frame, pool="non_wolves"),))
wolf_role(id="makeup_artist", label="Makeup Artist", emoji="💄", classes=("manipulation",),
          weight=-4, summary="Disguises a non-wolf as any role for two nights.",
          card="Each night you may visit one non-wolf and plant evidence: name any role "
               "(ideally one in this game) as the option. Investigators who check them see "
               "that role tonight and tomorrow night.",
          actions=(act("disguise", "manipulation", "Visit a non-wolf; option = the role they "
                       "should appear as.", _disguise, pool="non_wolves", options=("*",)),))
wolf_role(id="hypnotist", label="Hypnotist", emoji="🌀", classes=("manipulation",), weight=-4,
          summary="Hypnotizes a non-wolf so their next day vote copies the Hypnotist's.",
          card="Each night you may visit one non-wolf and hypnotize them: in the next day's "
               "vote their vote automatically becomes the same as yours (only while you are "
               "alive). They wake up dizzy after voting.",
          actions=(act("hypnotize", "manipulation", "Visit a non-wolf; tomorrow their vote "
                       "copies yours.", _hypnotize, pool="non_wolves"),))
wolf_role(id="mimic", label="Mimic", emoji="🪞", classes=("manipulation",), weight=-3,
          summary="Appears to investigators as the role of a player of their choosing.",
          card="Each night you may choose one player (you don't move): tonight, investigators "
               "who check you see that player's role (as it appears) instead of yours.",
          actions=(act("mimic", "manipulation", "Choose a player; tonight you appear as their "
                       "role.", _mimic, movement="none"),))
wolf_role(id="obscurist", label="Obscurist", emoji="🌫️", classes=("protection",), weight=-4,
          summary="Shrouds a home so Village information roles learn nothing there.",
          card="Each night you may travel to any home, a fellow wolf's included. Tonight, "
               "Village-side information roles targeting that home learn nothing. Like all "
               "protection, you can't pick the same home two nights in a row.",
          actions=(act("obscure", "protection", "Travel to a home; Village investigators "
                       "learn nothing there tonight.", _obscure, movement="travel",
                       pool="anyone"),))
