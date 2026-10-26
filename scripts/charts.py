"""Draw the insight charts from data/games.db as standalone SVG files.

Usage: uv run python scripts/charts.py [--out data/charts] [--game GAME_ID] [--include-fake]

Writes wolf-reads.svg, claims.svg, cost-per-seat.svg, moods.svg and heat-<game>.svg (the most
recent finished game unless --game is given). Open them in a browser or drop them in a README.
"""
import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aiplays.core.hub import get_hub
from aiplays.modes.werewolf.insights import minds, moods, svg, svg_grids, talk
from aiplays.modes.werewolf.insights.heat import heat
from aiplays.modes.werewolf.insights.load import load_games
from aiplays.settings import get_catalog


def label(model: str) -> str:
    try:
        return get_catalog().get(model).label
    except KeyError:
        return model


async def main(a: argparse.Namespace) -> None:
    repo = get_hub().repo
    await repo.init()
    games = await load_games(repo, include_fake=a.include_fake)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    sus, tk = minds.suspicion(games), talk.per_model(games)
    reads = sorted(((m, c) for m, c in sus["models"].items() if c["reads"]), key=lambda x: -x[1]["hits"] / x[1]["reads"])
    rows = [(label(m), 100 * c["hits"] / c["reads"], f"{round(100 * c['hits'] / c['reads'])}%", f"{c['reads']} reads")
            for m, c in reads]
    base = 100 * sus["baseline"]
    files = {"wolf-reads.svg": svg.bars(
        "Who spots the wolves?", f"When a villager named a prime suspect, how often was it a real wolf · {len(games)} games",
        rows, marker=(base, f"random pick {round(base)}%"))}
    claimers = sorted((m for m in tk if tk[m]["claims_village"] + tk[m]["claims_wolves"]),
                      key=lambda m: -tk[m]["claims_village"])
    files["claims.svg"] = svg_grids.claims(
        [(label(m), tk[m]["honest_village"], tk[m]["claims_village"], tk[m]["honest_wolves"],
          tk[m]["claims_wolves"]) for m in claimers],
        "Role claims, checked against the real card", "Every public role claim, as a villager and as a wolf")
    costs = sorted(((m, t["cost_usd"] / t["seats"]) for m, t in tk.items() if t["seats"]), key=lambda x: -x[1])
    files["cost-per-seat.svg"] = svg.bars(
        "What one seat costs per game", "Average API cost of one player for a whole game (local models are free)",
        [(label(m), v, f"${v:.2f}", "") for m, v in costs], highlight=None)
    mood = moods.moods_by_model(games)
    files["moods.svg"] = svg_grids.moods({label(m): v for m, v in mood.items()}, list(moods.MOODS))
    finished = [g for g in games if g.status == "finished"]
    game = next((g for g in games if g.id.startswith(a.game)), None) if a.game else (finished or games)[-1]
    if game:
        files[f"heat-{game.id[:8]}.svg"] = svg_grids.heatmap(game, heat(game))
    for name, body in files.items():
        (out / name).write_text(body, encoding="utf-8")
        print(out / name)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent.parent / "data" / "charts"))
    ap.add_argument("--game", default="", help="game id (or prefix) for the heat map")
    ap.add_argument("--include-fake", action="store_true")
    asyncio.run(main(ap.parse_args()))
