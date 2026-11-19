"""CM tables whose district is named in a free-text concept (D-247): normalize and run."""

import re
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.catalog.pipeline import CmDistrictConceptPipeline
from hi_db.models import GeoAdminUnit
from hi_domain.geo.codes import admin_unit_id
from hi_domain.geo.names import name_key
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.catalog_harvester.common import slugify
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline
from hi_ingestion.pipelines.stat_tables.normalize import (
    OBS_COLUMNS,
    Observations,
    RowError,
    dims_key,
    parse_period,
    parse_value,
)
from hi_ingestion.pipelines.stat_tables.publish import replace_observations
from hi_ingestion.pipelines.stat_tables.quality import (
    CheckResult,
    QualityReport,
    district_checks,
    row_counts,
    run_quality,
)
from hi_ingestion.pipelines.stat_tables.run import write_silver
from hi_ingestion.pipelines.zone_context.normalize import observation
from hi_ingestion.pipelines.zone_context.run import nothing_quarantined

PARSER_VERSION = "cm_district_concept-1.0.0"


def district_names(engine: Engine, municipio_ine: str) -> dict[str, str]:
    """name_key of each district of the municipio in the geography -> its code."""
    with Session(engine) as session:
        rows = session.execute(
            select(GeoAdminUnit.code_official, GeoAdminUnit.name).where(
                GeoAdminUnit.level == "distrito"
            )
        ).all()
    return {name_key(str(n)): str(c) for c, n in rows if str(c).startswith(municipio_ine)}


def _row(
    row: Mapping[str, str], spec: CmDistrictConceptPipeline, names: Mapping[str, str]
) -> dict[str, Any] | None:
    """The row's observation, or None for a row of no district (counted apart)."""
    concept = " ".join(row[spec.concept_column].split())
    if re.search(spec.unassigned_pattern, concept):
        return None
    found = re.search(spec.district_pattern, concept)
    code = names.get(name_key(found.group("district"))) if found else None
    if code is None:
        msg = f"concept {concept[:80]!r} names no district of the geography"
        raise RowError(msg)
    start, end = parse_period(row[spec.period_column])
    dims = {dim: slugify(row[col]) for col, dim in spec.dimension_columns.items()}
    if not all(dims.values()):
        msg = f"a row of {code} without {', '.join(spec.dimension_columns)}"
        raise RowError(msg)
    value, null_reason = parse_value(row[spec.value_column], spec.missing_markers, spec.csv.decimal)
    return observation(
        metric_id=spec.metric_id,
        territory_level=TerritoryLevel.DISTRITO.value,
        territory_code=code,
        territory_name=found.group("district") if found else None,
        admin_unit_id=admin_unit_id(TerritoryLevel.DISTRITO.value, code),
        period_start=start,
        period_end=end,
        dims=dims,
        dims_key=dims_key(dims),
        value=value,
        null_reason=null_reason,
        unit=row[spec.unit_column] if spec.unit_column else None,
        raw_value=row[spec.value_column],
    )


@dataclass(frozen=True)
class DistrictObservations(Observations):
    unassigned_with_figure: int = 0  # rows of no district with a figure (not «-»)


def normalize_district_concept(
    frame: pd.DataFrame, spec: CmDistrictConceptPipeline, names: Mapping[str, str]
) -> DistrictObservations:
    """Rows before `period_min` are counted as out_of_window; rows of no district as
    out_of_scope; a row that cannot be read is quarantined."""
    records: list[dict[str, str]] = frame.to_dict("records")  # pyright: ignore[reportAssignmentType]
    recent = [
        (i, r)
        for i, r in enumerate(records)
        if spec.period_min is None
        or not r[spec.period_column].isdigit()
        or int(r[spec.period_column]) >= spec.period_min
    ]
    rows: list[dict[str, Any]] = []
    bad: list[dict[str, Any]] = []
    unassigned = with_figure = 0
    for index, row in recent:
        try:
            kept = _row(row, spec, names)
        except (RowError, KeyError) as exc:
            bad.append({"source_row": index, "reason": str(exc), "raw": str(row)[:300]})
            continue
        if kept is None:
            unassigned += 1
            # Rows of no district carry «-» today; one with a figure is reported, never read
            with_figure += row[spec.value_column] not in spec.missing_markers
        else:
            rows.append(kept)
    return DistrictObservations(
        pd.DataFrame(rows, columns=OBS_COLUMNS),
        pd.DataFrame(bad, columns=["source_row", "reason", "raw"]),
        len(recent) - unassigned,
        out_of_window=len(records) - len(recent),
        out_of_scope=unassigned,
        unassigned_with_figure=with_figure,
    )


def latest_year_complete(obs: Observations, expected: int) -> CheckResult:
    """Blocking: the latest year read publishes every district (a renamed one would vanish)."""
    frame = obs.frame
    latest = frame["period_start"].max() if not frame.empty else None
    codes = set(frame.loc[frame["period_start"] == latest, "territory_code"])
    return CheckResult(
        "latest_year_every_district",
        True,
        len(codes) == expected,
        {"period": str(latest), "districts": len(codes), "expected": expected},
    )


def district_concept_steps(
    engine: Engine, catalog: Catalog, spec: CmDistrictConceptPipeline
) -> PipelineSteps[DistrictObservations]:
    metrics = {m: catalog.metrics[m] for m in spec.metric_ids()}

    def quality(obs: DistrictObservations) -> dict[str, Any]:
        known = set(district_names(engine, spec.municipio_ine).values())
        base = run_quality(obs, metrics, set())
        return QualityReport(
            [
                *base.checks,
                nothing_quarantined(obs.quarantine),
                *district_checks(obs.frame, known, spec.expected_districts),
                latest_year_complete(obs, spec.expected_districts),
            ]
        ).to_dict()

    def publish(
        session: Session, obs: DistrictObservations, version_id: uuid.UUID
    ) -> dict[str, int]:
        return {
            "observations": replace_observations(session, obs.frame, [spec.metric_id], version_id)
        }

    return PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=spec.csv,
        resource_role=spec.resource_role,
        normalize=lambda frame: normalize_district_concept(
            frame, spec, district_names(engine, spec.municipio_ine)
        ),
        quarantine=lambda obs: obs.quarantine,
        quality=quality,
        counts=lambda obs: (
            row_counts(obs.frame)
            | {"out_of_window": obs.out_of_window, "unassigned": obs.out_of_scope or 0}
            | {"unassigned_with_figure": obs.unassigned_with_figure}
        ),
        write_silver=write_silver,
        publish=publish,
    )


def run_district_concept_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: CmDistrictConceptPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
) -> RunSummary:
    return run_pipeline(
        engine,
        catalog,
        spec.dataset_id,
        district_concept_steps(engine, catalog, spec),
        source,
        evidence_root=evidence_root,
        data_dir=data_dir,
    )
