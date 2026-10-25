"""Bring a games database to the latest Alembic revision (run on app start and in tests)."""
import asyncio

from alembic import command
from alembic.config import Config

from aiplays.settings import ROOT


def _upgrade(url: str) -> None:
    cfg = Config(str(ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "migrations"))
    cfg.set_main_option("sqlalchemy.url", url)
    cfg.attributes["configure_logger"] = False
    command.upgrade(cfg, "head")


async def upgrade(url: str) -> None:
    # env.py drives its own event loop, so run it off the app's loop.
    await asyncio.to_thread(_upgrade, url)
