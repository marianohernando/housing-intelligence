"""Exit 0 if the latest quality_report.json of every given dataset passed.

Usage: uv run python scripts/check_quality_reports.py <dataset_id> [...]
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "evidence" / "gate-01"


def main(dataset_ids: list[str]) -> int:
    ok = True
    for dataset_id in dataset_ids:
        reports = sorted(ROOT.glob(f"*/{dataset_id}/quality_report.json"))
        passed = bool(reports) and json.loads(reports[-1].read_text())["passed"] is True
        ok &= passed
        when = reports[-1].parent.parent.name if reports else "-"
        print(f"{dataset_id:40s} {when} {'PASS' if passed else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
