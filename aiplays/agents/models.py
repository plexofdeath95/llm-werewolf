"""Catalog entry -> ADK LiteLlm model routed through OpenRouter."""
from google.adk.models.lite_llm import LiteLlm

from aiplays.settings import ModelEntry, get_settings

OUTPUT_HEADROOM = 1200  # visible-answer tokens on top of the reasoning cap
MIN_REASONING = {"anthropic": 1024}  # Anthropic skips thinking below its minimum budget


def build_model(entry: ModelEntry, reasoning_tokens: int | None) -> LiteLlm:
    get_settings()  # ensures OPENROUTER_API_KEY is exported for LiteLLM
    extra: dict = {}
    if reasoning_tokens:
        reasoning_tokens = max(reasoning_tokens, MIN_REASONING.get(entry.provider, 0))
        extra["extra_body"] = {"reasoning": {"max_tokens": reasoning_tokens}}
    return LiteLlm(
        model=f"openrouter/{entry.slug}",
        max_tokens=(reasoning_tokens or 0) + OUTPUT_HEADROOM,
        num_retries=1,
        timeout=120,
        **extra,
    )
