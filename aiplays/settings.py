"""App settings (.env) and the model catalog (config/models.yaml)."""
import os
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def _sqlite(name: str) -> str:
    return f"sqlite+aiosqlite:///{(DATA / name).as_posix()}"


class ModelEntry(BaseModel):
    id: str
    label: str
    slug: str
    provider: str = ""
    color: str = "#888888"
    tier: str = "standard"
    enabled: bool = True
    stream: bool = True  # SSE; Google models via OpenRouter stalled mid-stream
    reasoning_off: str = "minimal"  # how to turn reasoning off: minimal | disable


class Catalog(BaseModel):
    models: list[ModelEntry]
    default_players: int = 8
    player_names: list[str]

    def get(self, model_id: str) -> ModelEntry:
        for m in self.models:
            if m.id == model_id:
                return m
        raise KeyError(f"unknown model id: {model_id}")

    def roster(self, n: int | None = None) -> list[str]:
        """n model ids: every unique model (standard tier first) before any repeats."""
        n = n or self.default_players
        order = sorted((m for m in self.models if m.enabled), key=lambda m: m.tier != "standard")
        return [order[i % len(order)].id for i in range(n)]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / ".env", extra="ignore")
    open_router_key: str = ""
    games_db_url: str = _sqlite("games.db")
    adk_db_url: str = _sqlite("adk_sessions.db")
    max_concurrency: int = 12
    catalog_file: Path = ROOT / "config" / "models.yaml"
    music_dir: Path | None = None  # licensed background music, served read-only


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    if s.open_router_key:
        os.environ.setdefault("OPENROUTER_API_KEY", s.open_router_key)
    os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")
    DATA.mkdir(exist_ok=True)
    return s


@lru_cache
def get_catalog() -> Catalog:
    raw = yaml.safe_load(get_settings().catalog_file.read_text(encoding="utf-8"))
    return Catalog(**raw)


@lru_cache
def get_speech_styles() -> list[dict]:
    path = ROOT / "config" / "speech_styles.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8")).get("speech_styles", [])


@lru_cache
def get_personas() -> list[dict]:
    path = ROOT / "config" / "personas.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8")).get("personas", [])
