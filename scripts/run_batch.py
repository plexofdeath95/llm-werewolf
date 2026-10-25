"""Run games headless (same engine as the UI) to build a benchmark dataset; replay in the UI.

Usage: uv run python scripts/run_batch.py --games 3 --players 8 [--style mixed|classic]
       [--models a,b,c] [--fake] [--max-cost 10] [--parallel 1]
"""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aiplays.core.config import GameConfig, SeatConfig  # noqa: E402
from aiplays.core.hub import get_hub  # noqa: E402
from aiplays.core.mode import get_mode  # noqa: E402
from aiplays.settings import get_catalog, get_settings  # noqa: E402


def config(args: argparse.Namespace, i: int) -> GameConfig:
    models = args.models.split(",") if args.models else get_catalog().roster(args.players)
    seats = [SeatConfig(model_id=models[k % len(models)]) for k in range(args.players)]
    deck = get_mode("werewolf").default_deck(args.players, style=args.style)
    return GameConfig(seats=seats, deck=deck, fake=args.fake, fake_delay=0,
                      max_cost_usd=args.max_cost, seed=None if args.seed is None
                      else args.seed + i)


async def one(args: argparse.Namespace, i: int, sem: asyncio.Semaphore) -> None:
    async with sem:
        hub = get_hub()
        s = await hub.start(config(args, i))
        await s.task
        won = [p.name for p in s.state.players if p.won]
        print(f"game {s.id}: {s.state.winner} won after {s.state.round} rounds, "
              f"${s.budget.spent:.2f}; winners: {', '.join(won)}", flush=True)


async def main(args: argparse.Namespace) -> None:
    get_settings()
    await get_hub().repo.init()
    sem = asyncio.Semaphore(args.parallel)
    await asyncio.gather(*(one(args, i, sem) for i in range(args.games)))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=1)
    ap.add_argument("--players", type=int, default=get_catalog().default_players)
    ap.add_argument("--style", default="mixed", choices=["mixed", "classic"])
    ap.add_argument("--models", default="")
    ap.add_argument("--fake", action="store_true")
    ap.add_argument("--max-cost", type=float, default=10.0)
    ap.add_argument("--parallel", type=int, default=1)
    ap.add_argument("--seed", type=int, default=None)
    asyncio.run(main(ap.parse_args()))
