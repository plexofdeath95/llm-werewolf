"""WerewolfMode: wires roles, briefing and the night/dawn/day loop into the engine."""
import random
from pathlib import Path

from aiplays.agents.prompts import render
from aiplays.core.mode import GameMode, register
from aiplays.core.moderator import Moderator
from aiplays.core.state import GameState, Player
from aiplays.modes.werewolf import roles as ww
from aiplays.modes.werewolf.day import dawn, day
from aiplays.modes.werewolf.night import night
from aiplays.modes.werewolf.win import winner
from aiplays.settings import get_catalog

MAX_ROUNDS = 12  # safety net; real games end far sooner


@register
class WerewolfMode(GameMode):
    id = "werewolf"
    name = "Werewolf"
    min_players = 5
    max_players = 16
    prompts_dir = Path(__file__).parent / "prompts"
    roles = ww.ROLES

    def default_deck(self, n: int) -> list[str]:
        return ww.distribution(n)

    def assign_roles(self, state: GameState, rng: random.Random,
                     deck: list[str] | None = None) -> None:
        ww.assign(state, rng, deck)

    def briefing(self, state: GameState, player: Player, reveal_models: bool) -> str:
        cat = get_catalog()
        roster = "\n".join(
            f"- {p.name}" + (f" (played by {cat.get(p.model_id).label})" if reveal_models else "")
            for p in state.players)
        pack = [w for w in state.on_team(ww.WOLVES) if w is not player]
        mates = (f"Your fellow werewolves: {state.names(pack)}." if player.team == ww.WOLVES
                 and pack else "")
        rules = render("rules", self.prompts_dir, count=len(state.players),
                       setup=ww.summary(len(state.players)))
        return render("briefing", self.prompts_dir, name=player.name, rules=rules, roster=roster,
                      role=render(f"role_{player.role}", self.prompts_dir), mates=mates)

    async def play(self, mod: Moderator) -> str:
        st = mod.state
        await mod.announce(f"Welcome to Werewolf. {len(st.players)} players, hidden roles: "
                           f"{ww.summary(len(st.players))}. The first night begins.")
        while st.round < MAX_ROUNDS:
            st.round += 1
            await dawn(mod, await night(mod))
            if w := winner(st):
                return w
            await day(mod)
            if w := winner(st):
                return w
        return "nobody"
