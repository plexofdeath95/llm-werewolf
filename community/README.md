# Community games

This folder holds shared Werewolf games, one file per game in `games/<id>.json.gz`. Import them to replay any game in the UI or to add them to your benchmark tables:

```bash
uv run python scripts/import_games.py      # loads every file here into data/games.db
uv run python scripts/stats.py             # tables now include the imported games
```

Then open History in the UI to watch any of them.

The first 14 games were played in October 2026 while the project was being built, so a few early ones used older rules. See the commit history for what changed.

## What a game file contains

One gzipped JSON document with format `aiplays-game/1`:
- `game`: the settings, deck, seed, winner, round count and cost.
- `players`: each seat's name, model, secret role, team and fate.
- `events`: everything that happened, in order, including speeches, private thoughts, reactions, night actions and results, votes and per-call cost.

It does **not** contain API keys or the players' raw prompt histories (those stay in your local `data/adk_sessions.db`).

## Submitting your games

1. Play games with real models, either in the UI or with `scripts/run_batch.py`. Demo-mode games are not accepted.
2. Export them. Only new finished games are written:
   ```bash
   uv run python scripts/export_games.py
   ```
3. Check the files:
   ```bash
   uv run python scripts/import_games.py --check community/games/<id>.json.gz
   ```
4. Open a pull request that adds only your new files. In the description, say which models you used and whether you changed any rules, prompts or settings (for example, a different deck or speech style).

Please don't edit other people's files. If you find a broken one, open an issue.
