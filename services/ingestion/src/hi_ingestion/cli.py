"""`hi-ingest` command line."""

import typer

from hi_ingestion import __version__

app = typer.Typer(help="Housing Intelligence ingestion CLI", no_args_is_help=True)
catalog_app = typer.Typer(help="Source catalog commands", no_args_is_help=True)
app.add_typer(catalog_app, name="catalog")


@app.command()
def version() -> None:
    """Print the ingestion package version."""
    typer.echo(__version__)


if __name__ == "__main__":
    app()
