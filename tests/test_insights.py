"""Werewolf insights on a tiny hand-made game: suspicion, claims, heat map, quotes and charts."""
from aiplays.core.events import GameEvent, Kind
from aiplays.modes.werewolf.insights import minds, svg, svg_grids, talk
from aiplays.modes.werewolf.insights.heat import heat, render
from aiplays.modes.werewolf.insights.load import Game, Seat
from aiplays.modes.werewolf.insights.quotes import mine
from aiplays.modes.werewolf.insights.tables import tables

SEATS = {"p1": Seat("Ann", "m-a", "seer", "village", True), "p2": Seat("Ben", "m-b", "alpha", "wolves", False),
         "p3": Seat("Cat", "m-a", "villager", "village", True)}


def ev(seq, kind, actor=None, text="", data=None, target=None, phase="discussion"):
    return GameEvent(kind=kind, seq=seq, actor=actor, target=target, text=text, phase=phase,
                     data=data or {})


EVENTS = [
    ev(1, Kind.PHASE, data={"phase": "discussion"}),
    ev(2, Kind.REACTION, "p1", "Ben is the wolf", {"suspect": "Ben", "thought": "I checked Ben, a wolf"}),
    ev(3, Kind.REACTION, "p3", "", {"suspect": "Ann", "thought": "I'll wait and stay quiet"}),
    ev(4, Kind.SPEECH, "p1", "Me Seer. Ben wolf.", {"claim": "seer"}),
    ev(5, Kind.REACTION, "p3", "Vote Ben", {"suspect": "Ben", "thought": "Ann sounds sure. Ben then."}),
    ev(6, Kind.REACTION, "p2", "Ann lies", {"suspect": "Ann", "thought": "Kill the seer tonight"}),
    ev(7, Kind.SPEECH, "p2", "Me Seer too. Ann lie!", {"claim": "seer"}),
    ev(8, Kind.SPEECH, "p2", "Me no wolf. Me just fool.", {"channel": "last words"}, phase="vote"),
    ev(9, Kind.DEATH, target="p2", phase="vote"),
]
GAME = Game("g1", "finished", "village", {}, SEATS, EVENTS)


def test_suspicion_and_changes():
    s = minds.suspicion([GAME])
    a = s["models"]["m-a"]  # Ann and Cat are both model m-a, on the village team
    assert (a["reads"], a["hits"]) == (3, 2)  # Ann->Ben, Cat->Ann, Cat->Ben
    assert (a["changes"], a["switches"], a["switch_hits"]) == (1, 1, 1)
    assert s["moves"] == {"innocent -> wolf": 1}
    assert s["outcomes"]["switched"] == (1, 1)


def test_claims_lines_and_tables():
    t = talk.per_model([GAME])
    assert (t["m-a"]["honest_village"], t["m-a"]["claims_village"]) == (1, 1)
    assert (t["m-b"]["honest_wolves"], t["m-b"]["claims_wolves"]) == (0, 1)
    assert t["m-a"]["passes"] == 1 and t["m-b"]["lines"] == 1  # last words aren't a public line
    assert all(cols and rows for cols, rows in tables([GAME]).values())


def test_heat_counts_living_suspicion():
    cols = heat(GAME)
    assert [c["counts"]["Ben"] for c in cols] == [1, 2]  # after line 4: Ann; after line 7: Ann + Cat
    assert cols[1]["counts"]["Ann"] == 1  # Ben suspects Ann
    assert "Ben alpha*" in render(GAME, cols)


def test_quotes_and_charts():
    kinds = {q.kind for q in mine([GAME])}
    assert {"last-words", "one-liners", "thoughts"} <= kinds
    assert [q.text for q in mine([GAME], ["last-words"])] == ["Me no wolf. Me just fool."]
    assert svg.bars("t", "s", [("A", 3, "3", "")]).startswith("<svg")
    assert "Ben · Alpha (wolf)" in svg_grids.heatmap(GAME, heat(GAME))
