"""Cut a rendered game into a short highlight reel with ffmpeg.

Key moments play at 1x with their own voices and music; the stretches between them are
fast-forwarded (with a ">> 12x" badge), audio included: pitched up like a tape on fast-forward,
so the players chatter like chipmunks.

Usage: uv run python scripts/highlights.py GAME_ID [--minutes 4]
Needs data/videos/<id>.mp4 (render_video.py) and <id>/timeline.json (video_timeline.py).
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from highlight_plan import FAST, GAP_MAX, SPEED, load, moments, plan  # noqa: E402
from video_tools import OUT, ffmpeg  # noqa: E402

FONT = "C\\:/Windows/Fonts/arialbd.ttf"
FADE = 0.06
RATE = 48000
PITCH = 2.0  # chipmunk factor; the rest of the speed-up is time-compression (atempo)


def _tempo(factor: float) -> str:
    """atempo takes at most 100x per filter, so chain it for bigger speed-ups."""
    steps = []
    while factor > 100:
        steps.append("atempo=100")
        factor /= 100
    return ",".join(steps + [f"atempo={max(0.5, factor):.4f}"])


def graph(segments: list[tuple[str, float, float]]) -> str:
    lines, labels = [], []
    for i, (kind, a, b) in enumerate(segments):
        dur, video = b - a, f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS"
        if kind == FAST:
            speed = max(SPEED, dur / GAP_MAX)
            dur = dur / speed
            badge = (f"drawtext=fontfile='{FONT}':text='>> {speed:.0f}x':x=w-tw-48:y=150:"
                     "fontsize=46:fontcolor=white:box=1:boxcolor=black@0.55:boxborderw=14")
            video += f",setpts=PTS/{speed:.4f},{badge}"
            pitch = min(PITCH, speed)
            audio = (f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS,"
                     f"asetrate={RATE * pitch:.0f},aresample={RATE},{_tempo(speed / pitch)},"
                     "volume=0.8")
        else:
            audio = f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS"
        fade = f"afade=t=in:d={FADE},afade=t=out:st={max(0.0, dur - FADE):.3f}:d={FADE}"
        lines += [f"{video},fps=30,format=yuv420p[v{i}]", f"{audio},{fade}[a{i}]"]
        labels.append(f"[v{i}][a{i}]")
    lines.append("".join(labels) + f"concat=n={len(segments)}:v=1:a=1[v][a]")
    return ";\n".join(lines)


def main(a: argparse.Namespace) -> None:
    events, ts, revealed = load(a.game)
    segments = plan(moments(events, ts, revealed), ts[-1], a.minutes * 60)
    work = OUT / a.game
    script = work / "highlights.ffgraph"
    script.write_text(graph(segments), encoding="utf-8")
    out = OUT / f"{a.game}_highlights.mp4"
    kept = sum(b - x for k, x, b in segments if k != FAST)
    print(f"{len(segments)} segments, {kept:.0f}s at 1x -> {out}")
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(OUT / f"{a.game}.mp4"),
                    "-/filter_complex", str(script), "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac",
                    "-b:a", "192k", "-movflags", "+faststart", str(out)], check=True)
    print(f"done: {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("game")
    ap.add_argument("--minutes", type=float, default=4.0)
    main(ap.parse_args())
