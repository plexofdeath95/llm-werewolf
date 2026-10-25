"""Hard project rule (CLAUDE.md): every source file is at most 100 lines."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {".venv", "node_modules", "dist", ".git", "data"}
LIMIT = 100


def test_no_source_file_exceeds_limit():
    too_long = []
    for path in ROOT.rglob("*"):
        if path.suffix not in {".py", ".ts", ".tsx"} or SKIP & set(path.parts):
            continue
        n = len(path.read_text(encoding="utf-8").splitlines())
        if n > LIMIT:
            too_long.append(f"{path.relative_to(ROOT)}: {n} lines")
    assert not too_long, "files over 100 lines:\n" + "\n".join(too_long)
