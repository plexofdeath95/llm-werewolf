"""Local models: Ollama discovery, call routing and seating without an OpenRouter key."""
import httpx

from aiplays.agents import ollama
from aiplays.agents.models import build_model, max_output
from aiplays.settings import Catalog, ModelEntry

TAGS = {"models": [{"name": "qwen3:8b", "details": {"family": "qwen3"}},
                   {"name": "gpt-oss:20b", "details": {"family": "gptoss"}},
                   {"name": "nomic-embed-text:latest", "details": {"family": "nomic-bert"}}]}


class _Resp:
    def json(self):
        return TAGS


def test_discover_lists_chat_models_only(monkeypatch):
    monkeypatch.setattr(httpx, "get", lambda url, timeout: _Resp())
    found = ollama.discover("http://localhost:11434")
    assert [m.slug for m in found] == ["qwen3:8b", "gpt-oss:20b"]
    assert all(m.provider == "ollama" and m.tier == "local" and m.deadline_scale > 1 for m in found)


def test_discover_without_ollama_is_empty(monkeypatch):
    def refuse(url, timeout):
        raise httpx.ConnectError("refused")
    monkeypatch.setattr(httpx, "get", refuse)
    assert ollama.discover("http://localhost:11434") == []


def test_local_calls_go_to_ollama_with_a_thinking_switch():
    entry = ollama.entry("qwen3:8b")
    quick, deep = build_model(entry, 0), build_model(entry, 2048)
    assert quick.model == "ollama_chat/qwen3:8b"
    assert quick._additional_args["reasoning_effort"] == "none"
    assert deep._additional_args["reasoning_effort"] == "medium"
    assert deep._additional_args["response_format"] == {"type": "json_object"}
    assert "extra_body" not in deep._additional_args  # no OpenRouter reasoning field
    assert max_output(entry, 2048) == 2048 + 1200
    assert ollama.effort("gpt-oss:20b", 0) == "low"  # gpt-oss can't switch thinking off


def test_without_a_cloud_key_only_local_models_are_seated(monkeypatch):
    cloud = ModelEntry(id="gpt", label="GPT", slug="openai/gpt", provider="openai")
    cat = Catalog(models=[cloud, ollama.entry("qwen3:8b")], player_names=["A"])
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    assert cat.roster(3) == ["ollama/qwen3:8b"] * 3
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    assert cat.roster(2) == ["gpt", "ollama/qwen3:8b"]
