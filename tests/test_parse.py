import pytest

from aiplays.agents.parse import parse_reply, partial_thought, schema_hint
from aiplays.agents.schemas import Choice, Reaction


def test_parses_json_inside_markdown_fence():
    r = parse_reply('```json\n{"thought": "hm", "urgency": 7, "message": "hi"}\n```', Reaction)
    assert r.urgency == 7 and r.message == "hi"


def test_urgency_on_100_scale_is_rescaled():
    assert parse_reply('{"urgency": 85}', Reaction).urgency == 8
    assert parse_reply('{"urgency": "high"}', Reaction).urgency == 0


def test_addressing_string_becomes_list():
    assert parse_reply('{"addressing": "Bob"}', Reaction).addressing == ["Bob"]


def test_invalid_reply_raises_value_error():
    with pytest.raises(ValueError):
        parse_reply("I refuse to answer in JSON", Choice)


def test_partial_thought_from_unfinished_stream():
    assert partial_thought('{"thought": "Bob is lyi') == "Bob is lyi"
    assert partial_thought('{"urgency": 3') is None


def test_schema_hint_lists_fields():
    hint = schema_hint(Choice)
    assert '"target"' in hint and '"thought"' in hint
