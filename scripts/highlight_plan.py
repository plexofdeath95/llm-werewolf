"""Choose a highlight reel's segments from a game's events and its video timeline.

Key moments play at 1x with their voices; everything between them is fast-forwarded.
Priority 0 always stays (intro, deaths, vote results, last words, game over), then role
claims and interrupts, then the most urgent other lines, until the time budget is used.
"""
import json
import sqlite3
from bisect import bisect_left
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEEP, FAST = "keep", "fast"
SPEED, GAP_MAX = 10.0, 2.5  # fast-forward at least 10x, and no gap longer than 2.5s on screen
SHOWN = {"speech", "moderator", "narration", "phase", "death", "reveal", "vote", "vote_result",
         "game_over"}


def load(game: str) -> tuple[list[dict], list[float], list[int]]:
    db = sqlite3.connect(ROOT / "data" / "games.db")
    events = [{"seq": s, "kind": k, "data": json.loads(d)} for s, k, d in db.execute(
        "select seq, kind, data from game_events where game_id=? order by seq", (game,))]
    tl = json.loads((ROOT / "data" / "videos" / game / "timeline.json").read_text("utf-8"))
    return events, [t for t, _ in tl], [n for _, n in tl]


def moments(events: list[dict], ts: list[float], revealed: list[int]) -> list[tuple]:
    """(start, end, priority, weight) windows in video seconds."""
    def at(seq: int) -> float:
        return ts[min(bisect_left(revealed, seq), len(ts) - 1)]
    end = ts[-1]
    shown = [e for e in events if e["kind"] in SHOWN]
    out = [(0.0, 8.0, 0, 0)]
    for i, e in enumerate(shown):
        t, d = at(e["seq"]), e["data"]
        nxt = at(shown[i + 1]["seq"]) if i + 1 < len(shown) else end
        if e["kind"] == "phase":
            out.append((t - 0.5, t + 3, 1, 0))
        elif e["kind"] == "death":
            out.append((t - 1, t + 7, 0, 0))
        elif e["kind"] == "vote_result":
            out.append((t - 10, t + 5, 0, 0))
        elif e["kind"] == "game_over":
            out.append((t - 2, end, 0, 0))
        elif e["kind"] == "speech":
            prio = 0 if d.get("channel") == "last words" else \
                1 if d.get("claim") or d.get("interrupt") else 2
            out.append((t - 0.3, min(nxt, t + 15), prio, d.get("urgency", 0)))
    return [(max(0.0, a), min(end, b), p, w) for a, b, p, w in out if b > a]


def merge(windows: list[tuple]) -> list[tuple[float, float]]:
    spans: list[list[float]] = []
    for a, b, *_ in sorted(windows):
        if spans and a - spans[-1][1] < 1.5:  # tiny gaps aren't worth a fast-forward
            spans[-1][1] = max(spans[-1][1], b)
        else:
            spans.append([a, b])
    return [(a, b) for a, b in spans]


def gap_out(gap: float) -> float:
    return min(GAP_MAX, gap / SPEED)


def runtime(keeps: list[tuple[float, float]], end: float) -> float:
    edges = [0.0] + [x for k in keeps for x in k] + [end]
    gaps = [edges[i + 1] - edges[i] for i in range(0, len(edges), 2)]
    return sum(b - a for a, b in keeps) + sum(gap_out(g) for g in gaps if g > 0)


def plan(windows: list[tuple], end: float, budget: float) -> list[tuple[str, float, float]]:
    chosen: list[tuple] = []
    for prio in (0, 1, 2):
        for w in sorted((w for w in windows if w[2] == prio), key=lambda w: -w[3]):
            if prio == 0 or runtime(merge(chosen + [w]), end) <= budget:
                chosen.append(w)
    segments, cursor = [], 0.0
    for a, b in merge(chosen):
        if a > cursor:
            segments.append((FAST, cursor, a))
        segments.append((KEEP, a, b))
        cursor = b
    if end - cursor > 0.5:
        segments.append((FAST, cursor, end))
    return segments
