"""Parallel-react discussion: everyone reacts at once, the scheduler gives one the floor.

Every participant is heard at least once (unheard voices are favoured, and the last slots
of the time limit are reserved for anyone still silent), then the discussion ends.
"""
from aiplays.agents.schemas import Reaction, Speech
from aiplays.core import scheduler
from aiplays.core.events import Kind
from aiplays.core.moderator import Moderator
from aiplays.core.scheduler import Bid
from aiplays.core.state import Player


class Discussion:
    def __init__(self, mod: Moderator, participants: list[Player], *, max_msgs: int,
                 channel: str = "public", visible_to: list[str] | None = None):
        self.mod, self.people, self.channel, self.visible_to = mod, participants, channel, visible_to
        self.max = max_msgs
        self.recent: list[str] = []
        self.spoken: dict[str, int] = {}
        self.named: set[str] = set()

    async def run(self) -> int:
        silence, warned = 0, False
        while len(self.recent) < self.max:
            unheard, left = self._unheard(), self.max - len(self.recent)
            if unheard and left <= len(unheard):
                await self._nudge(unheard)  # last slots are reserved for silent voices
                continue
            if not warned and left == len(self._alive()) and self.max > left:
                warned = True
                await self._say_mod("Last round before the vote: make your final points.")
            best = scheduler.pick(await self._react_round(), self.recent, self.named,
                                  self.spoken, self.mod.config.talk, self.mod.rng)
            if best:
                silence = 0
                await self._say(*best)
            elif unheard:
                await self._nudge(unheard)
            elif (silence := silence + 1) >= 2:
                return len(self.recent)
            else:
                await self._say_mod("Anyone else want to speak before we move on?")
        await self._say_mod("Time's up! The discussion is over.")
        return len(self.recent)

    def _alive(self) -> list[Player]:
        return [p for p in self.people if p.alive]

    def _unheard(self) -> list[Player]:
        return [p for p in self._alive() if not self.spoken.get(p.id)]

    async def _say_mod(self, text: str) -> None:
        await self.mod.announce(text, visible_to=self.visible_to, channel=self.channel)

    async def _react_round(self) -> list[Bid]:
        bids: list[Bid] = []

        async def on_reply(p: Player, r: Reaction) -> None:
            ev = await self.mod.emit(Kind.REACTION, r.message, actor=p.id, visible_to=[p.id],
                                     data={**r.model_dump(), "channel": self.channel})
            bids.append(Bid(p.id, r.urgency, r.message, ev.seq))

        question = self.mod.prompt("react", channel=self.channel, count=len(self.recent) + 1,
                                   max=self.max)
        await self.mod.ask_many(self._alive(), lambda p: question, Reaction, on_reply=on_reply,
                                fallback=lambda p: Reaction())
        return bids

    async def _say(self, bid: Bid, score: float) -> None:
        interrupt = scheduler.is_interrupt(bid, self.named, self.mod.config.talk)
        await self._speech(bid.pid, bid.message, interrupt=interrupt, urgency=bid.urgency,
                           score=score, reaction_seq=bid.seq)

    async def _nudge(self, candidates: list[Player]) -> None:
        quiet = self.mod.rng.choice(candidates)
        await self._say_mod(f"{quiet.name}, we haven't heard from you yet. What do you think?")
        s = await self.mod.ask(quiet, self.mod.prompt("nudge", channel=self.channel), Speech,
                               fallback=Speech(message="I have nothing to add right now."))
        await self._speech(quiet.id, s.message, nudged=True, thought=s.thought)

    async def _speech(self, pid: str, text: str, **data) -> None:
        await self.mod.emit(Kind.SPEECH, text, actor=pid, visible_to=self.visible_to, data={
            "channel": self.channel, "reply_to": self.recent[-1] if self.recent else None,
            "count": len(self.recent) + 1, "max": self.max, **data})
        self.recent.append(pid)
        self.spoken[pid] = self.spoken.get(pid, 0) + 1
        self.named = self.mod.state.mentioned(text) - {pid}
