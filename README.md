# AI Plays Games 🐺

LLMs play social deduction games against each other while you watch them think. Werewolf comes first, with all 80 roles from the [WikiWolf](http://wikiwolf.wikidot.com/) list. Every model runs through OpenRouter as a Google ADK agent. A deterministic moderator runs the game, every game is saved for replay and benchmarking, and the web UI shows the table in a 3D tavern.

- **See every mind.** Each player writes a private thought before it speaks, and you can read all of them live or in replay.
- **Natural turn-taking.** After every line, all players react at once and the most urgent one gets the floor, so interruptions happen.
- **Benchmarks.** Win rates, how often villagers suspect the real wolves, honesty of role claims, talk style and cost per model.
- **Share games.** Export your games as small files and import other people's from [`community/`](community/README.md).

## Requirements

- Python 3.12 or newer
- Node.js 22 LTS (20.19 or newer works)
- An [OpenRouter API key](https://openrouter.ai/keys) for real games. Demo mode needs no key.
- Optional: [uv](https://docs.astral.sh/uv/) (recommended), your own `.mp3` files for music, and ffmpeg plus Microsoft Edge for rendering videos.

## Install

**With uv (recommended):**

```bash
git clone <this repo> AI-plays-games
cd AI-plays-games
uv sync                                  # creates .venv with the pinned dependencies
cd frontend && npm install && cd ..
cp .env.example .env                     # then put your OpenRouter key in .env
```

**With pip:**

```bash
git clone <this repo> AI-plays-games
cd AI-plays-games
python -m venv .venv
source .venv/bin/activate                # Windows: .venv\Scripts\activate
pip install -r requirements.txt          # add -r requirements-dev.txt for tests and video tools
cd frontend && npm install && cd ..
cp .env.example .env                     # Windows: copy .env.example .env
```

The commands below use `uv run python`. With pip, activate the venv and use plain `python` instead.

## Run

```bash
./dev.sh          # macOS / Linux
./dev.ps1         # Windows (PowerShell)
```

This starts the API on `:8000` and the UI on http://localhost:5173.

In the lobby, pick a player count and click **auto-fill**. It seats as many different models as it can before repeating any. Pick a deck and a speech style, then press **Start**. **Demo mode** runs scripted fake players with no API calls, which is handy for trying the UI.

To check your key and models before a real game, make one cheap call per model:

```bash
uv run python scripts/smoke_models.py
```

**What it costs:** with the default models a game costs roughly $0.50 to $5; our first 22 games cost $34 in total. Each game pauses itself if it reaches its cost cap (`max_cost_usd`, $10 by default), and you can resume it from the UI.

## How a game works

1. **Night.** Private channels (wolf den, masons, lovers, the cult) talk first. Then every player with a night ability picks an action, all at the same time. The engine resolves the night in WikiWolf priority order: role-block → protection → manipulation → information → role-copy → support → killing.
   - Moving abilities either *visit* a home or *travel* to it, and some roles react to visitors.
   - Each player gets private results at dawn.
2. **Day.** Players discuss with *parallel-react* turn-taking.
   - After every message, all living players react privately at the same time with a thought, an urgency from 0 to 10, a prime suspect and a draft line.
   - The scheduler gives the floor to the most urgent player. Being named earns a bonus, players who have not spoken yet are preferred, and there's some jitter.
   - A named player who reacts with high urgency is shown as an **interruption**.
   - Discussion ends after a set number of rounds, and everyone gets heard at least once.
3. **Vote.** Everyone votes simultaneously, and the plurality is eliminated (a tie means nobody). Votes can be modified by roles: the Mayor can stuff the ballot or pardon, and the Hypnotist can copy a player's vote. Lynch triggers also run here (Knight, Jester, Executioner…).

Players never get the rules second-hand. Every briefing includes the full rules plus a card for each role in the deck, generated from the same definitions the engine enforces.

## Watching them think

- **Inner monologue.** Every reply has a `thought` field, streamed live. Click a player to read their full log.
- **Native reasoning.** When the provider exposes it (Grok, Kimi and DeepSeek do today), it appears in the Mind panel.
- **Per-call details.** Cost, latency and token use are recorded for every call.
- **Replay.** Every game can be replayed from History with seek and speed controls.

## Benchmarks and batches

```bash
uv run python scripts/run_batch.py --games 10 --budget 20 --speech caveman   # headless games, $20 cap in total
uv run python scripts/stats.py                                               # per-model tables
```

Batch games shuffle the seats and give every enabled model a seat before repeating any. The tables cover win rate (overall and by team), survival, how often village votes hit real wolves, how well wolves deflect votes, talkativeness and interrupts, and cost and latency. The same data is served at `GET /api/games/stats`.

## Share your games

```bash
uv run python scripts/export_games.py          # your finished games -> community/games/<id>.json.gz
uv run python scripts/import_games.py          # everything in community/games/ -> your local DB
```

Imported games show up in History for replay and count in `stats.py`. To add your games to the shared set, see [community/README.md](community/README.md).

## Videos (optional)

```bash
uv run python scripts/render_video.py GAME_ID      # full replay -> data/videos/GAME_ID.mp4 (with sound)
uv run python scripts/video_timeline.py GAME_ID    # map video seconds -> game events
uv run python scripts/highlights.py GAME_ID --minutes 4   # highlight reel with fast-forwards
```

These need the dev requirements, ffmpeg on your PATH, and Microsoft Edge (`uv run playwright install ffmpeg` once). They have only been tested on Windows. `render_video.py` opens a visible Edge window and records whatever the speakers play, so keep other sounds off while it runs. The highlight reel keeps deaths, votes, last words and the winner at normal speed and fast-forwards everything in between, with chipmunk voices.

## Music (optional)

No music ships with the repo. Set `MUSIC_DIR` in `.env` to a folder of your own `.mp3` files, then either list tracks per mood in `config/music.yaml` or drop files into sub-folders named after the moods (`lobby`, `day`, `night`, `vote`, `dawn`, `village_wins`, `wolves_wins`, `neutral_wins`).

## Configuration

| File | What it controls |
|---|---|
| `.env` | Your OpenRouter key, plus optional `MUSIC_DIR` |
| `config/models.yaml` | The model catalog: any OpenRouter slug, its colour, tier, and whether it is enabled |
| `config/personas.yaml` | Optional character prompts you can give a seat |
| `config/speech_styles.yaml` | Speech styles for spoken lines (cave-man, pirate, noir, Shakespeare) |
| `config/music.yaml` | Background music per mood |

## Data

| File | What it holds |
|---|---|
| `data/games.db` | Games, players, every event (speech, reactions, votes, night actions, thoughts, costs). Schema managed by **Alembic**. |
| `data/adk_sessions.db` | Each player's raw LLM conversation, kept by ADK's `DatabaseSessionService`. |
| `community/games/` | Shared game files (see above). |

`data/` is created on first run and is not committed. To change the schema, edit `aiplays/db/tables.py`, run `uv run alembic revision --autogenerate -m "..."`, and commit the migration. The app applies migrations on startup.

## Layout

```
aiplays/core/        game-agnostic engine: events, bus, moderator, conversation, scheduler, voting, session
aiplays/agents/      ADK PlayerAgent (LiteLlm → OpenRouter), prompts, digest, schemas, fake agents
aiplays/modes/werewolf/   roles/ (80 roles in small files), night/, day/, deck, rules, win
aiplays/db/          tables, repo, stats, share (game files), Alembic runner
frontend/            Vite + React + react-three-fiber game room, HUD, lobby, history/replay
config/              models, personas, speech styles, music
community/           shared game files
scripts/             smoke test, batches, stats, export/import, videos
```

New game modes such as Blood on the Clocktower go in `aiplays/modes/<mode>/` and reuse everything else.

## Tests

`uv run pytest` runs entirely offline:
- role-by-role night-resolution tests
- prompt rendering for all 80 roles
- full fake games that check engine invariants
- game file export and import
- the 100-line rule

## Contributing

Contributions are welcome: new roles, game modes, models, analysis and shared games. Read [CONTRIBUTING.md](CONTRIBUTING.md) first. The project rules, including at most 100 lines per file, are in [CLAUDE.md](CLAUDE.md).

## License

[MIT](LICENSE)
