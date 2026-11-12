"""QA for a directory: the region is all there, ids are unique, capacity is a number."""

from hi_contracts.catalog.pipeline import FacilityDirectoryPipeline
from hi_ingestion.pipelines.directory.normalize import Directory, published_capacities
from hi_ingestion.pipelines.places.quality import PII_TERMS, CheckResult, QualityReport

MAX_QUARANTINE_RATIO = 0.05
MIN_CAPACITY_SHARE = 0.9  # a directory that declares capacity publishes it for almost everyone


def run_directory_quality(directory: Directory, spec: FacilityDirectoryPipeline) -> QualityReport:
    frame = directory.frame
    kept = len(frame) + len(directory.quarantine)
    ratio = len(directory.quarantine) / kept if kept else 1.0
    duplicated = int(frame["external_id"].duplicated().sum())
    leaked = [c for c in spec.kept_columns() if any(t in c.casefold() for t in PII_TERMS)]
    checks = [
        CheckResult(
            "rows_in_scope",
            True,
            spec.min_rows <= len(frame) <= spec.max_rows,
            {"entries": len(frame), "min": spec.min_rows, "max": spec.max_rows},
        ),
        CheckResult("unique_ids", True, duplicated == 0, {"duplicates": duplicated}),
        CheckResult(
            "quarantine_ratio",
            True,
            ratio <= MAX_QUARANTINE_RATIO,
            {
                "quarantined": len(directory.quarantine),
                "ratio": round(ratio, 4),
                "rows": directory.quarantine.to_dict("records"),  # pyright: ignore[reportUnknownMemberType]
            },
        ),
        CheckResult("no_contact_columns", True, not leaked, {"leaked_columns": leaked}),
        CheckResult(
            "scope_filter",
            False,
            True,
            {"source_rows": directory.source_rows, "out_of_scope": directory.out_of_scope},
        ),
    ]
    if spec.capacity_column:
        capacities = published_capacities(directory)
        share = len(capacities) / len(frame) if len(frame) else 0.0
        checks.append(
            CheckResult(
                "capacity_published",
                True,
                share >= MIN_CAPACITY_SHARE,
                {"share": round(share, 4), "total": sum(capacities)},
            )
        )
    return QualityReport(checks)
