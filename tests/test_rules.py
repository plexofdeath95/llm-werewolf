import random

from aiplays.core.state import GameState, Player
from aiplays.modes.werewolf.roles import assign, distribution, summary
from aiplays.modes.werewolf.win import winner


def _state(n: int) -> GameState:
    return GameState("g", "werewolf", 1, [Player(f"p{i}", f"N{i}", i, "m") for i in range(n)])


def test_distribution_sizes():
    assert sorted(distribution(5)) == sorted(["werewolf", "seer"] + ["villager"] * 3)
    assert distribution(8).count("werewolf") == 2 and "doctor" in distribution(8)
    assert distribution(16).count("werewolf") == 4


def test_summary_text():
    assert summary(6) == "1 Werewolf, 1 Seer, 1 Doctor, 3 Villagers"


def test_winner_conditions():
    st = _state(6)
    assign(st, random.Random(3))
    assert winner(st) is None
    for p in st.on_team("wolves"):
        p.alive = False
    assert winner(st) == "village"
    st = _state(6)
    assign(st, random.Random(3))
    for p in [p for p in st.players if p.team == "village"][:4]:
        p.alive = False
    assert winner(st) == "wolves"
