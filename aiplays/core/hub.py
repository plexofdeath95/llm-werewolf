"""Hub: the process-wide registry of live game sessions and the shared repo."""
from functools import lru_cache

from aiplays.core.config import GameConfig
from aiplays.core.session import GameSession
from aiplays.db.repo import Repo
from aiplays.settings import get_settings


class Hub:
    def __init__(self, repo: Repo):
        self.repo = repo
        self.sessions: dict[str, GameSession] = {}

    async def start(self, cfg: GameConfig) -> GameSession:
        session = GameSession(cfg, self.repo)
        self.sessions[session.id] = session
        await session.start()
        return session

    def live(self, game_id: str) -> GameSession | None:
        return self.sessions.get(game_id)

    async def shutdown(self) -> None:
        for s in self.sessions.values():
            if s.task and not s.task.done():
                s.task.cancel()


@lru_cache
def get_hub() -> Hub:
    return Hub(Repo(get_settings().games_db_url))
