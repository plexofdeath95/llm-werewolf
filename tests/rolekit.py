"""Helpers for role unit tests: tiny games, hand-made acts, one-night resolution."""
import random

from aiplays.core.state import GameState, Player
from aiplays.modes.werewolf.night import options
from aiplays.modes.werewolf.night.context import Act, Night
from aiplays.modes.werewolf.night.resolve import resolve
from aiplays.modes.werewolf.roles import ROLES

NAMES = ["Ann", "Ben", "Cat", "Dan", "Eve", "Fay", "Gus", "Hal", "Ivy", "Jon", "Kim", "Lou"]


def game(*roles: str, seed: int = 1) -> GameState:
    """Players p0..pN with the given roles (setup hooks run, like a real deal)."""
    ps = [Player(f"p{i}", NAMES[i], i, "m", role=r, team=ROLES[r].team)
          for i, r in enumerate(roles)]
    st = GameState("g", "werewolf", seed, ps)
    rng = random.Random(seed)
    for p in ps:
        if hook := ROLES[p.role].hook("on_start"):
            hook(st, p, rng)
    return st


def night(state: GameState, n: int = 1) -> Night:
    return Night(state, n, random.Random(0))


def act(n: Night, actor: Player, action: str, *targets: Player, option: str = "") -> Act:
    """Queue an action exactly as collect() would (incl. uses/cooldown bookkeeping)."""
    a = next(x for x in options.available(n.state, actor, n.n) if x.name == action)
    made = Act(actor, a, list(targets), option)
    n.acts.append(made)
    options.record(n.state, actor, a, made.targets, n.n)
    return made


def run(n: Night) -> Night:
    resolve(n)
    return n


def notes(n: Night, p: Player) -> str:
    return " | ".join(n.notes.get(p.id, []))
