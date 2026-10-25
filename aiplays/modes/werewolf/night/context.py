"""Night: one night's acts and resolution state (visits, blocks, protection, attacks)."""
from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass

from aiplays.core.state import GameState, Player
from aiplays.modes.werewolf.roles.base import ROLES, ActionDef, RoleDef
from aiplays.modes.werewolf.status import Status, role_of, status


@dataclass
class Act:
    actor: Player
    action: ActionDef
    targets: list[Player]
    option: str = ""
    blocked: bool = False
    failed: bool = False  # never arrived: target hidden, jailed, nightmare...

    @property
    def moves(self) -> bool:
        return self.action.movement != "none"


@dataclass
class Attack:
    target: Player
    by: Player | None
    cause: str
    unstoppable: bool = False
    home: str = ""  # whose home was hit (differs from target for linked occupants)


class Night:
    def __init__(self, state: GameState, n: int, rng: random.Random):
        self.state, self.n, self.rng = state, n, rng
        self.acts: list[Act] = []
        self.jailed: set[str] = set()
        self.hidden: set[str] = set()
        self.resident: dict[str, str] = {}   # house owner -> who sleeps there (transporter)
        self.redirect: dict[str, str] = {}   # actor -> forced destination (angler)
        self.linked: dict[str, list[Player]] = defaultdict(list)  # home -> extra occupants
        self.visits: dict[str, list[Act]] = defaultdict(list)  # house owner -> arriving acts
        self.left_home: set[str] = set()
        self.heals: dict[str, list[Player]] = defaultdict(list)
        self.guards: dict[str, list[Player]] = defaultdict(list)
        self.martyrs: dict[str, list[Player]] = defaultdict(list)
        self.shrouded: dict[str, set[str]] = defaultdict(set)  # house -> teams denied info
        self.attacks: list[Attack] = []
        self.notes: dict[str, list[str]] = defaultdict(list)
        self.public: list[str] = []
        self.deaths: dict[str, str] = {}

    # --- lookups -----------------------------------------------------------------
    def st(self, p: Player) -> Status:
        return status(self.state, p)

    def role(self, p: Player) -> RoleDef:
        return ROLES[role_of(self.state, p)]

    def team(self, p: Player) -> str:
        return "cult" if "cult" in self.st(p).flags else self.role(p).team

    def visitors(self, p: Player) -> list[Act]:
        return [a for a in self.visits.get(p.id, []) if not a.failed]

    def acts_by(self, p: Player) -> list[Act]:
        return [a for a in self.acts if a.actor is p]

    # --- effects -----------------------------------------------------------------
    def note(self, p: Player, text: str) -> None:
        self.notes[p.id].append(text)

    def attack(self, target: Player, by: Player | None, cause: str,
               unstoppable: bool = False) -> None:
        """Attack target and anyone sharing their home tonight (lovers, sleepwalkers)."""
        for p in [target, *self.linked.get(target.id, [])]:
            self.attacks.append(Attack(p, by, cause, unstoppable, home=target.id))

    def block(self, p: Player) -> None:
        for a in self.acts_by(p):
            if not a.action.unblockable:
                a.blocked = True

    def appear(self, p: Player, role_id: str, until: int | None = None) -> None:
        """Investigators see p as role_id until night `until` (inclusive)."""
        self.st(p).marks["appear"] = (until or self.n, role_id)

    def seen_role(self, p: Player) -> str:
        until, role_id = self.st(p).marks.get("appear", (0, ""))
        return role_id if until >= self.n else role_of(self.state, p)

    def seen_team(self, p: Player) -> str:
        return ROLES[self.seen_role(p)].team

    def can_learn(self, a: Act, target: Player) -> bool:
        """Info fails at a shrouded house (Smokescreener / Obscurist)."""
        return self.role(a.actor).team not in self.shrouded.get(target.id, set())
