"""Gate 2 golden transport cases against DATABASE_URL (data/fixtures/golden/transport_golden.yaml).

Each case: a stop of the dataset lies near a public landmark, matches the expected name, falls in
the expected municipio and census section, and shows plausible service. Exit 1 on any failure.
Usage: uv run python scripts/check_transport_golden.py
"""

import sys
import unicodedata
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import Connection, text

from hi_db.session import make_engine

GOLDEN = (
    Path(__file__).resolve().parents[1] / "data" / "fixtures" / "golden" / "transport_golden.yaml"
)
NEAR_SQL = text(
    """
    SELECT canonical_name, municipio_ine, seccion_admin_unit_id, attributes,
           round(ST_Distance(geom_25830, ST_Transform(
               ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), 25830))) AS distance_m
      FROM place_master
     WHERE official_dataset_id = :dataset_id
       AND ST_DWithin(geom_25830, ST_Transform(
               ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), 25830), :radius_m)
     ORDER BY distance_m
    """
)


def _plain(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def _failures(case: dict[str, Any], rows: list[dict[str, Any]]) -> list[str]:
    if "name_contains" in case:
        rows = [r for r in rows if _plain(case["name_contains"]) in _plain(r["canonical_name"])]
    if len(rows) < case.get("min_count", 1):
        return [f"{len(rows)} matching stops within {case['radius_m']} m"]
    best, attrs = rows[0], rows[0]["attributes"]
    problems: list[str] = []
    if "municipio_ine" in case and best["municipio_ine"] != case["municipio_ine"]:
        problems.append(f"municipio {best['municipio_ine']} != {case['municipio_ine']}")
    if best["seccion_admin_unit_id"] is None:
        problems.append("no census section assigned")
    if "headway_peak_min" in case:
        low, high = case["headway_peak_min"]
        headway = attrs.get("headway_peak_min")
        if headway is None or not low <= headway <= high:
            problems.append(f"peak headway {headway} outside [{low}, {high}]")
    if attrs.get("n_routes", 0) < case.get("min_routes", 0):
        problems.append(f"{attrs.get('n_routes')} routes < {case['min_routes']}")
    if attrs.get("departures_day", 0) < case.get("min_departures_day", 1):
        problems.append(f"{attrs.get('departures_day')} departures a day")
    return problems


def check(conn: Connection, case: dict[str, Any]) -> bool:
    params = {k: case[k] for k in ("lon", "lat", "dataset_id", "radius_m")}
    rows = [dict(r) for r in conn.execute(NEAR_SQL, params).mappings()]
    problems = _failures(case, rows)
    nearest = f"{rows[0]['canonical_name']} at {rows[0]['distance_m']} m" if rows else "none"
    verdict = "FAIL" if problems else "PASS"
    print(f"{verdict}  {case['id']}: {case['label']} -> nearest {nearest} {problems or ''}")
    return not problems


def main() -> int:
    cases: list[dict[str, Any]] = yaml.safe_load(GOLDEN.read_text())["cases"]
    with make_engine().connect() as conn:
        results = [check(conn, case) for case in cases]
    print(f"{sum(results)}/{len(results)} golden transport cases PASS")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
