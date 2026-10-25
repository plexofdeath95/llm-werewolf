"""Werewolf roles, teams and the role distribution for a given table size."""
import random

from aiplays.core.role import Role
from aiplays.core.state import GameState

WOLVES, VILLAGE = "wolves", "village"

ROLES: dict[str, Role] = {
    "werewolf": Role("werewolf", "Werewolf", WOLVES, "🐺"),
    "seer": Role("seer", "Seer", VILLAGE, "🔮"),
    "doctor": Role("doctor", "Doctor", VILLAGE, "🩺"),
    "villager": Role("villager", "Villager", VILLAGE, "🧑‍🌾"),
}


def distribution(n: int) -> list[str]:
    """Wolves = n//4 (min 1); a Seer from 5 players, a Doctor from 6; the rest villagers."""
    roles = ["werewolf"] * max(1, n // 4)
    if n >= 5:
        roles.append("seer")
    if n >= 6:
        roles.append("doctor")
    return roles + ["villager"] * (n - len(roles))


def assign(state: GameState, rng: random.Random) -> None:
    roles = distribution(len(state.players))
    rng.shuffle(roles)
    for p, r in zip(state.players, roles):
        p.role, p.team = r, ROLES[r].team


def summary(n: int) -> str:
    """e.g. '2 Werewolves, 1 Seer, 1 Doctor, 4 Villagers'."""
    counts: dict[str, int] = {}
    for r in distribution(n):
        counts[r] = counts.get(r, 0) + 1
    return ", ".join(f"{c} {ROLES[r].label}{'s' if c > 1 else ''}" for r, c in counts.items())
