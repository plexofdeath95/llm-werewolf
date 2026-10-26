"""Default decks: faction sizes by table size, then a random but sensible role mix."""
import random

from aiplays.core.state import GameState
from aiplays.modes.werewolf.roles.base import NEUTRAL, ROLES, VILLAGE, WOLVES

CORE_VILLAGE = ("seer", "doctor")
# Sum of role weights (+ helps the village, - the wolves). Unbalanced random decks let the
# village win by day 2, so mixed decks pick the closest of many candidates to this target:
# a slight village edge, since the wolves already know each other.
TARGET_BALANCE = 1
CANDIDATES = 300


def sizes(n: int) -> tuple[int, int, int]:
    """(village, wolves, neutrals) for n players."""
    wolves = max(1, int(n * 0.27 + 0.5))  # ~1 in 4; half-up, not round()'s banker's rounding
    neutrals = 0 if n < 7 else 1 if n < 11 else 2
    return n - wolves - neutrals, wolves, neutrals


def _pool(team: str, exclude: tuple[str, ...] = ()) -> list[str]:
    return sorted(r.id for r in ROLES.values()
                  if r.team == team and r.in_deck and r.group == 1 and r.id not in exclude)


def default_deck(n: int, rng: random.Random | None = None, style: str = "mixed") -> list[str]:
    rng = rng or random.Random()
    village, wolves, neutrals = sizes(n)
    neutrals_ok = min(neutrals, len(_pool(NEUTRAL)))  # small pools: give seats to the village
    village, neutrals = village + neutrals - neutrals_ok, neutrals_ok
    if style == "classic":
        core = list(CORE_VILLAGE[: max(0, village - 1)])
        return ["alpha"] + ["wolf"] * (wolves - 1) + core + ["villager"] * (village - len(core)) \
            + rng.sample(_pool(NEUTRAL), neutrals)
    tries = [_mixed(village, wolves, neutrals, rng) for _ in range(CANDIDATES)]
    return min(tries, key=lambda d: abs(balance(d) - TARGET_BALANCE))


def _mixed(village: int, wolves: int, neutrals: int, rng: random.Random) -> list[str]:
    core = list(CORE_VILLAGE[: 1 if village < 5 else 2])  # Seer + Doctor swamp tiny tables
    plain = rng.randint(village // 4, max(village // 4, (village - len(core)) // 2))
    extra = rng.sample(_pool(VILLAGE, CORE_VILLAGE + ("villager",)), village - len(core) - plain)
    return (["alpha"] + rng.sample(_pool(WOLVES, ("alpha",)), wolves - 1)
            + core + extra + ["villager"] * plain + rng.sample(_pool(NEUTRAL), neutrals))


def balance(deck: list[str]) -> int:
    return sum(ROLES[r].weight for r in deck)


def assign(state: GameState, rng: random.Random, deck: list[str] | None) -> None:
    roles = list(deck) if deck else default_deck(len(state.players), rng)
    rng.shuffle(roles)
    for p, r in zip(state.players, roles):
        p.role, p.team = r, ROLES[r].team
    for p in state.players:  # role setup: executioner targets, assassin lists, ...
        hook = ROLES[p.role].hook("on_start")
        if hook:
            hook(state, p, rng)


def summary(roles: list[str]) -> str:
    counts: dict[str, int] = {}
    for r in roles:
        counts[r] = counts.get(r, 0) + 1
    return ", ".join(f"{c}x {ROLES[r].label}" if c > 1 else ROLES[r].label
                     for r, c in counts.items())
