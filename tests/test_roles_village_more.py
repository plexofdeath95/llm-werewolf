"""More village roles through the real night resolver."""
from rolekit import act, game, night, notes, run


def test_vigilante_guilt_after_killing_a_villager():
    st = game("alpha", "vigilante", "villager", "seer", "villager")
    n = night(st)
    act(n, st.players[1], "shoot", st.players[2])
    run(n)
    assert set(n.deaths) == {"p1", "p2"}


def test_knight_has_two_lives():
    st = game("alpha", "knight", "villager", "seer", "villager")
    n = night(st)
    act(n, st.players[0], "kill", st.players[1])
    run(n)
    assert not n.deaths and n.st(st.players[1]).lives == 1


def test_mechanist_trap_catches_first_visitor():
    st = game("alpha", "mechanist", "villager", "seer", "villager")
    mech = st.players[1]
    n1 = night(st, 1)
    act(n1, mech, "build")
    run(n1)
    n = night(st, 2)
    act(n, mech, "place", st.players[2])
    act(n, st.players[0], "kill", st.players[2])
    run(n)
    assert "p0" in n.deaths


def test_lovers_share_one_home():
    st = game("alpha", "lovers", "lovers", "seer", "villager")
    n = night(st)
    act(n, st.players[1], "stay", option="my home")
    act(n, st.players[0], "kill", st.players[1])
    run(n)
    assert set(n.deaths) == {"p1", "p2"}


def test_scholar_counts_wolves_on_night_one():
    st = game("alpha", "scholar", "villager", "seer", "wolf")
    n = night(st)
    act(n, st.players[1], "study")
    run(n)
    assert "2 Werewolf-team" in notes(n, st.players[1])
