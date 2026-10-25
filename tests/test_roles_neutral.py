"""Neutral killers and disease through the real night resolver."""
from rolekit import act, game, night, run

from aiplays.modes.werewolf.roles.base import ROLES
from aiplays.modes.werewolf.status import status


def after(n):
    """What night/phase.py does after resolution: after_night hooks for survivors."""
    for p in n.state.alive():
        if (h := ROLES[p.role].hook("after_night")) and p.id not in n.deaths:
            h(n, p)
    return n


def test_arsonist_douses_then_ignition_ignores_heals():
    st = game("arsonist", "doctor", "villager", "villager", "villager")
    ars, doc, vic = st.players[:3]
    act(n := night(st, 1), ars, "douse", vic)
    run(n)
    assert "doused" in status(st, vic).flags
    n = night(st, 2)
    act(n, ars, "ignite")
    act(n, doc, "heal", vic)
    after(run(n))
    assert n.deaths == {vic.id: "burned alive by the Arsonist"}
    assert status(st, ars).marks["ignited"] == 1


def test_arsonist_blocker_gets_doused_instead():
    st = game("arsonist", "escort", "villager", "villager", "villager")
    n = night(st)
    act(n, st.players[0], "douse", st.players[2])
    act(n, st.players[1], "block", st.players[0])
    run(n)
    assert "doused" in status(st, st.players[1]).flags
    assert "doused" not in status(st, st.players[2]).flags


def test_murderer_kills_its_visitor_instead():
    st = game("murderer", "doctor", "villager", "villager", "villager")
    mur, doc, vic = st.players[:3]
    n = night(st)
    act(n, mur, "murder", vic)
    act(n, doc, "heal", mur)
    run(n)
    assert list(n.deaths) == [doc.id] and status(st, mur).kills_by_team == {"village": 1}


def test_crone_only_kills_targets_who_go_out():
    st = game("crone", "doctor", "doctor", "villager", "villager")
    crone, out, home = st.players[:3]
    n = night(st)
    act(n, crone, "stalk", out)
    act(n, out, "heal", st.players[3])
    run(n)
    assert n.deaths == {out.id: "killed by the Crone"}
    n = night(st, 3)
    act(n, crone, "stalk", home)
    act(n, home, "heal", home)  # self-heal: never leaves home
    assert not run(n).deaths


def test_vampire_drains_borrows_powers_and_is_immune_while_hunting():
    st = game("vampire", "doctor", "alpha", "villager", "villager")
    vamp, doc, alpha = st.players[:3]
    n = night(st)
    act(n, vamp, "drain", doc)
    act(n, alpha, "kill", vamp)
    run(n)
    assert list(n.deaths) == [doc.id]
    assert status(st, vamp).marks["borrow"] == (2, "doctor") and n.seen_role(vamp) == "doctor"


def test_vampire_blocker_dies_in_place_of_victim():
    st = game("vampire", "escort", "villager", "villager", "villager")
    n = night(st)
    act(n, st.players[0], "drain", st.players[2])
    act(n, st.players[1], "block", st.players[0])
    assert list(run(n).deaths) == [st.players[1].id]
