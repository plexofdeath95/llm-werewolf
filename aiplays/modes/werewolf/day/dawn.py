"""Dawn: deliver private night results, reveal the dead, run death triggers."""
from aiplays.core.events import Kind
from aiplays.core.moderator import Moderator
from aiplays.core.state import Player
from aiplays.modes.werewolf.night.context import Night
from aiplays.modes.werewolf.roles.base import ROLES
from aiplays.modes.werewolf.status import role_of


async def dawn(mod: Moderator, n: Night) -> None:
    st = mod.state
    await mod.set_phase("dawn", f"Day {st.round}")
    for pid, notes in n.notes.items():
        for text in notes:
            await mod.emit(Kind.ACTION, text, actor=pid, visible_to=[pid],
                           data={"action": "result", "channel": "night"})
    dead = [st.by_id(pid) for pid in n.deaths]
    if not dead:
        await mod.announce("The sun rises. Miraculously, nobody died last night.", narrate=True)
    for p in dead:
        await mod.kill(p, n.deaths[p.id], f"{p.name} was found dead this morning.")
    for line in n.public:
        await mod.announce(line)
    if dead:
        await mod.narrate(f"Found dead at dawn: {st.names(dead)}.")
    await deaths_triggered(mod, dead)


async def deaths_triggered(mod: Moderator, dead: list[Player]) -> None:
    """on_death hooks; they may kill more players, whose hooks then run too."""
    queue = list(dead)
    while queue:
        p = queue.pop(0)
        hook = ROLES[role_of(mod.state, p)].hook("on_death")
        if not hook:
            continue
        before = {q.id for q in mod.state.players if not q.alive}
        await hook(mod, p)
        queue += [q for q in mod.state.players if not q.alive and q.id not in before]
