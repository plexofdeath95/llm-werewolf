"""PlayerAgent: one ADK LlmAgent + Runner + persisted session per player."""
import asyncio
import time

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import BaseSessionService

from aiplays.agents.base import Delta, Reply, T
from aiplays.agents.models import build_model
from aiplays.agents.parse import parse_reply, schema_hint
from aiplays.agents.pricing import cost
from aiplays.agents.turn import run_turn
from aiplays.settings import ModelEntry

_RETRY = "Your last reply was not valid ({error}). Reply again with ONLY the JSON object."
# Hard deadline per call (quick react / deep decision). A stalled provider stream would
# otherwise hold the whole table; on timeout the caller falls back to a safe default.
DEADLINE = {False: 90.0, True: 150.0}


class PlayerAgent:
    def __init__(self, *, agent_name: str, entry: ModelEntry, instruction: str,
                 app_name: str, user_id: str, session_id: str,
                 quick: int | None, deep: int | None,
                 sem: asyncio.Semaphore, session_service: BaseSessionService):
        self.entry = entry
        # Two model configs differing only in reasoning cap; swapped per call (one call
        # per player is ever in flight, so swapping on the shared agent is safe).
        self._models = {False: build_model(entry, quick), True: build_model(entry, deep)}
        self._agent = LlmAgent(name=agent_name, model=self._models[False],
                               static_instruction=instruction)
        self._runner = Runner(app_name=app_name, agent=self._agent,
                              session_service=session_service, auto_create_session=True)
        self._ids = (user_id, session_id)
        self._sem = sem

    async def ask(self, prompt: str, schema: type[T], *, deep: bool = False,
                  choices: list[str] | None = None,
                  on_delta: Delta | None = None) -> Reply[T]:
        self._agent.model = self._models[deep]
        started = time.monotonic()
        text = f"{prompt}\n\n{schema_hint(schema)}"
        reply: Reply[T] = Reply(value=None)
        async with self._sem:
            for attempt in range(2):
                try:
                    raw, thoughts, usage = await asyncio.wait_for(
                        run_turn(self._runner, *self._ids, text, on_delta), DEADLINE[deep])
                except TimeoutError:
                    reply.error = f"no answer within {DEADLINE[deep]:.0f}s"
                    break
                except Exception as e:  # provider/network failure after LiteLLM retries
                    reply.error = f"{type(e).__name__}: {e}"
                    break
                reply.raw, reply.thoughts = raw, reply.thoughts + thoughts
                reply.cost += cost(self.entry.slug, usage)
                reply.usage = usage
                try:
                    reply.value, reply.error = parse_reply(raw, schema), None
                    break
                except ValueError as e:
                    reply.error = str(e)
                    text = _RETRY.format(error=e)
        reply.latency = time.monotonic() - started
        return reply
