"""Benign, group and movement neutrals through the real night resolver."""
from rolekit import act, game, night, notes, run

from aiplays.modes.werewolf.night import options
from aiplays.modes.werewolf.status import role_of, status


def test_survivor_safe_at_home_unless_blocked_but_dies_with_host():
    st = game("survivor", "alpha", "escort", "villager", "villager")
    sur, alpha, esc, host = st.players[:4]
    act(n := night(st, 1), alpha, "kill", sur)
    assert not run(n).deaths and "nowhere" in notes(n, sur)
    n = night(st, 2)
    act(n, sur, "hide", host)
    act(n, esc, "block", sur)
    act(n, alpha, "kill", sur)
    assert sur.id in run(n).deaths
    st = game("survivor", "alpha", "escort", "villager", "villager")
    act(n := night(st, 1), st.players[0], "hide", st.players[3])
    act(n, st.players[1], "kill", st.players[3])
    assert set(run(n).deaths) == {"p0", "p3"}


def test_amnesiac_becomes_a_dead_players_role():
    st = game("amnesiac", "alpha", "seer", "villager", "villager")
    st.players[2].alive = False
    act(n := night(st, 2), st.players[0], "remember", st.players[2])
    run(n)
    assert role_of(st, st.players[0]) == "seer"


def test_executioner_picks_a_target_once_while_it_lives():
    st = game("executioner", "villager", "villager", "villager", "villager")
    exe = st.players[0]
    act(n := night(st, 1), exe, "target", st.players[2])
    run(n)
    assert status(st, exe).marks["target"] == "p2" and not options.available(st, exe, 2)


def test_cult_converts_and_its_blocker_joins_too():
    st = game("cult_leader", "escort", "villager", "villager", "villager")
    lead, esc = st.players[:2]
    n = night(st)
    act(n, lead, "convert", st.players[2])
    act(n, esc, "block", lead)
    run(n)
    assert "cult" in status(st, esc).flags and "cult" not in status(st, st.players[2]).flags
    assert "cult" in status(st, esc).marks["chats"]


def test_cupid_makes_lovers_who_borrow_the_stay_ability():
    st = game("cupid", "villager", "alpha", "villager", "villager")
    act(n := night(st, 1), st.players[0], "shoot", st.players[1], st.players[2])
    run(n)
    lover = status(st, st.players[1])
    assert "lover" in lover.flags and lover.marks["beloved"] == "p2"
    assert any(a.name == "stay" for a in options.available(st, st.players[1], 2))


def test_creed_kills_only_when_every_member_strikes_the_same_player():
    st = game("creed", "creed", "creed", "villager", "villager", "villager")
    n = night(st)
    for c in st.players[:3]:
        act(n, c, "strike", st.players[3])
    assert list(run(n).deaths) == ["p3"] and st.memory["creed_kills"] == 1
    n = night(st, 2)
    for c, t in zip(st.players[:3], (4, 4, 5)):
        act(n, c, "strike", st.players[t])
    assert not run(n).deaths and "not united" in notes(n, st.players[0])


def test_detour_sends_a_visitor_elsewhere():
    st = game("detour", "doctor", "villager", "villager", "villager")
    det, doc, house = st.players[:3]
    n = night(st)
    act(n, det, "detour", house)
    act(n, doc, "heal", house)
    run(n)
    assert doc.id in n.redirect and not n.heals.get(house.id)
    assert "ended up at" in notes(n, doc) and status(st, det).marks["moved"] == ["village"]


def test_orphan_shares_hosts_fate_and_can_adopt():
    st = game("orphan", "alpha", "seer", "villager", "villager")
    orph, alpha, _, host = st.players[:4]
    act(n := night(st, 1), orph, "lodge", host)
    act(n, alpha, "kill", host)
    assert set(run(n).deaths) == {orph.id, host.id}
    st = game("orphan", "alpha", "seer", "villager", "villager")
    act(n := night(st, 2), st.players[0], "adopt", st.players[2])
    run(n)
    assert role_of(st, st.players[0]) == "seer"
