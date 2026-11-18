"""No tracked file carries a local path: home, session scratchpad or Desktop folder layout.

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
DESKTOP = "~/" + "Desktop"
WORKSPACE = DESKTOP + "/DATAMAD"
SLUG = "-" + "Users" + "-"  # a project slug starts so: the home folder with hyphens for slashes


def test_redact_replaces_home_and_scratchpad() -> None:
    redact = _redact_paths().redact
    home = USERS + "/jane.doe-1/code/repo/apps/web"
    scratch = "/private" + TMP + "501/" + SLUG + "jane-Desktop-repo/abc/tasks/x.txt"
    assert redact(f" RUN  v5.0.5 {home}\n") == " RUN  v5.0.5 ~/code/repo/apps/web\n"
    assert redact(f"see {scratch}") == "see <scratchpad>/abc/tasks/x.txt"
    assert redact(TMP + "501/" + SLUG + "jane-x/f") == "<scratchpad>/f"
    bare = USERS + "/bob"
    assert redact(f'"{bare}" ({bare}) {bare}:12, {bare}, {bare}.') == '"~" (~) ~:12, ~, ~.'
    untouched = f"~/code and {USERS}/<usuario>/ and /usr/bin and /opt{bare}/x and Docker Desktop"
    assert redact(untouched) == untouched


def test_redact_replaces_the_repo_checkout() -> None:
    redact = _redact_paths().redact
    repo = WORKSPACE + "/housing-intelligence"
    assert redact(f" RUN  v5.0.5 {repo}/apps/web\n") == " RUN  v5.0.5 <repo>/apps/web\n"
    from_home = USERS + "/jane/Desktop/DATAMAD/housing-intelligence"
    assert redact(f"--directory {from_home} hi-mcp") == "--directory <repo> hi-mcp"
    assert redact(f"`{repo}`, {repo}.") == "`<repo>`, <repo>."


def test_redact_replaces_the_workspace_and_its_sibling_folders() -> None:
    redact = _redact_paths().redact
    assert redact(f"{WORKSPACE}/hi-web/apps/web") == "<workspace>/hi-web/apps/web"
    assert redact(f"DIR={WORKSPACE}/prompts/ref npm") == "DIR=<workspace>/prompts/ref npm"
    assert redact(f"en `{WORKSPACE}` y") == "en `<workspace>` y"
    archive = WORKSPACE + "/housing-intelligence-archive"
    assert redact(archive) == "<workspace>/housing-intelligence-archive"


def test_redact_replaces_any_other_desktop_path() -> None:
    redact = _redact_paths().redact
    assert redact(f"{DESKTOP}/repo/apps/web") == "<desktop>/repo/apps/web"
    assert redact(f"en {DESKTOP}.") == "en <desktop>."
    assert redact(USERS + "/jane/Desktop") == "<desktop>"
    assert redact(f"{WORKSPACE}x/y") == "<desktop>/DATAMADx/y"


def test_redact_replaces_a_project_slug_outside_a_scratchpad() -> None:
    """Claude Code's project folders (`~/.claude/projects/<slug>`) carry the Mac's user name."""
    redact = _redact_paths().redact
    memory = USERS + "/jane/.claude/projects/" + SLUG + "jane-Desktop-DATAMAD/memory/MEMORY.md"
    assert redact(memory) == "~/.claude/projects/<project-slug>/memory/MEMORY.md"
    projects = "~/.claude/projects/"
    assert redact(projects + SLUG + "x-Desktop-a") == projects + "<project-slug>"
    assert redact(f"slug {SLUG}jane-Desktop.") == "slug <project-slug>"
    # Not inside a longer word, and a scratchpad still reads as one
    untouched = f"see-also{SLUG}guide and Users-x"
    assert redact(untouched) == untouched
    assert redact(TMP + "501/" + SLUG + "jane-x/abc") == "<scratchpad>/abc"


def test_redact_leaves_its_own_output_alone() -> None:
    redact = _redact_paths().redact
    slug = f"~/.claude/projects/{SLUG}jane-Desktop/m"
    repo = WORKSPACE + "/housing-intelligence"
    once = redact(f"{USERS}/jane {DESKTOP}/a {WORKSPACE}/b {repo}/c {slug}")
    assert once == "~ <desktop>/a <workspace>/b <repo>/c ~/.claude/projects/<project-slug>/m"
    assert redact(once) == once


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
