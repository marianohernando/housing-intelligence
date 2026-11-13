"""Run the golden search scenarios (data/fixtures/golden/search_scenarios.yaml) through the
real search service on the local database (read-only) and check what each one expects; the
`barrio_scenarios` go through the search inside a district (D-232).

Usage: uv run python scripts/golden_search.py   (exit 1 if any expectation fails)
"""

import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import Connection, create_engine

from hi_api.services.barrios import DISTRICT_TRIP_NOTE, district, load_barrios, search_barrios
from hi_api.services.search import load, search
from hi_contracts.public import FactKind, FactTopic, RankedZone, ScenarioState, SearchResult
from hi_domain.fit import anchor_km
from hi_domain.search import run_search

GOLDEN = Path(__file__).resolve().parents[1] / "data" / "fixtures" / "golden"
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://housing:housing@localhost:5440/housing"
)


TRANSIT_MINUTES = re.compile(r"^(\d+) min en transporte público")


def transit_minutes(ranked: RankedZone) -> float | None:
    """Minutes by public transport to the first place of work, from its fact (D-220)."""
    for fact in ranked.facts:
        found = TRANSIT_MINUTES.match(fact.text) if fact.topic is FactTopic.TRAYECTO else None
        if found:
            return float(found.group(1))
    return None


TOP = 5


def failures(result: SearchResult, expect: dict[str, Any]) -> list[str]:
    check = result.reality_check
    anchor = result.scenario.anchors[0] if result.scenario.anchors else None
    km = [anchor_km(r.zone, anchor) or 0.0 for r in result.results] if anchor else []
    rules = {
        "min_results": lambda v: len(result.results) >= v,
        "max_results": lambda v: len(result.results) <= v,
        "results_within_km": lambda v: all(k <= v for k in km),
        "top_within_km": lambda v: bool(km) and km[0] <= v,
        "top_within_minutes": lambda v: (
            bool(result.results) and (transit_minutes(result.results[0]) or float("inf")) <= v
        ),
        "all_unknown": lambda v: (check.zones_unknown == check.zones_evaluated) is v,
        # D-227: buying, every result has a published appraised value behind its budget PASS
        "results_priced": lambda v: (
            all(
                any(c.constraint_id == "budget" and c.value is not None for c in r.constraints)
                for r in result.results
            )
            is v
        ),
        # D-222: the first zones have an urban park within the «Zonas verdes» window
        "top_green_strength": lambda v: (
            len(result.results) >= v
            and all(
                any(
                    f.topic is FactTopic.ZONAS_VERDES and f.kind is FactKind.STRENGTH
                    for f in r.facts
                )
                for r in result.results[:v]
            )
        ),
        # D-223: the first 5 zones have a step-free station at most v minutes away on foot
        "top5_step_free_within_minutes": lambda v: (
            len(result.results) >= TOP
            and all(
                any(
                    f.topic is FactTopic.ACCESIBILIDAD
                    and f.indicator is not None
                    and f.indicator.value is not None
                    and f.indicator.value <= v
                    for f in r.facts
                )
                for r in result.results[:TOP]
            )
        ),
        "binding": lambda v: check.binding_constraint == v,
        # D-228: with the rent of new leases the budget limits: raising it adds zones
        "budget_step_adds_zones": lambda v: any(
            r.constraint_id == "budget" and r.added_zones >= v for r in check.relaxations
        ),
        # D-232: the barrios of one district
        "barrios": lambda v: check.zones_evaluated == v,
        "ranked": lambda v: set(v) <= {r.zone.name for r in result.results},
        "near_miss": lambda v: set(v) <= {r.zone.name for r in result.near_misses},
        "distinct_pct_min": lambda v: len({z.match_pct for z in result.all_zones}) >= v,
        "own_trips": lambda v: (
            all(
                DISTRICT_TRIP_NOTE not in f.text
                for r in [*result.results, *result.near_misses]
                for f in r.facts
            )
            is v
        ),
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
    for ranked in result.results[: 10 if result.reality_check.zones_evaluated <= 10 else 5]:
        per = "" if result.scenario.budget and result.scenario.budget.kind == "buy" else "/mes"
        cost = f" · ≈ {ranked.estimated_cost_eur:.0f} €{per}" if ranked.estimated_cost_eur else ""
        print(f"  {ranked.rank}. {ranked.zone.name} · {ranked.match_pct} %{cost}")
        for fact in ranked.facts:
            print(f"       - {fact.text} (confianza {fact.confidence:.2f})")
    for miss in result.near_misses[:3]:
        print(f"  casi: {miss.zone.name} (falla {', '.join(miss.failed_constraints)})")


def main() -> int:
    golden = yaml.safe_load((GOLDEN / "search_scenarios.yaml").read_text())
    scenarios, barrio_items = golden["scenarios"], golden.get("barrio_scenarios", [])
    failed_any = False
    with create_engine(DATABASE_URL).connect() as conn:
        for item in scenarios:
            scenario = ScenarioState.model_validate(item["scenario"])
            result, _, _ = search(conn, scenario)
            failed = failures(result, item["expect"])
            # Same order whatever order the zones come in (ties never depend on the database).
            reversed_zones = load(conn, scenario).zones[::-1]
            again = [r.zone.code for r in run_search(scenario, reversed_zones).results]
            if again != [r.zone.code for r in result.results]:
                failed.append("stable_order")
            failed_any |= bool(failed)
            report(item["profile_id"], result, failed)
        failed_any |= barrio_goldens(conn, barrio_items)
    total = len(scenarios) + len(barrio_items)
    print(f"\n{total} escenarios dorados · {'FALLA' if failed_any else 'todos OK'}")
    return 1 if failed_any else 0


def barrio_goldens(conn: Connection, items: list[dict[str, Any]]) -> bool:
    """D-232: the same checks inside one district, by barrio; True if any fails."""
    failed_any = False
    for item in items:
        scenario = ScenarioState.model_validate(item["scenario"])
        result, _, _ = search_barrios(conn, scenario, item["distrito"])
        failed = failures(result, item["expect"])
        zones = load_barrios(conn, scenario, district(conn, item["distrito"])).zones[::-1]
        again = [r.zone.code for r in run_search(scenario, zones).results]
        if again != [r.zone.code for r in result.results]:
            failed.append("stable_order")
        failed_any |= bool(failed)
        report(f"{item['profile_id']} en {result.distrito.name} (barrios)", result, failed)
        print(f"  todos: {', '.join(f'{z.zone.name} {z.match_pct} %' for z in result.all_zones)}")
    return failed_any


if __name__ == "__main__":
    sys.exit(main())
