"""No tracked file carries a local home or session scratchpad path (they contain the user's name).

The patterns live in scripts/redact_paths.py, which also cleans command output before it is saved
as evidence: `make test 2>&1 | uv run python scripts/redact_paths.py > evidence/...`.
"""

import importlib.util
import shutil
import subprocess
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[2]


def _redact_paths() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "redact_paths", REPO_ROOT / "scripts" / "redact_paths.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Built in pieces so that this file holds no path the tree test below would flag.
USERS, TMP = "/Users", "/tmp/claude-"  # noqa: S108 (test data, not a temporary file)


def test_redact_replaces_home_and_scratchpad() -> None:
    redact = _redact_paths().redact
    home = USERS + "/jane.doe-1/Desktop/repo/apps/web"
    scratch = "/private" + TMP + "501/-Users-jane-Desktop-repo/abc/tasks/x.txt"
    assert redact(f" RUN  v5.0.5 {home}\n") == " RUN  v5.0.5 ~/Desktop/repo/apps/web\n"
    assert redact(f"see {scratch}") == "see <scratchpad>/abc/tasks/x.txt"
    assert redact(TMP + "501/-Users-jane-x/f") == "<scratchpad>/f"
    bare = USERS + "/bob"
    assert redact(f'"{bare}" ({bare}) {bare}:12, {bare}, {bare}.') == '"~" (~) ~:12, ~, ~.'
    untouched = f"~/Desktop and {USERS}/<usuario>/ and /usr/bin and /opt{bare}/x"
    assert redact(untouched) == untouched


def test_no_tracked_file_has_a_local_path() -> None:
    redact = _redact_paths().redact
    git = shutil.which("git")
    assert git, "git is needed to list the tracked files"
    files = subprocess.run(  # noqa: S603 (fixed argv, no external input)
        [git, "ls-files", "-z"], cwd=REPO_ROOT, capture_output=True, check=True
    ).stdout.split(b"\0")
    offenders = []
    for name in filter(None, files):
        path = REPO_ROOT / name.decode()
        if not path.is_file():
            continue
        raw = path.read_bytes()
        if b"\0" in raw:
            continue
        text = raw.decode("utf-8", errors="replace")
        if redact(text) != text:
            offenders.append(name.decode())
    assert not offenders, f"local paths (run scripts/redact_paths.py over them): {offenders}"
