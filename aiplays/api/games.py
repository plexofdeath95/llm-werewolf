"""Start games and read stored games."""
from fastapi import APIRouter, HTTPException

from aiplays.core.config import GameConfig
from aiplays.core.hub import get_hub
from aiplays.core.mode import get_mode
from aiplays.db.stats import report
from aiplays.settings import get_catalog, get_speech_styles

router = APIRouter(prefix="/api/games")


def _validate(cfg: GameConfig) -> None:
    try:
        mode = get_mode(cfg.mode)
    except KeyError:
        raise HTTPException(400, f"unknown mode {cfg.mode}")
    n = len(cfg.seats)
    if not mode.min_players <= n <= mode.max_players:
        raise HTTPException(400, f"{mode.name} needs {mode.min_players}-{mode.max_players} players")
    if cfg.deck is not None:
        unknown = [r for r in cfg.deck if r not in mode.roles]
        if len(cfg.deck) != n or unknown:
            raise HTTPException(400, f"deck must list {n} known roles; unknown: {unknown}")
    if cfg.speech_style and cfg.speech_style not in {s["id"] for s in get_speech_styles()}:
        raise HTTPException(400, f"unknown speech style {cfg.speech_style}")
    cat = get_catalog()
    for model_id in [s.model_id for s in cfg.seats] + [cfg.narrator_model or cfg.seats[0].model_id]:
        try:
            if not cat.get(model_id).enabled:
                raise HTTPException(400, f"model {model_id} is disabled in config/models.yaml")
        except KeyError:
            raise HTTPException(400, f"unknown model {model_id}")


@router.post("")
async def start(cfg: GameConfig) -> dict:
    _validate(cfg)
    session = await get_hub().start(cfg)
    return {"id": session.id}


@router.get("")
async def list_games() -> list[dict]:
    return await get_hub().repo.list_games()


@router.get("/stats")
async def stats(include_fake: bool = False) -> dict:
    """Per-model benchmark tables (same queries as scripts/stats.py)."""
    return await report(get_hub().repo, include_fake)


@router.post("/{game_id}/stop")
async def stop(game_id: str) -> dict:
    session = get_hub().live(game_id)
    if not session or not session.running:
        raise HTTPException(404, "no live game with that id")
    await get_hub().stop(game_id)
    return {"stopped": game_id}


@router.get("/{game_id}")
async def get_game(game_id: str) -> dict:
    game = await get_hub().repo.get_game(game_id)
    if not game:
        raise HTTPException(404, "game not found")
    return game
