"""`hi-ingest` command line."""

import json
from datetime import date
from pathlib import Path
from typing import Annotated

import typer
from sqlalchemy import Engine

from hi_contracts.catalog.enums import Priority
from hi_contracts.catalog.pipeline import (
    CmPostcodeConceptPipeline,
    CmStatTablePipeline,
    GtfsFeedPipeline,
    MadridPadronPipeline,
    OsmWalkNetworkPipeline,
    PointsPipeline,
)
from hi_db.session import make_engine
from hi_domain.catalog.scoring import score_candidate
from hi_ingestion import __version__
from hi_ingestion.catalog.loader import DEFAULT_CATALOG_DIR, Catalog, load_catalog
from hi_ingestion.catalog.sync import sync_catalog
from hi_ingestion.catalog_harvester.drafts import (
    DRAFTS_DIR,
    curate,
    promote,
    write_drafts,
    write_report,
)
from hi_ingestion.catalog_harvester.runner import HARVESTABLE, harvest_sources, read_candidates
from hi_ingestion.pipelines.admin_boundaries import config as admin_config
from hi_ingestion.pipelines.admin_boundaries.run import (
    fetch_inputs,
    local_inputs,
    run_admin_boundaries,
)
from hi_ingestion.pipelines.common import EVIDENCE_GATE_01, RunSummary
from hi_ingestion.pipelines.fetch import local_file
from hi_ingestion.pipelines.gtfs.run import run_gtfs_pipeline
from hi_ingestion.pipelines.osm_network.run import run_osm_network_pipeline
from hi_ingestion.pipelines.padron.run import run_padron_pipeline
from hi_ingestion.pipelines.places.run import run_places_pipeline
from hi_ingestion.pipelines.stat_tables.run import run_metric_pipeline

app = typer.Typer(help="Housing Intelligence ingestion CLI", no_args_is_help=True)
catalog_app = typer.Typer(help="Source catalog commands", no_args_is_help=True)
app.add_typer(catalog_app, name="catalog")

CatalogDir = Annotated[Path, typer.Option(help="Catalog directory")]
DatabaseUrl = Annotated[str | None, typer.Option(envvar="DATABASE_URL", help="SQLAlchemy URL")]


@app.command()
def version() -> None:
    """Print the ingestion package version."""
    typer.echo(__version__)


@catalog_app.command("validate")
def catalog_validate(catalog_dir: CatalogDir = DEFAULT_CATALOG_DIR) -> None:
    """Validate every catalog YAML and cross references."""
    catalog = load_catalog(catalog_dir)
    typer.echo(
        f"OK: {len(catalog.sources)} sources, {len(catalog.datasets)} datasets, "
        f"{len(catalog.drafts)} drafts, {len(catalog.features)} features, "
        f"{len(catalog.metrics)} metrics, {len(catalog.pipelines)} pipelines"
    )


@catalog_app.command("sync")
def catalog_sync(
    catalog_dir: CatalogDir = DEFAULT_CATALOG_DIR, database_url: DatabaseUrl = None
) -> None:
    """Upsert curated sources and datasets into the registry tables."""
    counts = sync_catalog(make_engine(database_url), load_catalog(catalog_dir))
    typer.echo("synced " + ", ".join(f"{v} {k}" for k, v in counts.items()))


@catalog_app.command("harvest")
def catalog_harvest(
    source: Annotated[list[str] | None, typer.Option(help="source_id (repeatable)")] = None,
    all_sources: Annotated[bool, typer.Option("--all", help="Every harvestable source")] = False,
) -> None:
    """List candidate datasets from open data catalogs into data/catalog/candidates/."""
    catalog = load_catalog()
    selected: list[str] = list(HARVESTABLE) if all_sources or not source else source
    for result in harvest_sources(catalog, selected):
        typer.echo(
            f"{result.source_id}: {result.status} pages={result.pages} "
            f"candidates={len(result.candidates)} {result.message or ''}"
        )


@catalog_app.command("draft")
def catalog_draft(
    top: Annotated[int, typer.Option(help="Number of drafts to write")] = 120,
    run_label: Annotated[str, typer.Option(help="Report label")] = date.today().isoformat(),
) -> None:
    """Score every candidate, regenerate datasets/_drafts and the scorecard report."""
    catalog = load_catalog(include_drafts=False)  # drafts are regenerated below
    scored = [score_candidate(c) for c in read_candidates()]
    drafts = write_drafts(scored, catalog, top)
    status_path = DEFAULT_CATALOG_DIR / "reports" / f"harvest_{run_label}.json"
    status = json.loads(status_path.read_text()) if status_path.exists() else []
    report = write_report(scored, status, run_label, catalog)
    typer.echo(f"scored {len(scored)} candidates, wrote {len(drafts)} drafts, report {report.name}")


@catalog_app.command("promote")
def catalog_promote(
    dataset_id: str,
    priority: Annotated[Priority, typer.Option(help="Curated priority")],
    reviewed_by: Annotated[str, typer.Option(help="Reviewer id")],
) -> None:
    """Move a draft into the curated catalog with an explicit review."""
    target = promote(DRAFTS_DIR / f"{dataset_id}.yaml", priority, reviewed_by)
    typer.echo(f"promoted -> {target}")


@catalog_app.command("curate")
def catalog_curate(curation_file: Path) -> None:
    """Apply a versioned curation file (candidates -> curated datasets)."""
    written = curate(curation_file, read_candidates())
    typer.echo(f"curated {len(written)} datasets")


def _print_summary(summary: RunSummary) -> None:
    payload = {
        "dataset_id": summary.dataset_id,
        "status": summary.status,
        "version": summary.version_label,
        "counts": summary.counts,
        "quality_passed": summary.quality.get("passed"),
        "evidence": str(summary.evidence_dir) if summary.evidence_dir else None,
    }
    typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))


def _run_one(
    dataset_id: str, catalog: Catalog, engine: Engine, local: Path | None, evidence: bool
) -> RunSummary:
    evidence_root = EVIDENCE_GATE_01 if evidence else None
    if dataset_id == admin_config.SECTIONS_DATASET:
        inputs = local_inputs(local) if local else fetch_inputs(catalog)
        return run_admin_boundaries(engine, catalog, inputs, evidence_root=evidence_root)
    spec = catalog.pipelines.get(dataset_id)
    if isinstance(spec, CmStatTablePipeline | CmPostcodeConceptPipeline):
        source = local_file(dataset_id, spec.resource_role, local) if local else None
        return run_metric_pipeline(engine, catalog, spec, source, evidence_root=evidence_root)
    if isinstance(spec, MadridPadronPipeline):
        source = local_file(dataset_id, spec.resource_role, local) if local else None
        return run_padron_pipeline(engine, catalog, spec, source, evidence_root=evidence_root)
    if isinstance(spec, PointsPipeline):
        source = local_file(dataset_id, spec.resource_role, local) if local else None
        return run_places_pipeline(engine, catalog, spec, source, evidence_root=evidence_root)
    if isinstance(spec, GtfsFeedPipeline):
        source = local_file(dataset_id, spec.resource_role, local) if local else None
        return run_gtfs_pipeline(engine, catalog, spec, source, evidence_root=evidence_root)
    if isinstance(spec, OsmWalkNetworkPipeline):
        source = local_file(dataset_id, spec.resource_role, local) if local else None
        return run_osm_network_pipeline(engine, catalog, spec, source, evidence_root=evidence_root)
    typer.echo(f"No pipeline registered for {dataset_id}", err=True)
    raise typer.Exit(2)


@app.command("run")
def run_dataset(
    dataset_id: str,
    local: Annotated[
        Path | None, typer.Option(help="Offline input: directory (geography) or file")
    ] = None,
    evidence: Annotated[bool, typer.Option(help="Write evidence/gate-01 artifacts")] = True,
    database_url: DatabaseUrl = None,
) -> None:
    """Run one dataset pipeline (Bronze -> Silver -> PostGIS)."""
    summary = _run_one(dataset_id, load_catalog(), make_engine(database_url), local, evidence)
    _print_summary(summary)
    if summary.status == "FAILED":
        raise typer.Exit(1)


@app.command("run-all")
def run_all(
    evidence: Annotated[bool, typer.Option(help="Write evidence/gate-01 artifacts")] = True,
    database_url: DatabaseUrl = None,
) -> None:
    """Geography first, then every declared pipeline. Exit 1 if any run fails quality."""
    catalog = load_catalog()
    engine = make_engine(database_url)
    order = [admin_config.SECTIONS_DATASET, *sorted(catalog.pipelines)]
    failed: list[str] = []
    for dataset_id in order:
        summary = _run_one(dataset_id, catalog, engine, None, evidence)
        typer.echo(f"{dataset_id}: {summary.status} {summary.version_label or ''}")
        if summary.status == "FAILED":
            failed.append(dataset_id)
    if failed:
        typer.echo(f"FAILED: {failed}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
