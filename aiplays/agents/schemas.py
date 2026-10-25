"""Structured replies players give. Shared by every game mode."""
from pydantic import BaseModel, Field, field_validator

THOUGHT = ("Your private reasoning right now. Spectators can read it; other players never can. "
           "Be candid: suspicions, plans, bluffs.")


class Reaction(BaseModel):
    """A react-round bid: how badly you want the floor and what you'd say."""
    thought: str = Field("", description=THOUGHT)
    urgency: int = Field(0, description="0-10. 0-2 = stay quiet, 5 = something useful, "
                                        "8-10 = must respond now (accused, asked, or key info).")
    addressing: list[str] = Field(default_factory=list,
                                  description="Names of the players you are speaking to, if any.")
    message: str = Field("", description="What you say aloud if you get the floor: 1-3 natural "
                                         "sentences. Empty string to stay silent.")

    @field_validator("urgency", mode="before")
    @classmethod
    def _clamp(cls, v: object) -> int:
        try:
            n = float(v)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return 0
        if n > 10:  # some models answer on a 0-100 scale
            n = n / 10 if n <= 100 else 10
        return int(max(0, min(10, round(n))))

    @field_validator("addressing", mode="before")
    @classmethod
    def _listify(cls, v: object) -> list[str]:
        if isinstance(v, str):
            return [v] if v else []
        return [str(x) for x in v] if isinstance(v, list) else []


class Speech(BaseModel):
    """Something said when called on directly (nudges, last words, narration)."""
    thought: str = Field("", description=THOUGHT)
    message: str = Field("", description="What you say aloud: 1-3 natural sentences.")


class Choice(BaseModel):
    """Pick one option: votes, night kills, inspections, protections."""
    thought: str = Field("", description=THOUGHT)
    target: str = Field("nobody", description="Exactly one name from the options (or 'nobody').")
    reason: str = Field("", description="One short sentence explaining your choice; shared with "
                                        "whoever sees this choice.")
