"""Game end (faction level) and per-player wins (neutrals have their own conditions)."""
from aiplays.core.state import GameState, Player
from aiplays.modes.werewolf.roles.base import NEUTRAL, ROLES, VILLAGE, WOLVES
from aiplays.modes.werewolf.status import role_of, status


def team_of(state: GameState, p: Player) -> str:
    return "cult" if "cult" in status(state, p).flags else ROLES[role_of(state, p)].team


def winner(state: GameState) -> str | None:
    """'village' | 'wolves' | 'neutral' | 'nobody' when the game is over, else None."""
    alive = state.alive()
    if not alive:
        return "nobody"
    for p in alive:  # role-specific endings (cult takeover, hunter's last stand...)
        decides = ROLES[role_of(state, p)].hook("decides")
        if decides and (result := decides(state, p)):
            if result == NEUTRAL:
                state.memory["neutral_winner"] = p.id
            return result
    wolves = sum(team_of(state, p) == WOLVES for p in alive)
    hostile = sum(ROLES[role_of(state, p)].hostile for p in alive)
    if wolves == 0 and hostile == 0:
        return VILLAGE
    if hostile == 0 and wolves >= len(alive) - wolves:
        return WOLVES
    if wolves == 0 and hostile >= len(alive) - hostile:
        return NEUTRAL
    return None


def winners(state: GameState, result: str) -> list[str]:
    """Ids of every player who won (team win, or their own neutral condition)."""
    won = []
    for p in state.players:
        hook = ROLES[role_of(state, p)].hook("win")
        if hook:
            ok = hook(state, p, result)
        else:
            ok = team_of(state, p) == result and result in (VILLAGE, WOLVES)
            ok = ok or (result == NEUTRAL and state.memory.get("neutral_winner") == p.id)
        ok = ok or (team_of(state, p) == "cult" and bool(state.memory.get("cult_won")))
        if ok:
            won.append(p.id)
    return won
