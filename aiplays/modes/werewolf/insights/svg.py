"""Standalone SVG charts on a dark card (reads well in light and dark viewers): primitives,
the card itself and a horizontal bar chart."""
from collections.abc import Iterable

BG, INK, SOFT, MUTE, GOLD = "#10141f", "#f1ece2", "#aab3c5", "#8a93a6", "#f2b544"
SLATE, LINE, WOLF, VILL = "#5b6785", "#2b3448", "#d9722c", "#3f8fe0"
RAMP = ["#232a3c", "#3d3a36", "#6b5330", "#c48a2e", "#e0a23a", "#f8cf6a"]  # 0 .. 5+
FONT = "Segoe UI, Helvetica, Arial, sans-serif"


def esc(t) -> str:
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, t, size=16, color=INK, anchor="start", weight=400) -> str:
    return (f'<text x="{x:.0f}" y="{y:.0f}" font-size="{size}" fill="{color}" '
            f'text-anchor="{anchor}" font-weight="{weight}">{esc(t)}</text>')


def rect(x, y, w, h, fill, rx=4, extra="") -> str:
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}"{extra}/>')


def card(width: int, height: int, title: str, subtitle: str, body: Iterable[str]) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" font-family="{FONT}">{rect(0, 0, width, height, BG, 16)}'
            f'{text(40, 52, title, 28, INK, weight=700)}{text(40, 82, subtitle, 16, SOFT)}'
            + "".join(body) + "</svg>")


def bars(title: str, subtitle: str, rows: list[tuple[str, float, str, str]], *,
         highlight: int | None = 0, scale: float | None = None, marker: tuple[float, str] | None = None,
         width: int = 1200) -> str:
    """rows: (label, value, value text, note). `marker` draws a dashed reference line."""
    x0, y0, pitch = 200, 120, 54
    top = max([v for _, v, _, _ in rows] + [marker[0] if marker else 0]) or 1
    sc = scale or (width - x0 - 260) / top
    body = []
    for i, (label, v, vt, note) in enumerate(rows):
        y, w = y0 + i * pitch, max(v * sc, 3)
        body += [text(x0 - 16, y + 23, label, 17, INK, "end"),
                 rect(x0, y, w, 32, GOLD if i == highlight else SLATE),
                 text(x0 + w + 12, y + 23, vt, 17, INK, weight=700),
                 text(x0 + w + 22 + 11 * len(vt), y + 23, note, 15, MUTE)]
    end = y0 + len(rows) * pitch
    if marker:
        mx = x0 + marker[0] * sc
        body += [(f'<line x1="{mx:.0f}" y1="{y0 - 10}" x2="{mx:.0f}" y2="{end}" stroke="{INK}" '
                  f'stroke-width="2" stroke-dasharray="7 6" opacity="0.7"/>'),
                 text(mx, end + 24, marker[1], 15, MUTE, "middle")]
    return card(width, end + (50 if marker else 30), title, subtitle, body)
