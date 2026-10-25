"""A whole Werewolf game with offline FakeAgents: engine invariants, no API calls."""
import random

from aiplays.core.config import GameConfig, SeatConfig
from aiplays.core.events import Kind
from aiplays.core.session import GameSession
from aiplays.db.repo import Repo
from aiplays.modes.werewolf.deck import default_deck
from aiplays.modes.werewolf.win import team_of


async def _play(tmp_path, seed: int, style: str = "mixed") -> GameSession:
    repo = Repo(f"sqlite+aiosqlite:///{(tmp_path / f'g{seed}{style}.db').as_posix()}")
    await repo.init()
    deck = default_deck(8, random.Random(seed), style=style)
    cfg = GameConfig(seats=[SeatConfig(model_id="claude-haiku-5.5")] * 8, seed=seed,
                     deck=deck, fake=True, fake_delay=0)
    s = GameSession(cfg, repo)
    await s.start()
    await s.task
    return s


async def test_fake_games_finish_with_consistent_events(tmp_path):
    for seed, style in [(i, "classic") for i in range(3)] + [(i, "mixed") for i in range(8)]:
        s = await _play(tmp_path, seed, style)
        evs = s.bus.history
        assert evs[-1].kind == Kind.GAME_OVER, [e.text for e in evs[-3:]]
        assert s.state.winner in {"village", "wolves", "neutral", "nobody"}
        dead_at: dict[str, int] = {}
        # dealt wolves plus anyone who became one (an Orphan or Amnesiac copying a wolf role)
        wolves = {p.id for p in s.state.players
                  if p.team == "wolves" or team_of(s.state, p) == "wolves"}
        for ev in evs:
            if ev.kind == Kind.DEATH:
                dead_at[ev.target] = ev.seq
            if ev.kind == Kind.SPEECH and ev.actor in dead_at:
                raise AssertionError(f"dead player {ev.actor} spoke (seq {ev.seq})")
            if ev.data.get("channel") == "wolf den":
                assert ev.visible_to and set(ev.visible_to) <= wolves
        saved = await s.repo.load_events(s.id)
        assert len(saved) == len(evs)
        game = await s.repo.get_game(s.id)
        assert game["status"] == "finished" and len(game["players"]) == 8
