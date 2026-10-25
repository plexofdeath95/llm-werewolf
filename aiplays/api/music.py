"""Background music: mood -> track URLs (config/music.yaml) and the files themselves."""
from functools import lru_cache
from urllib.parse import quote

import yaml
from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles

from aiplays.settings import ROOT, get_settings

router = APIRouter(prefix="/api")
FILES = "/api/music/files"


@lru_cache
def _moods() -> dict[str, list[str]]:
    raw = yaml.safe_load((ROOT / "config" / "music.yaml").read_text(encoding="utf-8"))
    return raw.get("moods", {})


@router.get("/music")
def music() -> dict:
    folder = get_settings().music_dir
    if not folder or not folder.exists():
        return {"enabled": False, "moods": {}}
    moods = {mood: [f"{FILES}/{quote(t)}.mp3" for t in tracks
                    if (folder / f"{t}.mp3").exists()]
             for mood, tracks in _moods().items()}
    return {"enabled": True, "moods": moods}


def mount_files(app: FastAPI) -> None:
    folder = get_settings().music_dir
    if folder and folder.exists():
        app.mount(FILES, StaticFiles(directory=folder), name="music")
