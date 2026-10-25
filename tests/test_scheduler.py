import random

from aiplays.core.config import TalkConfig
from aiplays.core.scheduler import Bid, is_interrupt, limits, pick

CFG = TalkConfig(jitter=0)
RNG = random.Random(0)


def test_everyone_passing_returns_none():
    bids = [Bid("a", 9, ""), Bid("b", 2, "hmm")]
    assert pick(bids, [], set(), set(), CFG, RNG) is None


def test_named_player_beats_slightly_more_urgent_bid():
    bids = [Bid("a", 7, "x"), Bid("b", 6, "y")]
    best, _ = pick(bids, [], named={"b"}, spoken={"a", "b"}, cfg=CFG, rng=RNG)
    assert best.pid == "b"


def test_last_speaker_is_penalised():
    bids = [Bid("a", 8, "again"), Bid("b", 6, "me")]
    best, _ = pick(bids, ["a"], set(), {"a", "b"}, CFG, RNG)
    assert best.pid == "b"


def test_quiet_bonus_for_players_who_have_not_spoken():
    bids = [Bid("a", 6, "x"), Bid("b", 5, "y")]
    best, _ = pick(bids, [], set(), {"a"}, CFG, RNG)
    assert best.pid == "b"


def test_interrupt_needs_name_and_high_urgency():
    assert is_interrupt(Bid("a", 9, "x"), {"a"}, CFG)
    assert not is_interrupt(Bid("a", 9, "x"), set(), CFG)
    assert not is_interrupt(Bid("a", 5, "x"), {"a"}, CFG)


def test_limits_scale_with_table_and_cap():
    assert limits(6, CFG) == (6, 24)
    assert limits(10, CFG) == (10, 30)
