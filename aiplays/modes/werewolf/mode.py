"""WerewolfMode (WikiWolf ruleset): deck, briefing, and the night/dawn/day loop."""
import random
from pathlib import Path

from aiplays.core.mode import GameMode, register
from aiplays.core.moderator import Moderator
from aiplays.core.state import GameState, Player
from aiplays.modes.werewolf import deck, rules, win
from aiplays.modes.werewolf.day.dawn import dawn
from aiplays.modes.werewolf.day.phase import day
from aiplays.modes.werewolf.night.phase import night
from aiplays.modes.werewolf.roles import ROLES

MAX_ROUNDS = 15  # safety net; real games end far sooner


@register
class WerewolfMode(GameMode):
    id = "werewolf"
    name = "Werewolf"
    min_players = 5
    max_players = 16
    prompts_dir = Path(__file__).parent / "prompts"
    roles = ROLES

    def default_deck(self, n: int, style: str = "mixed") -> list[str]:
        return deck.default_deck(n, style=style)

    def assign_roles(self, state: GameState, rng: random.Random,
                     deck_ids: list[str] | None = None) -> None:
        deck.assign(state, rng, deck_ids)

    def briefing(self, state: GameState, player: Player, reveal_models: bool) -> str:
        return rules.briefing(state, player, reveal_models)

    def winners(self, state: GameState, result: str) -> list[str]:
        return win.winners(state, result)

    def describe(self) -> dict:
        info = super().describe()
        for rid, r in self.roles.items():
            info["roles"][rid].update(classes=list(r.classes), summary=r.summary,
                                      weight=r.weight, in_deck=r.in_deck, group=r.group)
        return info

    async def play(self, mod: Moderator) -> str:
        st = mod.state
        await mod.announce(f"Welcome to Werewolf. {len(st.players)} players. Roles in play: "
                           f"{deck.summary([p.role for p in st.players])}. Night 1 begins.")
        while st.round < MAX_ROUNDS:
            st.round += 1
            await dawn(mod, await night(mod))
            if result := win.winner(st):
                return result
            await day(mod)
            if result := win.winner(st):
                return result
        return "nobody"
