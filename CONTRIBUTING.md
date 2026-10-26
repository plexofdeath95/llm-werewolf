# Contributing

Thanks for helping. This guide covers setup, the code rules, and how to add models, roles, game modes and shared games.

## Setup

```bash
uv sync                      # includes the dev tools (pytest, ruff, playwright)
cd frontend && npm install && cd ..
uv run pytest                # offline; no API key needed
```

With pip, use `pip install -r requirements-dev.txt` instead of `uv sync`.

## Code rules

These are strict; `tests/test_file_sizes.py` enforces the first one.

1. **Small files.** Every `.py`, `.ts` and `.tsx` file is at most 100 lines. When a file grows, split it by responsibility.
2. **Reuse first.** Before writing something new, look for an existing module, helper or component and extend it. That includes the libraries already in use: ADK, LiteLLM, FastAPI, SQLAlchemy, React and react-three-fiber/drei.
3. **Keep the core game-agnostic.** `aiplays/core/`, `aiplays/agents/`, `aiplays/db/`, `aiplays/api/` and the frontend never mention Werewolf. Game rules live in `aiplays/modes/<mode>/`.
4. **Prompt text** goes in user messages or `static_instruction`, never in the templated `instruction`, because `{}` there triggers ADK state injection.

## Adding a model

Add an entry to `config/models.yaml` with an OpenRouter slug, then check it with one real call:

```bash
uv run python scripts/smoke_models.py
```

Useful fields:
- `stream: false` for providers that stall mid-stream.
- `reasoning_off: disable` for models that ignore a reasoning budget.
- `enabled: false` to keep a model in the catalog without auto-filling it.

## Adding a role or a game mode

- **A Werewolf role** is one small file in `aiplays/modes/werewolf/roles/`, built from `role(...)` and `act(...)`. Its card text is generated into every briefing. Add a test next to the existing `tests/test_roles_*.py`.
- **A new game mode** is a new folder in `aiplays/modes/<mode>/` that reuses the moderator, conversation, voting, agents, DB and UI. Register it the way `modes/werewolf/mode.py` does.

## Sharing games

Played some games? See [community/README.md](community/README.md) for how to export them and open a pull request.

## Before you open a pull request

- `uv run ruff check .` and `uv run pytest` pass.
- `cd frontend && npm run build` passes if you touched the frontend.
- Nothing from `.env`, `data/` or your music folder is committed.
- New game files pass `uv run python scripts/import_games.py --check`.

## How pull requests are merged

`main` is protected. Every change arrives as a pull request from a branch or fork, and it can merge when:
- both CI checks pass (**Python tests** and **Frontend build**, run by GitHub Actions on every pull request);
- the maintainer has approved it (reviews are requested automatically through `.github/CODEOWNERS`);
- every review conversation is resolved.

A new push dismisses an earlier approval. Force-pushing to `main` and deleting it are blocked.
