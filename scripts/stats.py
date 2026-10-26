"""Print the per-model benchmark tables (see aiplays/db/stats.py for the queries).

Usage: uv run python scripts/stats.py [--include-fake]
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aiplays.core.hub import get_hub
from aiplays.db.stats import report


def show(title: str, cols: list[str], rows: list[list]) -> None:
    widths = [max(len(str(x)) for x in [c, *(r[i] for r in rows)]) for i, c in enumerate(cols)]
    print(f"\n## {title}")
    print("  ".join(c.ljust(w) for c, w in zip(cols, widths)))
    for r in rows:
        print("  ".join(str(x).ljust(w) for x, w in zip(r, widths)))
    if not rows:
        print("(no data yet)")


async def main(include_fake: bool) -> None:
    for title, t in (await report(get_hub().repo, include_fake)).items():
        show(title, t["columns"], t["rows"])


if __name__ == "__main__":
    asyncio.run(main("--include-fake" in sys.argv))
