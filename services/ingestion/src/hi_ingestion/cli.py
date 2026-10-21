"""`hi-ingest` command line."""

import json
from datetime import date
from pathlib import Path
from typing import Annotated

import typer

from hi_contracts.catalog.enums import Priority
from hi_db.session import make_engine
from hi_domain.catalog.scoring import score_candidate
from hi_ingestion import __version__
from hi_ingestion.catalog.loader import DEFAULT_CATALOG_DIR, load_catalog
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

EVIDENCE_GATE_01 = DEFAULT_CATALOG_DIR.parents[1] / "evidence" / "gate-01"

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


@app.command("run")
def run_dataset(
    dataset_id: str,
    local_dir: Annotated[
        Path | None, typer.Option(help="Offline inputs (sections + names.csv + barrios.csv)")
    ] = None,
    evidence: Annotated[bool, typer.Option(help="Write evidence/gate-01 artifacts")] = True,
    database_url: DatabaseUrl = None,
) -> None:
    """Run a dataset pipeline (Bronze -> Silver -> PostGIS)."""
    if dataset_id != admin_config.SECTIONS_DATASET:
        typer.echo(f"No pipeline registered for {dataset_id}", err=True)
        raise typer.Exit(2)
    catalog = load_catalog()
    inputs = local_inputs(local_dir) if local_dir else fetch_inputs(catalog)
    summary = run_admin_boundaries(
        make_engine(database_url),
        catalog,
        inputs,
        evidence_root=EVIDENCE_GATE_01 if evidence else None,
    )
    typer.echo(json.dumps({
        "status": summary.status,
        "version": summary.version_label,
        "counts": summary.counts,
        "quality_passed": summary.quality.get("passed"),
        "evidence": str(summary.evidence_dir) if summary.evidence_dir else None,
    }, indent=2))  # fmt: skip
    if summary.status == "FAILED":
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
