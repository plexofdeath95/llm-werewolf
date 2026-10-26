"""Find a game's highlight-worthy moments as windows of video time.

Priority 0 always stays (intro, night walks, deaths, vote results, last words, game over,
and hand-picked lines), then role claims, interrupts and wolf-den plotting, then the most
urgent other lines.
"""
import json
import sqlite3
from bisect import bisect_left
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NIGHT_MAX = 30.0  # seconds of each night's walk-to-houses sequence kept at 1x
VOICE_CPS = 9.0   # the replay's voices speak about 9 characters a second at 1x
SHOWN = {"speech", "moderator", "narration", "phase", "death", "reveal", "vote", "vote_result",
         "game_over"}


def load(game: str) -> tuple[list[dict], list[float], list[int]]:
    db = sqlite3.connect(ROOT / "data" / "games.db")
    events = [{"seq": s, "kind": k, "text": x, "data": json.loads(d)} for s, k, x, d in db.execute(
        "select seq, kind, text, data from game_events where game_id=? order by seq", (game,))]
    tl = json.loads((ROOT / "data" / "videos" / game / "timeline.json").read_text("utf-8"))
    return events, [t for t, _ in tl], [n for _, n in tl]


def moments(events: list[dict], ts: list[float], revealed: list[int],
            picks: set[int] = frozenset()) -> list[tuple]:
    """(start, end, priority, weight) windows in video seconds; `picks` are hand-chosen
    SPEECH seqs that always stay."""
    def at(seq: int) -> float:
        return ts[min(bisect_left(revealed, seq), len(ts) - 1)]
    end = ts[-1]
    shown = [e for e in events if e["kind"] in SHOWN]
    out = [(0.0, 6.0, 0, 0)] + nights(events, at)
    for i, e in enumerate(shown):
        t, d = at(e["seq"]), e["data"]
        nxt = at(shown[i + 1]["seq"]) if i + 1 < len(shown) else end
        if e["kind"] == "phase":
            out.append((t - 0.5, t + 3, 1, 0))
        elif e["kind"] == "death":
            out.append((t - 1, t + 7, 0, 0))
        elif e["kind"] == "vote_result":
            out.append((t - 6, t + 4, 0, 0))
        elif e["kind"] == "game_over":
            out.append((t - 2, end, 0, 0))
        elif e["kind"] == "speech":
            den = d.get("channel") == "wolf den"
            prio = 0 if d.get("channel") == "last words" or e["seq"] in picks else \
                1 if d.get("claim") or d.get("interrupt") or den else 2
            voice = len(e["text"]) / VOICE_CPS + 1.0  # spoken length, not the pause after
            out.append((t - 0.3, min(nxt, t + voice), prio, d.get("urgency", 0)))
    return [(max(0.0, a), min(end, b), p, w) for a, b, p, w in out if b > a]


def nights(events: list[dict], at) -> list[tuple]:
    """Each night's walk-to-houses sequence: from its first action until dawn (capped)."""
    out, first = [], None
    for e in events:
        acted = e["kind"] == "action" and e["data"].get("channel") == "night" \
            and e["data"].get("action") != "result"
        if acted and first is None:
            first = at(e["seq"])
        elif e["kind"] == "phase" and e["data"].get("phase") == "dawn" and first is not None:
            out.append((first - 1, min(at(e["seq"]) + 1, first + NIGHT_MAX), 0, 0))
            first = None
    return out
