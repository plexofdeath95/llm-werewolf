"""Catalog entry -> ADK LiteLlm model, routed through OpenRouter or a local Ollama."""
import litellm
from google.adk.models.lite_llm import LiteLlm

from aiplays.agents import ollama
from aiplays.settings import ModelEntry, get_settings

litellm.suppress_debug_info = True  # no "Provider List" banner for models it can't price (local)

OUTPUT_HEADROOM = 1200  # visible-answer tokens on top of the reasoning cap
MIN_REASONING = {"anthropic": 1024}  # Anthropic skips thinking below its minimum budget
# How to switch reasoning off: some endpoints allow disabling it, others make it mandatory
# (GPT, Sonnet, Grok) and accept only a minimal effort.
REASONING_OFF = {"disable": {"enabled": False}, "minimal": {"effort": "minimal"}}


def reasoning_body(entry: ModelEntry, tokens: int | None) -> dict | None:
    """OpenRouter `reasoning` field: None = provider default, 0 = off, N = token cap."""
    if tokens is None:
        return None
    if tokens == 0:
        return REASONING_OFF[entry.reasoning_off]
    return {"max_tokens": max(tokens, MIN_REASONING.get(entry.provider, 0))}


def max_output(entry: ModelEntry, tokens: int | None) -> int:
    if entry.provider == ollama.PROVIDER:  # thinking counts against Ollama's output limit
        return (tokens or 0) + OUTPUT_HEADROOM
    body = reasoning_body(entry, tokens) or {}
    return body.get("max_tokens", 0) + OUTPUT_HEADROOM


def build_model(entry: ModelEntry, reasoning_tokens: int | None) -> LiteLlm:
    settings = get_settings()  # also exports OPENROUTER_API_KEY for LiteLLM
    if entry.provider == ollama.PROVIDER:
        return _local(entry, reasoning_tokens, settings.ollama_url)
    body = reasoning_body(entry, reasoning_tokens)
    extra = {"extra_body": {"reasoning": body}} if body else {}
    return LiteLlm(
        model=f"openrouter/{entry.slug}",
        max_tokens=max_output(entry, reasoning_tokens),
        num_retries=1,
        timeout=120,
        **extra,
    )


def _local(entry: ModelEntry, reasoning_tokens: int | None, url: str) -> LiteLlm:
    """Ollama: JSON mode keeps small models parseable; thinking is a switch, not a budget."""
    effort = ollama.effort(entry.slug, reasoning_tokens)
    return LiteLlm(
        model=f"ollama_chat/{entry.slug}",
        api_base=url or "http://localhost:11434",
        max_tokens=max_output(entry, reasoning_tokens),
        response_format={"type": "json_object"},
        num_retries=1,
        timeout=120 * entry.deadline_scale,
        **({"reasoning_effort": effort} if effort else {}),
    )
