"""Replace local home and session scratchpad paths (they contain the user's name) in output.

Home directories become `~` and session scratchpads `<scratchpad>`. Use it as a filter before
saving output as evidence:
    make test 2>&1 | uv run python scripts/redact_paths.py > evidence/gate-XX/<date>/<file>.txt
scripts/evidence.py applies it to every log, and tests/data/test_no_local_paths.py fails if a
tracked file still has one of these paths.
"""

import re
import sys

NAME = r"[A-Za-z0-9._-]*[A-Za-z0-9_-]"  # a trailing dot is punctuation, not part of the name
PATTERNS = [
    (re.compile(rf"(?:/private)?/tmp/claude-[0-9]+/{NAME}"), "<scratchpad>"),
    (re.compile(rf"(?<![\w.-])/Users/{NAME}"), "~"),  # not inside a longer path (/opt/Users/…)
]


def redact(text: str) -> str:
    for pattern, replacement in PATTERNS:
        text = pattern.sub(replacement, text)
    return text


if __name__ == "__main__":
    sys.stdout.write(redact(sys.stdin.read()))
