"""Dawn (reveal the night's victim) and Day (discussion, simultaneous vote, elimination)."""
from aiplays.agents.schemas import Speech
from aiplays.core import scheduler
from aiplays.core.conversation import Discussion
from aiplays.core.events import Kind
from aiplays.core.moderator import Moderator
from aiplays.core.state import Player
from aiplays.core.voting import choose, plurality, tally


async def dawn(mod: Moderator, victim: Player | None) -> None:
    await mod.set_phase("dawn", f"Day {mod.state.round}")
    if victim:
        await mod.kill(victim, "killed by werewolves",
                       f"Dawn breaks. {victim.name} was found dead.", narrate=True)
    else:
        await mod.announce("Dawn breaks. Miraculously, nobody died last night.", narrate=True)


async def day(mod: Moderator) -> None:
    st = mod.state
    alive = st.alive()
    await mod.set_phase("discussion", f"Day {st.round}: discussion")
    await mod.announce(f"Discuss: who among you is a werewolf? Still alive: {st.names(alive)}.")
    lo, hi = scheduler.limits(len(alive), mod.config.talk)
    await Discussion(mod, alive, min_msgs=lo, max_msgs=hi).run()

    await mod.set_phase("vote", f"Day {st.round}: vote")
    await mod.announce("Discussion is over. Everyone votes at the same time.")
    votes = await choose(mod, alive, alive, "day_vote", verb="votes to eliminate")
    counts = tally(votes)
    out_id = plurality(votes)
    summary = ", ".join(f"{st.by_id(t).name}: {n}" for t, n in counts.most_common()) or "no votes"
    await mod.emit(Kind.VOTE_RESULT, f"Votes: {summary}.", target=out_id,
                   data={"counts": dict(counts), "eliminated": out_id})
    if not out_id:
        await mod.announce("The vote is tied. Nobody is eliminated today.")
        return
    await _eliminate(mod, st.by_id(out_id))


async def _eliminate(mod: Moderator, p: Player) -> None:
    await mod.announce(f"{p.name}, the village has chosen you. Any last words?")
    words = await mod.ask(p, mod.prompt("last_words"), Speech, deep=True,
                          fallback=Speech(message="..."))
    await mod.emit(Kind.SPEECH, words.message, actor=p.id,
                   data={"channel": "last words", "thought": words.thought})
    await mod.kill(p, "eliminated by vote", f"{p.name} is eliminated by the village.",
                   narrate=True)
