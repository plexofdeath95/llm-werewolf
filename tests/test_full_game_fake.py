"""A whole Werewolf game with offline FakeAgents: engine invariants, no API calls."""
from aiplays.core.config import GameConfig, SeatConfig
from aiplays.core.events import Kind
from aiplays.core.session import GameSession
from aiplays.db.repo import Repo


async def _play(tmp_path, seed: int) -> GameSession:
    repo = Repo(f"sqlite+aiosqlite:///{(tmp_path / f'g{seed}.db').as_posix()}")
    await repo.init()
    cfg = GameConfig(seats=[SeatConfig(model_id="claude-haiku-5.5")] * 8, seed=seed,
                     fake=True, fake_delay=0)
    s = GameSession(cfg, repo)
    await s.start()
    await s.task
    return s


async def test_fake_games_finish_with_consistent_events(tmp_path):
    for seed in range(5):
        s = await _play(tmp_path, seed)
        evs = s.bus.history
        assert evs[-1].kind == Kind.GAME_OVER
        assert s.state.winner in {"village", "wolves"}
        dead_at: dict[str, int] = {}
        wolves = {p.id for p in s.state.players if p.team == "wolves"}
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
