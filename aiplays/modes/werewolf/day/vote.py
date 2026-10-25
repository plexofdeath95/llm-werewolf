"""Day vote with role modifiers: hypnosis (vote copy) and the Mayor's ballot stuffing."""
from collections import Counter

from aiplays.core.events import Kind
from aiplays.core.moderator import Moderator
from aiplays.core.voting import choose, leader, tally


async def day_vote(mod: Moderator) -> tuple[dict[str, str | None], str | None]:
    st = mod.state
    alive = st.alive()
    votes = await choose(mod, alive, alive, "day_vote", verb="votes to eliminate")
    await _hypnosis(mod, votes)
    counts = tally(votes)
    out = leader(counts)
    for pid, extra in st.memory.pop("vote_bonus", {}).items():
        if not votes.get(pid) or not st.by_id(pid).alive:
            continue
        trial = Counter(counts)
        trial[votes[pid]] += extra
        if leader(trial) != out:  # stuffing only counts when it changes the outcome
            counts, out = trial, leader(trial)
            await mod.announce(f"{st.by_id(pid).name} stuffs the ballot box: +{extra} votes "
                               f"for {st.by_id(votes[pid]).name}!")
    summary = ", ".join(f"{st.by_id(t).name}: {c}" for t, c in counts.most_common()) or "no votes"
    await mod.emit(Kind.VOTE_RESULT, f"Votes: {summary}.", target=out,
                   data={"counts": dict(counts), "eliminated": out})
    return votes, out


async def _hypnosis(mod: Moderator, votes: dict[str, str | None]) -> None:
    st = mod.state
    for victim, hypnotist in st.memory.pop("vote_copy", {}).items():
        if victim in votes and hypnotist in votes and st.by_id(hypnotist).alive:
            votes[victim] = votes[hypnotist]
            await mod.emit(Kind.ACTION, "You wake up feeling dizzy after voting.", actor=victim,
                           visible_to=[victim], data={"action": "result", "channel": "day"})
