"""Ask every player with a night ability what they do, in parallel; validate into Acts."""
from aiplays.agents.schemas import Action
from aiplays.core.events import Kind
from aiplays.core.moderator import Moderator
from aiplays.core.state import Player
from aiplays.modes.werewolf.night import options
from aiplays.modes.werewolf.night.context import Act, Night
from aiplays.modes.werewolf.roles.base import PRIORITY


async def collect(mod: Moderator, n: Night) -> None:
    st = mod.state
    actors = [p for p in st.alive() if options.available(st, p, n.n)]

    def question(p: Player) -> str:
        return mod.prompt("night_action", menu=options.describe(st, p, n.n))

    def sample(p: Player) -> list[str]:
        """Valid 'action:target+target' picks; only the offline FakeAgent uses these."""
        picks = ["skip"]
        for a in options.available(st, p, n.n):
            pool = options.targets(st, p, a, n.n)
            if len(pool) >= a.targets:
                names = "+".join(t.name for t in mod.rng.sample(pool, a.targets))
                picks.append(f"{a.name}:{names}" + (f"|{a.options[0]}" if a.options else ""))
        return picks

    replies = await mod.ask_many(actors, question, Action, deep=True, choices=sample,
                                 fallback=lambda p: Action())
    for p in actors:
        act = _validate(mod, n, p, replies[p.id])
        if act:
            n.acts.append(act)
            options.record(st, p, act.action, act.targets, n.n)
            await mod.emit(Kind.ACTION, replies[p.id].reason, actor=p.id,
                           target=act.targets[0].id if act.targets else None, visible_to=[p.id],
                           data={"action": act.action.name, "cls": act.action.cls,
                                 "targets": [t.id for t in act.targets], "option": act.option,
                                 "movement": act.action.movement, "order": _order(act),
                                 "thought": replies[p.id].thought, "channel": "night"})


def _order(act: Act) -> int:
    """Resolution order for the UI's night replay: early moves first, then PRIORITY."""
    cls = act.action.cls
    return -1 if cls == "early" else PRIORITY.index(cls) if cls in PRIORITY else len(PRIORITY)


def _validate(mod: Moderator, n: Night, p: Player, r: Action) -> Act | None:
    st = mod.state
    if r.action.strip().lower() in ("", "skip", "none", "nothing"):
        return None
    menu = {a.name.lower(): a for a in options.available(st, p, n.n)}
    a = menu.get(r.action.strip().lower())
    if not a:
        n.note(p, f'"{r.action}" is not one of your abilities tonight, so you did nothing.')
        return None
    pool = options.targets(st, p, a, n.n)
    chosen: list[Player] = []
    for name in r.targets:
        t = st.by_name(name, pool)
        if t and t not in chosen and len(chosen) < a.targets:
            chosen.append(t)
    option = r.option.strip() if a.options == ("*",) else next(
        (o for o in a.options if o.lower() == r.option.strip().lower()), "")
    if len(chosen) < a.targets or (a.options and not option):
        n.note(p, f"Your {a.name} needed {a.targets} valid target(s)"
                  + (" and an option" if a.options else "") + ", so it did nothing.")
        return None
    return Act(p, a, chosen, option)
