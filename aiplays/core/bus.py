"""EventBus: numbers, persists and fans out game events to live subscribers."""
import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from aiplays.core.events import GameEvent

Sink = Callable[[GameEvent], Awaitable[None]]


class EventBus:
    def __init__(self, game_id: str, sink: Sink | None = None):
        self.game_id = game_id
        self.history: list[GameEvent] = []
        self._sink = sink
        self._subs: set[asyncio.Queue] = set()

    async def publish(self, ev: GameEvent) -> GameEvent:
        ev.seq = len(self.history) + 1
        ev.game_id = self.game_id
        self.history.append(ev)
        if self._sink:
            await self._sink(ev)
        self._fan_out({"type": "event", "event": ev.model_dump(mode="json")})
        return ev

    def flash(self, payload: dict[str, Any]) -> None:
        """Ephemeral live-only message (e.g. streaming thought deltas); never persisted."""
        self._fan_out({"type": "live", **payload})

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._subs.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        self._subs.discard(q)

    def _fan_out(self, msg: dict[str, Any]) -> None:
        for q in self._subs:
            q.put_nowait(msg)
