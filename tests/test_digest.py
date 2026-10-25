"""The digest tells a player which of their react-round drafts were never heard."""
from aiplays.agents import digest
from aiplays.core.events import GameEvent, Kind
from rolekit import game


def _events():
    return [
        GameEvent(kind=Kind.REACTION, seq=1, actor="p0", text="I was not blocked."),
        GameEvent(kind=Kind.REACTION, seq=2, actor="p1", text="Carol, were you blocked?"),
        GameEvent(kind=Kind.SPEECH, seq=3, actor="p1", text="Carol, were you blocked?",
                  data={"reaction_seq": 2}),
        GameEvent(kind=Kind.REACTION, seq=4, actor="p0", text="", data={}),  # a pass
    ]


def test_losing_draft_is_flagged_as_unheard():
    st = game("villager", "villager", "villager")
    text, last = digest.build(_events(), st, st.players[0], since=0)
    assert '(Not heard: you wanted to say "I was not blocked."' in text
    assert 'Ben: "Carol, were you blocked?"' in text
    assert last == 4


def test_winning_draft_and_passes_are_not_flagged():
    st = game("villager", "villager", "villager")
    text, _ = digest.build(_events(), st, st.players[1], since=0)
    assert "Not heard" not in text
    assert 'Ben (you): "Carol, were you blocked?"' in text


def test_other_players_drafts_stay_hidden():
    st = game("villager", "villager", "villager")
    text, _ = digest.build(_events(), st, st.players[2], since=0)
    assert "I was not blocked" not in text
