"""Map a rendered replay video to game events: read how far the replay bar's gold fill has
advanced, twice a second, and save [(video seconds, events revealed)] as timeline.json.

Usage: uv run python scripts/video_timeline.py GAME_ID
"""
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from video_tools import OUT, ROOT, ffmpeg

BAR_Y, BAR_X0, FPS, W = 1000, 70, 2, 1920  # 1920x1080 layout: replay bar row and its start


def _gold(row: np.ndarray) -> np.ndarray:
    r, g, b = row[:, 0].astype(int), row[:, 1].astype(int), row[:, 2].astype(int)
    return (r > 190) & (g > 130) & (g < 215) & (b < 125)


def fill_ends(video: Path) -> list[int]:
    """Right end (x) of the gold fill in each sampled frame."""
    raw = subprocess.run([ffmpeg(), "-v", "error", "-i", str(video), "-vf",
                          f"fps={FPS},crop={W}:2:0:{BAR_Y}", "-f", "rawvideo", "-pix_fmt",
                          "rgb24", "-"], capture_output=True, check=True).stdout
    rows = np.frombuffer(raw, np.uint8).reshape(-1, 2, W, 3)[:, 0]  # 4:2:0 needs even crops
    ends = []
    for row in rows:
        xs = np.where(_gold(row)[BAR_X0:])[0]
        ends.append(BAR_X0 + int(xs.max()) if len(xs) else BAR_X0)
    return ends


def build(game: str) -> list[tuple[float, int]]:
    total = sqlite3.connect(ROOT / "data" / "games.db").execute(
        "select count(*) from game_events where game_id=?", (game,)).fetchone()[0]
    ends = fill_ends(OUT / f"{game}.mp4")
    full = max(ends)  # the replay reaches the last event before the video ends
    best, out = 0, []
    for i, x in enumerate(ends):
        revealed = round((x - BAR_X0) / max(1, full - BAR_X0) * total)
        best = max(best, revealed)  # the bar only moves forward in a straight replay
        out.append((i / FPS, best))
    return out


if __name__ == "__main__":
    gid = sys.argv[1]
    timeline = build(gid)
    path = OUT / gid / "timeline.json"
    path.write_text(json.dumps(timeline), encoding="utf-8")
    print(f"{len(timeline)} samples -> {path}; last: {timeline[-1]}")
