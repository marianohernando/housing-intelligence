"""QA for observations: keys, territories, value semantics and additivity of totals."""

from dataclasses import asdict, dataclass, field
from typing import Any

import pandas as pd

from hi_contracts.catalog import MetricSpec
from hi_contracts.catalog.enums import AggregationMethod, NullReason
from hi_ingestion.pipelines.stat_tables.normalize import Observations

KEY = ["metric_id", "territory_level", "territory_code", "period_start", "dims_key"]
MAX_QUARANTINE_RATIO = 0.005
MAX_PARSE_ERROR_RATIO = 0.001
ADDITIVITY_TOLERANCE = 0.005
ADDITIVITY_MIN_SHARE_OK = 0.99
TOTAL = "total"


@dataclass(frozen=True)
class CheckResult:
    name: str
    critical: bool
    passed: bool
    details: dict[str, Any] = field(default_factory=dict[str, Any])


@dataclass
class QualityReport:
    checks: list[CheckResult]

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks if c.critical)

    def to_dict(self) -> dict[str, Any]:
        return {"passed": self.passed, "checks": [asdict(c) for c in self.checks]}


GroupKey = tuple[str, str, str, str, tuple[tuple[str, str], ...]]


def _group_sums(
    records: list[dict[str, Any]], dim: str
) -> tuple[dict[GroupKey, float], dict[GroupKey, float]]:
    totals: dict[GroupKey, float] = {}
    members: dict[GroupKey, float] = {}
    for record in records:
        dims: dict[str, str] = record["dims"]
        if dim not in dims:
            continue
        others = tuple(sorted((k, v) for k, v in dims.items() if k != dim))
        key: GroupKey = (
            record["metric_id"],
            record["territory_level"],
            record["territory_code"],
            str(record["period_start"]),
            others,
        )
        if dims[dim] == TOTAL:
            totals[key] = float(record["value"])
        else:
            members[key] = members.get(key, 0.0) + float(record["value"])
    return totals, members


def _additivity(frame: pd.DataFrame, dims: list[str]) -> CheckResult:
    """For every dimension with a 'total' member, members (others fixed) sum to the total."""
    columns = ["metric_id", "territory_level", "territory_code", "period_start", "dims", "value"]
    records: list[dict[str, Any]] = frame.loc[frame["value"].notna(), columns].to_dict("records")  # pyright: ignore[reportAssignmentType]
    checked = 0
    failures: list[dict[str, Any]] = []
    for dim in dims:
        totals, members = _group_sums(records, dim)
        for key, total in totals.items():
            if total <= 0 or key not in members:
                continue
            checked += 1
            if abs(members[key] - total) / total > ADDITIVITY_TOLERANCE:
                failures.append(
                    {
                        "dim": dim,
                        "key": [str(k) for k in key[:4]],
                        "total": total,
                        "members": members[key],
                    }
                )
    share_ok = 1 - len(failures) / checked if checked else 1.0
    return CheckResult(
        "totals_are_additive",
        critical=False,
        passed=share_ok >= ADDITIVITY_MIN_SHARE_OK,
        details={
            "groups_checked": checked,
            "failures": len(failures),
            "failures_sample": failures[:5],
            "share_ok": round(share_ok, 5),
        },
    )


def run_quality(
    obs: Observations, metrics: dict[str, MetricSpec], known_municipios: set[str]
) -> QualityReport:
    frame = obs.frame
    duplicated = frame.duplicated(KEY)
    munis = set(frame.loc[frame["territory_level"] == "municipio", "territory_code"])
    unknown_munis = sorted(munis - known_municipios)
    sum_metrics = {
        m
        for m, spec in metrics.items()
        if spec.aggregation_method in {AggregationMethod.SUM, AggregationMethod.COUNT}
    }
    negatives = frame[(frame["metric_id"].isin(sorted(sum_metrics))) & (frame["value"] < 0)]
    parse_errors = int((frame["null_reason"] == NullReason.PARSE_ERROR.value).sum())
    missing = int((frame["null_reason"] == NullReason.SOURCE_MISSING.value).sum())
    n = max(len(frame), 1)
    dims = sorted({d for spec in metrics.values() for d in spec.dimensions})
    checks = [
        CheckResult("has_observations", True, len(frame) > 0, {"observations": len(frame)}),
        CheckResult(
            "quarantine_ratio",
            True,
            len(obs.quarantine) / max(obs.source_rows, 1) <= MAX_QUARANTINE_RATIO,
            {
                "quarantined": len(obs.quarantine),
                "reasons": obs.quarantine["reason"].value_counts().head(5).to_dict(),
            },
        ),
        CheckResult(
            "unique_keys", True, not bool(duplicated.any()), {"duplicates": int(duplicated.sum())}
        ),
        CheckResult(
            "municipios_resolve_to_geography",
            True,
            not unknown_munis,
            {"unknown": unknown_munis[:20], "municipios": len(munis)},
        ),
        CheckResult("non_negative_counts", True, negatives.empty, {"negatives": len(negatives)}),
        CheckResult(
            "parse_error_ratio",
            True,
            parse_errors / n <= MAX_PARSE_ERROR_RATIO,
            {"parse_errors": parse_errors},
        ),
        CheckResult(
            "missing_is_explicit_not_zero",
            False,
            True,
            {"source_missing": missing, "ratio": round(missing / n, 4)},
        ),
        CheckResult(
            "municipio_coverage",
            False,
            not munis or len(munis) == len(known_municipios),
            {"covered": len(munis), "expected": len(known_municipios)},
        ),
        _additivity(frame, dims),
    ]
    return QualityReport(checks)


def district_checks(
    frame: pd.DataFrame, known_districts: set[str], expected: int
) -> list[CheckResult]:
    """Blocking: every district resolves in the geography and none is missing."""
    codes = set(frame.loc[frame["territory_level"] == "distrito", "territory_code"])
    unknown = sorted(codes - known_districts)
    return [
        CheckResult(
            "districts_resolve_to_geography",
            True,
            not unknown,
            {"unknown": unknown, "districts": len(codes)},
        ),
        CheckResult(
            "district_coverage",
            True,
            len(codes) == expected,
            {"covered": len(codes), "expected": expected},
        ),
    ]


def barrio_checks(
    frame: pd.DataFrame, known_barrios: set[str], expected: int | None
) -> list[CheckResult]:
    """Blocking: every barrio row resolves in the geography (D-232) and, when the pipeline
    declares how many barrios it publishes, none is missing. No barrio rows, no checks."""
    codes = set(frame.loc[frame["territory_level"] == "barrio", "territory_code"])
    if not codes and expected is None:
        return []
    unknown = sorted(codes - known_barrios)
    checks = [
        CheckResult(
            "barrios_resolve_to_geography",
            True,
            not unknown,
            {"unknown": unknown[:20], "barrios": len(codes)},
        )
    ]
    if expected is not None:
        checks.append(
            CheckResult(
                "barrio_coverage",
                True,
                len(codes) == expected,
                {"covered": len(codes), "expected": expected},
            )
        )
    return checks


def row_counts(frame: pd.DataFrame) -> dict[str, int]:
    counts: dict[str, int] = {}
    for metric_id, level in zip(frame["metric_id"], frame["territory_level"], strict=True):
        key = f"{metric_id}|{level}"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))
