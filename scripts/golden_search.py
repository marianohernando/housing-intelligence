"""Run the golden search scenarios (data/fixtures/golden/search_scenarios.yaml) through the
real search service on the local database (read-only) and check what each one expects.

Usage: uv run python scripts/golden_search.py   (exit 1 if any expectation fails)
"""

import os
import sys
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import create_engine

from hi_api.services.search import search
from hi_contracts.public import ScenarioState, SearchResult
from hi_domain.fit import anchor_km

GOLDEN = Path(__file__).resolve().parents[1] / "data" / "fixtures" / "golden"
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://housing:housing@localhost:5440/housing"
)


def failures(result: SearchResult, expect: dict[str, Any]) -> list[str]:
    check = result.reality_check
    anchor = result.scenario.anchors[0] if result.scenario.anchors else None
    km = [anchor_km(r.zone, anchor) or 0.0 for r in result.results] if anchor else []
    rules = {
        "min_results": lambda v: len(result.results) >= v,
        "max_results": lambda v: len(result.results) <= v,
        "results_within_km": lambda v: all(k <= v for k in km),
        "top_within_km": lambda v: bool(km) and km[0] <= v,
        "all_unknown": lambda v: (check.zones_unknown == check.zones_evaluated) is v,
        "binding": lambda v: check.binding_constraint == v,
    }
    return [f"{key}={value}" for key, value in expect.items() if not rules[key](value)]


def report(profile: str, result: SearchResult, failed: list[str]) -> None:
    check = result.reality_check
    print(f"\n## {profile}: {'OK' if not failed else 'FALLA ' + ', '.join(failed)}")
    print(
        f"zonas {check.zones_evaluated} · cumplen {check.zones_passing} · "
        f"desconocidas {check.zones_unknown} · condición que más quita: {check.binding_constraint}"
    )
    for option in check.relaxations:
        print(f"  Reality Check: {option.label} → +{option.added_zones} zonas")
    for ranked in result.results[:5]:
        cost = f" · ≈ {ranked.estimated_cost_eur:.0f} €/mes" if ranked.estimated_cost_eur else ""
        print(f"  {ranked.rank}. {ranked.zone.name} · {ranked.match_pct} %{cost}")
        for fact in ranked.facts:
            print(f"       - {fact.text} (confianza {fact.confidence:.2f})")
    for miss in result.near_misses[:3]:
        print(f"  casi: {miss.zone.name} (falla {', '.join(miss.failed_constraints)})")


def main() -> int:
    scenarios = yaml.safe_load((GOLDEN / "search_scenarios.yaml").read_text())["scenarios"]
    failed_any = False
    with create_engine(DATABASE_URL).connect() as conn:
        for item in scenarios:
            scenario = ScenarioState.model_validate(item["scenario"])
            result, _, _ = search(conn, scenario)
            failed = failures(result, item["expect"])
            failed_any |= bool(failed)
            report(item["profile_id"], result, failed)
    print(f"\n{len(scenarios)} escenarios dorados · {'FALLA' if failed_any else 'todos OK'}")
    return 1 if failed_any else 0


if __name__ == "__main__":
    sys.exit(main())
