"""Shared helpers for the video scripts: paths, ffmpeg lookup, system-audio loopback."""
import glob
import os
import shutil
import threading
import time
import wave
from pathlib import Path

import numpy as np
import soundcard as sc

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "videos"
RATE = 48000


def ffmpeg() -> str:
    found = shutil.which("ffmpeg") or next(iter(glob.glob(os.path.expandvars(
        r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\*FFmpeg*\**\bin\ffmpeg.exe"), recursive=True)), None)
    if not found:
        raise SystemExit("ffmpeg not found: install it (winget install Gyan.FFmpeg)")
    return found


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
