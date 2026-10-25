import random

from aiplays.core.voting import plurality, tally


def test_tally_ignores_abstentions():
    assert tally({"a": "x", "b": "x", "c": None}) == {"x": 2}


def test_plurality_winner():
    assert plurality({"a": "x", "b": "x", "c": "y"}) == "x"


def test_tie_means_nobody_without_rng():
    assert plurality({"a": "x", "b": "y"}) is None


def test_tie_broken_with_rng():
    assert plurality({"a": "x", "b": "y"}, random.Random(1)) in {"x", "y"}


def test_no_votes():
    assert plurality({"a": None}) is None
