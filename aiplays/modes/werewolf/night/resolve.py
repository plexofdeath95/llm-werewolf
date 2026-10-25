"""Resolve a night in WikiWolf movement-priority order, then settle attacks into deaths."""
from aiplays.modes.werewolf.night.context import Act, Night
from aiplays.modes.werewolf.night.settle import settle
from aiplays.modes.werewolf.roles.base import PRIORITY, TEAM_ORDER

BLOCKED = "Someone kept you busy all night: your action did not happen."


def resolve(n: Night) -> None:
    for a in [a for a in n.acts if a.action.cls == "early"]:
        _run(n, a)  # transporter / angler / coward / detour reshape movement first
    for cls in PRIORITY:
        if cls == "killing":  # standing effects that react to tonight's movement: traps, bombs
            for p in n.state.alive():
                if hook := n.role(p).hook("passive"):
                    hook(n, p)
        for a in sorted(_of(n, cls), key=lambda a: _order(n, a)):
            _run(n, a)
        if cls == "role_block":
            _move(n)
    settle(n)
    for a in n.acts:
        if a.action.after and not a.blocked and not a.failed:
            a.action.after(n, a)


def _of(n: Night, cls: str) -> list[Act]:
    return [a for a in n.acts if a.action.cls == cls]


def _order(n: Night, a: Act) -> tuple[int, int, int]:
    """Blockers aimed at blockers go first; then village, neutral, wolves; then seat."""
    hits_blocker = any(n.role(t).classes[:1] == ("role_block",) for t in a.targets)
    return (0 if hits_blocker else 1, TEAM_ORDER.get(n.role(a.actor).team, 1), a.actor.seat)


def _run(n: Night, a: Act) -> None:
    if not a.actor.alive or a.actor.id in n.deaths:
        return
    if a.blocked and not a.action.unblockable:
        n.note(a.actor, BLOCKED)
        return
    if not a.failed:
        a.action.handler(n, a)


def _move(n: Night) -> None:
    """After role-blocks: work out where everyone actually went and who visited whom."""
    for a in n.acts:
        if a.blocked or not a.moves:
            continue
        if a.action.aim:
            a.action.aim(n, a)
        if a.actor.id in n.redirect:
            a.targets = [n.state.by_id(n.redirect[a.actor.id])]
        landed = []
        for t in a.targets:
            if t is a.actor or not t.alive:
                landed.append(t)  # self-targets and graveyard visits don't leave home
                continue
            t = n.state.by_id(n.resident.get(t.id, t.id))
            if t.id in n.hidden or t.id in n.jailed or _nightmare(n, a, t):
                a.failed = True
                n.note(a.actor, f"You could not reach {t.name} tonight.")
                break
            n.visits[t.id].append(a)
            n.left_home.add(a.actor.id)
            landed.append(t)
        a.targets = landed


def _nightmare(n: Night, a: Act, t) -> bool:
    return n.st(a.actor).marks.get("nightmare") == t.id
