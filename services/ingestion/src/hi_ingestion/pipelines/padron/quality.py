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


def _padron_total(obs: Observations) -> float:
    frame = obs.frame
    totals = frame.loc[[dims.get("edad") == TOTAL_AGE for dims in frame["dims"]], "value"]
    return float(totals.sum())


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


def run_padron_quality(
    obs: Observations,
    spec: MadridPadronPipeline,
    metrics: dict[str, MetricSpec],
    known_districts: set[str],
    census_total: float | None,
) -> QualityReport:
    base = run_quality(obs, {spec.metric_id: metrics[spec.metric_id]}, known_municipios=set())
    return QualityReport(
        [
            *base.checks,
            *district_checks(obs.frame, known_districts, spec.expected_districts),
            _census_check(_padron_total(obs), census_total),
        ]
    )
