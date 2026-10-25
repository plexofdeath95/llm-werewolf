"""Drive the game UI in a visible Edge window (Playwright): screenshots, console errors,
jitter of floating labels, and a click test. Dev tool for UI work.

Usage: uv run python scripts/ui_snap.py [--game ID] [--shots 6] [--every 4] [--click Alice]
       (no --game: starts a fake 8-player game first)
"""
import argparse
import json
import statistics
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

UI, API = "http://localhost:5173", "http://127.0.0.1:8000"
OUT = Path(__file__).resolve().parent.parent / "data" / "ui_snaps"


def new_fake_game() -> str:
    roster = json.load(urllib.request.urlopen(f"{API}/api/roster?n=8"))
    body = json.dumps({"seats": [{"model_id": m} for m in roster], "fake": True,
                       "fake_delay": 1.5, "seed": 7}).encode()
    req = urllib.request.Request(f"{API}/api/games", body, {"content-type": "application/json"})
    return json.load(urllib.request.urlopen(req))["id"]


def label_boxes(page) -> dict[str, tuple[float, float]]:
    """Centre of every name tag, keyed by its text: lets us measure on-screen jitter."""
    boxes = {}
    for tag in page.locator(".nametag").all():
        b = tag.bounding_box()
        if b:
            boxes[tag.inner_text().split("\n")[0]] = (b["x"] + b["width"] / 2, b["y"])
    return boxes


def main(a: argparse.Namespace) -> None:
    game = a.game or new_fake_game()
    OUT.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge", headless=False)
        page = browser.new_page(viewport={"width": a.width, "height": a.height})
        page.on("console", lambda m: m.type == "error" and errors.append(m.text))
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(f"{UI}/game/{game}")
        page.wait_for_timeout(3000)
        tracks: dict[str, list[tuple[float, float]]] = {}
        for i in range(a.shots):
            for name, xy in label_boxes(page).items():
                tracks.setdefault(name, []).append(xy)
            page.screenshot(path=OUT / f"shot_{i}.png")
            page.wait_for_timeout(a.every * 1000)
        if a.click:
            tag = page.locator(".nametag", has_text=a.click).first
            try:
                box = tag.bounding_box()  # rest the pointer first: the camera holds still
                page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                page.wait_for_timeout(400)
                tag.click(timeout=3000)
                page.wait_for_timeout(800)
                print("click ok; mind panel mentions name:",
                      a.click in (page.locator(".mind").first.inner_text(timeout=2000)))
            except Exception as e:
                print("CLICK FAILED:", str(e).splitlines()[0])
            page.screenshot(path=OUT / "after_click.png")
            page.wait_for_timeout(400)
            tip = page.locator(".tooltip")
            print("tooltip on hover:", tip.inner_text()[:80].replace("\n", " | ")
                  if tip.count() else "NONE")
            page.screenshot(path=OUT / "hover.png")
        browser.close()
    print("game:", game, "| shots in", OUT)
    for name, pts in tracks.items():
        if len(pts) > 1:
            dx = statistics.pstdev(p[0] for p in pts)
            dy = statistics.pstdev(p[1] for p in pts)
            print(f"jitter {name:12} dx={dx:6.1f}px dy={dy:6.1f}px")
    print("console errors:", len(errors), *errors[:5], sep="\n  ")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", default="")
    ap.add_argument("--shots", type=int, default=6)
    ap.add_argument("--every", type=float, default=4)
    ap.add_argument("--click", default="Alice")
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--height", type=int, default=900)
    main(ap.parse_args())
