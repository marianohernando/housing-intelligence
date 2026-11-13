"""Gate 3 golden walking-access cases against DATABASE_URL (data/fixtures/golden/walk_golden.yaml).

Each case: the feature has a value for the zone, within the expected bounds, with a confidence
of at least 0.5. Then, over every computed row, the median and the share of each destination
agree: the street-weighted median is within the window exactly when half the street or more is.
Exit 1 on any failure.
Usage: uv run python scripts/check_walk_golden.py
"""

import sys
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import Connection, text

from hi_contracts.catalog import FeatureSpec
from hi_db.session import make_engine
from hi_ingestion.catalog.loader import load_catalog

GOLDEN = Path(__file__).resolve().parents[1] / "data" / "fixtures" / "golden" / "walk_golden.yaml"
MIN_CONFIDENCE = 0.5
VALUE_SQL = text(
    """
    SELECT value, confidence FROM feature_value
     WHERE feature_id = :feature AND territory_level = :level AND territory_code = :code
    """
)
DISAGREE_SQL = text(
    """
    SELECT count(*) FILTER (WHERE m.value IS NOT NULL) AS compared,
           count(*) FILTER (WHERE (m.value IS NULL) <> (s.value IS NULL)
                               OR (m.value <= :window) <> (s.value >= 50)) AS disagree
      FROM feature_value m
      JOIN feature_value s USING (territory_level, territory_code)
     WHERE m.feature_id = :median AND s.feature_id = :share
    """
)


def _case_failures(conn: Connection, case: dict[str, Any]) -> list[str]:
    row = conn.execute(VALUE_SQL, case).mappings().first()
    if row is None or row["value"] is None:
        return ["no value"]
    value, failures = float(row["value"]), []
    if "max" in case and value > case["max"]:
        failures.append(f"{value:.1f} > {case['max']}")
    if "min" in case and value < case["min"]:
        failures.append(f"{value:.1f} < {case['min']}")
    if float(row["confidence"]) < MIN_CONFIDENCE:
        failures.append(f"confidence {row['confidence']:.2f}")
    return failures


def _destination(spec: FeatureSpec) -> tuple[Any, ...]:
    f = spec.formula.model_dump()
    return (f["destination_category"], str(f.get("subcategories")), str(f.get("attributes")))


def walk_pairs() -> list[tuple[str, str, float]]:
    """(median feature, share feature, window in minutes) for each destination kind."""
    walk = [s for s in load_catalog().features.values() if s.formula.method == "network_walk_time"]
    medians = {
        _destination(s): s.feature_id
        for s in walk
        if s.formula.model_dump()["statistic"] == "median_minutes"
    }
    return [
        (medians[_destination(s)], s.feature_id, float(s.formula.model_dump()["within_minutes"]))
        for s in walk
        if s.formula.model_dump()["statistic"] == "share_within"
    ]


def main() -> int:
    cases = yaml.safe_load(GOLDEN.read_text())["cases"]
    failed = 0
    with make_engine().connect() as conn:
        for case in cases:
            failures = _case_failures(conn, case)
            failed += bool(failures)
            print(f"{'FAIL' if failures else 'PASS'} {case['id']}: {'; '.join(failures) or 'ok'}")
        for median, share, window in walk_pairs():
            params = {"median": median, "share": share, "window": window}
            row = conn.execute(DISAGREE_SQL, params).mappings().one()
            bad = row["disagree"] > 0 or row["compared"] == 0
            failed += bad
            print(
                f"{'FAIL' if bad else 'PASS'} {median} <= {window:g} min <=> {share} >= 50 %: "
                f"{row['compared']} zones, {row['disagree']} disagree"
            )
    print(f"{failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
