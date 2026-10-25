"""Asking players: digest + question -> agent -> accounted, validated answer."""
import asyncio
from collections.abc import Awaitable, Callable

from aiplays.agents import digest
from aiplays.agents.base import Agent, Reply, T
from aiplays.core.bus import EventBus
from aiplays.core.events import GameEvent, Kind
from aiplays.core.gate import Budget, Gate
from aiplays.core.state import GameState, Player

OnReply = Callable[[Player, T], Awaitable[None]]


class Asker:
    state: GameState
    bus: EventBus
    gate: Gate
    budget: Budget
    agents: dict[str, Agent]
    cursor: dict[str, int]

    async def emit(self, kind: Kind, text: str = "", **fields) -> GameEvent:
        return await self.bus.publish(GameEvent(
            kind=kind, text=text, round=self.state.round, phase=self.state.phase, **fields))

    async def ask(self, player: Player, question: str, schema: type[T], *, fallback: T,
                  deep: bool = False, choices: list[str] | None = None) -> T:
        await self.gate.wait()
        return await self._ask(player, question, schema, fallback, deep, choices)

    async def ask_many(self, players: list[Player], question: Callable[[Player], str],
                       schema: type[T], *, fallback: Callable[[Player], T], deep: bool = False,
                       choices: Callable[[Player], list[str]] | None = None,
                       on_reply: OnReply | None = None) -> dict[str, T]:
        """Ask everyone in parallel; on_reply fires as each answer lands."""
        await self.gate.wait()

        async def one(p: Player) -> tuple[str, T]:
            value = await self._ask(p, question(p), schema, fallback(p), deep,
                                    choices(p) if choices else None)
            if on_reply:
                await on_reply(p, value)
            return p.id, value

        return dict(await asyncio.gather(*(one(p) for p in players)))

    async def _ask(self, p: Player, question: str, schema: type[T], fallback: T,
                   deep: bool, choices: list[str] | None) -> T:
        context, self.cursor[p.id] = digest.build(
            self.bus.history, self.state, p, self.cursor.get(p.id, 0))
        prompt = f"{context}\n\n{question}" if context else question

        def on_delta(thought: str, draft: str | None) -> None:
            self.bus.flash({"actor": p.id, "thought": thought, "draft": draft})

        reply = await self.agents[p.id].ask(prompt, schema, deep=deep, choices=choices,
                                            on_delta=on_delta)
        await self._account(p.id, reply, schema.__name__)
        if reply.value is None:
            await self.emit(Kind.ERROR, reply.error or "no reply", actor=p.id,
                            data={"fallback": fallback.model_dump()})
            return fallback
        return reply.value

    async def _account(self, actor: str, reply: Reply, schema_name: str) -> None:
        """Log the call (native reasoning, usage, latency, cost) and enforce the budget."""
        await self.emit(Kind.THOUGHT, reply.thoughts, actor=actor, visible_to=[actor], data={
            "schema": schema_name, "usage": reply.usage, "latency": round(reply.latency, 2),
            "cost": reply.cost, "spent": self.budget.spent + reply.cost})
        if self.budget.add(reply.cost):
            self.gate.pause()
            await self.emit(Kind.STATUS, f"Budget of ${self.budget.max_usd:.2f} reached; paused.",
                            data={"paused": True, "budget": True})
