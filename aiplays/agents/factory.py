"""Build the agent for every seat (ADK or fake) plus the optional narrator."""
import asyncio
import random
from functools import lru_cache

from google.adk.sessions import DatabaseSessionService

from aiplays.agents.base import Agent
from aiplays.agents.fake import FakeAgent
from aiplays.agents.player_agent import PlayerAgent
from aiplays.agents.prompts import render
from aiplays.core.config import GameConfig
from aiplays.core.mode import GameMode
from aiplays.core.state import GameState
from aiplays.settings import get_catalog, get_settings


@lru_cache
def session_service() -> DatabaseSessionService:
    return DatabaseSessionService(db_url=get_settings().adk_db_url)


@lru_cache
def _semaphore() -> asyncio.Semaphore:
    return asyncio.Semaphore(get_settings().max_concurrency)


def build_agents(state: GameState, mode: GameMode, cfg: GameConfig) -> dict[str, Agent]:
    if cfg.fake:
        rng = random.Random(state.seed)
        return {p.id: FakeAgent(p, state, rng, cfg.fake_delay) for p in state.players}
    catalog, agents = get_catalog(), {}
    for p in state.players:
        instruction = mode.briefing(state, p, cfg.reveal_models)
        if p.persona:
            instruction += "\n\n" + render("persona", persona=p.persona)
        agents[p.id] = PlayerAgent(
            agent_name=f"seat_{p.seat}", entry=catalog.get(p.model_id), instruction=instruction,
            app_name=mode.id, user_id=state.game_id, session_id=p.id,
            quick=cfg.quick_reasoning, deep=cfg.deep_reasoning,
            sem=_semaphore(), session_service=session_service())
    return agents


def build_narrator(state: GameState, cfg: GameConfig) -> Agent | None:
    if not cfg.narrator_model or cfg.fake:
        return None
    return PlayerAgent(
        agent_name="narrator", entry=get_catalog().get(cfg.narrator_model),
        instruction=render("narrator"), app_name="narrator", user_id=state.game_id,
        session_id="narrator", quick=None, deep=None,
        sem=_semaphore(), session_service=session_service())
