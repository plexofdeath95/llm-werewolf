"""React rounds that never wait for the slowest model.

Everyone not already thinking is asked at once. A round closes when a quorum of the table
has answered plus a short grace (or at a cap); stragglers keep thinking and their reaction
simply joins a later round, like a slow talker who chimes in a beat late.
"""
import asyncio
import math

from aiplays.agents.schemas import Reaction
from aiplays.core.events import Kind
from aiplays.core.moderator import Moderator
from aiplays.core.scheduler import Bid
from aiplays.core.state import Player


class Reactions:
    def __init__(self, mod: Moderator, channel: str):
        self.mod, self.channel = mod, channel
        self.inflight: dict[str, asyncio.Task] = {}

    async def round(self, players: list[Player], question: str) -> list[Bid]:
        for p in players:
            if p.id not in self.inflight:
                self.inflight[p.id] = asyncio.create_task(self._react(p, question))
        done = await self._window(set(self.inflight.values()))
        bids = []
        for pid, task in list(self.inflight.items()):
            if task in done:
                del self.inflight[pid]
                bids.append(task.result())
        return bids

    async def settle(self, pid: str) -> None:
        """Wait for a player's in-flight reaction before asking them anything else."""
        task = self.inflight.pop(pid, None)
        if task:
            await asyncio.gather(task, return_exceptions=True)

    async def close(self) -> None:
        """Discussion over: drop reactions still being thought about."""
        for task in self.inflight.values():
            task.cancel()
        await asyncio.gather(*self.inflight.values(), return_exceptions=True)
        self.inflight.clear()

    async def _react(self, p: Player, question: str) -> Bid:
        r = await self.mod.ask(p, question, Reaction, fallback=Reaction())
        st = self.mod.state
        suspect = st.by_name(r.suspect)
        claim = self.mod.mode.resolve_role(r.claim)
        ev = await self.mod.emit(Kind.REACTION, r.message, actor=p.id, visible_to=[p.id], data={
            **r.model_dump(), "suspect": suspect.name if suspect else "", "claim": claim,
            "channel": self.channel})
        return Bid(p.id, r.urgency, r.message, ev.seq, claim=claim,
                   suspect=suspect.name if suspect else "")

    async def _window(self, tasks: set[asyncio.Task]) -> set[asyncio.Task]:
        cfg = self.mod.config.talk
        loop = asyncio.get_running_loop()
        start, quorum = loop.time(), max(1, math.ceil(len(tasks) * cfg.quorum))
        done, pending = {t for t in tasks if t.done()}, {t for t in tasks if not t.done()}
        while pending and len(done) < quorum:
            left = cfg.round_cap_s - (loop.time() - start)
            if done and left <= 0:
                break
            new, pending = await asyncio.wait(pending, timeout=left if done else None,
                                              return_when=asyncio.FIRST_COMPLETED)
            done |= new
        if pending and done:  # quorum reached: a short grace for the rest
            new, pending = await asyncio.wait(pending, timeout=cfg.grace_s)
            done |= new
        return done
