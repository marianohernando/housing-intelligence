"""Point facility pipelines (points_csv) on the generic runner."""

import json
from pathlib import Path
from typing import Any

from shapely import STRtree, from_wkb
from shapely.geometry import Point
from sqlalchemy import Engine, text

from hi_contracts.catalog.pipeline import FacilityDirectoryPipeline, PointsPipeline
from hi_ingestion.bronze import REPO_ROOT
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.directory.normalize import DIRECTORY_FILE
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.places.coordinates import Located, fold_name
from hi_ingestion.pipelines.places.directory import LoadedDirectory, read_entries
from hi_ingestion.pipelines.places.geocoder import CachedGeocoder
from hi_ingestion.pipelines.places.normalize import (
    MADRID_MUNICIPIO,
    Places,
    Repair,
    normalize_places,
)
from hi_ingestion.pipelines.places.publish import replace_places
from hi_ingestion.pipelines.places.quality import run_quality
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline

# 1.1: coordinate repair (D-216); 1.2: the street must match; 1.3: directories (D-218);
# 1.3.1: stricter directory rules (equal street words, public/private veto); 1.4: primary care
PARSER_VERSION = "places-1.4.0"
GEOCODER_CACHE = Path("bronze") / "geocoding" / "cartociudad.json"
_UNITS = text(
    """
    SELECT level, code_official, name, ST_AsBinary(geom_4326) AS wkb
      FROM geo_admin_unit
     WHERE level = 'municipio' OR (level = 'distrito' AND code_official LIKE :madrid)
    """
)


class GeographyLocator:
    """Municipio and Madrid district of a lon/lat point, from the canonical geography."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.levels: dict[str, tuple[STRtree, list[str]]] = {}
        for level in ("municipio", "distrito"):
            chosen = [r for r in rows if r["level"] == level]
            geoms = [from_wkb(bytes(r["wkb"])) for r in chosen]
            self.levels[level] = (STRtree(geoms), [str(r["code_official"]) for r in chosen])

    def _code(self, level: str, lon: float, lat: float) -> str | None:
        tree, codes = self.levels[level]
        hits = tree.query(Point(lon, lat), predicate="within")
        return codes[int(hits[0])] if len(hits) else None

    def __call__(self, lon: float, lat: float) -> Located:
        return Located(self._code("municipio", lon, lat), self._code("distrito", lon, lat))


def _counts(places: Places) -> dict[str, Any]:
    by_sub = (
        places.frame["subcategory"].value_counts().head(10).to_dict() if len(places.frame) else {}
    )
    return {
        "places_normalized": len(places.frame),
        "quarantined": len(places.quarantine),
        "top_subcategories": by_sub,
    }


def write_places_silver(places: Places, directory: Path) -> Path:
    path = directory / "places.csv.gz"
    places.frame.to_csv(path, index=False)
    return path


def build_repair(engine: Engine, spec: PointsPipeline, data_dir: Path) -> Repair | None:
    """Coordinate repair for registers that declare an address (D-216); None otherwise."""
    if not spec.address_template:
        return None
    with engine.connect() as conn:
        rows = [
            dict(r) for r in conn.execute(_UNITS, {"madrid": f"{MADRID_MUNICIPIO}%"}).mappings()
        ]
    names = {
        fold_name(str(r["name"])): str(r["code_official"])
        for r in rows
        if r["level"] == "municipio"
    }
    return Repair(GeographyLocator(rows), CachedGeocoder(data_dir / GEOCODER_CACHE), names)


_DIRECTORY_VERSION = text(
    """
    SELECT bronze_manifest_path, version_label
      FROM dataset_version
     WHERE dataset_id = :dataset_id AND is_last_valid
    """
)


def directory_input(manifest: dict[str, Any]) -> FetchedFile:
    """The directory's Bronze file as an input of the register's run. The role carries the
    directory's parser, so a new parser on the same file also reprocesses the register."""
    bronze = dict(manifest["inputs"][0])
    path = Path(str(bronze.pop("path")))
    return FetchedFile(
        **bronze
        | {
            "role": f"directory@{manifest['parser_version']}",
            "path": path if path.is_absolute() else REPO_ROOT / path,
        }
    )


def load_directories(
    engine: Engine, catalog: Catalog, spec: PointsPipeline
) -> tuple[list[LoadedDirectory], list[FetchedFile]]:
    """The last valid Silver of each directory the register declares, and its Bronze input.

    A directory that was never ingested is left out: its places keep the register's name and
    the quality report says which directory is missing.
    """
    loaded: list[LoadedDirectory] = []
    inputs: list[FetchedFile] = []
    for link in spec.directories:
        directory_spec = catalog.pipelines.get(link.dataset_id)
        if not isinstance(directory_spec, FacilityDirectoryPipeline):
            msg = f"{spec.dataset_id}: {link.dataset_id} is not a facility_directory pipeline"
            raise TypeError(msg)
        with engine.connect() as conn:
            row = conn.execute(_DIRECTORY_VERSION, {"dataset_id": link.dataset_id}).first()
        if row is None:
            continue
        manifest_path = Path(str(row.bronze_manifest_path))
        if not manifest_path.is_absolute():
            manifest_path = REPO_ROOT / manifest_path
        manifest = json.loads(manifest_path.read_text())
        inputs.append(directory_input(manifest))
        loaded.append(
            LoadedDirectory(
                dataset_id=link.dataset_id,
                source_id=catalog.datasets[link.dataset_id].source_id,
                version_label=str(row.version_label),
                capacity_unit=directory_spec.capacity_unit,
                kinds=link.kinds,
                name_prefix=link.name_prefix,
                entries=read_entries(manifest_path.parent / DIRECTORY_FILE),
            )
        )
    return loaded, inputs


def run_places_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: PointsPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
) -> RunSummary:
    source_id = catalog.datasets[spec.dataset_id].source_id
    repair = build_repair(engine, spec, data_dir)
    directories, directory_inputs = load_directories(engine, catalog, spec)
    steps: PipelineSteps[Places] = PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=spec.csv,
        resource_role=spec.resource_role,
        normalize=lambda frame: normalize_places(frame, spec, repair, directories),
        quarantine=lambda places: places.quarantine,
        quality=lambda places: run_quality(places, spec).to_dict(),
        counts=_counts,
        write_silver=write_places_silver,
        publish=lambda session, places, version_id: replace_places(
            session, places, spec.dataset_id, source_id, version_id
        ),
    )
    return run_pipeline(
        engine,
        catalog,
        spec.dataset_id,
        steps,
        source,
        evidence_root=evidence_root,
        data_dir=data_dir,
        extra_inputs=directory_inputs,
    )
