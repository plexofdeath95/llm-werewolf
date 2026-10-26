"""Werewolf insights from data/games.db: what the models suspected, claimed, felt and said.

Usage: uv run python scripts/insights.py tables [--csv DIR] [--include-fake]
       uv run python scripts/insights.py heat GAME_ID
       uv run python scripts/insights.py quotes [--kind last-words|wolf-den|one-liners|thoughts]
                                                [--model kimi] [--grep REGEX] [--limit 40]

Games with fewer than 8 spoken lines (aborted runs) are skipped. Import shared games first
(scripts/import_games.py) to analyse them too.
"""
import argparse
import asyncio
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from stats import show  # scripts/stats.py: the same plain-text table printer

from aiplays.core.hub import get_hub
from aiplays.modes.werewolf.insights.heat import heat, render
from aiplays.modes.werewolf.insights.load import load_games
from aiplays.modes.werewolf.insights.quotes import KINDS, mine
from aiplays.modes.werewolf.insights.tables import tables


def save_csv(folder: str, title: str, cols: list, rows: list) -> None:
    Path(folder).mkdir(parents=True, exist_ok=True)
    name = "".join(c if c.isalnum() else "_" for c in title.lower())[:50].strip("_")
    with open(Path(folder) / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([cols, *rows])


async def main(a: argparse.Namespace) -> None:
    repo = get_hub().repo
    await repo.init()
    games = await load_games(repo, include_fake=a.include_fake,
                             min_speeches=0 if a.cmd == "heat" else 8)
    if a.cmd == "tables":
        print(f"{len(games)} games, {sum(g.status == 'finished' for g in games)} finished")
        for title, (cols, rows) in tables(games).items():
            show(title, cols, rows)
            if a.csv:
                save_csv(a.csv, title, cols, rows)
    elif a.cmd == "heat":
        game = next((g for g in games if g.id.startswith(a.game)), None)
        if not game:
            sys.exit(f"no game {a.game}")
        print(f"Game {game.id} ({game.winner or game.status}): suspicion after every line\n")
        print(render(game, heat(game)))
    else:
        quotes = mine(games, a.kind or KINDS, a.model, a.grep)
        for q in quotes[-a.limit:]:
            print(f"[{q.game[:8]}#{q.seq} {q.model} · {q.name}, {q.role} · {q.kind}]\n  {q.text}\n")
        print(f"{len(quotes)} matching quote(s), showing the last {min(a.limit, len(quotes))}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-fake", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("tables").add_argument("--csv", default="", help="also save each table as CSV here")
    sub.add_parser("heat").add_argument("game", help="game id or its first characters")
    q = sub.add_parser("quotes")
    q.add_argument("--kind", action="append", choices=KINDS)
    q.add_argument("--model", default="", help="model id substring, e.g. kimi")
    q.add_argument("--grep", default="", help="regular expression to match")
    q.add_argument("--limit", type=int, default=40)
    asyncio.run(main(ap.parse_args()))
