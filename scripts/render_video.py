"""Render a stored game's replay to an MP4 with sound: a visible Edge window recorded by
Playwright, plus a loopback recording of what the PC plays (voices + music), muxed by ffmpeg.

Usage: uv run python scripts/render_video.py [GAME_ID] [--size 1920x1080] [--speed 1]
Keep other sounds off while it renders: the audio track is whatever the speakers play.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import threading
import time
import urllib.request
import wave
from pathlib import Path

import numpy as np
import soundcard as sc
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "videos"
UI, API, RATE = "http://localhost:5173", "http://127.0.0.1:8000", 48000


class LoopbackRecorder(threading.Thread):
    """Records the default speaker's output to a 16-bit stereo WAV until stopped."""

    def __init__(self, path: Path):
        super().__init__(daemon=True)
        self.path, self.stop, self.started_at = path, threading.Event(), None

    def run(self) -> None:
        mic = sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True)
        with mic.recorder(samplerate=RATE, channels=2) as rec, wave.open(str(self.path), "wb") as w:
            w.setnchannels(2), w.setsampwidth(2), w.setframerate(RATE)
            self.started_at = time.monotonic()
            while not self.stop.is_set():
                chunk = np.clip(rec.record(numframes=RATE // 10), -1, 1)
                w.writeframes((chunk * 32767).astype("<i2").tobytes())


def latest_finished() -> str:
    games = json.load(urllib.request.urlopen(f"{API}/api/games"))
    return next(g["id"] for g in games if g["status"] == "finished")


def ffmpeg() -> str:
    found = shutil.which("ffmpeg") or next(iter(glob.glob(os.path.expandvars(
        r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\*FFmpeg*\**\bin\ffmpeg.exe"), recursive=True)), None)
    if not found:
        raise SystemExit("ffmpeg not found: install it (winget install Gyan.FFmpeg)")
    return found


def record(game: str, w: int, h: int, speed: str, work: Path) -> tuple[Path, float, LoopbackRecorder]:
    audio = LoopbackRecorder(work / "audio.wav")
    audio.start()
    while audio.started_at is None:
        time.sleep(0.05)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge", headless=False,
                                     args=["--autoplay-policy=no-user-gesture-required"])
        ctx = browser.new_context(viewport={"width": w, "height": h}, record_video_dir=str(work),
                                  record_video_size={"width": w, "height": h})
        video_t0 = time.monotonic()
        page = ctx.new_page()
        page.goto(f"{UI}/game/{game}")
        page.wait_for_timeout(2500)
        page.mouse.click(w // 2, h // 3)  # a user gesture: lets music and voices play
        page.locator(".controls select").first.select_option(speed)
        page.wait_for_selector(".gameover", timeout=90 * 60_000)
        page.wait_for_timeout(8000)  # linger on the winner card
        video = page.video
        ctx.close()  # finalises the .webm
        browser.close()
        return Path(video.path()), video_t0 - audio.started_at, audio


def main(a: argparse.Namespace) -> None:
    game = a.game or latest_finished()
    w, h = (int(x) for x in a.size.split("x"))
    work = OUT / game
    work.mkdir(parents=True, exist_ok=True)
    print(f"rendering game {game} at {w}x{h}, {a.speed}x (keep other audio off)...")
    webm, offset, audio = record(game, w, h, a.speed, work)
    audio.stop.set()
    audio.join()
    out = OUT / f"{game}.mp4"
    subprocess.run([ffmpeg(), "-y", "-loglevel", "error", "-i", str(webm),
                    "-ss", f"{max(0.0, offset):.3f}", "-i", str(work / "audio.wav"),
                    "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", str(out)], check=True)
    print(f"done: {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("game", nargs="?", default="")
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--speed", default="1", help="playback speed: 0.5, 1, 2, 4 or 8")
    main(ap.parse_args())
