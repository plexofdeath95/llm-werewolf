"""Night: wolf den chat + kill vote, then the Seer and Doctor act. Returns the victim."""
from aiplays.core.conversation import Discussion
from aiplays.core.events import Kind
from aiplays.core.moderator import Moderator
from aiplays.core.state import Player
from aiplays.core.voting import choose, plurality
from aiplays.modes.werewolf.roles import WOLVES

DEN = "wolf den"


async def night(mod: Moderator) -> Player | None:
    st = mod.state
    await mod.set_phase("night", f"Night {st.round}")
    await mod.announce("Night falls. Everyone closes their eyes.", narrate=True)
    target = await _wolves(mod)
    await _seer(mod)
    saved = await _doctor(mod)
    if target and saved and saved.id == target.id:
        return None
    return target


async def _wolves(mod: Moderator) -> Player | None:
    st = mod.state
    wolves = st.on_team(WOLVES)
    prey = [p for p in st.alive() if p.team != WOLVES]
    ids = [w.id for w in wolves]
    if not wolves or not prey:
        return None
    await mod.announce(f"Werewolves ({st.names(wolves)}), open your eyes and pick a victim.",
                       visible_to=ids, channel=DEN)
    if len(wolves) > 1:
        n = len(wolves)
        await Discussion(mod, wolves, channel=DEN, visible_to=ids,
                         min_msgs=n, max_msgs=2 * n + 1).run()
    votes = await choose(mod, wolves, prey, "night_kill", verb="wants to kill",
                         channel=DEN, visible_to=ids)
    victim_id = plurality(votes, mod.rng) or mod.rng.choice(prey).id
    victim = st.by_id(victim_id)
    await mod.emit(Kind.ACTION, f"The pack will kill {victim.name}.", target=victim.id,
                   visible_to=ids, data={"action": "kill", "channel": DEN})
    return victim


async def _seer(mod: Moderator) -> None:
    st = mod.state
    for seer in st.with_role("seer"):
        seen: list[str] = st.memory.setdefault("seer_checked", [])
        options = [p for p in st.alive(exclude=seer) if p.id not in seen] or st.alive(exclude=seer)
        pick = (await choose(mod, [seer], options, "night_seer", verb="inspects",
                             channel="seer", visible_to=[seer.id]))[seer.id]
        target = st.by_id(pick) if pick else mod.rng.choice(options)
        seen.append(target.id)
        verdict = "a WEREWOLF" if target.team == WOLVES else "NOT a werewolf"
        await mod.emit(Kind.ACTION, f"Your vision reveals: {target.name} is {verdict}.",
                       actor=seer.id, target=target.id, visible_to=[seer.id],
                       data={"action": "inspect", "result": target.team, "channel": "seer"})


async def _doctor(mod: Moderator) -> Player | None:
    st = mod.state
    saved = None
    for doc in st.with_role("doctor"):
        last = st.memory.get("doctor_last")
        options = [p for p in st.alive() if p.id != last]
        pick = (await choose(mod, [doc], options, "night_doctor", verb="protects",
                             channel="doctor", visible_to=[doc.id], allow_self=True))[doc.id]
        saved = st.by_id(pick) if pick else mod.rng.choice(options)
        st.memory["doctor_last"] = saved.id
        await mod.emit(Kind.ACTION, f"You protect {saved.name} tonight.", actor=doc.id,
                       target=saved.id, visible_to=[doc.id],
                       data={"action": "protect", "channel": "doctor"})
    return saved
