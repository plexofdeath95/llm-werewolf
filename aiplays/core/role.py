"""Role definition shared by all game modes; each mode declares its own set."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Role:
    id: str
    label: str
    team: str
    emoji: str = ""
