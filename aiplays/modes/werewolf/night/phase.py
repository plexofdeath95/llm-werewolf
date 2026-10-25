"""One full night: start-of-night hooks, private chats, parallel actions, resolution."""
from aiplays.core.moderator import Moderator
from aiplays.modes.werewolf.night.chats import night_chats
from aiplays.modes.werewolf.night.collect import collect
from aiplays.modes.werewolf.night.context import Night
from aiplays.modes.werewolf.night.resolve import resolve
from aiplays.modes.werewolf.roles.base import ROLES
from aiplays.modes.werewolf.status import role_of


async def night(mod: Moderator) -> Night:
    st = mod.state
    await mod.set_phase("night", f"Night {st.round}")
    await mod.announce("Night falls. Everyone goes home and bolts the door.", narrate=True)
    for p in st.alive():
        hook = ROLES[role_of(st, p)].hook("before_night")
        if hook:
            await hook(mod, p)
    await night_chats(mod)
    n = Night(st, st.round, mod.rng)
    await collect(mod, n)
    resolve(n)
    for a in n.acts:  # async follow-ups that need the models (e.g. asking the dead)
        if a.action.late and not a.blocked and not a.failed:
            await a.action.late(mod, n, a)
    for p in st.alive():
        hook = ROLES[role_of(st, p)].hook("after_night")
        if hook and p.id not in n.deaths:
            hook(n, p)
    st.memory["last_night"] = n
    return n
