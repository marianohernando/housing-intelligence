"""Verify or regenerate docs/manifest.json (sha256 of every documentation file).

Usage:
  uv run python scripts/check_docs_manifest.py docs              # verify
  uv run python scripts/check_docs_manifest.py docs --write 0.5.2  # regenerate
`CLAUDE.md` lives at the repo root and is tracked under that key.
"""

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT_FILES = {"CLAUDE.md"}
TRACKED_SUFFIXES = {".md"}


def _resolve(docs_dir: Path, rel: str) -> Path:
    return docs_dir.parent / rel if rel in ROOT_FILES else docs_dir / rel


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(docs_dir: Path) -> tuple[int, list[str], list[str]]:
    manifest = json.loads((docs_dir / "manifest.json").read_text())
    changed: list[str] = []
    missing: list[str] = []
    ok = 0
    for rel, meta in manifest["files"].items():
        path = _resolve(docs_dir, rel)
        if not path.exists():
            missing.append(rel)
        elif _sha(path) != meta["sha256"]:
            changed.append(rel)
        else:
            ok += 1
    return ok, changed, missing


def write(docs_dir: Path, version: str) -> int:
    files = sorted(p for p in docs_dir.rglob("*") if p.is_file() and p.suffix in TRACKED_SUFFIXES)
    entries = {str(p.relative_to(docs_dir)): p for p in files}
    entries |= {name: docs_dir.parent / name for name in ROOT_FILES}
    manifest = {
        "version": version,
        "updated": datetime.now(UTC).isoformat(),
        "markdown_files": len(entries),
        "files": {
            k: {"sha256": _sha(p), "bytes": p.stat().st_size} for k, p in sorted(entries.items())
        },
    }
    (docs_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    )
    print(f"wrote manifest v{version} with {len(entries)} files")
    return 0


def main() -> int:
    docs_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "docs")
    if "--write" in sys.argv:
        return write(docs_dir, sys.argv[sys.argv.index("--write") + 1])
    ok, changed, missing = check(docs_dir)
    print(f"{ok} files OK, {len(changed)} changed, {len(missing)} missing")
    for rel in changed:
        print("  changed:", rel)
    for rel in missing:
        print("  missing:", rel)
    return 1 if changed or missing else 0


if __name__ == "__main__":
    sys.exit(main())
