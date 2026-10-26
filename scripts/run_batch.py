"""Run games headless (same engine as the UI) to build a benchmark dataset; replay in the UI.

Usage: uv run python scripts/run_batch.py --games 3 --players 8 [--style mixed|classic]
       [--models a,b,c] [--speech caveman] [--fake] [--max-cost 10] [--budget 20] [--parallel 1]

Without --models, every enabled model gets a seat, the extra seats go to random repeats, and
seats are shuffled each game. --budget caps the whole batch: a game only starts while the
spend so far, plus a reserve for each game still running and for the new one, fits under it.
"""
import argparse
import asyncio
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aiplays.core.config import GameConfig, SeatConfig
from aiplays.core.hub import get_hub
from aiplays.core.mode import get_mode
from aiplays.settings import get_catalog, get_settings

RESERVE = 3.0  # rough cost of one 8-player game, held back for every game still running


def models_for(args: argparse.Namespace, rng: random.Random) -> list[str]:
    if args.models:
        return args.models.split(",")
    cat = get_catalog()
    unique = list(dict.fromkeys(cat.roster(len(cat.models))))
    n = args.players
    picked = rng.sample(unique, n) if n <= len(unique) else unique + rng.choices(unique, k=n - len(unique))
    rng.shuffle(picked)
    return picked


def config(args: argparse.Namespace, i: int) -> GameConfig:
    seed = None if args.seed is None else args.seed + i
    models = models_for(args, random.Random(seed))
    seats = [SeatConfig(model_id=models[k % len(models)]) for k in range(args.players)]
    deck = get_mode("werewolf").default_deck(args.players, style=args.style)
    return GameConfig(seats=seats, deck=deck, fake=args.fake, fake_delay=0, seed=seed,
                      max_cost_usd=args.max_cost, speech_style=args.speech or None)


def committed(live: list) -> float:
    return sum(s.budget.spent if s.task.done() else max(s.budget.spent, RESERVE) for s in live)


async def one(args: argparse.Namespace, i: int, sem: asyncio.Semaphore, live: list) -> None:
    async with sem:
        if args.budget and committed(live) + RESERVE > args.budget:
            print(f"game {i + 1}: not started, the ${args.budget:.2f} batch budget is committed", flush=True)
            return
        s = await get_hub().start(config(args, i))
        live.append(s)
        await s.task
        won = [p.name for p in s.state.players if p.won]
        print(f"game {s.id}: {s.state.winner} won after {s.state.round} rounds, "
              f"${s.budget.spent:.2f}; winners: {', '.join(won)}", flush=True)


async def main(args: argparse.Namespace) -> None:
    get_settings()
    await get_hub().repo.init()
    sem, live = asyncio.Semaphore(args.parallel), []
    await asyncio.gather(*(one(args, i, sem, live) for i in range(args.games)))
    print(f"batch done: {len(live)} games, ${sum(s.budget.spent for s in live):.2f} spent", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=1)
    ap.add_argument("--players", type=int, default=get_catalog().default_players)
    ap.add_argument("--style", default="mixed", choices=["mixed", "classic"])
    ap.add_argument("--models", default="")
    ap.add_argument("--fake", action="store_true")
    ap.add_argument("--speech", default="", help="speech style id from config/speech_styles.yaml")
    ap.add_argument("--max-cost", type=float, default=10.0)
    ap.add_argument("--budget", type=float, default=0.0, help="total USD for the whole batch (0 = no cap)")
    ap.add_argument("--parallel", type=int, default=1)
    ap.add_argument("--seed", type=int, default=None)
    asyncio.run(main(ap.parse_args()))
