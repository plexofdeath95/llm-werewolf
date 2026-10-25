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


def _agent(monkeypatch, replies):
    """PlayerAgent whose model calls return (or raise) the scripted replies in order."""
    calls = []

    async def scripted(runner, user, session, text, on_delta=None, stream=True):
        calls.append((text, player.agent_model_name()))
        item = replies[len(calls) - 1]
        if isinstance(item, Exception):
            raise item
        return item

    monkeypatch.setattr(player_agent, "run_turn", scripted)
    monkeypatch.setattr(player_agent, "RETRY_PAUSE", 0)
    player = player_agent.PlayerAgent(
        agent_name="p", entry=get_catalog().get("kimi-k3.1-pro"), instruction="t",
        app_name="t", user_id="u", session_id="s", quick=0, deep=2048,
        sem=asyncio.Semaphore(1), session_service=InMemorySessionService())
    player.agent_model_name = lambda: id(player._agent.model)
    return player, calls


async def test_dropped_connection_is_retried(monkeypatch):
    player, calls = _agent(monkeypatch, [ConnectionError("closed"),
                                         ('{"urgency": 5, "message": "hi"}', "", {})])
    reply = await player.ask("q", Reaction)
    assert reply.value and reply.value.message == "hi" and len(calls) == 2
    assert "connection dropped" in calls[1][0]


async def test_overthinking_retries_without_reasoning(monkeypatch):
    full = {"candidates_token_count": 2048 + 1200}
    player, calls = _agent(monkeypatch, [("", "thinking...", full),
                                         ('{"target": "Ann"}', "", {})])
    from aiplays.agents.schemas import Choice
    reply = await player.ask("q", Choice, deep=True)
    assert reply.value and reply.value.target == "Ann"
    assert calls[0][1] != calls[1][1] and calls[1][1] == id(player._models["off"])
