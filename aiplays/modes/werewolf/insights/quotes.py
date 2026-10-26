"""Quote mining: last words, wolf-den chat, short punchy lines and private thoughts."""
import re
from dataclasses import dataclass

from aiplays.modes.werewolf.insights.load import Game

KINDS = ("last-words", "wolf-den", "one-liners", "thoughts")


@dataclass
class Quote:
    game: str
    seq: int
    model: str
    name: str
    role: str
    kind: str
    text: str


def mine(games: list[Game], kinds=KINDS, model: str = "", pattern: str = "",
         max_words: int = 12) -> list[Quote]:
    """Quotes of the given kinds. `model` filters by model id substring, `pattern` by regex
    (case-insensitive); one-liners are public lines of at most `max_words` words."""
    rx = re.compile(pattern, re.IGNORECASE) if pattern else None
    out = []
    for g in games:
        for e in g.events:
            seat = g.seats.get(e.actor or "")
            if not seat or (model and model not in seat.model):
                continue
            for kind, text in _candidates(e, max_words):
                if kind in kinds and (rx is None or rx.search(text)):
                    out.append(Quote(g.id, e.seq, seat.model, seat.name, seat.role, kind, text))
    return out


def _candidates(e, max_words: int):
    channel = e.data.get("channel", "public")
    if e.kind == "speech" and channel == "last words":
        yield "last-words", e.text
    elif e.kind == "speech" and channel == "wolf den":
        yield "wolf-den", e.text
    elif e.kind == "speech" and channel == "public" and len(e.text.split()) <= max_words:
        yield "one-liners", e.text
    if e.data.get("thought"):
        yield "thoughts", e.data["thought"]
