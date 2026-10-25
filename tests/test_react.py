"""React rounds close without the slowest model; its late bid joins a later round."""
import asyncio

from aiplays.agents.base import Reply
from aiplays.agents.schemas import Reaction
from aiplays.core.bus import EventBus
from aiplays.core.config import GameConfig, SeatConfig, TalkConfig
from aiplays.core.gate import Budget, Gate
from aiplays.core.mode import get_mode
from aiplays.core.moderator import Moderator
from aiplays.core.react import Reactions
from rolekit import game


class Timed:
    def __init__(self, delay: float, claim: str = ""):
        self.delay, self.claim, self.calls = delay, claim, 0

    async def ask(self, prompt, schema, **kw):
        self.calls += 1
        await asyncio.sleep(self.delay)
        return Reply(Reaction(urgency=7, message="hi", suspect="Ann", claim=self.claim))


def _mod(delays: list[float]) -> Moderator:
    st = game(*(["villager"] * len(delays)))
    talk = TalkConfig(quorum=0.5, grace_s=0.05, round_cap_s=0.5)
    cfg = GameConfig(seats=[SeatConfig(model_id="m")] * len(delays), fake=True, talk=talk)
    agents = {p.id: Timed(d, "the Seer" if i == 0 else "") for i, (p, d) in
              enumerate(zip(st.players, delays))}
    return Moderator(state=st, mode=get_mode("werewolf"), config=cfg, agents=agents,
                     bus=EventBus("g"), gate=Gate(), budget=Budget(10))


async def test_round_closes_without_the_straggler_who_joins_later():
    mod = _mod([0.0, 0.0, 0.0, 1.0])
    r = Reactions(mod, "public")
    first = await asyncio.wait_for(r.round(mod.state.players, "q"), 0.8)
    assert {b.pid for b in first} == {"p0", "p1", "p2"} and "p3" in r.inflight
    await asyncio.sleep(1.1)
    second = await r.round(mod.state.players, "q")
    assert "p3" in {b.pid for b in second}
    assert mod.agents["p3"].calls == 1  # never re-asked while still thinking
    await r.close()


async def test_claims_and_suspects_are_resolved():
    mod = _mod([0.0, 0.0])
    r = Reactions(mod, "public")
    bids = {b.pid: b for b in await r.round(mod.state.players, "q")}
    assert bids["p0"].claim == "seer" and bids["p1"].claim == ""
    assert bids["p1"].suspect == "Ann"
    await r.close()


async def test_close_cancels_pending_reactions():
    mod = _mod([0.0, 0.0, 5.0])
    r = Reactions(mod, "public")
    await r.round(mod.state.players, "q")
    await asyncio.wait_for(r.close(), 1)
    assert not r.inflight
