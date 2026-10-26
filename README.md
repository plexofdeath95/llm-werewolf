# LLM Werewolf 🐺

LLMs play Werewolf against each other in a 3D tavern, and you can read every player's private thoughts as the game goes. It has all 80 [WikiWolf](http://wikiwolf.wikidot.com/) roles, runs any model on OpenRouter, and saves every game for replay.

![A day in the tavern: one player claims Seer while another's private thoughts are open on the left](docs/media/day.jpg)

> “Me no Alpha. Me just fool.”
> — DeepSeek, the Alpha, in its last words

## Run it

You need Python 3.12+, Node 22 and an [OpenRouter key](https://openrouter.ai/keys). Demo mode works without a key.

```bash
git clone https://github.com/plexofdeath95/llm-werewolf.git
cd llm-werewolf
uv sync                          # or make a venv and: pip install -r requirements.txt
cd frontend && npm install && cd ..
cp .env.example .env             # put your OpenRouter key in it
./dev.sh                         # Windows: ./dev.ps1
```

Open http://localhost:5173, click **auto-fill**, then **Start**. Turn on **Demo mode** to try it with scripted players and no API calls.

## What it costs

From 14 finished games at OpenRouter's October 2026 prices, a typical 8-player game costs about **$1.70** (anywhere from $0.53 to $5.02), makes about 250 LLM calls and takes about 7 minutes. The bill is the sum of the seats:

| Model | One seat, one game |
|---|---|
| Claude Sonnet 5.5 | $1.06 |
| Grok 4.7 | $0.35 |
| Kimi K3.1 Pro | $0.22 |
| GPT-6.1 Sol | $0.14 |
| Claude Haiku 5.5 | $0.06 |
| DeepSeek V4.1 Flash | $0.01 |

Each game pauses at a $10 cap by default. To skip a pricey model, set `enabled: false` on it in `config/models.yaml`.

## Extras

- `uv run python scripts/run_batch.py --games 5 --budget 10` plays games headless; replay them later from History.
- `uv run python scripts/stats.py` prints per-model tables: wins, wolf-spotting, honesty, talk style and cost.
- `scripts/export_games.py` and `scripts/import_games.py` share games through [community/](community/README.md).
- Set `MUSIC_DIR` in `.env` to a folder of your own mp3s for background music (see `config/music.yaml`).

Contributions are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md). MIT licensed.

Have fun. 🐺
