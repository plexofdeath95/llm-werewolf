"""FakeAgent: offline, seeded, scripted player for tests and the no-cost UI demo."""
import asyncio
import random

from aiplays.agents.base import Delta, Reply, T
from aiplays.agents.schemas import Action, Choice, Reaction, Speech
from aiplays.core.state import GameState, Player

_LINES = [
    "I have a bad feeling about {x}.", "{x}, why so quiet today?", "I trust {x}, for now.",
    "Let's not rush this. What do we actually know?", "Something about {x}'s vote bugs me.",
    "{x}, where were you last night? Figuratively speaking.", "I'm just a humble villager.",
]


class FakeAgent:
    def __init__(self, player: Player, state: GameState, rng: random.Random, delay: float = 0.0):
        self.player, self.state, self.rng, self.delay = player, state, rng, delay

    async def ask(self, prompt: str, schema: type[T], *, deep: bool = False,
                  choices: list[str] | None = None,
                  on_delta: Delta | None = None) -> Reply[T]:
        others = [p.name for p in self.state.alive(exclude=self.player)] or ["everyone"]
        x = self.rng.choice(others)
        thought = f"Hmm. {x} is acting odd. As a {self.player.role} I should be careful."
        for i in range(1, 4):
            if on_delta:
                on_delta("", thought[: len(thought) * i // 3])
            await asyncio.sleep(self.delay * self.rng.random() / 3)
        line = self.rng.choice(_LINES).format(x=x)
        if schema is Reaction:
            claim = self.rng.choice([q.role for q in self.state.players])                 if self.rng.random() < 0.12 else ""  # sometimes a (true or bluffed) role claim
            value = Reaction(thought=thought, urgency=self.rng.randint(0, 10), suspect=x,
                             addressing=[x] if "{x}" in line else [], message=line, claim=claim)
        elif schema is Speech:
            value = Speech(thought=thought, message=line)
        elif schema is Choice:
            value = Choice(thought=thought, target=self.rng.choice(choices or others),
                           reason=f"Gut feeling about {x}.")
        elif schema is Action:  # choices look like "skip" or "heal:Bob+Carol|option"
            pick = self.rng.choice(choices or ["skip"])
            name, _, rest = pick.partition(":")
            names, _, option = rest.partition("|")
            value = Action(thought=thought, action=name, targets=names.split("+") if names else [],
                           option=option, reason=f"Acting on a hunch about {x}.")
        else:
            value = schema()
        return Reply(value=value, thoughts=f"(fake reasoning) Considering {x}...", raw="")  # type: ignore[arg-type]
