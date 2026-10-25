"""Game configuration as sent by the lobby / batch runner."""
from pydantic import BaseModel, Field


class TalkConfig(BaseModel):
    """Discussion length and the parallel-react scheduler's weights (core/scheduler.py)."""
    rounds: int = 3               # time limit: up to rounds x alive messages, then the vote
    max_messages: int = 30        # hard cap regardless of table size
    pass_threshold: int = 3
    named_bonus: float = 3.0
    unheard_bonus: float = 4.0    # hasn't spoken yet this discussion: strongly preferred
    repeat_penalty: float = 0.75  # per message already said this discussion
    last_penalty: float = 3.0
    second_last_penalty: float = 1.5
    jitter: float = 0.5
    interrupt_urgency: int = 8


class SeatConfig(BaseModel):
    model_id: str
    name: str | None = None
    persona: str | None = None    # optional extra system prompt; None = model's default self


class GameConfig(BaseModel):
    mode: str = "werewolf"
    seats: list[SeatConfig]
    deck: list[str] | None = None  # role ids in play (one per seat); None = mode's balanced default
    seed: int | None = None
    max_cost_usd: float = 10.0
    quick_reasoning: int = 512    # reasoning-token cap for react rounds
    deep_reasoning: int = 2048    # cap for votes, night actions, last words
    narrator_model: str | None = None
    reveal_on_death: bool = True
    reveal_models: bool = False   # do players know which model the others are?
    fake: bool = False            # offline scripted agents (tests / UI demo)
    fake_delay: float = 0.8       # seconds of simulated thinking per fake call
    talk: TalkConfig = Field(default_factory=TalkConfig)
