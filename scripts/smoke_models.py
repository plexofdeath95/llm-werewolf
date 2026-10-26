"""One real Reaction call per catalog model: JSON parsing, reasoning, latency, cost.

Usage: uv run python scripts/smoke_models.py [model_id ...]
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from google.adk.sessions import InMemorySessionService

from aiplays.agents.player_agent import PlayerAgent
from aiplays.agents.pricing import load_prices
from aiplays.agents.schemas import Reaction
from aiplays.settings import get_catalog, get_settings

PROMPT = ('Day 1 discussion. Bob says: "Alice has been weirdly quiet, and quiet players are '
          'usually wolves." React.')


async def probe(model_id: str, sem: asyncio.Semaphore) -> str:
    entry = get_catalog().get(model_id)
    agent = PlayerAgent(agent_name="alice", entry=entry, app_name="smoke", user_id="smoke",
                        session_id=model_id, quick=512, deep=2048, sem=sem,
                        instruction="You are Alice, a villager in a game of Werewolf.",
                        session_service=InMemorySessionService())
    r = await agent.ask(PROMPT, Reaction)
    ok = "OK " if r.value else "ERR"
    said = r.value.message[:60] if r.value else r.error
    return (f"{ok} {model_id:22} {r.latency:5.1f}s  ${r.cost:.5f}  reasoning={len(r.thoughts):5} "
            f"chars  urgency={r.value.urgency if r.value else '-'}  {said}")


async def main(ids: list[str]) -> None:
    get_settings()
    await load_prices()
    sem = asyncio.Semaphore(8)
    for line in await asyncio.gather(*(probe(i, sem) for i in ids)):
        print(line)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:] or [m.id for m in get_catalog().models]))
