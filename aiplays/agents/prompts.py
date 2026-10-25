"""Prompt templates: <mode>/prompts/<name>.md first, then the shared aiplays/prompts/."""
from functools import lru_cache
from pathlib import Path
from string import Template

SHARED = Path(__file__).resolve().parent.parent / "prompts"


@lru_cache
def _template(path: Path) -> Template:
    return Template(path.read_text(encoding="utf-8"))


def render(name: str, mode_dir: Path | None = None, **values: object) -> str:
    for folder in (mode_dir, SHARED):
        if folder and (folder / f"{name}.md").exists():
            return _template(folder / f"{name}.md").safe_substitute(**values).strip()
    raise FileNotFoundError(f"prompt template not found: {name}")
