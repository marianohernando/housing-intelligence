"""The census of premises of Madrid (D-247) on the generic runner, with its blocking checks."""

import uuid
from pathlib import Path
from typing import Any

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from hi_contracts.catalog import MetricSpec
from hi_contracts.catalog.pipeline import MadridPremisesCensusPipeline
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.padron.run import known_barrios, known_districts
from hi_ingestion.pipelines.premises.normalize import (
    PremisesObservations,
    clean,
    normalize_premises,
)
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline
from hi_ingestion.pipelines.stat_tables.publish import replace_observations
from hi_ingestion.pipelines.stat_tables.quality import (
    CheckResult,
    QualityReport,
    barrio_checks,
    district_checks,
    row_counts,
    run_quality,
)
from hi_ingestion.pipelines.stat_tables.run import write_silver

PARSER_VERSION = "madrid_premises_census-1.0.0"


def proximity_labels_check(
    result: PremisesObservations, spec: MadridPremisesCensusPipeline
) -> list[CheckResult]:
    """Blocking: every proximity epígrafe the file uses carries the declared description (a
    changed one is read by a person first). One the file no longer uses is reported."""
    declared = {code: label for group in spec.proximity.values() for code, label in group.items()}
    changed = {
        code: result.epigrafes[code]
        for code, label in declared.items()
        if code in result.epigrafes and clean(result.epigrafes[code]) != clean(label)
    }
    absent = sorted(code for code in declared if code not in result.epigrafes)
    return [
        CheckResult("proximity_epigrafes_as_declared", True, not changed, {"changed": changed}),
        CheckResult("proximity_epigrafes_in_the_file", False, not absent, {"absent": absent}),
    ]


def premises_quality(
    result: PremisesObservations,
    spec: MadridPremisesCensusPipeline,
    metrics: dict[str, MetricSpec],
    districts: set[str],
    barrios: set[str],
) -> QualityReport:
    """The common checks on what is published, and on the whole file: its size, one load date,
    no undeclared code, few premises without a barrio and the 21 districts and 131 barrios."""
    base = run_quality(result.obs, metrics, set())
    frame = result.obs.frame
    blocking = result.obs.quarantine.loc[result.obs.quarantine["blocking"].astype(bool)]
    extra = [
        CheckResult(
            "file_size",
            True,
            spec.min_rows <= result.rows <= spec.max_rows,
            {"rows": result.rows, "min": spec.min_rows, "max": spec.max_rows},
        ),
        CheckResult(
            "one_load_date", True, len(result.dates) == 1, {"dates": sorted(map(str, result.dates))}
        ),
        CheckResult(
            "no_undeclared_code",
            True,
            blocking.empty,
            {"rows": len(blocking), "reasons": blocking["reason"].value_counts().head(5).to_dict()},
        ),
        CheckResult(
            "few_premises_without_barrio",
            True,
            result.unplaced <= spec.max_unplaced,
            {"unplaced": result.unplaced, "max": spec.max_unplaced},
        ),
        *proximity_labels_check(result, spec),
        *district_checks(frame, districts, spec.expected_districts),
        *barrio_checks(frame, barrios, spec.expected_barrios),
    ]
    return QualityReport([*base.checks, *extra])


def counts(result: PremisesObservations) -> dict[str, Any]:
    return row_counts(result.obs.frame) | {
        "rows": result.rows,
        "premises": result.premises,
        "counted": result.counted,
        "pending_epigrafe_rows": result.pending,
        "unplaced": result.unplaced,
        **{f"not_counted|{k}": v for k, v in sorted(result.not_counted.items())},
    }


def premises_steps(
    engine: Engine, catalog: Catalog, spec: MadridPremisesCensusPipeline
) -> PipelineSteps[PremisesObservations]:
    metrics = {m: catalog.metrics[m] for m in spec.metric_ids()}

    def publish(
        session: Session, result: PremisesObservations, version_id: uuid.UUID
    ) -> dict[str, int]:
        frame = result.obs.frame
        return {"observations": replace_observations(session, frame, spec.metric_ids(), version_id)}

    return PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=spec.csv,
        resource_role=spec.resource_role,
        normalize=lambda frame: normalize_premises(frame, spec),
        quarantine=lambda result: result.obs.quarantine,
        quality=lambda result: premises_quality(
            result,
            spec,
            metrics,
            known_districts(engine, spec.municipio_ine),
            known_barrios(engine, spec.municipio_ine),
        ).to_dict(),
        counts=counts,
        write_silver=lambda result, directory: write_silver(result.obs, directory),
        publish=publish,
    )


def run_premises_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: MadridPremisesCensusPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
) -> RunSummary:
    return run_pipeline(
        engine,
        catalog,
        spec.dataset_id,
        premises_steps(engine, catalog, spec),
        source,
        evidence_root=evidence_root,
        data_dir=data_dir,
    )
