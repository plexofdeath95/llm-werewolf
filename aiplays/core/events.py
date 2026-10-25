"""GameEvent: the single record type for everything that happens in a game."""
import time
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Kind(StrEnum):
    SETUP = "setup"            # roster + roles (spectator info)
    PHASE = "phase"            # phase change, e.g. night 2 / day discussion
    MODERATOR = "moderator"    # rule-driven announcement
    NARRATION = "narration"    # optional LLM flavor text
    SPEECH = "speech"          # something a player said aloud (to visible_to)
    REACTION = "reaction"      # a player's private react-round bid
    THOUGHT = "thought"        # native model reasoning for one call
    VOTE = "vote"
    VOTE_RESULT = "vote_result"
    ACTION = "action"          # private night action / result
    DEATH = "death"
    REVEAL = "reveal"
    STATUS = "status"          # paused / resumed / budget warnings
    ERROR = "error"
    GAME_OVER = "game_over"


class GameEvent(BaseModel):
    kind: Kind
    seq: int = 0
    game_id: str = ""
    round: int = 0
    phase: str = ""
    actor: str | None = None
    target: str | None = None
    text: str = ""
    data: dict[str, Any] = Field(default_factory=dict)
    visible_to: list[str] | None = None  # None = public
    ts: float = Field(default_factory=time.time)

    def visible(self, player_id: str) -> bool:
        return self.visible_to is None or player_id in self.visible_to
