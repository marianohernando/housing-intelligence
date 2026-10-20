"""Verify docs/ files against docs/manifest.json (sha256). Usage: check_docs_manifest.py docs/"""
import hashlib, json, sys
from pathlib import Path

def main(docs_dir: str) -> int:
    root = Path(docs_dir)
    manifest = json.loads((root / "manifest.json").read_text())
    bad, missing, ok = [], [], 0
    for rel, meta in manifest["files"].items():
        if rel == "CLAUDE.md":
            continue  # lives at repo root
        p = root / rel
        if not p.exists():
            missing.append(rel); continue
        if hashlib.sha256(p.read_bytes()).hexdigest() != meta["sha256"]:
            bad.append(rel); continue
        ok += 1
    print(f"{ok} files OK, {len(bad)} changed, {len(missing)} missing (manifest v{manifest['version']})")
    for r in bad: print("  changed:", r)
    for r in missing: print("  missing:", r)
    return 1 if (bad or missing) else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "docs"))
