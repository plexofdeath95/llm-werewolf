"""Every prompt a real (non-fake) game sends renders fully: no unfilled $placeholders."""
import re

import pytest
from rolekit import game

from aiplays.agents.prompts import render
from aiplays.modes.werewolf import rules
from aiplays.modes.werewolf.night import options
from aiplays.modes.werewolf.roles import ROLES

PLACEHOLDER = re.compile(r"\$[a-z_]+")
PLAYABLE = sorted(r for r in ROLES if not r.startswith("zz"))


@pytest.mark.parametrize("role_id", PLAYABLE)
def test_briefing_and_night_menu_render_for_every_role(role_id):
    st = game(role_id, "alpha", "villager", "seer", "doctor", "villager")
    me = st.players[0]
    text = rules.briefing(st, me, reveal_models=False)
    assert me.name in text and ROLES[role_id].label in text
    assert not PLACEHOLDER.search(text), PLACEHOLDER.findall(text)
    menu = options.describe(st, me, 1)
    night = render("night_action", rules.PROMPTS, round=1, menu=menu)
    assert not PLACEHOLDER.search(night)


@pytest.mark.parametrize("template", ["react", "nudge", "day_vote", "last_words", "mayor"])
def test_shared_and_mode_templates_render(template):
    text = render(template, rules.PROMPTS, round=2, channel="public", count=3, max=24,
                  options="Ann, Ben")
    assert text and not PLACEHOLDER.search(text), PLACEHOLDER.findall(text)


@pytest.mark.parametrize("style_id", ["caveman", "pirate", "noir", "shakespeare"])
def test_speech_styles_render(style_id):
    from aiplays.agents.factory import _style_text
    text = render("speech_style", style=_style_text(style_id))
    assert "SPEECH STYLE" in text and len(text) > 120 and not PLACEHOLDER.search(text)


def test_unknown_style_adds_nothing():
    from aiplays.agents.factory import _style_text
    assert _style_text(None) == "" and _style_text("klingon") == ""
