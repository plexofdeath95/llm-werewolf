"""Deck building and win conditions."""
import random

from aiplays.modes.werewolf.deck import default_deck, sizes
from aiplays.modes.werewolf.roles import ROLES
from aiplays.modes.werewolf.win import winner
from rolekit import game


def test_faction_sizes():
    assert sizes(5) == (4, 1, 0)
    assert sizes(8) == (5, 2, 1)
    assert sizes(16) == (10, 4, 2)


def test_classic_deck_has_core_roles():
    deck = default_deck(8, random.Random(1), style="classic")
    assert deck.count("alpha") == 1 and "seer" in deck and "doctor" in deck
    assert len(deck) == 8


def test_mixed_decks_are_valid_and_unique_per_faction():
    for seed in range(20):
        deck = default_deck(10, random.Random(seed))
        assert len(deck) == 10 and deck.count("alpha") == 1
        specials = [r for r in deck if r != "villager"]
        assert len(specials) == len(set(specials))
        assert all(ROLES[r].group == 1 for r in deck)


def test_village_wins_when_wolves_gone():
    st = game("alpha", "seer", "villager", "doctor", "villager")
    st.players[0].alive = False
    assert winner(st) == "village"


def test_wolves_win_at_parity():
    st = game("alpha", "wolf", "villager", "doctor", "villager")
    st.players[3].alive = st.players[4].alive = False
    assert winner(st) == "wolves"


def test_game_continues_otherwise():
    st = game("alpha", "seer", "villager", "doctor", "villager")
    assert winner(st) is None


def test_hunter_last_stand():
    st = game("alpha", "hunter", "villager", "doctor", "villager")
    for p in st.players[2:]:
        p.alive = False
    assert winner(st) == "village"


def test_resolve_role_from_free_text():
    from aiplays.core.mode import get_mode
    mode = get_mode("werewolf")
    assert mode.resolve_role("Seer") == "seer"
    assert mode.resolve_role("the Alignment Seer") == "alignment_seer"
    assert mode.resolve_role("jack of all trades") == "jack_of_all_trades"
    assert mode.resolve_role("") == "" and mode.resolve_role("pirate") == ""


def test_mixed_decks_are_balanced():
    from aiplays.modes.werewolf.deck import TARGET_BALANCE, balance
    for n in range(6, 13):
        for seed in range(5):
            b = balance(default_deck(n, random.Random(seed)))
            assert TARGET_BALANCE - 2 <= b <= TARGET_BALANCE + 4, (n, seed, b)
