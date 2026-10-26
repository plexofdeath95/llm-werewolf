"""Grid-style SVG charts: role-claim units, a suspicion heat map and a mood grid."""
from aiplays.modes.werewolf.insights.load import Game
from aiplays.modes.werewolf.insights.svg import (
    GOLD,
    INK,
    LINE,
    MUTE,
    RAMP,
    SOFT,
    VILL,
    WOLF,
    card,
    rect,
    text,
)


def claims(rows: list[tuple[str, int, int, int, int]], title: str, subtitle: str) -> str:
    """rows: (label, honest as village, claims as village, honest as wolf, claims as wolf)."""
    xv, xw, step, y0, pitch = 190, 900, 23, 140, 44
    body = [text(xv, y0 - 16, "AS A VILLAGER", 15, GOLD, weight=700),
            text(xw, y0 - 16, "AS A WOLF", 15, GOLD, weight=700)]
    for i, (label, vok, vn, wok, wn) in enumerate(rows):
        y = y0 + i * pitch
        body.append(text(xv - 20, y + 20, label, 17, INK, "end"))
        for x0, ok, n in ((xv, vok, vn), (xw, wok, wn)):
            body += [rect(x0 + k * step, y + 4, 19, 22, VILL if k < ok else WOLF, 3) for k in range(min(n, 30))]
            body.append(text(x0 + min(n, 30) * step + 8, y + 21, f"{ok} of {n}", 15, MUTE))
    end = y0 + len(rows) * pitch
    body += [rect(40, end + 14, 18, 18, VILL, 3), text(66, end + 29, "honest claim", 15, SOFT),
             rect(190, end + 14, 18, 18, WOLF, 3), text(216, end + 29, "bluff", 15, SOFT)]
    return card(1280, end + 56, title, subtitle, body)


def heatmap(game: Game, cols: list[dict]) -> str:
    x0, gap, y0, rh = 250, 12, 150, 34
    days = sorted({c["day"] for c in cols})
    cw = (1240 - x0 - gap * (len(days) - 1)) / max(1, len(cols))
    xs = [x0 + i * cw + days.index(c["day"]) * gap for i, c in enumerate(cols)]
    firsts = {d: xs[[c["day"] for c in cols].index(d)] for d in days}
    body = [text(x, y0 - 14, f"DAY {d}", 15, GOLD, weight=700) for d, x in firsts.items()]
    for r, s in enumerate(game.seats.values()):
        y = y0 + r * rh
        role = s.role.replace("_", " ").title() + (" (wolf)" if s.team == "wolves" else "")
        body.append(text(x0 - 16, y + 21, f"{s.name} · {role}", 15, WOLF if s.team == "wolves" else INK, "end"))
        for x, c in zip(xs, cols):
            v = c["counts"][s.name]
            body.append(rect(x + 1, y + 2, cw - 2, rh - 6, LINE if v is None else RAMP[min(v, 5)], 2,
                             ' opacity="0.35"' if v is None else ""))
    end = y0 + len(game.seats) * rh
    body += [text(40, end + 34, "suspicion:", 15, MUTE)]
    body += [rect(120 + 30 * i, end + 21, 26, 16, c, 2) for i, c in enumerate(RAMP)]
    body.append(text(308, end + 34, "0 to 5+ players · faded = out of the game", 15, MUTE))
    winner = f", {game.winner} win" if game.winner else ""
    return card(1280, end + 60, "Who the table suspected, after every line",
                f"Game {game.id[:8]}{winner}: each cell counts the living players naming that person", body)


def moods(rows: dict[str, dict[str, int]], words: list[str]) -> str:
    x0, y0, rh = 230, 130, 46
    cw = (1240 - x0) / len(words)
    step = lambda v: 0 if v < 5 else 1 if v < 15 else 2 if v < 25 else 3 if v < 35 else 4 if v < 50 else 5
    body = [text(x0 + (i + 0.5) * cw, y0 - 14, w.title(), 15, SOFT, "middle", 700) for i, w in enumerate(words)]
    for r, (label, vals) in enumerate(rows.items()):
        y = y0 + r * rh
        body.append(text(x0 - 16, y + 27, label, 17, INK, "end"))
        for i, w in enumerate(words):
            v = vals[w]
            body += [rect(x0 + i * cw + 2, y + 2, cw - 4, rh - 6, RAMP[step(v)], 4),
                     text(x0 + (i + 0.5) * cw, y + 28, v, 17, "#161b26" if step(v) >= 3 else INK, "middle", 700)]
    return card(1280, y0 + len(rows) * rh + 30, "Mood words in their private thoughts",
                "Mentions per 100 private thoughts (simple word lists; brighter = more)", body)
