"""Parallel-react discussion: everyone reacts at once, the scheduler gives one the floor."""
from aiplays.agents.schemas import Reaction, Speech
from aiplays.core import scheduler
from aiplays.core.events import Kind
from aiplays.core.moderator import Moderator
from aiplays.core.scheduler import Bid
from aiplays.core.state import Player


class Discussion:
    def __init__(self, mod: Moderator, participants: list[Player], *, channel: str = "public",
                 visible_to: list[str] | None = None, min_msgs: int, max_msgs: int):
        self.mod, self.people, self.channel, self.visible_to = mod, participants, channel, visible_to
        self.min, self.max = min_msgs, max_msgs
        self.recent: list[str] = []
        self.spoken: dict[str, int] = {}
        self.named: set[str] = set()

    async def run(self) -> int:
        silence = 0
        while len(self.recent) < self.max:
            bids = await self._react_round()
            best = scheduler.pick(bids, self.recent, self.named, set(self.spoken),
                                  self.mod.config.talk, self.mod.rng)
            if best:
                silence = 0
                await self._say(*best)
            elif len(self.recent) < self.min:
                await self._nudge()
            elif (silence := silence + 1) >= 2:
                break
            else:
                await self.mod.announce("Anyone else want to speak before we move on?",
                                        visible_to=self.visible_to, channel=self.channel)
        return len(self.recent)

    async def _react_round(self) -> list[Bid]:
        bids: list[Bid] = []
        alive = [p for p in self.people if p.alive]

        async def on_reply(p: Player, r: Reaction) -> None:
            ev = await self.mod.emit(Kind.REACTION, r.message, actor=p.id, visible_to=[p.id],
                                     data={**r.model_dump(), "channel": self.channel})
            bids.append(Bid(p.id, r.urgency, r.message, ev.seq))

        question = self.mod.prompt("react", channel=self.channel, count=len(self.recent) + 1,
                                   max=self.max)
        await self.mod.ask_many(alive, lambda p: question, Reaction, on_reply=on_reply,
                                fallback=lambda p: Reaction())
        return bids

    async def _say(self, bid: Bid, score: float) -> None:
        cfg, st = self.mod.config.talk, self.mod.state
        interrupt = scheduler.is_interrupt(bid, self.named, cfg)
        await self.mod.emit(Kind.SPEECH, bid.message, actor=bid.pid, visible_to=self.visible_to,
                            data={"channel": self.channel, "interrupt": interrupt,
                                  "urgency": bid.urgency, "score": score,
                                  "reply_to": self.recent[-1] if self.recent else None,
                                  "reaction_seq": bid.seq})
        self._record(bid.pid)
        self.named = st.mentioned(bid.message) - {bid.pid}

    async def _nudge(self) -> None:
        alive = [p for p in self.people if p.alive]
        quiet = min(alive, key=lambda p: (self.spoken.get(p.id, 0), self.mod.rng.random()))
        await self.mod.announce(f"{quiet.name}, you've been quiet. Anything to share?",
                                visible_to=self.visible_to, channel=self.channel)
        s = await self.mod.ask(quiet, self.mod.prompt("nudge", channel=self.channel), Speech,
                               fallback=Speech(message="I have nothing to add right now."))
        await self.mod.emit(Kind.SPEECH, s.message, actor=quiet.id, visible_to=self.visible_to,
                            data={"channel": self.channel, "nudged": True, "thought": s.thought})
        self._record(quiet.id)
        self.named = self.mod.state.mentioned(s.message) - {quiet.id}

    def _record(self, pid: str) -> None:
        self.recent.append(pid)
        self.spoken[pid] = self.spoken.get(pid, 0) + 1
