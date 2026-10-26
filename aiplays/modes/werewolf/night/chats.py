"""Private night channels: wolf den, masons, lovers, creed, cult... (reuses Discussion)."""
from aiplays.core.conversation import Discussion
from aiplays.core.moderator import Moderator
from aiplays.core.state import Player
from aiplays.modes.werewolf.roles.base import ROLES
from aiplays.modes.werewolf.status import role_of, status


def channels(mod: Moderator) -> dict[str, list[Player]]:
    """channel -> living members. Roles declare chats; flags (lovers, cult) can add more."""
    st, out = mod.state, {}
    for p in st.alive():
        extra = tuple(status(st, p).marks.get("chats", ()))
        for ch in ROLES[role_of(st, p)].chats + extra:
            out.setdefault(ch, []).append(p)
    return out


async def night_chats(mod: Moderator) -> None:
    for ch, members in channels(mod).items():
        ids = [m.id for m in members]
        if len(members) < 2:  # say so, or a solo den looks like a skipped phase
            await mod.announce(f"[{ch}] {members[0].name} is alone tonight: nobody to plot with.",
                               visible_to=ids, channel=ch)
            continue
        await mod.announce(f"[{ch}] {mod.state.names(members)}: you may talk privately now.",
                           visible_to=ids, channel=ch)
        n = len(members)
        await Discussion(mod, members, channel=ch, visible_to=ids, max_msgs=2 * n + 1).run()
