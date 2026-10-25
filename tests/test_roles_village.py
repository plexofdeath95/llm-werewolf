"""Village roles through the real night resolver."""
from rolekit import act, game, night, notes, run


def test_doctor_saves_and_is_told():
    st = game("alpha", "doctor", "villager", "seer", "villager")
    alpha, doc, vic = st.players[0], st.players[1], st.players[2]
    n = night(st)
    act(n, alpha, "kill", vic)
    act(n, doc, "heal", vic)
    run(n)
    assert not n.deaths and "saved" in notes(n, doc) and "nursed" in notes(n, vic)


def test_doctor_cannot_repeat_target_next_night():
    from aiplays.modes.werewolf.night import options
    st = game("alpha", "doctor", "villager", "seer", "villager")
    doc, vic = st.players[1], st.players[2]
    act(night(st, 1), doc, "heal", vic)
    heal = next(a for a in options.available(st, doc, 2) if a.name == "heal")
    assert vic not in options.targets(st, doc, heal, 2)


def test_escort_blocks_the_alpha():
    st = game("alpha", "escort", "villager", "seer", "villager")
    n = night(st)
    act(n, st.players[0], "kill", st.players[2])
    act(n, st.players[1], "block", st.players[0])
    run(n)
    assert not n.deaths and "busy" in notes(n, st.players[0])


def test_seer_sees_role_and_framing_lies():
    st = game("alpha", "seer", "villager", "doctor", "villager")
    n = night(st)
    act(n, st.players[1], "inspect", st.players[2])
    n.appear(st.players[2], "alpha")
    run(n)
    assert "Alpha" in notes(n, st.players[1])


def test_lookout_sees_the_killer():
    st = game("alpha", "lookout", "villager", "seer", "villager")
    n = night(st)
    act(n, st.players[0], "kill", st.players[2])
    act(n, st.players[1], "watch", st.players[2])
    run(n)
    assert "Ann" in notes(n, st.players[1]) and n.deaths == {"p2": "killed by the werewolves"}


def test_veteran_alert_kills_visitors():
    st = game("alpha", "veteran", "villager", "seer", "villager")
    n = night(st)
    act(n, st.players[0], "kill", st.players[1])
    act(n, st.players[1], "alert")
    run(n)
    assert "p0" in n.deaths


def test_bodyguard_trades_with_attacker():
    st = game("alpha", "bodyguard", "villager", "seer", "villager")
    n = night(st)
    act(n, st.players[0], "kill", st.players[2])
    act(n, st.players[1], "guard", st.players[2])
    run(n)
    assert set(n.deaths) == {"p0", "p1"}


def test_jailor_protects_and_blocks():
    st = game("alpha", "jailor", "villager", "seer", "villager")
    n = night(st)
    act(n, st.players[0], "kill", st.players[2])
    act(n, st.players[1], "jail", st.players[2])
    run(n)
    assert not n.deaths
