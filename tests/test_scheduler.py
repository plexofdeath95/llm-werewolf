import random

from aiplays.core.config import TalkConfig
from aiplays.core.scheduler import Bid, is_interrupt, limit, pick

CFG = TalkConfig(jitter=0)
RNG = random.Random(0)


def test_everyone_passing_returns_none():
    bids = [Bid("a", 9, ""), Bid("b", 2, "hmm")]
    assert pick(bids, [], set(), set(), CFG, RNG) is None


def test_named_player_beats_slightly_more_urgent_bid():
    bids = [Bid("a", 7, "x"), Bid("b", 6, "y")]
    best, _ = pick(bids, [], named={"b"}, spoken={"a": 1, "b": 1}, cfg=CFG, rng=RNG)
    assert best.pid == "b"


def test_last_speaker_is_penalised():
    bids = [Bid("a", 8, "again"), Bid("b", 6, "me")]
    best, _ = pick(bids, ["a"], set(), {"a": 1, "b": 1}, CFG, RNG)
    assert best.pid == "b"


def test_unheard_voice_beats_a_more_urgent_regular():
    bids = [Bid("a", 9, "x"), Bid("b", 6, "y")]
    best, _ = pick(bids, [], set(), {"a": 2}, CFG, RNG)
    assert best.pid == "b"


def test_repeat_penalty_grows_with_messages_said():
    bids = [Bid("a", 8, "x"), Bid("b", 7, "y")]
    best, _ = pick(bids, [], set(), {"a": 3, "b": 1}, CFG, RNG)
    assert best.pid == "b"


def test_interrupt_needs_name_and_high_urgency():
    assert is_interrupt(Bid("a", 9, "x"), {"a"}, CFG)
    assert not is_interrupt(Bid("a", 9, "x"), set(), CFG)
    assert not is_interrupt(Bid("a", 5, "x"), {"a"}, CFG)


def test_limit_is_rounds_times_table_with_cap():
    assert limit(6, CFG) == 18
    assert limit(12, CFG) == 30
    assert limit(5, CFG.model_copy(update={"rounds": 0})) == 5  # never below one round
