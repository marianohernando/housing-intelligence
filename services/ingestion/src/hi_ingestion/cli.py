"""`hi-ingest` command line."""

from pathlib import Path
from typing import Annotated

import typer

from hi_db.session import make_engine
from hi_ingestion import __version__
from hi_ingestion.catalog.loader import DEFAULT_CATALOG_DIR, load_catalog
from hi_ingestion.catalog.sync import sync_catalog

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
        f"{len(catalog.drafts)} drafts, {len(catalog.features)} features"
    )


@catalog_app.command("sync")
def catalog_sync(
    catalog_dir: CatalogDir = DEFAULT_CATALOG_DIR, database_url: DatabaseUrl = None
) -> None:
    """Upsert curated sources and datasets into the registry tables."""
    counts = sync_catalog(make_engine(database_url), load_catalog(catalog_dir))
    typer.echo(f"synced {counts['sources']} sources, {counts['datasets']} datasets")


if __name__ == "__main__":
    app()
