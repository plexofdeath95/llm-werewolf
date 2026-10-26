# AI Plays Games 🐺

LLMs play social deduction games against each other while you watch them think. Werewolf comes first, with all 80 roles from the [WikiWolf](http://wikiwolf.wikidot.com/) list. Every model runs through OpenRouter as a Google ADK agent. A deterministic moderator runs the game, every game is saved for replay and benchmarking, and the web UI shows the table in a 3D tavern.

## Quick start

```powershell
uv sync                       # creates .venv and installs Python deps
cd frontend; npm install; cd ..
./dev.ps1                     # API on :8000 (auto-reload) and UI on http://localhost:5173
```

`.env` needs these two lines (see `.env.example`):

```
OPEN_ROUTER_KEY=sk-or-...
MUSIC_DIR=/path/to/your/music   # optional background music
```

In the lobby, pick a player count, then click **auto-fill**. It seats as many different models as it can before repeating any. Then pick a deck and press **Start**. **Demo mode** runs scripted fake players with no API calls, which is handy for checking the UI.

## How a game works

1. **Night.** Private channels (wolf den, masons, lovers, the cult) talk first. Then every player with a night ability picks an action, all at the same time. The engine resolves the night in WikiWolf priority order: role-block → protection → manipulation → information → role-copy → support → killing.
   - Moving abilities either *visit* a home or *travel* to it, and some roles react to visitors.
   - Each player gets private results at dawn.
2. **Day.** Players discuss with *parallel-react* turn-taking.
   - After every message, all living players react privately at the same time with a thought, an urgency from 0 to 10, and a draft line.
   - The scheduler gives the floor to the most urgent player. Being named earns a bonus, having just spoken earns a penalty, and there's some jitter.
   - A named player who reacts with high urgency is shown as an **interruption**.
   - If the table goes quiet, the moderator calls on the quietest player.
3. **Vote.** Everyone votes simultaneously, and the plurality is eliminated (a tie means nobody). Votes can be modified by roles: the Mayor can stuff the ballot or pardon, and the Hypnotist can copy a player's vote. Lynch triggers also run here (Knight, Jester, Executioner…).

Players never get the rules second-hand. Every briefing includes the full rules plus a card for each role in the deck, generated from the same definitions the engine enforces.

## Watching them think

- **Inner monologue.** Every reply has a `thought` field, streamed live into thought bubbles above each avatar.
- **Native reasoning.** When the provider exposes it (Grok, Kimi and DeepSeek do today), it appears in the Mind panel.
- **Per-call details.** Cost, latency and token use are recorded for every call.
- **Replay.** Every game can be replayed from History with seek and speed controls.

## Benchmarks

```powershell
uv run python scripts/run_batch.py --games 5 --players 8     # headless real games
uv run python scripts/stats.py                               # per-model tables
```

The tables cover win rate (overall and by team), survival, how often village votes hit real wolves, how well wolves deflect votes, talkativeness and interrupts, and cost and latency. The same data is served at `GET /api/games/stats`.

## Videos

```powershell
uv run python scripts/render_video.py GAME_ID      # full replay -> data/videos/GAME_ID.mp4 (with sound)
uv run python scripts/video_timeline.py GAME_ID    # map video seconds -> game events
uv run python scripts/highlights.py GAME_ID --minutes 4   # highlight reel with fast-forwards
```

`render_video.py` opens a visible Edge window and records it with Playwright. It also records whatever the speakers play (voices and music), so keep other sounds off while it runs.

The highlight reel keeps deaths, votes, last words, claims, interrupts and the winner at normal speed, and fast-forwards everything in between. During fast-forwards the voices speed up and turn into chipmunk chatter.

## Data

| File | What it holds |
|---|---|
| `data/games.db` | Games, players, every event (speech, reactions, votes, night actions, thoughts, costs). Schema managed by **Alembic**. |
| `data/adk_sessions.db` | Each player's raw LLM conversation, kept by ADK's `DatabaseSessionService`. |

To change the schema: edit `aiplays/db/tables.py`, run `uv run alembic revision --autogenerate -m "..."`, and commit the migration. The app applies migrations on startup.

## Layout

```
aiplays/core/        game-agnostic engine: events, bus, moderator, conversation, scheduler, voting, session
aiplays/agents/      ADK PlayerAgent (LiteLlm → OpenRouter), prompts, digest, schemas, fake agents
aiplays/modes/werewolf/   roles/ (80 roles in small files), night/, day/, deck, rules, win
aiplays/db/          tables, repo, stats, Alembic runner
frontend/            Vite + React + react-three-fiber game room, HUD, lobby, history/replay
config/              models.yaml (catalog), personas.yaml, music.yaml
scripts/             smoke_models, run_batch, stats
```

New game modes such as Blood on the Clocktower go in `aiplays/modes/<mode>/` and reuse everything else. The project rules are in [CLAUDE.md](CLAUDE.md): at most 100 lines per file, and reuse before writing anything new.

## Tests

`uv run pytest` runs entirely offline:
- role-by-role night-resolution tests
- prompt rendering for all 80 roles
- full fake games that check engine invariants
- the 100-line rule
