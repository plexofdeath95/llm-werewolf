"""Who suspected whom: suspicion accuracy, a random-pick baseline, and changes of mind.

Every reaction names a prime suspect. For village players we check it against the real wolves,
and compare with pointing at a random living player.
"""
from collections import Counter, defaultdict

from aiplays.modes.werewolf.insights.load import Game


def suspicion(games: list[Game]) -> dict:
    """Per model: village reads (`reads`, `hits`), changes of suspect (`changes`, `pairs`) and
    switches that landed on a wolf (`switches`, `switch_hits`); plus the overall `baseline` and
    the `kept` / `switched` / `first` hit counts and where switches went (`moves`)."""
    per: dict[str, Counter] = defaultdict(Counter)
    outcome, moves, base = Counter(), Counter(), []
    for g in games:
        wolves, dead, last = g.wolves, set(), {}
        for e in g.events:
            if e.kind == "death":
                dead.add(e.target)
            if e.kind != "reaction" or e.actor not in g.seats or not e.data.get("suspect"):
                continue
            seat, s = g.seats[e.actor], e.data["suspect"]
            m = per[seat.model]
            prev = last.get(e.actor)
            if prev is not None:
                m["pairs"] += 1
                m["changes"] += s != prev
            if seat.team == "village":
                hit = s in wolves
                m["reads"] += 1
                m["hits"] += hit
                alive = [q for pid, q in g.seats.items() if pid not in dead and pid != e.actor]
                base.append(sum(q.team == "wolves" for q in alive) / max(1, len(alive)))
                kind = "first" if prev is None else "switched" if s != prev else "kept"
                outcome[kind, hit] += 1
                if kind == "switched":
                    m["switches"] += 1
                    m["switch_hits"] += hit
                    moves[("wolf" if prev in wolves else "innocent") + " -> "
                          + ("wolf" if hit else "innocent")] += 1
            last[e.actor] = s
    return {"models": dict(per), "baseline": sum(base) / max(1, len(base)),
            "outcomes": {k: (outcome[k, True], outcome[k, True] + outcome[k, False])
                         for k in ("first", "kept", "switched")},
            "moves": dict(moves)}
