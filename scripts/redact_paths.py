"""Replace local paths (they reveal the user's name and the Mac's folder layout) in output.

Home directories become `~` and session scratchpads `<scratchpad>`. Under the Desktop, the repo
checkout becomes `<repo>`, the folder that holds it next to its sibling worktrees and notes
`<workspace>`, and any other Desktop path `<desktop>`. Use it as a filter before saving output
as evidence:
    make test 2>&1 | uv run python scripts/redact_paths.py > evidence/gate-XX/<date>/<file>.txt
scripts/evidence.py applies it to every log, and tests/data/test_no_local_paths.py fails if a
tracked file still has one of these paths.
"""

import re
import sys

NAME = r"[A-Za-z0-9._-]*[A-Za-z0-9_-]"  # a trailing dot is punctuation, not part of the name
START = r"(?<![\w.-])"  # not inside a longer path (under /opt, say)
END = r"(?![\w-])"  # the whole folder name, not a prefix of a longer one

# Built in pieces so that this file holds no path the tree test would flag.
HOME_ROOT = "/" + "Users"
DESKTOP = "~/" + "Desktop"
WORKSPACE = DESKTOP + "/DATAMAD"
REPO = WORKSPACE + "/housing-intelligence"

# Order matters: a home path becomes `~` first, so the Desktop patterns also catch it.
PATTERNS = [
    (re.compile(rf"(?:/private)?/tmp/claude-[0-9]+/{NAME}"), "<scratchpad>"),
    (re.compile(rf"{START}{HOME_ROOT}/{NAME}"), "~"),
    (re.compile(rf"{START}{re.escape(REPO)}{END}"), "<repo>"),
    (re.compile(rf"{START}{re.escape(WORKSPACE)}{END}"), "<workspace>"),
    (re.compile(rf"{START}{re.escape(DESKTOP)}{END}"), "<desktop>"),
]


def redact(text: str) -> str:
    for pattern, replacement in PATTERNS:
        text = pattern.sub(replacement, text)
    return text


if __name__ == "__main__":
    sys.stdout.write(redact(sys.stdin.read()))
