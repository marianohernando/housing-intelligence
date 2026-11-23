"""F14: the open data files of apps/web/public/datos/, with no network.

- They are what scripts/export_dcat_sdm.py renders from the versioned catalogue (its --check).
- catalogo.dcat.jsonld is JSON-LD with the classes and mandatory properties of DCAT-AP 3.0.1 and
  the EU vocabularies it asks for.
- Every Smart Data Models entity validates against its official schema, copied in
  data/schemas/sdm/ and resolved locally with a `referencing` registry.
"""

import hashlib
import importlib.util
import json
from collections.abc import Iterator
from functools import cache
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[3]
SDM_DIR = ROOT / "data" / "schemas" / "sdm"
DATOS = ROOT / "apps" / "web" / "public" / "datos"
EU = "http://publications.europa.eu/resource/authority"
NAMESPACES = {
    "dcat": "http://www.w3.org/ns/dcat#",
    "dct": "http://purl.org/dc/terms/",
    "dcatap": "http://data.europa.eu/r5r/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "vcard": "http://www.w3.org/2006/vcard/ns#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "eli": "http://data.europa.eu/eli/ontology#",
}
# DCAT-AP 3.0.1: the mandatory properties of each class it uses
MANDATORY = {
    "dcat:Catalog": ("dct:title", "dct:description", "dct:publisher"),
    "dcat:Dataset": ("dct:title", "dct:description"),
    "dcat:Distribution": ("dcat:accessURL",),
    "dcat:DataService": ("dct:title", "dcat:endpointURL"),
    "foaf:Agent": ("foaf:name",),
}
KNOWN_TYPES = {*MANDATORY, "dct:LicenseDocument", "dct:RightsStatement", "foaf:Document"}
KNOWN_TYPES |= {"vcard:Kind", "eli:LegalResource", "skos:Concept", "skos:ConceptScheme"}
# The ranges of DCAT-AP 3.0.1: a value of a controlled vocabulary says its class (ITB range check)
RANGES = {
    "dct:format": "dct:MediaTypeOrExtent",
    "dcat:theme": "skos:Concept",
    "dct:spatial": "dct:Location",
    "dct:accrualPeriodicity": "dct:Frequency",
    "dct:language": "dct:LinguisticSystem",
    "dct:conformsTo": "dct:Standard",
    "dcat:themeTaxonomy": "skos:ConceptScheme",
    "dct:accessRights": "dct:RightsStatement",
    "dcatap:applicableLegislation": "eli:LegalResource",
    "dcatap:hvdCategory": "skos:Concept",
}
KNOWN_TYPES |= set(RANGES.values())
HVD_LEGISLATION = "http://data.europa.eu/eli/reg_impl/2023/138/oj"
PRE_COMMIT_MAX_KB = 2000  # check-added-large-files in .pre-commit-config.yaml


@cache
def exporter() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "export_dcat_sdm", ROOT / "scripts" / "export_dcat_sdm.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@cache
def context() -> Any:
    module = exporter()
    return module.load_context(module.load_catalog(include_drafts=False))


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


@cache
def catalogue() -> dict[str, Any]:
    return read(DATOS / "catalogo.dcat.jsonld")


def nodes(value: Any) -> Iterator[dict[str, Any]]:
    """Every node with a type, also the ones nested in another (distributions, licences)."""
    if isinstance(value, dict):
        if "@type" in value:
            yield value
        for key, item in value.items():
            if key != "@context":
                yield from nodes(item)
    elif isinstance(value, list):
        for item in value:
            yield from nodes(item)


def of_type(kind: str) -> list[dict[str, Any]]:
    return [n for n in nodes(catalogue()["@graph"]) if n["@type"] == kind]


def iris(value: Any) -> list[str]:
    items = value if isinstance(value, list) else [value]
    return [item["@id"] for item in items]


def test_the_files_are_what_the_script_renders() -> None:
    assert exporter().main(["--check"]) == 0


def test_the_catalogue_is_json_ld_with_the_dcat_ap_namespaces() -> None:
    document = catalogue()
    prefixes = document["@context"]
    assert {k: prefixes[k] for k in NAMESPACES} == NAMESPACES
    keys = {key for node in nodes(document["@graph"]) for key in node if not key.startswith("@")}
    assert {key.split(":")[0] for key in keys} <= set(prefixes)
    assert {node["@type"] for node in nodes(document["@graph"])} <= KNOWN_TYPES


def test_every_node_has_the_mandatory_properties_of_dcat_ap_3_0_1() -> None:
    for kind, required in MANDATORY.items():
        found = of_type(kind)
        assert found, f"no {kind}"
        for node in found:
            missing = [p for p in required if not node.get(p)]
            assert not missing, f"{node['@id']}: {missing}"
    for node in [*of_type("dcat:Catalog"), *of_type("dcat:Dataset"), *of_type("dcat:DataService")]:
        assert node["dct:title"]["@language"] == "es"
        assert node["dct:description"]["@value"].strip()
    agents = {agent["@id"] for agent in of_type("foaf:Agent")}
    publishers = [n["dct:publisher"]["@id"] for n in of_type("dcat:Dataset")]
    assert set(publishers) <= agents
    assert of_type("dcat:Catalog")[0]["dct:publisher"]["@id"] in agents


def test_the_catalogue_lists_every_dataset_we_use_and_the_api() -> None:
    ctx, module = context(), exporter()
    [catalog] = of_type("dcat:Catalog")
    datasets = {n["@id"] for n in of_type("dcat:Dataset")}
    assert set(iris(catalog["dcat:dataset"])) == datasets
    assert len(datasets) == len(ctx.used) + 3  # + indicators and the two SDM files
    cm = [d for d in ctx.used if module.is_cm_open_data(d)]
    assert len(cm) == 39
    [api] = of_type("dcat:DataService")
    assert api["dcat:endpointURL"]["@id"] == module.API_BASE
    assert iris(catalog["dcat:service"]) == [api["@id"]]
    [indicators] = [
        n for n in of_type("dcat:Dataset") if n["@id"] == api["dcat:servesDataset"]["@id"]
    ]
    sources = set(iris(indicators["dct:source"]))
    assert {module.iri("dataset", d.dataset_id) for d in cm} <= sources
    [via_api] = indicators["dcat:distribution"]
    assert via_api["dcat:accessService"]["@id"] == api["@id"]


def test_each_dataset_carries_its_landing_page_publisher_and_licence() -> None:
    ctx, module = context(), exporter()
    by_id = {n["dct:identifier"]: n for n in of_type("dcat:Dataset")}
    for dataset in ctx.used:
        node = by_id[dataset.dataset_id]
        assert node["dcat:landingPage"]["@id"] == module.portal_url(dataset)
        assert node["dcat:distribution"]
        for distribution in node["dcat:distribution"]:
            assert distribution["dcat:accessURL"]["@id"].startswith("http")
            assert distribution["dct:license"]["@id"].startswith("http")
    cm_licences = {
        d["dct:license"]["@id"]
        for dataset in ctx.used
        if module.is_cm_open_data(dataset)
        for d in by_id[dataset.dataset_id]["dcat:distribution"]
    }
    assert cm_licences == {f"{EU}/licence/CC_BY_4_0", "https://www.crtm.es/licencia-de-uso"}


def test_the_controlled_vocabularies_are_the_eu_ones() -> None:
    for node in nodes(catalogue()["@graph"]):
        for key, prefix in (
            ("dct:accrualPeriodicity", f"{EU}/frequency/"),
            ("dcat:theme", f"{EU}/data-theme/"),
            ("dct:format", f"{EU}/file-type/"),
            ("dct:language", f"{EU}/language/"),
            ("dct:spatial", "http://data.europa.eu/nuts/code/"),
            ("dcatap:hvdCategory", "http://data.europa.eu/bna/c_"),
        ):
            for value in iris(node[key]) if key in node else []:
                assert value.startswith(prefix), f"{node['@id']} {key}: {value}"
        for key, kind in RANGES.items():
            values = node.get(key, [])
            for value in values if isinstance(values, list) else [values]:
                assert value["@type"] == kind, f"{node['@id']} {key}: {value}"


def test_only_the_high_value_datasets_of_the_register_carry_an_hvd_category() -> None:
    hvd = context().hvd
    marked = {n["dct:identifier"]: n for n in of_type("dcat:Dataset") if "dcatap:hvdCategory" in n}
    assert set(marked) == set(hvd["datasets"])
    for dataset_id, node in marked.items():
        category = hvd["categories"][hvd["datasets"][dataset_id]["category"]]["uri"]
        assert node["dcatap:hvdCategory"]["@id"] == category
        assert node["dcatap:applicableLegislation"]["@id"] == HVD_LEGISLATION
        for distribution in node["dcat:distribution"]:
            assert distribution["dcatap:applicableLegislation"]["@id"] == HVD_LEGISLATION


# --- Smart Data Models -------------------------------------------------------------------------


@cache
def sdm_sources() -> dict[str, Any]:
    return read(SDM_DIR / "sources.json")


@cache
def registry() -> Registry[Any]:
    """The official URLs of the schemas, resolved to the copies in data/schemas/sdm/."""
    base = sdm_sources()["base_url"]
    resources = [
        (base + name, Resource.from_contents(read(SDM_DIR / name)))
        for name in sdm_sources()["files"]
    ]
    return Registry().with_resources(resources)


def validator(model: str) -> Draft202012Validator:
    schema = read(SDM_DIR / model / "schema.json")
    return Draft202012Validator(
        schema, registry=registry(), format_checker=Draft202012Validator.FORMAT_CHECKER
    )


def test_the_schema_copies_are_the_official_ones() -> None:
    for name, entry in sdm_sources()["files"].items():
        raw = (SDM_DIR / name).read_bytes()
        digests = {
            hashlib.sha256(raw).hexdigest(),
            hashlib.sha256(raw.removesuffix(b"\n")).hexdigest(),
        }
        assert entry["sha256"] in digests, name
        if "schemaVersion" in entry:
            assert json.loads(raw)["$schemaVersion"] == entry["schemaVersion"]


@pytest.mark.parametrize(
    ("file_name", "model"),
    [
        ("sdm/datasets.json", "dataModel.DCAT-AP/Dataset"),
        ("sdm/farmacias.json", "dataModel.PointOfInterest/PointOfInterest"),
    ],
)
def test_every_entity_validates_against_its_official_schema(file_name: str, model: str) -> None:
    document = read(DATOS / file_name)
    assert document["dataModel"]["name"] == model
    assert document["count"] == len(document["entities"]) > 0
    check = validator(model)
    for entity in document["entities"]:
        errors = [e.message for e in check.iter_errors(entity)]
        assert not errors, f"{entity['id']}: {errors[:3]}"


def test_the_validator_rejects_what_the_schemas_forbid() -> None:
    dataset = read(DATOS / "sdm" / "datasets.json")["entities"][0]
    assert not validator("dataModel.DCAT-AP/Dataset").is_valid(
        dataset | {"accessMechanism": "Level4AccessMechanism"}
    )
    place = read(DATOS / "sdm" / "farmacias.json")["entities"][0]
    without_name = {k: v for k, v in place.items() if k != "name"}
    assert not validator("dataModel.PointOfInterest/PointOfInterest").is_valid(without_name)


def test_the_meloda_levels_are_the_snapshot_ones() -> None:
    scores = context().meloda["datasets"]
    entities = read(DATOS / "sdm" / "datasets.json")["entities"]
    assert len(entities) == 39
    for entity in entities:
        dataset_id = entity["id"].rsplit(":", 1)[1]
        meloda = scores[dataset_id]
        assert entity["accessMechanism"] == f"Level{meloda['d2_access']}AccessMechanism"
        assert entity["standardization"] == f"Level{meloda['d4_standard']}Standardization"
        assert "dissemination" not in entity and "reputation" not in entity
    licences = {entity.get("license") for entity in entities}
    assert licences == {"CC-BY-4.0", None}  # the CRTM licence has no SPDX id


def test_the_pharmacies_keep_their_source_licence_and_attribution() -> None:
    ctx = context()
    path = DATOS / "sdm" / "farmacias.json"
    document = read(path)
    source = document["source"]
    assert source["url"] == "https://datos.comunidad.madrid/dataset/oficinas_farmacia"
    assert source["license"]["url"] == f"{EU}/licence/CC_BY_4_0"
    assert source["attribution"].startswith("Fuente: Comunidad de Madrid")
    assert document["count"] == len(ctx.places.places)
    assert {e["source"] for e in document["entities"]} == {source["url"]}
    assert all(e["name"].startswith("Farmacia · ") for e in document["entities"])
    assert path.stat().st_size < PRE_COMMIT_MAX_KB * 1024
