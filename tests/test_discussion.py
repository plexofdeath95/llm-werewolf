"""Discussion: everyone is heard at least once, quiet voices are called on, time limit holds."""
import random

from aiplays.agents.base import Reply
from aiplays.agents.schemas import Reaction, Speech
from aiplays.core.bus import EventBus
from aiplays.core.config import GameConfig, SeatConfig
from aiplays.core.conversation import Discussion
from aiplays.core.events import Kind
from aiplays.core.gate import Budget, Gate
from aiplays.core.mode import get_mode
from aiplays.core.moderator import Moderator
from rolekit import game


class Scripted:
    """Always the same urgency; 0 means 'never volunteers'."""

    def __init__(self, urgency: int):
        self.urgency = urgency

    async def ask(self, prompt, schema, **kw):
        if schema is Reaction:
            return Reply(Reaction(urgency=self.urgency, message="I think..." if self.urgency else ""))
        return Reply(Speech(message="Fine, here's my take."))


def _mod(urgencies: list[int]) -> Moderator:
    st = game(*(["villager"] * len(urgencies)))
    cfg = GameConfig(seats=[SeatConfig(model_id="m")] * len(urgencies), fake=True)
    return Moderator(state=st, mode=get_mode("werewolf"), config=cfg,
                     agents={p.id: Scripted(u) for p, u in zip(st.players, urgencies)},
                     bus=EventBus("g"), gate=Gate(), budget=Budget(10))


async def test_everyone_heard_and_limit_respected():
    mod = _mod([10, 9, 0, 0, 5])  # two loudmouths, two mutes, one moderate
    sent = await Discussion(mod, mod.state.players, max_msgs=8).run()
    speakers = [e.actor for e in mod.bus.history if e.kind == Kind.SPEECH]
    assert sent == len(speakers) == 8
    assert set(speakers) == {p.id for p in mod.state.players}
    nudged = [e.actor for e in mod.bus.history if e.kind == Kind.SPEECH and e.data.get("nudged")]
    assert {"p2", "p3"} <= set(nudged)
    assert any("Time's up" in e.text for e in mod.bus.history if e.kind == Kind.MODERATOR)


async def test_quiet_table_ends_once_all_heard():
    mod = _mod([0, 0, 0])
    mod.rng = random.Random(1)
    sent = await Discussion(mod, mod.state.players, max_msgs=9).run()
    assert sent == 3  # each called on once, then two silent rounds end it early
