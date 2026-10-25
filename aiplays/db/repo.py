"""Repo: async persistence for games, players and events (SQLite via aiosqlite)."""
import time

from sqlalchemy import event, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from aiplays.core.config import GameConfig
from aiplays.core.events import GameEvent
from aiplays.core.state import GameState
from aiplays.db.tables import Base, EventRow, GameRow, PlayerRow
from aiplays.settings import get_catalog


class Repo:
    def __init__(self, db_url: str):
        self.engine = create_async_engine(db_url)
        event.listen(self.engine.sync_engine, "connect", _fast_sqlite)
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def init(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def create_game(self, st: GameState, cfg: GameConfig) -> None:
        cat = get_catalog()
        async with self.session.begin() as s:
            s.add(GameRow(id=st.game_id, mode=st.mode, seed=st.seed, created_at=time.time(),
                          config=cfg.model_dump(mode="json")))
            s.add_all(PlayerRow(game_id=st.game_id, player_id=p.id, seat=p.seat, name=p.name,
                                model_id=p.model_id, slug=_slug(cat, p.model_id),
                                persona=p.persona, role=p.role, team=p.team)
                      for p in st.players)

    async def add_event(self, ev: GameEvent) -> None:
        async with self.session.begin() as s:
            s.add(EventRow(**ev.model_dump(mode="json", exclude={"game_id"}), game_id=ev.game_id))

    async def finish_game(self, st: GameState, status: str, cost_usd: float) -> None:
        async with self.session.begin() as s:
            await s.execute(update(GameRow).where(GameRow.id == st.game_id).values(
                status=status, winner=st.winner, rounds=st.round, cost_usd=cost_usd,
                ended_at=time.time()))
            for p in st.players:
                await s.execute(update(PlayerRow).where(
                    PlayerRow.game_id == st.game_id, PlayerRow.player_id == p.id).values(
                    alive=p.alive, died_round=p.died_round, death_cause=p.death_cause, won=p.won))

    async def list_games(self, limit: int = 100) -> list[dict]:
        async with self.session() as s:
            rows = await s.scalars(select(GameRow).order_by(GameRow.created_at.desc()).limit(limit))
            return [_row(g) for g in rows]

    async def get_game(self, game_id: str) -> dict | None:
        async with self.session() as s:
            game = await s.get(GameRow, game_id)
            if not game:
                return None
            players = await s.scalars(select(PlayerRow).where(PlayerRow.game_id == game_id)
                                      .order_by(PlayerRow.seat))
            return {**_row(game), "players": [_row(p) for p in players]}

    async def load_events(self, game_id: str) -> list[GameEvent]:
        async with self.session() as s:
            rows = await s.scalars(select(EventRow).where(EventRow.game_id == game_id)
                                   .order_by(EventRow.seq))
            return [GameEvent(**_row(r)) for r in rows]


def _fast_sqlite(conn, _record) -> None:
    """WAL + relaxed fsync: one commit per event stays cheap (hundreds per game)."""
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL")
    cur.execute("PRAGMA synchronous=NORMAL")
    cur.close()


def _row(obj) -> dict:
    return {c.key: getattr(obj, c.key) for c in obj.__table__.columns}


def _slug(cat, model_id: str) -> str:
    try:
        return cat.get(model_id).slug
    except KeyError:
        return model_id
