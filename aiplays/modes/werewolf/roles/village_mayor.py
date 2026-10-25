"""The Mayor: day-time influence over the vote (ballot stuffing or a pardon)."""
from aiplays.agents.schemas import Choice
from aiplays.core.events import Kind
from aiplays.core.moderator import Moderator
from aiplays.core.state import Player
from aiplays.modes.werewolf.roles.base import VILLAGE, role
from aiplays.modes.werewolf.status import status


class Mayor:
    @staticmethod
    async def day_action(mod: Moderator, p: Player) -> None:
        s = status(mod.state, p)
        left = [o for o in ("stuff", "pardon") if s.uses.get(o, 1) > 0]
        if not left:
            return
        c = await mod.ask(p, mod.prompt("mayor", options=", ".join(["none", *left])), Choice,
                          fallback=Choice(target="none"), deep=True, choices=["none", *left])
        pick = c.target.strip().lower()
        if pick not in left:
            return
        s.uses[pick] = 0
        if pick == "stuff":
            mod.state.memory.setdefault("vote_bonus", {})[p.id] = 2
        else:
            mod.state.memory["pardon"] = p.id
        await mod.emit(Kind.ACTION, c.reason or f"You prepare your {pick}.", actor=p.id,
                       visible_to=[p.id], data={"action": pick, "cls": "influence",
                                                "channel": "day", "thought": c.thought})


role(id="mayor", label="Mayor", team=VILLAGE, emoji="🎩", classes=("influence",), weight=4,
     hooks=Mayor, summary="Once each: stuff the ballot (+2 votes) or pardon today's eliminee.",
     card="Before a vote you may secretly prepare one power, each once per game: Vote Stuff "
          "(your vote counts 3 times, applied only if it changes the result) or Pardon "
          "(whoever is eliminated that day walks free).")
