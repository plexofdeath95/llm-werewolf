"""Werewolf win conditions."""
from aiplays.core.state import GameState
from aiplays.modes.werewolf.roles import VILLAGE, WOLVES


def winner(state: GameState) -> str | None:
    wolves = len(state.on_team(WOLVES))
    others = len(state.alive()) - wolves
    if wolves == 0:
        return VILLAGE
    if wolves >= others:
        return WOLVES
    return None
