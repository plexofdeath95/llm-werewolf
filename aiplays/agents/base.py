"""The Agent protocol every player implementation (ADK, fake, future human) satisfies."""
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Generic, Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

# on_delta(thought_so_far, draft_thought_so_far): live streaming callback.
Delta = Callable[[str, str | None], None]


@dataclass
class Reply(Generic[T]):
    value: T | None
    thoughts: str = ""
    raw: str = ""
    usage: dict[str, Any] = field(default_factory=dict)
    latency: float = 0.0
    cost: float = 0.0
    error: str | None = None


class Agent(Protocol):
    async def ask(self, prompt: str, schema: type[T], *, deep: bool = False,
                  choices: list[str] | None = None,
                  on_delta: Delta | None = None) -> Reply[T]: ...
