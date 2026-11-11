"""Official spellings for municipios and Madrid districts (DATA-022).

The section CSV of `cm_secciones_censales` writes '/' or the byte 0xD0 where the Ñ goes
('REDUE/A', 'GRIÐON') and drops accents ('VICALVARO'). Encoding cannot repair it, so the names
come from the latest valid version of statistical tables that publish them in full ('Griñón',
'Álamo (El)', 'Vicálvaro'). Geometry and codes stay untouched: only `geo_admin_unit.name`
changes, the run is recorded in `ingestion_run` with the versions used, and a critical check
blocks the update if any published name still carries a character outside Spanish spelling
(barrios included on purpose: nothing broken is published, even what this step does not fix).
Runs after the statistical tables (they resolve to the geography first). Re-running the
geography alone brings the CSV names back: run this step again after the tables.
"""

import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, select, text, update
from sqlalchemy.orm import Session

from hi_contracts.catalog.enums import AdminLevel, PipelineStage, RunStatus
from hi_db.models import DatasetVersion, GeoAdminUnit
from hi_domain.geo.names import invalid_name_chars
from hi_ingestion.pipelines.admin_boundaries import config
from hi_ingestion.pipelines.common import RunSummary, evidence_dir, write_json
from hi_ingestion.pipelines.tracking import StageTracker

STEP = "official_names"
NAMED_LEVELS = (AdminLevel.MUNICIPIO, AdminLevel.DISTRITO, AdminLevel.BARRIO)

_SOURCE_NAMES_SQL = text(
    """
    SELECT DISTINCT m.admin_unit_id, m.territory_name
    FROM metric_observation m
    JOIN dataset_version v ON v.id = m.dataset_version_id
    WHERE v.dataset_id = :dataset_id AND v.is_last_valid
      AND m.territory_level = :level
      AND m.admin_unit_id IS NOT NULL AND m.territory_name IS NOT NULL
    """
)


@dataclass(frozen=True)
class Unit:
    admin_unit_id: str
    level: str
    code_official: str
    name: str | None
    parent_admin_unit_id: str | None


@dataclass
class NamePlan:
    names: dict[str, str] = field(default_factory=dict[str, str])  # final name of every unit
    missing: list[str] = field(default_factory=list[str])  # no official name in the source
    conflicts: dict[str, list[str]] = field(default_factory=dict[str, list[str]])
    invalid: dict[str, list[str]] = field(default_factory=dict[str, list[str]])

    def changes(self, units: list[Unit]) -> list[dict[str, Any]]:
        return [
            {
                "admin_unit_id": u.admin_unit_id,
                "before": u.name,
                "after": self.names[u.admin_unit_id],
            }
            for u in units
            if u.admin_unit_id in self.names and self.names[u.admin_unit_id] != u.name
        ]

    def checks(self) -> list[dict[str, Any]]:
        def check(name: str, offenders: list[str] | dict[str, list[str]]) -> dict[str, Any]:
            sample = (
                dict(list(offenders.items())[:20])
                if isinstance(offenders, dict)
                else offenders[:20]
            )
            return {
                "name": name,
                "critical": True,
                "passed": not offenders,
                "details": {"count": len(offenders), "sample": sample},
            }

        return [
            check("every_municipio_and_madrid_district_has_official_name", self.missing),
            check("one_official_name_per_unit", self.conflicts),
            check("names_use_spanish_spelling_only", self.invalid),
        ]

    @property
    def passed(self) -> bool:
        return all(c["passed"] for c in self.checks())


def _single(names: dict[str, list[str]], unit_id: str, plan: NamePlan) -> str | None:
    found = sorted(set(names.get(unit_id, [])))
    if len(found) > 1:
        plan.conflicts[unit_id] = found
    if not found:
        plan.missing.append(unit_id)
    return found[0] if found else None


def plan_names(
    units: list[Unit],
    municipio_names: dict[str, list[str]],
    madrid_district_names: dict[str, list[str]],
) -> NamePlan:
    """Final name of every unit: official spelling where a source covers it, else unchanged."""
    plan = NamePlan()
    for unit in units:
        if unit.level == AdminLevel.MUNICIPIO:
            _keep(plan, unit, _single(municipio_names, unit.admin_unit_id, plan))
    for unit in units:
        if unit.level == AdminLevel.DISTRITO:
            _keep(plan, unit, _district_name(unit, plan, madrid_district_names))
        elif unit.level != AdminLevel.MUNICIPIO:
            _keep(plan, unit, None)
    for unit_id, name in plan.names.items():
        if bad := invalid_name_chars(name):
            plan.invalid[unit_id] = bad
    return plan


def _keep(plan: NamePlan, unit: Unit, official: str | None) -> None:
    """Official name if found, else the current one; a unit with neither stays out."""
    if name := official or unit.name:
        plan.names[unit.admin_unit_id] = name


def _district_name(
    unit: Unit, plan: NamePlan, madrid_district_names: dict[str, list[str]]
) -> str | None:
    if unit.code_official.startswith(config.MADRID_MUNICIPIO):
        return _single(madrid_district_names, unit.admin_unit_id, plan)
    municipio = plan.names.get(unit.parent_admin_unit_id or "")
    if not municipio:
        return None
    return config.CENSAL_DISTRICT_NAME.format(municipio=municipio, number=unit.code_official[5:])


def _load_units(session: Session) -> list[Unit]:
    rows = session.execute(
        select(
            GeoAdminUnit.admin_unit_id,
            GeoAdminUnit.level,
            GeoAdminUnit.code_official,
            GeoAdminUnit.name,
            GeoAdminUnit.parent_admin_unit_id,
        ).where(GeoAdminUnit.level.in_([level.value for level in NAMED_LEVELS]))
    )
    return [Unit(*row) for row in rows]


def _source_names(session: Session, dataset_id: str, level: AdminLevel) -> dict[str, list[str]]:
    names: dict[str, list[str]] = defaultdict(list)
    params = {"dataset_id": dataset_id, "level": level.value}
    for unit_id, name in session.execute(_SOURCE_NAMES_SQL, params):
        names[unit_id].append(" ".join(str(name).split()))
    return names


def _version_label(session: Session, dataset_id: str) -> str | None:
    return session.scalar(
        select(DatasetVersion.version_label).where(
            DatasetVersion.dataset_id == dataset_id, DatasetVersion.is_last_valid
        )
    )


def _geography_version(session: Session) -> uuid.UUID | None:
    return session.scalar(
        select(DatasetVersion.id).where(
            DatasetVersion.dataset_id == config.SECTIONS_DATASET, DatasetVersion.is_last_valid
        )
    )


def apply_official_names(engine: Engine, *, evidence_root: Path | None) -> RunSummary:
    tracker = StageTracker(engine, config.SECTIONS_DATASET)
    sources = {
        AdminLevel.MUNICIPIO: config.MUNICIPIO_NAMES_DATASET,
        AdminLevel.DISTRITO: config.MADRID_DISTRICT_NAMES_DATASET,
    }
    with Session(engine) as session:
        tracker.version_id = _geography_version(session)
        names_from = {s: _version_label(session, s) for s in sources.values()}
    summary = RunSummary("RUNNING", config.SECTIONS_DATASET, "", tracker.correlation_id)
    summary.version_label = f"{STEP}:" + ",".join(f"{k}@{v}" for k, v in names_from.items())

    with tracker.stage(PipelineStage.NORMALIZE) as metrics, Session(engine) as session:
        units = _load_units(session)
        plan = plan_names(
            units,
            _source_names(session, sources[AdminLevel.MUNICIPIO], AdminLevel.MUNICIPIO),
            _source_names(session, sources[AdminLevel.DISTRITO], AdminLevel.DISTRITO),
        )
        changes = plan.changes(units)
        metrics |= {"step": STEP, "names_from": names_from, "changes": len(changes)}
    with tracker.stage(PipelineStage.QUALITY_CHECK) as metrics:
        report = {"passed": plan.passed, "checks": plan.checks(), "names_from": names_from}
        metrics |= {"step": STEP, "passed": plan.passed}
    summary.quality, summary.counts = report, {"units": len(units), "changes": len(changes)}
    out = evidence_dir(evidence_root, STEP)
    if out:
        write_json(out / "quality_report.json", report)
        write_json(out / "changes.json", changes)
        summary.evidence_dir = out
    if not plan.passed:
        tracker.record(
            PipelineStage.PUBLISH_SILVER,
            RunStatus.SKIPPED,
            {"step": STEP, "reason": "quality failed"},
        )
        summary.status = "FAILED"
        return summary

    with (
        tracker.stage(PipelineStage.PUBLISH_SILVER) as metrics,
        Session(engine) as session,
        session.begin(),
    ):
        for change in changes:
            session.execute(
                update(GeoAdminUnit)
                .where(GeoAdminUnit.admin_unit_id == change["admin_unit_id"])
                .values(name=change["after"])
            )
        metrics |= {"step": STEP, "names_from": names_from, "updated": len(changes)}
    summary.status = "SUCCESS"
    return summary
