"""One streamed ADK turn: send a user message, surface live deltas, return final text."""
import time

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.genai import types

from aiplays.agents.base import Delta
from aiplays.agents.parse import partial_thought

_SSE = RunConfig(streaming_mode=StreamingMode.SSE)
_MIN_DELTA_GAP = 0.12  # seconds between live updates per player


class _Streamer:
    def __init__(self, on_delta: Delta | None):
        self.on_delta, self.thought, self.draft, self._last = on_delta, [], [], 0.0

    def feed(self, parts: list[types.Part]) -> None:
        for p in parts:
            (self.thought if p.thought else self.draft).append(p.text or "")
        now = time.monotonic()
        if self.on_delta and now - self._last >= _MIN_DELTA_GAP:
            self._last = now
            self.on_delta("".join(self.thought), partial_thought("".join(self.draft)))


async def run_turn(runner: Runner, user_id: str, session_id: str, text: str,
                   on_delta: Delta | None = None) -> tuple[str, str, dict]:
    """Return (final answer text, native reasoning text, usage dict)."""
    msg = types.Content(role="user", parts=[types.Part(text=text)])
    stream = _Streamer(on_delta)
    answer, reasoning, usage = "", "", {}
    async for ev in runner.run_async(user_id=user_id, session_id=session_id,
                                     new_message=msg, run_config=_SSE):
        parts = ev.content.parts if ev.content and ev.content.parts else []
        if ev.partial:
            stream.feed(parts)
            continue
        if ev.usage_metadata:
            usage = ev.usage_metadata.model_dump(exclude_none=True)
        for p in parts:
            if p.thought:
                reasoning += p.text or ""
            elif p.text:
                answer += p.text
    return answer, reasoning or "".join(stream.thought), usage
