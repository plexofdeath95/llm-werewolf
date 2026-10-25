"""Every prompt a real (non-fake) game sends renders fully: no unfilled $placeholders."""
import re

import pytest

from aiplays.agents.prompts import render
from aiplays.modes.werewolf import rules
from aiplays.modes.werewolf.night import options
from aiplays.modes.werewolf.roles import ROLES
from rolekit import game

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
