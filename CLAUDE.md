# AI Plays Games

LLMs (through OpenRouter and Google ADK) play social deduction games against each other. Werewolf is the first game. A web UI shows the game room, each player's thinking, and replays of past games.

## Hard rules (never deviate, under any circumstances)
1. **Small modular files.** Every source file (`.py`, `.ts`, `.tsx`) is **at most 100 lines**. `tests/test_file_sizes.py` enforces this. When a file grows, split it by responsibility.
2. **Reuse modules as much as possible.** Before writing anything, search for an existing module, helper or component that does the job, and extend it.
3. **Don't create something new if something already exists for it.** This covers our own code *and* libraries already in use: ADK (agents, sessions, DB-backed history), LiteLLM (providers, retries), FastAPI, SQLAlchemy, React and react-three-fiber/drei. No parallel re-implementations.
4. **Stay open to new game modes.** Everything in `aiplays/core/`, `aiplays/agents/`, `aiplays/db/`, `aiplays/api/` and the frontend is game-agnostic. Game-specific rules live only in `aiplays/modes/<mode>/`. A new mode (e.g. Blood on the Clocktower) is added as a new folder that reuses the moderator, conversation, voting, agents, DB and UI. Never hard-code Werewolf into shared code.

## Architecture
- `aiplays/core/`: the game-agnostic engine.
  - `events` + `bus`: every happening is a `GameEvent`, persisted and streamed.
  - `moderator`: rule-driven announcements and asks.
  - `conversation` + `scheduler`: parallel-react turn-taking.
  - `voting`, `session`, `gate`/`budget`: pause/step and the cost cap.
- `aiplays/agents/`: one ADK `LlmAgent` per player, sending `LiteLlm("openrouter/<slug>")` calls through `PlayerAgent.ask(prompt, Schema)`.
  - `models` builds the LiteLlm per catalog entry; `provider: ollama` entries go to `ollama_chat/<slug>` instead (JSON mode, thinking as an on/off switch, longer deadlines).
  - `ollama` discovers models pulled into a running Ollama and adds them to the catalog as tier `local`.
  - `digest` builds each player's view of the game, filtered by `visible_to`.
  - `fake` provides offline agents for tests and demo mode.
- `aiplays/db/`: game tables in `data/games.db`. ADK `DatabaseSessionService` keeps each player's raw history in `data/adk_sessions.db`.
  - `share`: portable game files (`aiplays-game/1`, gzipped JSON) for `community/games/`.
- `aiplays/modes/werewolf/`: roles, setup, the night and day phases, win check and `prompts/*.md`.
  - `insights/`: analysis of stored games (suspicion accuracy, changes of mind, claims, moods, heat maps, quotes, SVG charts) used by `scripts/insights.py` and `scripts/charts.py`.
- `frontend/`: Vite + React + TS with react-three-fiber. It has a 3D game room, a HUD and replay.
- `config/models.yaml`: the model catalog (OpenRouter slugs).

## Commands
- `uv sync`: install Python deps into `.venv` (pip users: `pip install -r requirements-dev.txt`)
- `uv run pytest`: run the tests (no API calls)
- `./dev.ps1` (Windows) or `./dev.sh` (macOS/Linux): start the backend on `:8000` and the frontend on `:5173`
- `uv run python scripts/smoke_models.py`: one real call per catalog model
- `uv run python scripts/run_batch.py --games N --budget USD`: run games headless, then replay them in the UI
- `uv run python scripts/stats.py`: benchmark tables (wins, vote accuracy, talk, cost)
- `uv run python scripts/insights.py tables|heat GAME|quotes` and `scripts/charts.py`: deeper Werewolf analysis and SVG charts
- `uv run python scripts/export_games.py` / `import_games.py [--check]`: share games via `community/games/`

## Public repo
- Never commit `.env`, `data/`, music or videos. `.gitignore` covers them; keep it that way.
- After changing dependencies in `pyproject.toml`, regenerate the pinned files:
  `uv export --no-hashes --no-dev --no-emit-project -o requirements.txt` and the dev group into `requirements-dev.txt` (it starts with `-r requirements.txt`).
- Shared game files in `community/games/` must pass `scripts/import_games.py --check`; don't rewrite other people's files.

## Notes
- `.env` holds `OPEN_ROUTER_KEY`. Settings map it to `OPENROUTER_API_KEY` for LiteLLM.
- Set `PYTHONUTF8=1` on Windows (LiteLLM file encoding).
- Keep `litellm>=1.84` (1.82.7 and 1.82.8 were compromised).
- Prompt text goes in user messages or `static_instruction`, never in the templated `instruction`, because `{}` there triggers ADK state injection.
