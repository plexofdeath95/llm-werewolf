"""Read-only lobby data: models, personas, rosters, modes and default decks."""
from fastapi import APIRouter, HTTPException

from aiplays.core.mode import get_mode, list_modes
from aiplays.settings import get_catalog, get_personas

router = APIRouter(prefix="/api")


@router.get("/models")
def models() -> dict:
    cat = get_catalog()
    return {"models": [m.model_dump() for m in cat.models],
            "default_players": cat.default_players, "personas": get_personas()}


@router.get("/roster")
def roster(n: int | None = None) -> list[str]:
    return get_catalog().roster(n)


@router.get("/modes")
def modes() -> list[dict]:
    return list_modes()


@router.get("/modes/{mode_id}/deck")
def deck(mode_id: str, n: int) -> list[str]:
    try:
        mode = get_mode(mode_id)
    except KeyError:
        raise HTTPException(404, f"unknown mode {mode_id}")
    if not mode.min_players <= n <= mode.max_players:
        raise HTTPException(400, f"{mode.name} needs {mode.min_players}-{mode.max_players} players")
    return mode.default_deck(n)
