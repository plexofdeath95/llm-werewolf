"""FastAPI app: REST + WebSocket API, and the built frontend when present."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from aiplays.api import catalog, games, stream
from aiplays.core.hub import get_hub
from aiplays.settings import ROOT, get_settings

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_settings()
    hub = get_hub()
    await hub.repo.init()
    yield
    await hub.shutdown()


app = FastAPI(title="AI Plays Games", lifespan=lifespan)
for module in (catalog, games, stream):
    app.include_router(module.router)

_dist = ROOT / "frontend" / "dist"
if _dist.exists():
    app.mount("/", StaticFiles(directory=_dist, html=True), name="frontend")
