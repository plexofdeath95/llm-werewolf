"""Models served by a local Ollama: found at startup and offered in the lobby as "(local)"."""
import hashlib
import logging

import httpx

from aiplays.settings import ModelEntry

log = logging.getLogger(__name__)
PROVIDER = "ollama"
LOCAL_DEADLINE_SCALE = 4.0  # one GPU answers the whole table in turn, so allow much longer
PALETTE = ["#e9c46a", "#f4a261", "#2a9d8f", "#8ecae6", "#b5838d", "#90be6d", "#cdb4db", "#f28482"]


def discover(url: str, timeout: float = 1.0) -> list[ModelEntry]:
    """Every chat model pulled into the Ollama at `url`; empty when it isn't running."""
    try:
        tags = httpx.get(f"{url.rstrip('/')}/api/tags", timeout=timeout).json().get("models", [])
    except (httpx.HTTPError, ValueError):
        return []
    found = [entry(m["name"]) for m in tags if not _embedding(m)]
    if found:
        log.info("Ollama at %s: %s", url, ", ".join(m.slug for m in found))
    return found


def entry(name: str) -> ModelEntry:
    color = PALETTE[int(hashlib.md5(name.encode()).hexdigest(), 16) % len(PALETTE)]
    return ModelEntry(id=f"ollama/{name}", label=f"{name} (local)", slug=name, provider=PROVIDER,
                      color=color, tier="local", deadline_scale=LOCAL_DEADLINE_SCALE)


def _embedding(tag: dict) -> bool:
    """Embedding models can't chat; Ollama lists them alongside the chat models."""
    family = ((tag.get("details") or {}).get("family") or "").lower()
    return "embed" in tag.get("name", "").lower() or "bert" in family


def effort(slug: str, tokens: int | None) -> str | None:
    """Ollama has no thinking budget, only a switch (or a level for gpt-oss): map the cap."""
    if tokens is None:
        return None
    if tokens == 0:
        return "low" if slug.startswith("gpt-oss") else "none"
    return "low" if tokens <= 1024 else "medium" if tokens <= 4096 else "high"
