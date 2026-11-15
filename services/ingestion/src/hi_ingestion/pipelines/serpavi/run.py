"""SERPAVI rent reference workbook (serpavi_rent, D-242) on the generic runner."""

from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from hi_contracts.catalog.pipeline import CsvFormat, SerpaviRentPipeline
from hi_db.models import GeoAdminUnit
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline
from hi_ingestion.pipelines.serpavi.normalize import normalize, parse_workbook
from hi_ingestion.pipelines.stat_tables.normalize import Observations
from hi_ingestion.pipelines.stat_tables.publish import replace_observations
from hi_ingestion.pipelines.stat_tables.quality import (
    CheckResult,
    QualityReport,
    district_checks,
    expected_municipios_check,
    row_counts,
    run_quality,
)
from hi_ingestion.pipelines.stat_tables.run import write_silver

PARSER_VERSION = "serpavi_rent-1.0.0"
MIN_SECTIONS_RESOLVED = 0.99  # sections of another census edition keep their code, unlinked
QUARTILES = ("p25", "mediana", "p75")  # names of `statistics` that must come in this order


def known_units(engine: Engine) -> dict[str, dict[str, str]]:
    """Code -> admin_unit_id of every unit of the geography, by level."""
    by_level: dict[str, dict[str, str]] = {}
    with Session(engine) as session:
        rows = session.execute(
            select(GeoAdminUnit.level, GeoAdminUnit.code_official, GeoAdminUnit.admin_unit_id)
        )
        for level, code, unit_id in rows:
            by_level.setdefault(str(level), {})[str(code)] = str(unit_id)
    return by_level


def _codes(frame: pd.DataFrame, level: str) -> set[str]:
    return set(frame.loc[frame["territory_level"] == level, "territory_code"])


def quartiles_ordered_check(frame: pd.DataFrame, spec: SerpaviRentPipeline) -> CheckResult:
    """Blocking: p25 <= median <= p75 wherever the three are published (a shifted column
    would break it)."""
    rent = frame.loc[(frame["metric_id"] == spec.rent_metric_id) & frame["value"].notna()]
    cells: dict[tuple[Any, ...], dict[str, float]] = {}
    for record in rent.to_dict("records"):
        dims: dict[str, str] = record["dims"]
        key = (
            record["territory_level"],
            record["territory_code"],
            str(record["period_start"]),
            dims[spec.typology_dim],
        )
        cells.setdefault(key, {})[dims[spec.statistic_dim]] = float(record["value"])
    low, mid, high = QUARTILES
    checked, broken = 0, []
    for key, values in cells.items():
        if not set(QUARTILES) <= set(values):
            continue
        checked += 1
        if not values[low] <= values[mid] <= values[high]:
            broken.append([*key[:2], key[3]])
    return CheckResult(
        "quartiles_ordered",
        True,
        not broken,
        {"checked": checked, "broken": len(broken), "sample": broken[:5]},
    )


def sections_check(frame: pd.DataFrame, spec: SerpaviRentPipeline) -> list[CheckResult]:
    """Blocking: at least `min_sections`; non-blocking: the share linked to the geography."""
    if "seccion_censal" not in spec.sheets:
        return []
    sections = frame.loc[frame["territory_level"] == "seccion_censal"]
    codes = set(sections["territory_code"])
    linked = set(sections.loc[sections["admin_unit_id"].notna(), "territory_code"])
    share = len(linked) / len(codes) if codes else 0.0
    checks = [
        CheckResult(
            "sections_resolve_to_geography",
            False,
            share >= MIN_SECTIONS_RESOLVED,
            {"sections": len(codes), "linked": len(linked), "unlinked": sorted(codes - linked)},
        )
    ]
    if spec.min_sections is not None:
        checks.append(
            CheckResult(
                "section_coverage",
                True,
                len(codes) >= spec.min_sections,
                {"covered": len(codes), "min": spec.min_sections},
            )
        )
    return checks


def quality(
    obs: Observations,
    spec: SerpaviRentPipeline,
    units: dict[str, dict[str, str]],
    catalog: Catalog,
) -> QualityReport:
    metrics = {m: catalog.metrics[m] for m in spec.metric_ids()}
    report = run_quality(obs, metrics, set(units.get("municipio", {})))
    checks = [
        *report.checks,
        expected_municipios_check(obs.frame, spec.expected_municipios),
        quartiles_ordered_check(obs.frame, spec),
        *sections_check(obs.frame, spec),
    ]
    if spec.expected_districts is not None:
        known = set(units.get("distrito", {}))
        checks += district_checks(obs.frame, known, spec.expected_districts)
    return QualityReport(checks)


def serpavi_counts(obs: Observations) -> dict[str, Any]:
    return row_counts(obs.frame) | {
        "out_of_province": obs.out_of_window,
        "territories": {
            level: len(_codes(obs.frame, level))
            for level in sorted(set(obs.frame["territory_level"]))
        },
    }


def serpavi_steps(
    engine: Engine, catalog: Catalog, spec: SerpaviRentPipeline
) -> PipelineSteps[Observations]:
    units = known_units(engine)
    unit_ids = {unit_id for by_code in units.values() for unit_id in by_code.values()}
    return PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=CsvFormat(),  # unused: the workbook is read by `parse`
        resource_role=spec.resource_role,
        parse=lambda path: parse_workbook(path, spec),
        normalize=lambda frame: normalize(frame, spec, unit_ids),
        quarantine=lambda obs: obs.quarantine,
        quality=lambda obs: quality(obs, spec, units, catalog).to_dict(),
        counts=serpavi_counts,
        write_silver=write_silver,
        publish=lambda session, obs, version_id: {
            "observations": replace_observations(session, obs.frame, spec.metric_ids(), version_id)
        },
    )


def run_serpavi_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: SerpaviRentPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
) -> RunSummary:
    return run_pipeline(
        engine,
        catalog,
        spec.dataset_id,
        serpavi_steps(engine, catalog, spec),
        source,
        evidence_root=evidence_root,
        data_dir=data_dir,
    )
