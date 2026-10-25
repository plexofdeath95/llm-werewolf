"""PlayerAgent never hangs the table: a stalled model call ends at the deadline."""
import asyncio

from google.adk.sessions import InMemorySessionService

from aiplays.agents import player_agent
from aiplays.agents.schemas import Reaction
from aiplays.settings import get_catalog


async def test_stalled_call_times_out_with_an_error(monkeypatch):
    async def stalled(*args, **kwargs):
        await asyncio.sleep(30)

    monkeypatch.setattr(player_agent, "run_turn", stalled)
    monkeypatch.setattr(player_agent, "DEADLINE", {False: 0.2, True: 0.2})
    agent = player_agent.PlayerAgent(
        agent_name="p", entry=get_catalog().models[0], instruction="test", app_name="t",
        user_id="u", session_id="s", quick=None, deep=None, sem=asyncio.Semaphore(1),
        session_service=InMemorySessionService())
    reply = await asyncio.wait_for(agent.ask("hello", Reaction), 5)
    assert reply.value is None and "no answer within" in (reply.error or "")
