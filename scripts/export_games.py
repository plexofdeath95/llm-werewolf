"""Export games from data/games.db as shareable files (community/games/<id>.json.gz).

Usage: uv run python scripts/export_games.py [GAME_ID ...] [--out community/games]
       [--include-unfinished] [--include-fake]

Without ids it exports every finished real game that is not in the folder yet. Ids can be
prefixes (the first 8 characters shown in the UI are enough).
"""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aiplays.core.hub import get_hub
from aiplays.db.share import export_game, write

ROOT = Path(__file__).resolve().parent.parent


def wanted(g: dict, args: argparse.Namespace) -> bool:
    if args.ids:
        return any(g["id"].startswith(i) for i in args.ids)
    return (args.include_unfinished or g["status"] == "finished") and \
        (args.include_fake or not g["config"].get("fake"))


async def main(args: argparse.Namespace) -> None:
    repo = get_hub().repo
    await repo.init()
    out = Path(args.out)
    games = [g for g in await repo.list_games(limit=100_000) if wanted(g, args)]
    done = 0
    for g in games:
        if not args.ids and (out / f"{g['id']}.json.gz").exists():
            continue
        doc = await export_game(repo, g["id"])
        models = sorted({p["model_id"] for p in doc["players"]})
        path = write(doc, out)
        print(f"{path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}: {g['status']}, "
              f"winner {g['winner'] or '-'}, {len(doc['events'])} events, {', '.join(models)}")
        done += 1
    print(f"exported {done} game(s) to {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--out", default=str(ROOT / "community" / "games"))
    ap.add_argument("--include-unfinished", action="store_true")
    ap.add_argument("--include-fake", action="store_true")
    asyncio.run(main(ap.parse_args()))
