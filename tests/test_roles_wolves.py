"""Werewolf-team roles (wolves_*.py, traps.py): one behavioural check per role."""
from rolekit import act, game, night, notes, run

from aiplays.modes.werewolf.night import options
from aiplays.modes.werewolf.night.context import Night
from aiplays.modes.werewolf.roles import effects
from aiplays.modes.werewolf.roles.base import VILLAGE, role
from aiplays.modes.werewolf.roles.base import act as action

# Minimal test-only village roles (kept out of decks): a plain body, a mover, an investigator.
role(id="zz_body", label="Test Body", team=VILLAGE, in_deck=False)
role(id="zz_walker", label="Test Walker", team=VILLAGE, in_deck=False,
     actions=(action("walk", "support", "Visit someone.", lambda n, a: None),))
role(id="zz_looker", label="Test Looker", team=VILLAGE, in_deck=False,
     actions=(action("look", "information", "Learn a role.", effects.inspect_role,
                     movement="none"),))


def setup(*roles: str) -> tuple:
    st = game(*roles)
    return (st, *st.players)


def test_consort_blocks_and_stalker_kills_only_movers():
    st, consort, stalker, walker, body = setup("consort", "stalker", "zz_walker", "zz_body")
    n = night(st)
    act(n, walker, "walk", body)
    act(n, stalker, "stalk", walker)
    run(n)
    assert n.deaths == {walker.id: "killed by the Stalker"}
    n = night(st, 3)
    act(n, walker, "walk", body)
    act(n, consort, "block", walker)
    act(n, stalker, "stalk", body)
    run(n)
    assert "busy" in notes(n, walker) and not n.deaths


def test_clairvoyant_bloodhound_and_spy_learn():
    st, cv, hound, spy, walker, body = setup("clairvoyant", "bloodhound", "spy", "zz_walker",
                                             "zz_body")
    n = night(st)
    act(n, walker, "walk", body)
    act(n, cv, "divine", body)
    act(n, hound, "sniff", walker)
    act(n, spy, "tail", walker)
    run(n)
    assert "Test Body" in notes(n, cv)
    assert "is one of" in notes(n, hound) and "Test Walker" in notes(n, hound)
    assert "went to: Eve" in notes(n, spy)


def test_graverobber_learns_and_borrows_and_corpses_are_single_use():
    st, robber, necro, looker, _body = setup("graverobber", "necromancer", "zz_looker", "zz_body")
    looker.alive = False
    n = night(st)
    act(n, robber, "rob", looker)
    run(n)
    assert "was the Test Looker" in notes(n, robber)
    assert any(a.name == "look" for a in options.available(st, robber, 2))
    n = night(st, 2)
    act(n, necro, "exhume", looker)
    run(n)
    assert "already disturbed" in notes(n, necro)


def test_framer_makeup_and_mimic_change_appearance():
    st, framer, mua, mimic, _looker, body, walker = setup(
        "framer", "makeup_artist", "mimic", "zz_looker", "zz_body", "zz_walker")
    n = night(st)
    act(n, framer, "frame", body)
    act(n, mua, "disguise", walker, option="Test Looker")
    act(n, mimic, "mimic", walker)
    run(n)
    assert n.seen_role(body) == "wolf" and n.seen_team(body) == "wolves"
    assert n.seen_role(mimic) == "zz_looker"  # mimics the walker's disguise
    assert Night(st, 2, n.rng).seen_role(walker) == "zz_looker"
    assert Night(st, 3, n.rng).seen_role(walker) == "zz_walker"


def test_obscurist_shrouds_and_hypnotist_copies_vote():
    st, obs, hyp, looker, body = setup("obscurist", "hypnotist", "zz_looker", "zz_body")
    n = night(st)
    act(n, obs, "obscure", body)
    act(n, hyp, "hypnotize", looker)
    act(n, looker, "look", body)
    run(n)
    assert "fog" in notes(n, looker)
    assert st.memory["vote_copy"] == {looker.id: hyp.id}
