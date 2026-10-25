"""Default decks: faction sizes by table size, then a random but sensible role mix."""
import random

from aiplays.core.state import GameState
from aiplays.modes.werewolf.roles.base import NEUTRAL, ROLES, VILLAGE, WOLVES

CORE_VILLAGE = ("seer", "doctor")


def sizes(n: int) -> tuple[int, int, int]:
    """(village, wolves, neutrals) for n players."""
    wolves = max(1, round(n / 4))
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
    core = list(CORE_VILLAGE[:village])
    plain = village // 4  # keep a few vanilla villagers for texture
    extra = rng.sample(_pool(VILLAGE, CORE_VILLAGE + ("villager",)), village - len(core) - plain)
    return (["alpha"] + rng.sample(_pool(WOLVES, ("alpha",)), wolves - 1)
            + core + extra + ["villager"] * plain + rng.sample(_pool(NEUTRAL), neutrals))


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
