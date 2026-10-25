"""Prompt templates: <mode>/prompts/<name>.md first, then the shared aiplays/prompts/."""
from functools import lru_cache
from pathlib import Path
from string import Template

SHARED = Path(__file__).resolve().parent.parent / "prompts"


@lru_cache
def _template(path: Path) -> Template:
    return Template(path.read_text(encoding="utf-8"))


def render(template: str, mode_dir: Path | None = None, /, **values: object) -> str:
    """Positional-only template/mode_dir, so any key (even `name`) can be a value."""
    for folder in (mode_dir, SHARED):
        if folder and (folder / f"{template}.md").exists():
            return _template(folder / f"{template}.md").safe_substitute(**values).strip()
    raise FileNotFoundError(f"prompt template not found: {template}")
