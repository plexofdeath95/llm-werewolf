"""Import shared game files into data/games.db so they replay in the UI and count in stats.

Usage: uv run python scripts/import_games.py [FILE ...] [--check]

Without files it imports everything in community/games/. Games already in the DB are skipped.
--check only validates the files (use it before opening a pull request).
"""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aiplays.core.hub import get_hub
from aiplays.db.share import check, import_game, read

ROOT = Path(__file__).resolve().parent.parent


async def main(args: argparse.Namespace) -> int:
    files = [Path(f) for f in args.files] or sorted((ROOT / "community" / "games").glob("*.json.gz"))
    repo = None if args.check else get_hub().repo
    if repo:
        await repo.init()
    added = skipped = bad = 0
    for path in files:
        try:
            doc = read(path)
            gid = check(doc)
            if repo and await import_game(repo, doc):
                added += 1
            else:
                skipped += 0 if args.check else 1
            print(f"ok   {path.name}: {gid}, {doc['game']['status']}, {len(doc['events'])} events")
        except Exception as e:  # noqa: BLE001 - report every broken file, not just the first
            bad += 1
            print(f"FAIL {path.name}: {e}")
    print(f"{len(files)} file(s): {added} imported, {skipped} already here, {bad} invalid")
    return 1 if bad else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--check", action="store_true")
    sys.exit(asyncio.run(main(ap.parse_args())))
