"""Model-agnostic JSON reply handling: schema hint, lenient parse, partial streaming peek."""
import json
import re

from pydantic import BaseModel, ValidationError

_PARTIAL_THOUGHT = re.compile(r'"thought"\s*:\s*"((?:[^"\\]|\\.)*)')


def schema_hint(schema: type[BaseModel]) -> str:
    props = schema.model_json_schema().get("properties", {})
    lines = [f'- "{k}" ({v.get("type", "string")}): {v.get("description", "")}'
             for k, v in props.items()]
    return ("Reply with ONLY a JSON object (no markdown, no extra text) with these keys:\n"
            + "\n".join(lines))


def extract_json(text: str) -> str:
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("no JSON object found in reply")
    return text[start:end + 1]


def parse_reply[T: BaseModel](text: str, schema: type[T]) -> T:
    try:
        return schema.model_validate(json.loads(extract_json(text)))
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(str(e).splitlines()[0]) from e


def partial_thought(text: str) -> str | None:
    """The (possibly unfinished) "thought" string from a JSON reply still being streamed."""
    m = _PARTIAL_THOUGHT.search(text)
    if not m:
        return None
    raw = m.group(1)
    try:
        return json.loads(f'"{raw}"')
    except json.JSONDecodeError:
        return raw.replace('\\"', '"').replace("\\n", "\n")
