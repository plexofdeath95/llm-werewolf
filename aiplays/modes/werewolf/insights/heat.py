"""Suspicion heat map of one game: after every public discussion line, how many living players
name each player as their prime suspect (None once that player is out)."""
from collections import Counter

from aiplays.modes.werewolf.insights.load import Game

SHADES = " .:-=+*#%@"  # 0..9 suspecters, for the text rendering


def heat(game: Game) -> list[dict]:
    """One column per public discussion line: {day, seq, speaker, counts: {name: int | None}}."""
    names = game.by_name
    latest, dead, cols, day = {}, set(), [], 0
    for e in game.events:
        if e.kind == "death":
            dead.add(e.target)
        if e.kind == "phase" and e.data.get("phase") == "discussion":
            day += 1
        if e.kind == "reaction" and e.data.get("suspect") in names and e.actor not in dead:
            latest[e.actor] = names[e.data["suspect"]]
        if e.kind == "speech" and e.phase == "discussion" and \
                e.data.get("channel", "public") == "public" and e.actor in game.seats:
            counts = Counter(t for a, t in latest.items() if a not in dead)
            cols.append({"day": day, "seq": e.seq, "speaker": game.seats[e.actor].name,
                         "counts": {s.name: None if pid in dead else counts.get(pid, 0)
                                    for pid, s in game.seats.items()}})
    return cols


def render(game: Game, cols: list[dict]) -> str:
    """Text heat map: a row per player, a character per line; ' ' = nobody, '@' = 9+, x = out."""
    width = max(len(s.name) + len(s.role) for s in game.seats.values()) + 4
    days = [c["day"] for c in cols]
    head = "".join("|" if i and days[i] != days[i - 1] else " " for i in range(len(cols)))
    rows = [" " * width + head]
    for s in game.seats.values():
        cells = "".join("x" if c["counts"][s.name] is None
                        else SHADES[min(c["counts"][s.name], 9)] for c in cols)
        wolf = "*" if s.team == "wolves" else " "
        rows.append(f"{s.name} {s.role}{wolf}".ljust(width) + cells)
    return "\n".join(rows + ["", "* = wolf team, x = out of the game, | = new day"])
