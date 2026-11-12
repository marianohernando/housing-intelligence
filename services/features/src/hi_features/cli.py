"""`hi-features` command line."""

from typing import Annotated

import typer

from hi_db.session import make_engine
from hi_features.compute import METHODS, compute, persist
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.catalog.sync import sync_catalog

app = typer.Typer(help="Feature Store (Gold)", no_args_is_help=True)
DatabaseUrl = Annotated[str | None, typer.Option(envvar="DATABASE_URL", help="SQLAlchemy URL")]


@app.command("compute")
def compute_features(
    feature: Annotated[
        list[str] | None, typer.Option(help="feature_id (repeatable); default all")
    ] = None,
    database_url: DatabaseUrl = None,
) -> None:
    """Compute and persist features declared in data/catalog/features."""
    catalog = load_catalog()
    engine = make_engine(database_url)
    sync_catalog(engine, catalog)
    selected = feature or sorted(catalog.features)
    for feature_id in selected:
        spec = catalog.features[feature_id]
        if spec.formula.method not in METHODS:
            typer.echo(
                f"{feature_id}: method {spec.formula.method} computed by its pipeline, skipped"
            )
            continue
        result = compute(engine, spec)
        n = persist(engine, spec, result)
        values: list[float | None] = result["value"].tolist()
        known = sum(1 for v in values if v is not None and v == v)  # NaN != NaN
        typer.echo(f"{feature_id}: {n} rows, {known} with value, {n - known} explicit unknown")


@app.command("commute")
def commute(database_url: DatabaseUrl = None) -> None:
    """Public transport minutes from every zone to every station and zone centre (CORE-009)."""
    from hi_features.commute import compute_commutes, persist

    matrix = compute_commutes(make_engine(database_url), load_catalog())
    n = persist(make_engine(database_url), matrix)
    known = sum(1 for m in matrix.times["minutes"].tolist() if m == m)  # NaN != NaN
    typer.echo(f"commute: {len(matrix.hubs)} hubs, {n} rows, {known} with minutes")


@app.command("version")
def version() -> None:
    typer.echo("0.0.1")
