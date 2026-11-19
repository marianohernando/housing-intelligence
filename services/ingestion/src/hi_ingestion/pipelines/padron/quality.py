"""QA for padrón observations: the stat-table checks plus district coverage and a census check."""

from hi_contracts.catalog import MetricSpec
from hi_contracts.catalog.pipeline import MadridPadronPipeline
from hi_domain.population import TOTAL_AGE
from hi_ingestion.pipelines.stat_tables.normalize import Observations
from hi_ingestion.pipelines.stat_tables.quality import (
    CheckResult,
    QualityReport,
    barrio_checks,
    district_checks,
    run_quality,
)

# Padrón and census differ in date and method (registered vs counted residents); beyond this
# gap the comparison is flagged for review, never blocking.
CENSUS_TOLERANCE = 0.05
# A district's population moves well under 1 % a month. Missing ages are published as 0, so a
# truncated file would look like a district that suddenly lost people: that blocks.
DISTRICT_CHANGE_TOLERANCE = 0.10
# D-247: a few people may come without a barrio (2 of 3.5 million on 1 Oct 2026). Beyond this
# share of a district, the barrio column is broken and the barrios would be short: that blocks.
WITHOUT_BARRIO_TOLERANCE = 0.001


def district_totals(obs: Observations, level: str = "distrito") -> dict[str, float]:
    frame = obs.frame
    rows = frame.loc[
        [
            lvl == level and dims.get("edad") == TOTAL_AGE
            for lvl, dims in zip(frame["territory_level"], frame["dims"], strict=True)
        ]
    ]
    return {
        str(code): float(value)
        for code, value in zip(rows["territory_code"], rows["value"], strict=True)
    }


def _barrios_add_up(obs: Observations, districts: dict[str, float]) -> list[CheckResult]:
    """Each district's barrios add up to it, but for the people without a barrio."""
    barrios = district_totals(obs, "barrio")
    if not barrios:
        return []
    added: dict[str, float] = {}
    for code, value in barrios.items():
        added[code[:7]] = added.get(code[:7], 0.0) + value
    short = {code: total - added.get(code, 0.0) for code, total in districts.items()}
    broken = sorted(
        code
        for code, gap in short.items()
        if gap < 0 or gap > WITHOUT_BARRIO_TOLERANCE * districts[code]
    )
    return [
        CheckResult(
            "barrios_add_up_to_districts",
            critical=True,
            passed=not broken,
            details={
                "without_barrio": {code: gap for code, gap in short.items() if gap},
                "broken": broken,
                "tolerance": WITHOUT_BARRIO_TOLERANCE,
            },
        )
    ]


def _census_check(padron_total: float, census_total: float | None) -> CheckResult:
    if not census_total:
        return CheckResult("total_vs_cm_census", False, True, {"census_total": None})
    ratio = padron_total / census_total
    return CheckResult(
        "total_vs_cm_census",
        critical=False,
        passed=abs(ratio - 1) <= CENSUS_TOLERANCE,
        details={
            "padron_total": padron_total,
            "census_total": census_total,
            "ratio": round(ratio, 4),
            "tolerance": CENSUS_TOLERANCE,
        },
    )


def _stability_check(current: dict[str, float], previous: dict[str, float] | None) -> CheckResult:
    """Each district against the last valid version (first load: nothing to compare)."""
    if not previous:
        return CheckResult("district_totals_stable", True, True, {"previous": None})
    changed = sorted(
        code
        for code, value in current.items()
        if previous.get(code)
        and abs(value - previous[code]) / previous[code] > DISTRICT_CHANGE_TOLERANCE
    )
    return CheckResult(
        "district_totals_stable",
        critical=True,
        passed=not changed,
        details={"changed": changed, "tolerance": DISTRICT_CHANGE_TOLERANCE},
    )


def run_padron_quality(
    obs: Observations,
    spec: MadridPadronPipeline,
    metrics: dict[str, MetricSpec],
    known_districts: set[str],
    census_total: float | None,
    previous_totals: dict[str, float] | None = None,
    known_barrios: set[str] | None = None,
) -> QualityReport:
    base = run_quality(obs, {m: metrics[m] for m in spec.metric_ids()}, known_municipios=set())
    totals = district_totals(obs)
    return QualityReport(
        [
            *base.checks,
            *district_checks(obs.frame, known_districts, spec.expected_districts),
            *barrio_checks(obs.frame, known_barrios or set(), spec.expected_barrios),
            *_barrios_add_up(obs, totals),
            _stability_check(totals, previous_totals),
            _census_check(sum(totals.values()), census_total),
        ]
    )
