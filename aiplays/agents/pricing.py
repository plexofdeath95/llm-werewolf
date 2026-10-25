"""Per-call cost from token usage x OpenRouter's published prices (fetched once)."""
import logging

import httpx

log = logging.getLogger(__name__)
_URL = "https://openrouter.ai/api/v1/models"
_prices: dict[str, tuple[float, float, float]] | None = None


async def load_prices() -> dict[str, tuple[float, float, float]]:
    """slug -> ($/token in, $/token out, $/token cached-in). Empty on failure."""
    global _prices
    if _prices is None:
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                data = (await client.get(_URL)).json()["data"]
            _prices = {m["id"]: _triple(m.get("pricing", {})) for m in data}
        except Exception as e:  # pricing is best-effort; never block a game on it
            log.warning("could not load OpenRouter prices: %s", e)
            _prices = {}
    return _prices


def _triple(p: dict) -> tuple[float, float, float]:
    prompt = float(p.get("prompt") or 0)
    return prompt, float(p.get("completion") or 0), float(p.get("input_cache_read") or prompt)


def cost(slug: str, usage: dict) -> float:
    price_in, price_out, price_cached = (_prices or {}).get(slug, (0.0, 0.0, 0.0))
    prompt = usage.get("prompt_token_count") or 0
    cached = usage.get("cached_content_token_count") or 0
    out = usage.get("candidates_token_count") or 0  # includes reasoning tokens
    return (prompt - cached) * price_in + cached * price_cached + out * price_out
