"""Neutral disease and hit-list roles through the real night resolver."""
from rolekit import act, game, night, run
from test_roles_neutral import after

from aiplays.modes.werewolf.night import options
from aiplays.modes.werewolf.status import status


def test_plague_kills_next_night_unstoppably_and_spreads_to_visitors():
    st = game("plague_bringer", "doctor", "villager", "villager", "villager")
    pb, doc, vic = st.players[:3]
    act(n := night(st, 1), pb, "infect", vic)
    assert not run(n).deaths and "infected" in status(st, vic).flags
    n = night(st, 2)
    act(n, doc, "heal", vic)
    run(n)
    assert n.deaths == {vic.id: "succumbed to the plague"}
    assert "infected" in status(st, doc).flags and status(st, pb).kills == 1


def test_parasite_feeds_on_the_dying_then_starves():
    st = game("parasite", "alpha", "villager", "villager", "villager")
    par, alpha, vic = st.players[:3]
    n = night(st, 1)
    act(n, alpha, "kill", vic)
    act(n, par, "transfuse", vic)
    after(run(n))
    assert status(st, par).marks["transfusions"] == 1 and status(st, par).marks["misses"] == 0
    vic.alive = False
    for k in (2, 3, 4):
        n = after(run(night(st, k)))
    assert n.deaths == {par.id: "starved without fresh blood"}


def test_assassin_may_only_shoot_listed_targets():
    st = game("assassin", "villager", "villager", "villager", "villager", "villager")
    ass = st.players[0]
    listed = status(st, ass).marks["targets"]
    shot = next(a for a in options.available(st, ass, 1) if a.name == "assassinate")
    assert len(listed) == 2 and {p.id for p in options.targets(st, ass, shot, 1)} == set(listed)
    act(n := night(st), ass, "assassinate", st.by_id(listed[0]))
    run(n)
    assert status(st, ass).marks["done"] == [listed[0]]
