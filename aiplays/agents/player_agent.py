"""PlayerAgent: one ADK LlmAgent + Runner + persisted session per player."""
import asyncio
import time

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import BaseSessionService

from aiplays.agents.base import Delta, Reply, T
from aiplays.agents.models import build_model, max_output
from aiplays.agents.parse import parse_reply, schema_hint
from aiplays.agents.pricing import cost
from aiplays.agents.turn import run_turn
from aiplays.settings import ModelEntry

_RETRY = "Your last reply was not valid ({error}). Reply again with ONLY the JSON object."
_REDO = "(The connection dropped before your answer arrived. Please answer my last message.)"
# Hard deadline per call (quick react / deep decision). A stalled provider stream would
# otherwise hold the whole table; on timeout the caller falls back to a safe default.
DEADLINE = {False: 60.0, True: 150.0}
ATTEMPTS = 3
RETRY_PAUSE = 1.5  # seconds before re-asking after a dropped connection


class PlayerAgent:
    def __init__(self, *, agent_name: str, entry: ModelEntry, instruction: str,
                 app_name: str, user_id: str, session_id: str,
                 quick: int | None, deep: int | None,
                 sem: asyncio.Semaphore, session_service: BaseSessionService):
        self.entry = entry
        # Model configs differing only in reasoning; swapped per call (one call per player is
        # ever in flight, so swapping on the shared agent is safe). "off" rescues a reply that
        # spent its whole budget reasoning and never wrote the answer.
        caps = {False: quick, True: deep, "off": 0 if quick is not None else None}
        self._models = {k: build_model(entry, v) for k, v in caps.items()}
        self._limit = {k: max_output(entry, v) for k, v in caps.items()}
        self._agent = LlmAgent(name=agent_name, model=self._models[False],
                               static_instruction=instruction)
        self._runner = Runner(app_name=app_name, agent=self._agent,
                              session_service=session_service, auto_create_session=True)
        self._ids = (user_id, session_id)
        self._sem = sem

    async def ask(self, prompt: str, schema: type[T], *, deep: bool = False,
                  choices: list[str] | None = None,
                  on_delta: Delta | None = None) -> Reply[T]:
        started, key = time.monotonic(), deep
        text = f"{prompt}\n\n{schema_hint(schema)}"
        reply: Reply[T] = Reply(value=None)
        async with self._sem:
            for attempt in range(ATTEMPTS):
                self._agent.model = self._models[key]
                try:
                    raw, thoughts, usage = await asyncio.wait_for(
                        run_turn(self._runner, *self._ids, text, on_delta, self.entry.stream),
                        DEADLINE[deep])
                except TimeoutError:
                    reply.error = f"no answer within {DEADLINE[deep]:.0f}s"
                    break
                # any provider failure (dropped stream, 5xx, rate limit) gets one more try
                except Exception as e:  # noqa: BLE001
                    reply.error = f"{type(e).__name__}: {str(e)[:300]}"
                    text = _REDO
                    await asyncio.sleep(RETRY_PAUSE)
                    continue
                reply.raw, reply.thoughts = raw, reply.thoughts + thoughts
                reply.cost += cost(self.entry.slug, usage)
                reply.usage = usage
                try:
                    reply.value, reply.error = parse_reply(raw, schema), None
                    break
                except ValueError as e:
                    reply.error = str(e)
                    text = _RETRY.format(error=e)
                    if self._overthought(usage, key):
                        key = "off"
        reply.latency = time.monotonic() - started
        return reply

    def _overthought(self, usage: dict, key) -> bool:
        """The reply used (almost) its whole token budget: reasoning crowded out the answer."""
        out = usage.get("candidates_token_count") or 0
        return key != "off" and self._models.get("off") is not None and \
            out >= self._limit[key] - 16
