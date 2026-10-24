"""Fast syntax gate: parse game entrypoints without importing Pygame."""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINTS = (
    "endless-platformer/main.py",
    "frog-crossing/main.py",
    "maze-roguelite/main.py",
    "pixel-patchwork/main.py",
    "pong/pong.py",
    "poste-slime/main.py",
    "tower-defense/main.py",
)


def validate() -> list[str]:
    failures = []
    for entrypoint in ENTRYPOINTS:
        path = ROOT / entrypoint
        if not path.is_file():
            failures.append(f"Missing game entrypoint: {entrypoint}")
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=entrypoint)
        except (SyntaxError, UnicodeError) as error:
            failures.append(f"{entrypoint}: {error}")
    return failures


if __name__ == "__main__":
    errors = validate()
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"OK: {len(ENTRYPOINTS)} playable entrypoints parse correctly")
