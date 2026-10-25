"""Startup cleanup cancels only games that went silent, never another process's live game."""
import time

from sqlalchemy import update

from aiplays.core.config import GameConfig, SeatConfig
from aiplays.core.events import GameEvent, Kind
from aiplays.db import repo as repo_mod
from aiplays.db.repo import Repo
from aiplays.db.tables import EventRow, GameRow
from rolekit import game


async def _game(repo: Repo, gid: str, last_event_age_s: float) -> None:
    st = game("villager", "villager", "villager", "villager", "alpha")
    st.game_id = gid
    await repo.create_game(st, GameConfig(seats=[SeatConfig(model_id="claude-haiku-5.5")] * 5))
    await repo.add_event(GameEvent(kind=Kind.PHASE, seq=1, game_id=gid, text="Night 1"))
    async with repo.session.begin() as s:
        ts = time.time() - last_event_age_s
        await s.execute(update(EventRow).where(EventRow.game_id == gid).values(ts=ts))
        await s.execute(update(GameRow).where(GameRow.id == gid).values(created_at=ts))


async def test_only_silent_games_are_cancelled(tmp_path):
    repo = Repo(f"sqlite+aiosqlite:///{(tmp_path / 'g.db').as_posix()}")
    await repo.init()
    await _game(repo, "live", last_event_age_s=5)
    await _game(repo, "dead", last_event_age_s=repo_mod.ORPHAN_AFTER_S + 60)
    await repo.init()  # a server restart
    assert (await repo.get_game("live"))["status"] == "running"
    assert (await repo.get_game("dead"))["status"] == "cancelled"
