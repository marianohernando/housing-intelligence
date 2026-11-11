"""QA for padrón observations: the stat-table checks plus district coverage and a census check."""

from hi_contracts.catalog import MetricSpec
from hi_contracts.catalog.pipeline import MadridPadronPipeline
from hi_domain.population import TOTAL_AGE
from hi_ingestion.pipelines.stat_tables.normalize import Observations
from hi_ingestion.pipelines.stat_tables.quality import (
    CheckResult,
    QualityReport,
    district_checks,
    run_quality,
)

# Padrón and census differ in date and method (registered vs counted residents); beyond this
# gap the comparison is flagged for review, never blocking.
CENSUS_TOLERANCE = 0.05
# A district's population moves well under 1 % a month. Missing ages are published as 0, so a
# truncated file would look like a district that suddenly lost people: that blocks.
DISTRICT_CHANGE_TOLERANCE = 0.10


def district_totals(obs: Observations) -> dict[str, float]:
    frame = obs.frame
    totals = frame.loc[[dims.get("edad") == TOTAL_AGE for dims in frame["dims"]]]
    return {
        str(code): float(value)
        for code, value in zip(totals["territory_code"], totals["value"], strict=True)
    }


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
) -> QualityReport:
    base = run_quality(obs, {spec.metric_id: metrics[spec.metric_id]}, known_municipios=set())
    totals = district_totals(obs)
    return QualityReport(
        [
            *base.checks,
            *district_checks(obs.frame, known_districts, spec.expected_districts),
            _stability_check(totals, previous_totals),
            _census_check(sum(totals.values()), census_total),
        ]
    )
