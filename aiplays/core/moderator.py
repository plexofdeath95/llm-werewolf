"""Moderator: the rule-driven host. Announces, changes phases, kills, narrates, asks."""
import random

from aiplays.agents.base import Agent
from aiplays.agents.prompts import render
from aiplays.agents.schemas import Speech
from aiplays.core.asker import Asker
from aiplays.core.bus import EventBus
from aiplays.core.config import GameConfig
from aiplays.core.events import Kind
from aiplays.core.gate import Budget, Gate
from aiplays.core.mode import GameMode
from aiplays.core.state import GameState, Player


class Moderator(Asker):
    def __init__(self, *, state: GameState, mode: GameMode, config: GameConfig,
                 agents: dict[str, Agent], bus: EventBus, gate: Gate, budget: Budget,
                 narrator: Agent | None = None):
        self.state, self.mode, self.config = state, mode, config
        self.agents, self.bus, self.gate, self.budget = agents, bus, gate, budget
        self.narrator = narrator
        self.cursor: dict[str, int] = {}
        self.rng = random.Random(state.seed)

    def prompt(self, name: str, **values: object) -> str:
        return render(name, self.mode.prompts_dir, round=self.state.round, **values)

    async def announce(self, text: str, *, visible_to: list[str] | None = None,
                       narrate: bool = False, **data) -> None:
        await self.emit(Kind.MODERATOR, text, visible_to=visible_to, data=data)
        if narrate:
            await self.narrate(text)

    async def set_phase(self, phase: str, label: str) -> None:
        self.state.phase = phase
        await self.emit(Kind.PHASE, label, data={"phase": phase})

    async def kill(self, p: Player, cause: str, text: str, *, narrate: bool = False) -> None:
        p.alive, p.died_round, p.death_cause = False, self.state.round, cause
        await self.emit(Kind.DEATH, text, target=p.id, data={"cause": cause})
        if self.config.reveal_on_death:
            await self.emit(Kind.REVEAL, f"{p.name} was {self.mode.role_label(p.role)}.",
                            target=p.id, data={"role": p.role, "team": p.team})
        if narrate:
            await self.narrate(text)

    async def narrate(self, facts: str) -> None:
        """Optional flavor line from the narrator model. Never changes game facts."""
        if not self.narrator:
            return
        reply = await self.narrator.ask(render("narrate", facts=facts), Speech)
        await self._account("narrator", reply, "Speech")
        if reply.value and reply.value.message:
            await self.emit(Kind.NARRATION, reply.value.message)
