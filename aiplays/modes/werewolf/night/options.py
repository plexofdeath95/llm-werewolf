"""Which abilities a player may use tonight, and on whom."""
from aiplays.core.state import GameState, Player
from aiplays.modes.werewolf.roles.base import ROLES, WOLVES, ActionDef
from aiplays.modes.werewolf.status import role_of, status


def available(state: GameState, p: Player, night: int) -> list[ActionDef]:
    s = status(state, p)
    actions = list(ROLES[role_of(state, p)].actions) + list(s.marks.get("borrowed", []))
    lent = s.marks.get("borrow")  # (night, role id): a corpse's / victim's powers for one night
    if lent and lent[0] == night:
        actions += [a for a in ROLES[lent[1]].actions if a.name not in {b.name for b in actions}]
    return [a for a in actions
            if night >= a.from_night and (a.only_night is None or a.only_night == night)
            and (a.uses is None or uses_left(s, a) > 0)
            and s.ready_on.get(a.name, 0) <= night
            and (a.ready is None or a.ready(state, p))]


def uses_left(s, a: ActionDef) -> int:
    return s.uses.get(a.uses_key or a.name, a.uses or 0)


def targets(state: GameState, p: Player, a: ActionDef, night: int) -> list[Player]:
    if a.targets == 0:
        return []
    alive = state.alive()
    if callable(a.pool):  # role-specific pools, e.g. an Assassin's target list
        return _no_repeat(state, p, a, night, a.pool(state, p))
    pool = {
        "others": [q for q in alive if q is not p],
        "anyone": alive,
        "dead": [q for q in state.players if not q.alive],
        "non_wolves": [q for q in alive if q is not p
                       and ROLES[role_of(state, q)].team != WOLVES],
    }[a.pool]
    return _no_repeat(state, p, a, night, pool)


def _no_repeat(state: GameState, p: Player, a: ActionDef, night: int,
               pool: list[Player]) -> list[Player]:
    last_night, last_ids = status(state, p).last.get(a.name, (0, []))
    if a.repeat_banned and last_night == night - 1:
        pool = [q for q in pool if q.id not in last_ids]
    return pool


def describe(state: GameState, p: Player, night: int) -> str:
    """Human-readable menu of tonight's abilities for the prompt."""
    lines, s = [], status(state, p)
    for a in available(state, p, night):
        opts = targets(state, p, a, night)
        bits = [f'- "{a.name}": {a.help}']
        if a.targets:
            bits.append(f"  Pick {a.targets} of: {state.names(opts) or '(nobody available)'}.")
        if a.options == ("*",):
            bits.append("  Option (required): free text, as described.")
        elif a.options:
            bits.append(f"  Option (required): one of {', '.join(a.options)}.")
        if a.uses is not None:
            bits.append(f"  Uses left: {uses_left(s, a)}.")
        lines.append("\n".join(bits))
    return "\n".join(lines)


def record(state: GameState, p: Player, a: ActionDef, chosen: list[Player], night: int) -> None:
    s = status(state, p)
    if a.uses is not None:
        s.uses[a.uses_key or a.name] = uses_left(s, a) - 1
    if a.cooldown:
        s.ready_on[a.name] = night + a.cooldown + 1
    s.last[a.name] = (night, [t.id for t in chosen])
