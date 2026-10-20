"""Verify docs/ files against docs/manifest.json (sha256).

Usage: uv run python scripts/check_docs_manifest.py docs
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT_ONLY_FILES = {"CLAUDE.md"}  # lives at repo root, not under docs/


def check(docs_dir: Path) -> tuple[int, list[str], list[str]]:
    manifest = json.loads((docs_dir / "manifest.json").read_text())
    changed: list[str] = []
    missing: list[str] = []
    ok = 0
    for rel, meta in manifest["files"].items():
        if rel in ROOT_ONLY_FILES:
            continue
        path = docs_dir / rel
        if not path.exists():
            missing.append(rel)
        elif hashlib.sha256(path.read_bytes()).hexdigest() != meta["sha256"]:
            changed.append(rel)
        else:
            ok += 1
    return ok, changed, missing


def main() -> int:
    docs_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "docs")
    ok, changed, missing = check(docs_dir)
    print(f"{ok} files OK, {len(changed)} changed, {len(missing)} missing")
    for rel in changed:
        print("  changed:", rel)
    for rel in missing:
        print("  missing:", rel)
    return 1 if changed or missing else 0


if __name__ == "__main__":
    sys.exit(main())
