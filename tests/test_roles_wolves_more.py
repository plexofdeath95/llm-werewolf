"""Werewolf-team movement, trap, potion and copy roles."""
from rolekit import act, night, notes, run
from test_roles_wolves import setup  # also registers the zz_ test roles

from aiplays.modes.werewolf.night import options


def test_angler_redirects_movers():
    st, angler, walker, body = setup("angler", "zz_walker", "zz_body")
    n = night(st)
    act(n, angler, "hook", walker)
    act(n, walker, "walk", body)
    run(n)
    assert [a.actor for a in n.visitors(angler)] == [walker] and not n.visitors(body)


def test_transporter_swaps_and_limits_wolves():
    st, tp, walker, x, y, wolf = setup("transporter", "zz_walker", "zz_body", "zz_body", "wolf")
    n = night(st)
    act(n, tp, "transport", x, y)
    act(n, walker, "walk", x)
    run(n)
    assert walker in [a.actor for a in n.visitors(y)] and "confused" in notes(n, x)
    n = night(st, 2)
    act(n, tp, "transport", tp, wolf)
    run(n)
    assert "at most one wolf" in notes(n, tp)


def test_scarecrow_nightmare_blocks_movement_and_only_visits_first():
    st, crow, walker, feared = setup("scarecrow", "zz_walker", "zz_body")
    n = night(st)
    act(n, crow, "frighten", walker, feared)
    a = act(n, walker, "walk", feared)
    run(n)
    assert a.failed and "nightmare about Cat" in notes(n, walker)
    assert [v.actor for v in n.visitors(walker)] == [crow] and not n.visitors(feared)


def test_warlock_brainwash_kills_next_nights_visit():
    st, warlock, walker, body = setup("warlock", "zz_walker", "zz_body")
    n = night(st)
    act(n, warlock, "brainwash", walker)
    act(n, walker, "walk", body)
    run(n)
    assert not n.deaths  # starts the next night
    n = night(st, 2)
    act(n, walker, "walk", body)
    run(n)
    assert n.deaths == {body.id: "killed by a brainwashed visitor"}
    assert "headache" in notes(n, walker)


def test_trapper_builds_places_and_catches_first_visitor():
    st, trapper, walker, body = setup("trapper", "zz_walker", "zz_body")
    assert [a.name for a in options.available(st, trapper, 1)] == ["build"]
    run_night = night(st)
    act(run_night, trapper, "build")
    run(run_night)
    n = night(st, 2)
    act(n, trapper, "place", body)
    act(n, walker, "walk", body)
    run(n)
    assert n.deaths == {walker.id: "caught in a trap"} and "sprung" in notes(n, trapper)


def test_potion_master_cooldown_and_poison():
    st, pm, body = setup("potion_master", "zz_body")
    n = night(st)
    act(n, pm, "poison", body)
    run(n)
    assert n.deaths == {body.id: "poisoned by the Potion Master"}
    names = lambda k: [a.name for a in options.available(st, pm, k)]
    assert "poison" not in names(2) and "poison" not in names(3) and "poison" in names(4)


def test_amoeba_right_guess_blocks_and_borrows_wrong_guess_does_nothing():
    st, amoeba, walker, body = setup("amoeba", "zz_walker", "zz_body")
    n = night(st)
    act(n, amoeba, "absorb", body, option="Test Walker")
    run(n)
    assert "failed" in notes(n, amoeba)
    n = night(st, 2)
    act(n, amoeba, "absorb", walker, option="the test walker")
    w = act(n, walker, "walk", body)
    run(n)
    assert w.blocked and "drained" in notes(n, walker)
    assert "walk" in [a.name for a in options.available(st, amoeba, 3)]
