"""How each model talked, claimed, reasoned and spent: per-model counters from the event log."""
import re
from collections import Counter, defaultdict

from aiplays.modes.werewolf.insights.load import Game

# A private thought complaining that the model's line never got the floor.
UNHEARD = re.compile(r"(drowned|never (actually )?been heard|cut off|not heard|wasn.t heard|"
                     r"didn.t get through|never got (the floor|through)|logged back)", re.IGNORECASE)


def per_model(games: list[Game]) -> dict[str, Counter]:
    """Counters per model: seats, finished seats and wins, public lines and their words,
    interruptions, reactions and passes, drafts (reactions with a line), role claims split by
    team (`claims_<team>` / `honest_<team>`), native reasoning chars and calls, private thoughts
    and their words, cut-off complaints, and API cost."""
    out: dict[str, Counter] = defaultdict(Counter)
    for g in games:
        for s in g.seats.values():
            out[s.model]["seats"] += 1
            if g.status == "finished":
                out[s.model]["finished"] += 1
                out[s.model]["wins"] += bool(s.won)
        for e in g.events:
            if e.actor not in g.seats:
                continue
            seat, d = g.seats[e.actor], e.data
            m = out[seat.model]
            if e.kind == "speech" and d.get("channel", "public") == "public":
                m["lines"] += 1
                m["words"] += len(e.text.split())
                m["interrupts"] += bool(d.get("interrupt"))
                if d.get("claim"):
                    m[f"claims_{seat.team}"] += 1
                    m[f"honest_{seat.team}"] += d["claim"] == seat.role
            if e.kind == "reaction":
                m["reactions"] += 1
                m["passes"] += not e.text.strip()
                m["drafts"] += bool(e.text.strip())
            if e.kind == "thought":
                m["native_calls"] += bool(e.text)
                m["native_chars"] += len(e.text)
                m["cost_usd"] += d.get("cost") or 0.0
            thought = d.get("thought") or ""
            if thought:
                m["thoughts"] += 1
                m["thought_words"] += len(thought.split())
                m["unheard"] += bool(UNHEARD.search(thought))
    return dict(out)
