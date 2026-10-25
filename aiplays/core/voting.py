"""Simultaneous choices (votes, kills, inspections, protections) and tallying."""
import random
from collections import Counter

from aiplays.agents.schemas import Choice
from aiplays.core.events import Kind
from aiplays.core.moderator import Moderator
from aiplays.core.state import Player


async def choose(mod: Moderator, voters: list[Player], candidates: list[Player], prompt: str, *,
                 verb: str = "votes for", channel: str = "public",
                 visible_to: list[str] | None = None, allow_self: bool = False,
                 **prompt_values: object) -> dict[str, str | None]:
    """Everyone picks at once; picks are revealed together. Returns voter id -> target id."""
    def options(p: Player) -> list[Player]:
        return [c for c in candidates if allow_self or c is not p]

    picks = await mod.ask_many(
        voters, lambda p: mod.prompt(prompt, options=mod.state.names(options(p)), **prompt_values),
        Choice, deep=True, choices=lambda p: [c.name for c in options(p)],
        fallback=lambda p: Choice(target="nobody", reason="(no answer)"))
    result: dict[str, str | None] = {}
    for p in voters:
        c = picks[p.id]
        target = mod.state.by_name(c.target, options(p))
        result[p.id] = target.id if target else None
        await mod.emit(Kind.VOTE, c.reason, actor=p.id, target=result[p.id],
                       visible_to=visible_to, data={"verb": verb, "channel": channel, "thought": c.thought,
                             "raw_target": c.target})
    return result


def tally(votes: dict[str, str | None]) -> Counter:
    return Counter(t for t in votes.values() if t)


def plurality(votes: dict[str, str | None], rng: random.Random | None = None) -> str | None:
    """Most-voted target. Ties: random pick if rng given, else None (no elimination)."""
    return leader(tally(votes), rng)


def leader(counts: Counter, rng: random.Random | None = None) -> str | None:
    if not counts:
        return None
    top = max(counts.values())
    leaders = sorted(t for t, n in counts.items() if n == top)
    if len(leaders) == 1:
        return leaders[0]
    return rng.choice(leaders) if rng else None
