"""A player's view of the game: what they could see since their last turn, as plain text."""
from aiplays.core.events import GameEvent, Kind
from aiplays.core.state import GameState, Player

_HIDDEN = {Kind.SETUP, Kind.REACTION, Kind.THOUGHT, Kind.STATUS, Kind.ERROR}


def _who(state: GameState, pid: str | None, me: Player) -> str:
    if not pid:
        return "nobody"
    p = state.by_id(pid)
    return f"{p.name} (you)" if p is me else p.name


def line(ev: GameEvent, state: GameState, me: Player) -> str | None:
    if ev.kind in _HIDDEN or not ev.visible(me.id):
        return None
    channel = ev.data.get("channel")
    tag = f"[{channel}] " if channel and channel != "public" else ""
    if ev.kind == Kind.PHASE:
        return f"\n=== {ev.text} ==="
    if ev.kind == Kind.SPEECH:
        return f'{tag}{_who(state, ev.actor, me)}: "{ev.text}"'
    if ev.kind == Kind.VOTE:
        verb = ev.data.get("verb", "votes for")
        reason = f" ({ev.text})" if ev.text else ""
        return f"{tag}{_who(state, ev.actor, me)} {verb} {_who(state, ev.target, me)}{reason}"
    if ev.kind == Kind.NARRATION:
        return f"Narrator: {ev.text}"
    return f"{tag}Moderator: {ev.text}"


def build(events: list[GameEvent], state: GameState, me: Player, since: int) -> tuple[str, int]:
    """Return (text of new visible events after seq `since`, newest seq)."""
    lines = [s for ev in events if ev.seq > since if (s := line(ev, state, me))]
    last = events[-1].seq if events else since
    if not lines:
        return "", last
    return "What happened since your last turn:\n" + "\n".join(lines), last
