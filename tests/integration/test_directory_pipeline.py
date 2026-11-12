"""Official directories (D-218): Silver only, then the register matches its places to them."""

import json
from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy import Engine, text

from hi_contracts.catalog.pipeline import FacilityDirectoryPipeline, PointsPipeline
from hi_ingestion.bronze import REPO_ROOT
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.common import RunSummary
from hi_ingestion.pipelines.directory.run import PARSER_VERSION as DIRECTORY_PARSER
from hi_ingestion.pipelines.directory.run import run_directory_pipeline
from hi_ingestion.pipelines.fetch import local_file
from hi_ingestion.pipelines.places.run import run_places_pipeline
from tests.integration.conftest import GOLDEN, ingest_directories

pytestmark = pytest.mark.db
REGISTER = "cm_centros_sanitarios"
HOSPITALS = "ms_catalogo_nacional_hospitales"
PRIMARY_CARE = "ms_catalogo_centros_atencion_primaria"
PRIMARY_CARE_SQL = text(
    "SELECT canonical_name FROM place_master WHERE official_dataset_id = :ds "
    "AND official_entity_id = :id"
)
NAMES_SQL = text(
    """
    SELECT official_entity_id AS id, canonical_name AS name,
           attributes->'directory'->>'match_method' AS method
      FROM place_master
     WHERE official_dataset_id = :ds AND subcategory LIKE 'Hospital%'
    """
)
ALIASES_SQL = text(
    "SELECT a.external_id, p.official_entity_id AS place, a.match_method "
    "FROM place_source_alias a JOIN place_master p USING (canonical_place_id) "
    "WHERE a.dataset_id = :ds"
)
BEDS_SQL = text(
    "SELECT attributes->'directory'->>'capacity' FROM place_master "
    "WHERE official_dataset_id = :ds AND official_entity_id = :id"
)
MANIFEST_SQL = text(
    "SELECT bronze_manifest_path FROM dataset_version WHERE dataset_id = :ds AND is_last_valid"
)


def _register(engine: Engine, tmp_path: Path) -> RunSummary:
    catalog = load_catalog()
    spec = catalog.pipelines[REGISTER]
    assert isinstance(spec, PointsPipeline)
    source = local_file(REGISTER, "primary", GOLDEN / "places_sample" / f"{REGISTER}.csv")
    return run_places_pipeline(
        engine, catalog, spec, source, evidence_root=tmp_path, data_dir=tmp_path
    )


def test_hospitals_take_the_directory_name_and_keep_the_register_as_source(
    published: RunSummary, migrated_engine: Engine, tmp_path: Path
) -> None:
    assert published.status == "SUCCESS"
    ingest_directories(migrated_engine, tmp_path)
    result = _register(migrated_engine, tmp_path)
    assert result.status in {"SUCCESS", "SKIPPED"}, result.quality
    with migrated_engine.connect() as conn:
        names = {r.id: (r.name, r.method) for r in conn.execute(NAMES_SQL, {"ds": REGISTER})}
        aliases = {
            r.place: (r.external_id, r.match_method)
            for r in conn.execute(ALIASES_SQL, {"ds": HOSPITALS})
        }
        manifest_path = conn.execute(MANIFEST_SQL, {"ds": REGISTER}).scalar_one()
    assert names["CH0001"] == ("Fremap Hospital Majadahonda", "direccion")
    assert names["CH0006"] == ("Hospital Fuensanta", "direccion")
    assert names["CH0008"] == ("Clínica La Luz", "direccion")
    assert aliases == {"CH0001": ("280856", "direccion"), "CH0006": ("280549", "direccion"),
                       "CH0008": ("280534", "direccion")}  # fmt: skip
    path = Path(manifest_path)
    manifest = json.loads((path if path.is_absolute() else REPO_ROOT / path).read_text())
    roles = sorted((i["dataset_id"], i["role"]) for i in manifest["inputs"])
    assert roles == [
        (REGISTER, "primary"),
        (PRIMARY_CARE, f"directory@{DIRECTORY_PARSER}"),
        (HOSPITALS, f"directory@{DIRECTORY_PARSER}"),
    ]


def test_primary_care_takes_its_name_from_the_ministry_catalogue(
    published: RunSummary, migrated_engine: Engine, tmp_path: Path
) -> None:
    """The register publishes no names for centros de salud: «Centro de salud Las Calesas»."""
    assert published.status == "SUCCESS"
    ingest_directories(migrated_engine, tmp_path)
    assert _register(migrated_engine, tmp_path).status in {"SUCCESS", "SKIPPED"}
    with migrated_engine.connect() as conn:

        def name(place_id: str) -> str:
            return conn.execute(PRIMARY_CARE_SQL, {"ds": REGISTER, "id": place_id}).scalar_one()

        assert name("CS0037") == "Centro de salud Las Calesas"
        assert name("CS0174") == "Centro de salud Juan de la Cierva"
        assert name("CS12674") == "Consultorio local La Acebeda"


def test_a_new_directory_version_reprocesses_the_register(
    published: RunSummary, migrated_engine: Engine, tmp_path: Path
) -> None:
    """The directory is an input of the register's run: same register file, new directory ->
    new checksum, so the names never go stale behind a «same checksum» skip."""
    assert published.status == "SUCCESS"
    ingest_directories(migrated_engine, tmp_path)
    first = _register(migrated_engine, tmp_path)
    again = _register(migrated_engine, tmp_path)
    assert again.status == "SKIPPED"
    assert again.checksum == first.checksum
    catalog = load_catalog()
    directory = catalog.pipelines[HOSPITALS]
    assert isinstance(directory, FacilityDirectoryPipeline)
    sheet = pd.read_excel(GOLDEN / "directory_sample" / f"{HOSPITALS}.xlsx", dtype=str)
    sheet.loc[sheet["CODCNH"] == "280549", "CAMAS"] = "21"  # the next edition: one more bed
    copy = tmp_path / f"{HOSPITALS}_next.xlsx"
    with pd.ExcelWriter(copy, engine="openpyxl") as writer:
        sheet.to_excel(writer, sheet_name=directory.sheet, index=False)
    try:
        changed = run_directory_pipeline(
            migrated_engine, catalog, directory, local_file(HOSPITALS, "primary", copy),
            evidence_root=None, data_dir=tmp_path,
        )  # fmt: skip
        assert changed.status == "SUCCESS", changed.quality
        after = _register(migrated_engine, tmp_path)
        assert after.status == "SUCCESS"
        assert after.checksum != first.checksum
        with migrated_engine.connect() as conn:
            beds = conn.execute(BEDS_SQL, {"ds": REGISTER, "id": "CH0006"}).scalar_one()
        assert beds == "21.0"
    finally:  # the other tests read the fixture edition
        ingest_directories(migrated_engine, tmp_path)
        _register(migrated_engine, tmp_path)
