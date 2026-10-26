"""Shared game files round-trip: export from one DB, import into another, nothing lost."""
import pytest
from rolekit import game

from aiplays.core.config import GameConfig, SeatConfig
from aiplays.core.events import GameEvent, Kind
from aiplays.db.repo import Repo
from aiplays.db.share import check, export_game, import_game, read, write


async def _repo(tmp_path, name: str) -> Repo:
    repo = Repo(f"sqlite+aiosqlite:///{(tmp_path / name).as_posix()}")
    await repo.init()
    return repo


async def test_round_trip(tmp_path):
    src = await _repo(tmp_path, "a.db")
    st = game("villager", "villager", "villager", "villager", "alpha")
    st.game_id = "g1"
    await src.create_game(st, GameConfig(seats=[SeatConfig(model_id="claude-haiku-5.5")] * 5))
    for seq, kind in enumerate((Kind.PHASE, Kind.SPEECH, Kind.GAME_OVER), 1):
        await src.add_event(GameEvent(kind=kind, seq=seq, game_id="g1", text=f"e{seq}",
                                      data={"thought": "hmm"}, visible_to=["p1"] if seq == 2 else None))
    doc = read(write(await export_game(src, "g1"), tmp_path / "out"))
    dst = await _repo(tmp_path, "b.db")
    assert await import_game(dst, doc) is True
    assert await import_game(dst, doc) is False  # already there
    again = await export_game(dst, "g1")
    assert again["players"] == doc["players"] and again["events"] == doc["events"]
    assert [e.text for e in await dst.load_events("g1")] == ["e1", "e2", "e3"]


def test_check_rejects_mixed_games():
    doc = {"format": "aiplays-game/1", "game": {"id": "g1"},
           "players": [{"game_id": "g1"}], "events": [{"game_id": "other", "seq": 1}]}
    with pytest.raises(ValueError):
        check(doc)
