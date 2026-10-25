"""Neutrals who play the day: Jester (wants the noose) and Maligned Prophet (marks the doomed)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from aiplays.agents.schemas import Choice
from aiplays.core.events import Kind
from aiplays.modes.werewolf.roles import neutral_kit as kit
from aiplays.modes.werewolf.roles.base import NEUTRAL, role
from aiplays.modes.werewolf.roles.neutral_kit import GOAL_TEXT
from aiplays.modes.werewolf.status import status

if TYPE_CHECKING:
    from aiplays.modes.werewolf.night.context import Night


class Jester:
    @staticmethod
    async def on_lynched(mod, p, voters) -> bool:
        status(mod.state, p).flags.add("jester_won")
        pool = [v for v in voters if v.alive and v is not p]
        if not pool:
            return False
        names = [v.name for v in pool]
        pick = await mod.ask(p, f"You were voted out, so you WIN. Choose one player who voted for "
                                f"you to take down with you: {', '.join(names)}.", Choice,
                             fallback=Choice(target=names[-1]), choices=names, deep=True)
        victim = mod.state.by_name(pick.target, pool) or pool[-1]
        await mod.kill(victim, "haunted by the Jester",
                       f"The Jester's curse strikes down {victim.name}!")
        from aiplays.modes.werewolf.day.dawn import deaths_triggered  # lazy: avoids a cycle
        await deaths_triggered(mod, [victim])
        return False

    win = staticmethod(lambda state, p, result: "jester_won" in status(state, p).flags)


def _seen(state, p, dead_id: str, day: int) -> None:
    """Count a death if it is the prophet's live mark (set on `day`)."""
    mark = status(state, p).marks.get("mark")
    if mark and mark == (day, dead_id):
        status(state, p).marks.pop("mark")
        kit.count(state, p, "seen")


class Prophet:
    @staticmethod
    async def day_action(mod, p) -> None:
        st = mod.state
        others = [q for q in st.alive() if q is not p]
        names = [q.name for q in others]
        pick = await mod.ask(p, f"Day {st.round}: mark one player you foresee dying before the "
                                f"next day ends: {', '.join(names)}.", Choice,
                             fallback=Choice(target=mod.rng.choice(names)), choices=names)
        t = st.by_name(pick.target, others)
        if t:
            status(st, p).marks["mark"] = (st.round, t.id)
            await mod.emit(Kind.ACTION, f"You marked {t.name}.", actor=p.id, target=t.id,
                           visible_to=[p.id], data={"action": "mark", "cls": "influence"})

    @staticmethod
    async def after_lynch(mod, q, lynched, voters) -> None:
        _seen(mod.state, q, lynched.id, mod.state.round)

    @staticmethod
    def after_night(n: Night, p) -> None:
        for pid in n.deaths:
            _seen(n.state, p, pid, n.n - 1)

    win = staticmethod(lambda state, p, result:
                       status(state, p).marks.get("seen", 0) >= kit.goal(state))


role(id="jester", label="Jester", team=NEUTRAL, emoji="🃏", classes=("killing",), weight=-1,
     hooks=Jester, summary="Wants to be voted out. Takes one of their voters down with them.",
     card="You win if the village votes you out; other sides can still win too. You have no "
          "night ability. When you are voted out, choose one player who voted for you: they "
          "die too (if you don't choose, the last of your voters in seating order dies).")

role(id="maligned_prophet", label="Maligned Prophet", team=NEUTRAL, emoji="📜",
     classes=("influence",), weight=0, hooks=Prophet,
     summary="Marks one player each day; wins after living to see enough marks die.",
     card="Each day, at the start of voting, you mark one other player. The mark lasts until "
          "the end of the next night: if that player is voted out that day or dies that night, "
          f"it counts. You win once at least {GOAL_TEXT} of your marks have died while you were "
          "alive to see it. Only one mark exists at a time; marking someone new replaces it.")
