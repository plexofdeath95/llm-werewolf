"""Portable game files: export a stored game as JSON and import it into another games DB.

A file holds one game's rows from games, game_players and game_events (the players' raw LLM
histories in adk_sessions.db stay local). Shared games live in community/games/.
"""
import gzip
import json
from pathlib import Path

from sqlalchemy import select

from aiplays.db.repo import Repo, _row
from aiplays.db.tables import EventRow, GameRow, PlayerRow

FORMAT = "aiplays-game/1"


async def export_game(repo: Repo, game_id: str) -> dict:
    async with repo.session() as s:
        game = await s.get(GameRow, game_id)
        if not game:
            raise KeyError(f"no game {game_id}")
        players = await s.scalars(select(PlayerRow).where(PlayerRow.game_id == game_id)
                                  .order_by(PlayerRow.seat))
        events = await s.scalars(select(EventRow).where(EventRow.game_id == game_id)
                                 .order_by(EventRow.seq))
        return {"format": FORMAT, "game": _row(game), "players": [_row(p) for p in players],
                "events": [_row(e) for e in events]}


def check(doc: dict) -> str:
    """Raise ValueError if doc is not a well-formed game file; return its game id."""
    if doc.get("format") != FORMAT:
        raise ValueError(f"not an {FORMAT} file")
    gid = doc["game"]["id"]
    rows = doc["players"] + doc["events"]
    if not doc["players"] or any(r.get("game_id") != gid for r in rows):
        raise ValueError(f"{gid}: players and events must all belong to the game")
    seqs = [e["seq"] for e in doc["events"]]
    if len(seqs) != len(set(seqs)):
        raise ValueError(f"{gid}: duplicate event seq")
    return gid


async def import_game(repo: Repo, doc: dict) -> bool:
    """Add a shared game to this DB. False when a game with that id is already here."""
    gid = check(doc)
    async with repo.session.begin() as s:
        if await s.get(GameRow, gid):
            return False
        s.add(GameRow(**doc["game"]))
        await s.flush()
        s.add_all(PlayerRow(**p) for p in doc["players"])
        s.add_all(EventRow(**e) for e in doc["events"])
    return True


def write(doc: dict, folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{doc['game']['id']}.json.gz"
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    return path


def read(path: Path) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return json.load(f)
