"""Day: discussion, day abilities, vote, and elimination (with lynch triggers)."""
import asyncio

from aiplays.agents.schemas import Speech
from aiplays.core import scheduler
from aiplays.core.conversation import Discussion
from aiplays.core.events import Kind
from aiplays.core.moderator import Moderator
from aiplays.core.state import Player
from aiplays.modes.werewolf.day.dawn import deaths_triggered
from aiplays.modes.werewolf.day.vote import day_vote
from aiplays.modes.werewolf.roles.base import ROLES
from aiplays.modes.werewolf.status import role_of


def _hook(mod: Moderator, p: Player, name: str):
    return ROLES[role_of(mod.state, p)].hook(name)


async def day(mod: Moderator) -> None:
    st = mod.state
    alive = st.alive()
    await mod.set_phase("discussion", f"Day {st.round}: discussion")
    limit = scheduler.limit(len(alive), mod.config.talk)
    await mod.announce(f"Discuss: who should be eliminated? Still alive: {st.names(alive)}. "
                       f"You have up to {limit} messages before the vote; everyone will be heard.")
    await Discussion(mod, alive, max_msgs=limit).run()

    await mod.set_phase("vote", f"Day {st.round}: vote")
    await asyncio.gather(*(h(mod, p) for p in alive if (h := _hook(mod, p, "day_action"))))
    await mod.announce("Discussion is over. Everyone votes at the same time.")
    votes, out = await day_vote(mod)
    if not out:
        await mod.announce("No clear majority. Nobody is eliminated today.")
        return
    voters = [st.by_id(v) for v, t in votes.items() if t == out]
    await eliminate(mod, st.by_id(out), voters)


async def eliminate(mod: Moderator, p: Player, voters: list[Player]) -> None:
    st = mod.state
    mayor = st.memory.pop("pardon", None)
    if mayor and st.by_id(mayor).alive:
        await mod.announce(f"{st.by_id(mayor).name} uses the Mayor's pardon: {p.name} walks free!")
        return
    hook = _hook(mod, p, "on_lynched")
    if hook and await hook(mod, p, voters):
        return  # e.g. the Knight survives on a spare life
    await mod.announce(f"{p.name}, the village has chosen you. Any last words?")
    words = await mod.ask(p, mod.prompt("last_words"), Speech, deep=True,
                          fallback=Speech(message="..."))
    await mod.emit(Kind.SPEECH, words.message, actor=p.id,
                   data={"channel": "last words", "thought": words.thought})
    await mod.kill(p, "eliminated by vote", f"{p.name} is eliminated by the village.",
                   narrate=True)
    st.memory.setdefault("lynched", []).append(p.id)
    for q in st.alive():
        if h := _hook(mod, q, "after_lynch"):
            await h(mod, q, p, voters)
    await deaths_triggered(mod, [p])
