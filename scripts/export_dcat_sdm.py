"""Publish the catalogue of the open data Vida Fácil uses as static files of the web (F14).

- apps/web/public/datos/catalogo.dcat.jsonld: DCAT-AP 3.0.1 in JSON-LD, the European profile
  (never DCAT-AP-ES). One dcat:Dataset per dataset we use (the ones with Gate 1 evidence, as
  pitch/datasets_cm.md counts them) from data/catalog/{sources,datasets}; the official title and
  licence of the CM ones from pitch/portal_cm_snapshot.json; the high-value datasets from
  data/catalog/manual/hvd_datasets.yaml. Plus our own: the indicators of the API (dct:source to
  every dataset), the API as a dcat:DataService and the two Smart Data Models files below.
- apps/web/public/datos/sdm/datasets.json: the CM datasets we use as Smart Data Models
  `dataModel.DCAT-AP/Dataset` entities, with the MELODA levels of pitch/meloda_cm_snapshot.json
  in the fields the model has for them (accessMechanism from D2, standardization from D4).
- apps/web/public/datos/sdm/farmacias.json: the pharmacies as `dataModel.PointOfInterest`
  entities, from data/catalog/manual/farmacias_places_api.csv, a dated read of the public API.

The official SDM schemas are copied in data/schemas/sdm/: the tests validate against them offline.

Usage:
    uv run python scripts/export_dcat_sdm.py                   # offline, deterministic
    uv run python scripts/export_dcat_sdm.py --check           # offline: fails if a file is stale
    uv run python scripts/export_dcat_sdm.py --refresh-places  # re-read the pharmacies (network)
"""

import argparse
import csv
import io
import json
import sys
import time
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import httpx
import yaml

from hi_contracts.catalog import DatasetSpec, SourceSpec
from hi_contracts.catalog.enums import Domain, PlaceCategory
from hi_contracts.public.places import PlaceCollection
from hi_domain.geo.codes import ine_municipality_from_cm
from hi_ingestion.catalog.loader import Catalog, load_catalog
from hi_ingestion.catalog.provenance import (
    CM_PORTAL_ROLE,
    CM_SOURCE_ID,
    is_cm_open_data,
    portal_url,
)

ROOT = Path(__file__).resolve().parents[1]
GATE1_DIR = ROOT / "evidence" / "gate-01"
PORTAL_SNAPSHOT = ROOT / "pitch" / "portal_cm_snapshot.json"
MELODA_SNAPSHOT = ROOT / "pitch" / "meloda_cm_snapshot.json"
MANUAL = ROOT / "data" / "catalog" / "manual"
HVD_SOURCE = MANUAL / "hvd_datasets.yaml"
PLACES_SNAPSHOT = MANUAL / "farmacias_places_api.csv"
SEARCH_SCOPE = ROOT / "data" / "catalog" / "zoning" / "search_scope.yaml"
SDM_SCHEMAS = ROOT / "data" / "schemas" / "sdm"
PUBLIC_DIR = ROOT / "apps" / "web" / "public"
DCAT_TARGET = PUBLIC_DIR / "datos" / "catalogo.dcat.jsonld"
SDM_DATASETS_TARGET = PUBLIC_DIR / "datos" / "sdm" / "datasets.json"
SDM_PLACES_TARGET = PUBLIC_DIR / "datos" / "sdm" / "farmacias.json"

SITE_URL = "https://vidafacil-madrid.vercel.app"
API_BASE = f"{SITE_URL}/api/v1"
PUBLISHER = "Vida Fácil"
API_PAUSE_S = 1.0  # at most one request a second to the production API
MELODA_API = "https://spain.meloda.org/api/v1"
OPENAPI_SPEC = "https://spec.openapis.org/oas/v3.1.0"

EU = "http://publications.europa.eu/resource/authority"
SDM_BASE = "https://smart-data-models.github.io/"
SDM_DATASET_MODEL = "dataModel.DCAT-AP/Dataset"
SDM_POI_MODEL = "dataModel.PointOfInterest/PointOfInterest"
NUTS_MADRID = "http://data.europa.eu/nuts/code/ES30"  # Comunidad de Madrid
CONTEXT = {
    "dcat": "http://www.w3.org/ns/dcat#",
    "dct": "http://purl.org/dc/terms/",
    "dcatap": "http://data.europa.eu/r5r/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "vcard": "http://www.w3.org/2006/vcard/ns#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "eli": "http://data.europa.eu/eli/ontology#",
}
# refresh_policy of the registry -> EU frequency; «unknown», «manual» and «none» say nothing
FREQUENCY = {
    "daily": "DAILY",
    "diario": "DAILY",
    "semanal": "WEEKLY",
    "mensual": "MONTHLY",
    "trimestral": "QUARTERLY",
    "semestral": "ANNUAL_2",
    "anual": "ANNUAL",
    "annual": "ANNUAL",
    "quinquenal": "QUINQUENNIAL",
    "continuo": "UPDATE_CONT",
}
FILE_TYPES = {"CSV", "GEOJSON", "HTML", "JSON", "PDF", "RDF", "SHP", "XLS", "XLSX", "XML", "ZIP"}
THEMES = {
    Domain.HOUSING: "SOCI",
    Domain.POPULATION: "SOCI",
    Domain.SOCIAL: "SOCI",
    Domain.INCOME: "ECON",
    Domain.ECONOMY: "ECON",
    Domain.EMPLOYMENT: "ECON",
    Domain.EDUCATION: "EDUC",
    Domain.HEALTH: "HEAL",
    Domain.TRANSPORT: "TRAN",
    Domain.URBANISM: "REGI",
    Domain.GEOGRAPHY: "REGI",
    Domain.ENVIRONMENT: "ENVI",
    Domain.SAFETY: "JUST",
}
# Their prefLabel in Spanish (EU Vocabularies, read with its SPARQL endpoint on 2026-11-23)
THEME_LABELS = {
    "SOCI": "Población y sociedad",
    "ECON": "Economía y finanzas",
    "EDUC": "Educación, cultura y deportes",
    "HEAL": "Salud",
    "TRAN": "Transporte",
    "REGI": "Regiones y ciudades",
    "ENVI": "Medio ambiente",
    "JUST": "Justicia, sistema judicial y seguridad pública",
    "GOVE": "Gobierno y sector público",
}
# A CKAN licence id of the CM portal that is an EU licence; any other keeps the registry's URL
PORTAL_LICENCES = {"cc-by": "CC_BY_4_0"}
# Words of a registry licence name -> EU licence; a name without them keeps its own URL
NAMED_LICENCES = (
    ("CC BY 4.0", "CC_BY_4_0"),
    ("Creative Commons Attribution 4.0", "CC_BY_4_0"),
    ("ODbL", "ODC_BL"),
    ("Apache License 2.0", "APACHE_2_0"),
)
SPDX = {"CC_BY_4_0": "CC-BY-4.0", "ODC_BL": "ODbL-1.0", "APACHE_2_0": "Apache-2.0"}
CC_BY_4_0 = f"{EU}/licence/CC_BY_4_0"
NOT_DISTRIBUTIONS = {"docs", CM_PORTAL_ROLE}  # documentation is a page; the CM page, the landing
GEOLOCATED = {"point", "polygon", "line"}  # the data carry coordinates (SDM `geolocation`)
MAX_FEATURES_NAMED = 6
PLACES_ES = {
    "education": "centros educativos",
    "health": "centros de salud y hospitales",
    "pharmacy": "farmacias",
    "social": "mayores y atención social",
    "transport": "transporte",
    "green": "parques",
    "other": "aparcamientos y otros lugares",
}
MODE_ES = {
    "metro": "metro",
    "metro_ligero": "metro ligero",
    "cercanias": "Cercanías",
    "emt": "autobuses EMT de Madrid",
    "autobus_urbano": "autobuses urbanos del resto de municipios",
    "autobus_interurbano": "autobuses interurbanos",
}
PLACES_COLUMNS = ["id", "name", "lon", "lat", "municipio", "seccion", "coordinates"]
GEOCODED_NOTE = (
    "Coordenadas geocodificadas por Vida Fácil: el registro no las traía o estaban fuera de sitio."
)


@dataclass(frozen=True)
class Licence:
    uri: str
    label: str | None  # the registry's name, for a licence with no EU code
    eu_code: str | None


@dataclass(frozen=True)
class Place:
    id: str
    name: str
    lon: float
    lat: float
    municipio: str | None
    seccion: str | None
    coordinates: str


@dataclass(frozen=True)
class PlacesRead:
    meta: dict[str, str]
    places: list[Place]


@dataclass(frozen=True)
class Context:
    catalog: Catalog
    used: list[DatasetSpec]
    portal: dict[str, dict[str, Any]]
    meloda: dict[str, Any]
    hvd: dict[str, Any]
    places: PlacesRead
    municipios: dict[str, str]


def public_url(path: Path) -> str:
    return f"{SITE_URL}/{path.relative_to(PUBLIC_DIR).as_posix()}"


CATALOG_URL = public_url(DCAT_TARGET)


def iri(kind: str, key: str) -> str:
    """Our own IRIs: fragments of the catalogue's URL, one per resource it describes."""
    return f"{CATALOG_URL}#{kind}/{key}"


def slug(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return "-".join("".join(c if c.isalnum() else " " for c in ascii_text.lower()).split())


def es(text: str) -> dict[str, str]:
    return {"@value": text, "@language": "es"}


def ref(uri: str) -> dict[str, str]:
    return {"@id": uri}


def typed(uri: str, kind: str) -> dict[str, str]:
    """A value of a controlled vocabulary, with the class DCAT-AP expects of it (its range)."""
    return {"@id": uri, "@type": kind}


def sdm_schema_url(model: str) -> str:
    return f"{SDM_BASE}{model}/schema.json"


def sdm_schema_version(model: str) -> str:
    schema = json.loads((SDM_SCHEMAS / model / "schema.json").read_text(encoding="utf-8"))
    return str(schema["$schemaVersion"])


# --- inputs ------------------------------------------------------------------------------------


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def used_datasets(catalog: Catalog) -> list[DatasetSpec]:
    """The datasets we use: the ones with Gate 1 evidence, as pitch/datasets_cm.md counts them."""
    return [
        dataset
        for dataset_id, dataset in sorted(catalog.datasets.items())
        if any(GATE1_DIR.glob(f"*/{dataset_id}/quality_report.json"))
    ]


def municipio_names() -> dict[str, str]:
    """INE code -> name, from the versioned list of the Instituto de Estadística (D-238)."""
    spec = yaml.safe_load(SEARCH_SCOPE.read_text(encoding="utf-8"))
    return {
        ine_municipality_from_cm(m["cm_code"]): m["name"]
        for zone in spec["zones"]
        for m in zone["municipios"]
    }


def places_pipeline(catalog: Catalog) -> Any:
    """The one pipeline that loads the pharmacies (D-216): its dataset and its name template."""
    matches = [
        p
        for p in catalog.pipelines.values()
        if getattr(p, "category", None) == PlaceCategory.PHARMACY
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one pharmacy pipeline, found {len(matches)}")
    return matches[0]


def read_places(path: Path) -> PlacesRead:
    """The snapshot: `# key: value` comment lines, then the CSV with its header."""
    lines = path.read_text(encoding="utf-8").splitlines()
    meta: dict[str, str] = {}
    for line in (x[2:] for x in lines if x.startswith("# ")):
        key, _, value = line.partition(": ")
        if key.isidentifier() and value:
            meta[key] = value
    rows = csv.DictReader(line for line in lines if not line.startswith("#"))
    places = [
        Place(
            id=r["id"],
            name=r["name"],
            lon=float(r["lon"]),
            lat=float(r["lat"]),
            municipio=r["municipio"] or None,
            seccion=r["seccion"] or None,
            coordinates=r["coordinates"],
        )
        for r in rows
    ]
    return PlacesRead(meta, places)


def load_context(catalog: Catalog) -> Context:
    return Context(
        catalog=catalog,
        used=used_datasets(catalog),
        portal=read_json(PORTAL_SNAPSHOT)["datasets"],
        meloda=read_json(MELODA_SNAPSHOT),
        hvd=yaml.safe_load(HVD_SOURCE.read_text(encoding="utf-8")),
        places=read_places(PLACES_SNAPSHOT),
        municipios=municipio_names(),
    )


# --- what each dataset is --------------------------------------------------------------------


def title(ctx: Context, dataset: DatasetSpec) -> str:
    portal = ctx.portal.get(dataset.dataset_id)
    return str(portal["title"]) if portal else dataset.name


def uses(catalog: Catalog, dataset: DatasetSpec) -> list[str]:
    """What the dataset feeds in Vida Fácil, in a few words."""
    names = sorted(
        {
            feature.human_name
            for feature in catalog.features.values()
            if any(s.dataset_id == dataset.dataset_id for s in feature.sources)
        }
    )
    shown = names[:MAX_FEATURES_NAMED]
    if len(names) > len(shown):
        shown.append(f"{len(names) - len(shown)} indicadores más")
    pipeline = catalog.pipelines.get(dataset.dataset_id)
    category = getattr(pipeline, "category", None)
    kind_of_place = getattr(pipeline, "subcategory_value", None)
    mode = getattr(pipeline, "mode", None)
    if category is not None:
        label = PLACES_ES.get(str(category), str(category))
        shown.append(f"los puntos del mapa ({(kind_of_place or label).lower()})")
    if mode:
        shown.append(f"las paradas de {MODE_ES.get(mode, mode)} con su frecuencia de paso")
    if pipeline is not None and pipeline.kind == "osm_walk_network":
        shown.append("la red peatonal con la que se miden los minutos a pie")
    if dataset.domain is Domain.GEOGRAPHY:
        shown.insert(0, "la geografía de las zonas del mapa")
    return shown


def description(catalog: Catalog, dataset: DatasetSpec) -> str:
    fed = uses(catalog, dataset)
    what = f"sirve para: {'; '.join(fed)}." if fed else "es un dato de apoyo."
    return f"Publica: {dataset.owner}. En Vida Fácil {what}"


def licence_of(source: SourceSpec, portal: dict[str, Any] | None) -> Licence | None:
    """The portal's licence of a CM dataset, else the registry's; None when neither has one."""
    code = PORTAL_LICENCES.get(str(portal.get("license_id"))) if portal else None
    name = portal["license_title"] if portal else source.license_name
    code = code or next((c for words, c in NAMED_LICENCES if name and words in name), None)
    if code:
        return Licence(f"{EU}/licence/{code}", None, code)
    if source.license_url is None:
        return None
    return Licence(str(source.license_url), name, None)


def dataset_licence(ctx: Context, dataset: DatasetSpec) -> Licence | None:
    source = ctx.catalog.sources[dataset.source_id]
    return licence_of(source, ctx.portal.get(dataset.dataset_id))


def frequency(dataset: DatasetSpec) -> str | None:
    code = FREQUENCY.get(dataset.refresh_policy.strip().lower())
    return f"{EU}/frequency/{code}" if code else None


def theme(dataset: DatasetSpec) -> str | None:
    """The EU data theme of the dataset's domain (its code), None for «other»."""
    return THEMES.get(dataset.domain)


def theme_uri(code: str) -> str:
    return f"{EU}/data-theme/{code}"


def concept(uri: str, label: str) -> dict[str, Any]:
    """A SKOS concept with its label, as the DCAT-AP shapes ask for one (skos:prefLabel)."""
    return {"@id": uri, "@type": "skos:Concept", "skos:prefLabel": es(label)}


def theme_concept(code: str) -> dict[str, Any]:
    return concept(theme_uri(code), THEME_LABELS[code])


def distribution_resources(dataset: DatasetSpec) -> list[Any]:
    return [r for r in dataset.resources if r.role not in NOT_DISTRIBUTIONS]


# --- DCAT-AP 3.0.1 -----------------------------------------------------------------------------


def licence_node(licence: Licence) -> dict[str, str]:
    node = {"@id": licence.uri, "@type": "dct:LicenseDocument"}
    if licence.label:
        node["rdfs:label"] = licence.label
    return node


def agent_iri(name: str) -> str:
    return iri("agente", slug(name))


def agent_node(name: str) -> dict[str, Any]:
    return {"@id": agent_iri(name), "@type": "foaf:Agent", "foaf:name": name}


def contact_node() -> dict[str, Any]:
    return {
        "@id": iri("contacto", "vida-facil"),
        "@type": "vcard:Kind",
        "vcard:fn": PUBLISHER,
        "vcard:hasURL": ref(f"{SITE_URL}/desarrolladores"),
    }


def distribution_nodes(ctx: Context, dataset: DatasetSpec) -> list[dict[str, Any]]:
    licence = dataset_licence(ctx, dataset)
    hvd = dataset.dataset_id in ctx.hvd["datasets"]
    nodes: list[dict[str, Any]] = []
    for n, resource in enumerate(distribution_resources(dataset), start=1):
        node: dict[str, Any] = {
            "@id": iri("distribucion", f"{dataset.dataset_id}/{n}"),
            "@type": "dcat:Distribution",
            "dct:title": es(resource.name),
            "dcat:accessURL": ref(str(resource.url)),
        }
        file_type = resource.format.upper()
        if file_type in FILE_TYPES:
            node["dct:format"] = typed(f"{EU}/file-type/{file_type}", "dct:MediaTypeOrExtent")
        if licence:
            node["dct:license"] = licence_node(licence)
        if hvd:
            node["dcatap:applicableLegislation"] = typed(
                ctx.hvd["legislation"], "eli:LegalResource"
            )
        nodes.append(node)
    return nodes


def dataset_node(ctx: Context, dataset: DatasetSpec) -> dict[str, Any]:
    node: dict[str, Any] = {
        "@id": iri("dataset", dataset.dataset_id),
        "@type": "dcat:Dataset",
        "dct:identifier": dataset.dataset_id,
        "dct:title": es(title(ctx, dataset)),
        "dct:description": es(description(ctx.catalog, dataset)),
        "dct:publisher": ref(agent_iri(dataset.owner)),
        "dcat:distribution": distribution_nodes(ctx, dataset),
    }
    landing = portal_url(dataset)
    if landing:
        node["dcat:landingPage"] = {"@id": landing, "@type": "foaf:Document"}
    pages = [str(r.url) for r in dataset.resources if r.role == "docs"]
    if pages:
        node["foaf:page"] = [{"@id": url, "@type": "foaf:Document"} for url in pages]
    if accrual := frequency(dataset):
        node["dct:accrualPeriodicity"] = typed(accrual, "dct:Frequency")
    if code := theme(dataset):
        node["dcat:theme"] = theme_concept(code)
    if is_cm_open_data(dataset):
        node["dct:spatial"] = typed(NUTS_MADRID, "dct:Location")
    hvd = ctx.hvd["datasets"].get(dataset.dataset_id)
    if hvd:
        category = ctx.hvd["categories"][hvd["category"]]
        node["dcatap:hvdCategory"] = concept(category["uri"], category["label"])
        node["dcatap:applicableLegislation"] = typed(ctx.hvd["legislation"], "eli:LegalResource")
    return node


def own_dataset(key: str, title_text: str, text: str, **extra: Any) -> dict[str, Any]:
    """A dataset Vida Fácil publishes: always ours, about the Comunidad de Madrid."""
    return {
        "@id": iri("dataset", key),
        "@type": "dcat:Dataset",
        "dct:identifier": key,
        "dct:title": es(title_text),
        "dct:description": es(text),
        "dct:publisher": ref(agent_iri(PUBLISHER)),
        "dcat:contactPoint": ref(iri("contacto", "vida-facil")),
        "dct:spatial": typed(NUTS_MADRID, "dct:Location"),
        **extra,
    }


def indicators_node(ctx: Context) -> dict[str, Any]:
    distribution = {
        "@id": iri("distribucion", "vida-facil-api"),
        "@type": "dcat:Distribution",
        "dct:title": es("API pública de Vida Fácil (JSON)"),
        "dcat:accessURL": ref(API_BASE),
        "dcat:accessService": ref(iri("servicio", "api")),
        "dct:format": typed(f"{EU}/file-type/JSON", "dct:MediaTypeOrExtent"),
        "dct:rights": {
            "@type": "dct:RightsStatement",
            "rdfs:label": es(
                "Cada cifra conserva la licencia de los conjuntos de datos de los que sale: la "
                "API devuelve, por cada uno, su licencia y el texto con el que hay que citarlo."
            ),
        },
    }
    return own_dataset(
        "vida-facil-indicadores",
        "Indicadores por zona de Vida Fácil",
        "Lo que falta en cada zona (escuela infantil, colegio, centro de salud, mayores, farmacia "
        "y vivienda), el encaje de cada zona con un hogar y los indicadores por municipio, "
        "distrito, barrio y sección censal que calcula Vida Fácil con los conjuntos de datos de "
        "este catálogo.",
        **{
            "dct:source": [ref(iri("dataset", d.dataset_id)) for d in ctx.used],
            "dcat:theme": [
                theme_concept("SOCI"),
                theme_concept("REGI"),
            ],
            "dcat:landingPage": {"@id": f"{SITE_URL}/desarrolladores", "@type": "foaf:Document"},
            "dcat:distribution": [distribution],
        },
    )


def sdm_distribution(key: str, target: Path, model: str, licence: Licence) -> dict[str, Any]:
    url = public_url(target)
    return {
        "@id": iri("distribucion", key),
        "@type": "dcat:Distribution",
        "dct:title": es(f"Smart Data Models: {model} (JSON)"),
        "dcat:accessURL": ref(url),
        "dcat:downloadURL": ref(url),
        "dct:format": typed(f"{EU}/file-type/JSON", "dct:MediaTypeOrExtent"),
        "dct:conformsTo": typed(sdm_schema_url(model), "dct:Standard"),
        "dct:license": licence_node(licence),
    }


def sdm_meloda_node(ctx: Context) -> dict[str, Any]:
    cm = [d for d in ctx.used if is_cm_open_data(d)]
    licence = Licence(CC_BY_4_0, None, "CC_BY_4_0")
    return own_dataset(
        "sdm-datasets-meloda",
        f"Los {len(cm)} conjuntos de datos de la Comunidad de Madrid que usa Vida Fácil, con "
        "su MELODA, en Smart Data Models",
        f"Una entidad Dataset de Smart Data Models ({SDM_DATASET_MODEL}) por cada uno, con los "
        "niveles de acceso y de estandarización que le da el Monitorizador MELODA "
        f"(spain.meloda.org, CC BY 4.0), leídos el {ctx.meloda['fetched_at']}.",
        **{
            "dct:source": [ref(iri("dataset", d.dataset_id)) for d in cm],
            "dcat:theme": theme_concept("GOVE"),
            "dcat:distribution": [
                sdm_distribution("sdm-datasets", SDM_DATASETS_TARGET, SDM_DATASET_MODEL, licence)
            ],
        },
    )


def sdm_places_node(ctx: Context) -> dict[str, Any]:
    dataset = ctx.catalog.datasets[places_pipeline(ctx.catalog).dataset_id]
    licence = dataset_licence(ctx, dataset)
    if licence is None:
        raise ValueError(f"{dataset.dataset_id}: the pharmacies need the licence of their source")
    return own_dataset(
        "sdm-farmacias",
        f"{title(ctx, dataset)} de la Comunidad de Madrid, como PointOfInterest de Smart Data "
        "Models",
        f"Las {len(ctx.places.places)} oficinas de farmacia del registro de la Comunidad de "
        f"Madrid, como entidades PointOfInterest de Smart Data Models ({SDM_POI_MODEL}), con "
        "su posición, su dirección y su municipio. El nombre es la calle y el número: el "
        "registro nombra a los titulares, que no se publican.",
        **{
            "dct:source": ref(iri("dataset", dataset.dataset_id)),
            "dcat:theme": theme_concept("HEAL"),
            "dcat:distribution": [
                sdm_distribution("sdm-farmacias", SDM_PLACES_TARGET, SDM_POI_MODEL, licence)
            ],
        },
    )


def api_service_node() -> dict[str, Any]:
    return {
        "@id": iri("servicio", "api"),
        "@type": "dcat:DataService",
        "dct:title": es("API pública de Vida Fácil"),
        "dct:description": es(
            "API REST de solo lectura, gratis y sin clave: qué falta en cada zona, qué zonas "
            "encajan con un hogar, los equipamientos del mapa, los conjuntos de datos y los "
            "indicadores, con la fuente de cada cifra."
        ),
        "dcat:endpointURL": ref(API_BASE),
        "dcat:endpointDescription": ref(f"{API_BASE}/openapi.json"),
        "dct:conformsTo": typed(OPENAPI_SPEC, "dct:Standard"),  # what openapi.json declares
        "dcat:servesDataset": ref(iri("dataset", "vida-facil-indicadores")),
        "dcat:landingPage": {"@id": f"{SITE_URL}/desarrolladores", "@type": "foaf:Document"},
        "dct:publisher": ref(agent_iri(PUBLISHER)),
        "dcat:contactPoint": ref(iri("contacto", "vida-facil")),
        "dct:accessRights": typed(f"{EU}/access-right/PUBLIC", "dct:RightsStatement"),
        "dct:spatial": typed(NUTS_MADRID, "dct:Location"),
    }


def catalog_node(datasets: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "@id": iri("catalogo", "vida-facil"),
        "@type": "dcat:Catalog",
        "dct:title": es("Catálogo de datos de Vida Fácil"),
        "dct:description": es(
            "Los conjuntos de datos abiertos que usa Vida Fácil, sobre todo del Portal de Datos "
            "Abiertos de la Comunidad de Madrid, con su licencia, su frecuencia y su tema, y lo "
            "que Vida Fácil publica con ellos: la API y los ficheros en Smart Data Models."
        ),
        "dct:publisher": ref(agent_iri(PUBLISHER)),
        "foaf:homepage": {"@id": SITE_URL, "@type": "foaf:Document"},
        "dct:license": licence_node(Licence(CC_BY_4_0, None, "CC_BY_4_0")),
        "dct:language": typed(f"{EU}/language/SPA", "dct:LinguisticSystem"),
        "dct:spatial": typed(NUTS_MADRID, "dct:Location"),
        "dcat:themeTaxonomy": {
            "@id": f"{EU}/data-theme",
            "@type": "skos:ConceptScheme",
            "dct:title": {"@value": "Data theme", "@language": "en"},
        },
        "dcat:dataset": [ref(d["@id"]) for d in datasets],
        "dcat:service": [ref(iri("servicio", "api"))],
    }


def render_dcat(ctx: Context) -> str:
    own = [indicators_node(ctx), sdm_meloda_node(ctx), sdm_places_node(ctx)]
    datasets = own + [dataset_node(ctx, d) for d in ctx.used]
    owners = sorted({d.owner for d in ctx.used} | {PUBLISHER})
    graph = [
        catalog_node(datasets),
        api_service_node(),
        contact_node(),
        *(agent_node(name) for name in owners),
        *datasets,
    ]
    return json.dumps({"@context": CONTEXT, "@graph": graph}, ensure_ascii=False, indent=2) + "\n"


# --- Smart Data Models -------------------------------------------------------------------------


def meloda_level(kind: str, value: int, top: int) -> str | None:
    """«Level2Standardization»: the SDM enumeration has no level 0 nor anything out of range."""
    return f"Level{value}{kind}" if 1 <= value <= top else None


def sdm_dataset(ctx: Context, dataset: DatasetSpec) -> dict[str, Any]:
    cm_portal = ctx.catalog.sources[CM_SOURCE_ID]
    entity: dict[str, Any] = {
        "id": f"urn:ngsi-ld:Dataset:vidafacil:{dataset.dataset_id}",
        "type": "Dataset",
        "title": {"es": title(ctx, dataset)},
        "description": {"es": description(ctx.catalog, dataset)},
        "publisher": dataset.owner,
        "landingPage": [portal_url(dataset)],
        "distribution": [str(r.url) for r in distribution_resources(dataset)],
        "belongsToCatalogue": str(cm_portal.base_url).rstrip("/"),
        "geolocation": dataset.geography in GEOLOCATED,
    }
    scores = ctx.meloda["datasets"].get(dataset.dataset_id)
    if scores:
        access = meloda_level("AccessMechanism", scores["d2_access"], 3)
        standard = meloda_level("Standardization", scores["d4_standard"], 4)
        entity |= {"accessMechanism": access} if access else {}
        entity |= {"standardization": standard} if standard else {}
        entity["isReferencedBy"] = [f"{MELODA_API}/datasets/{scores['meloda_id']}"]
    licence = dataset_licence(ctx, dataset)
    if licence and licence.eu_code in SPDX:
        entity["license"] = SPDX[licence.eu_code]
    if accrual := frequency(dataset):
        entity["accuralPeriodicity"] = accrual  # sic: the model's own spelling
    if code := theme(dataset):
        entity["theme"] = [theme_uri(code)]
    return entity


def render_sdm_datasets(ctx: Context) -> str:
    cm = [d for d in ctx.used if is_cm_open_data(d)]
    meloda = ctx.meloda
    document = {
        "title": f"Los {len(cm)} conjuntos de datos de la Comunidad de Madrid que usa Vida Fácil, "
        "con su MELODA",
        "description": "Entidades Dataset de Smart Data Models (DCAT-AP 3.0.0) con los niveles "
        "MELODA que el modelo prevé: accessMechanism (D2, acceso) y standardization (D4, "
        "estandarización). dissemination y reputation no se incluyen: el Monitorizador no las "
        "mide. license es el identificador SPDX de la licencia del portal: falta donde no tiene "
        "uno (la licencia de datos abiertos del CRTM). El resto de la puntuación está en la API "
        "del Monitorizador (isReferencedBy).",
        "dataModel": sdm_model(SDM_DATASET_MODEL),
        "meloda": {
            "source": meloda["source"],
            "method": meloda["method"],
            "readOn": meloda["fetched_at"],
            "license": meloda["license"],
            "attribution": meloda["attribution"],
        },
        "license": {"name": "CC BY 4.0", "url": "https://creativecommons.org/licenses/by/4.0/"},
        "catalog": CATALOG_URL,
        "generatedBy": "scripts/export_dcat_sdm.py",
        "count": len(cm),
        "entities": [sdm_dataset(ctx, d) for d in cm],
    }
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def sdm_model(model: str) -> dict[str, str]:
    return {
        "name": model,
        "schema": sdm_schema_url(model),
        "schemaVersion": sdm_schema_version(model),
    }


def poi_entity(ctx: Context, place: Place, source_url: str, prefix: str) -> dict[str, Any]:
    address = {"addressCountry": "ES", "addressRegion": "Comunidad de Madrid"}
    if place.name.startswith(prefix):
        address["streetAddress"] = place.name.removeprefix(prefix)
    locality = ctx.municipios.get(place.municipio or "")
    if locality:
        address["addressLocality"] = locality
    entity: dict[str, Any] = {
        "id": f"urn:ngsi-ld:PointOfInterest:vidafacil:{place.id}",
        "type": "PointOfInterest",
        "name": place.name,
        "category": [PlaceCategory.PHARMACY.value],
        "location": {"type": "Point", "coordinates": [place.lon, place.lat]},
        "address": address,
        "source": source_url,
        "dataProvider": PUBLISHER,
    }
    if place.municipio:
        entity["municipalityInfo"] = {
            "cityID": place.municipio,
            **({"cityName": locality} if locality else {}),
        }
    if place.coordinates == "geocoded":
        entity["description"] = GEOCODED_NOTE
    return entity


def places_document(ctx: Context) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """The file's metadata, with the source's licence and attribution, and its entities."""
    pipeline = places_pipeline(ctx.catalog)
    dataset = ctx.catalog.datasets[pipeline.dataset_id]
    source = ctx.catalog.sources[dataset.source_id]
    licence = dataset_licence(ctx, dataset)
    portal = ctx.portal.get(dataset.dataset_id)
    source_url = portal_url(dataset) or ""
    prefix = (pipeline.name_template or "").split("{")[0]
    meta = {
        "title": f"{title(ctx, dataset)} de la Comunidad de Madrid, como PointOfInterest",
        "description": "Entidades PointOfInterest de Smart Data Models. El nombre es sintético, "
        "la calle y el número: el registro nombra a los titulares, que no se publican. Las "
        "coordenadas son las del registro, salvo donde description dice que se geocodificaron.",
        "dataModel": sdm_model(SDM_POI_MODEL),
        "source": {
            "title": title(ctx, dataset),
            "publisher": dataset.owner,
            "url": source_url,
            "license": {
                "name": portal["license_title"] if portal else source.license_name,
                "url": licence.uri if licence else None,
            },
            "attribution": source.attribution_text,
        },
        "readFrom": {k: ctx.places.meta[k] for k in ("api", "contract", "read_on")},
        "catalog": CATALOG_URL,
        "generatedBy": "scripts/export_dcat_sdm.py",
        "count": len(ctx.places.places),
    }
    return meta, [poi_entity(ctx, p, source_url, prefix) for p in ctx.places.places]


def render_sdm_places(ctx: Context) -> str:
    """The metadata indented and one entity per line: small, and a diff shows each change."""
    meta, entities = places_document(ctx)
    head = json.dumps(meta, ensure_ascii=False, indent=2)[: -len("\n}")]
    rows = ",\n".join(f"    {json.dumps(e, ensure_ascii=False)}" for e in entities)
    return f'{head},\n  "entities": [\n{rows}\n  ]\n}}\n'


# --- refresh and main --------------------------------------------------------------------------


def fetch_places(category: str) -> tuple[list[Place], str]:
    """Every page of GET /places for one category, at most one request a second."""
    places: list[Place] = []
    page, pages, contract = 1, 1, ""
    with httpx.Client(timeout=120) as client:
        while page <= pages:
            if page > 1:
                time.sleep(API_PAUSE_S)
            response = client.get(f"{API_BASE}/places", params={"category": category, "page": page})
            response.raise_for_status()
            collection = PlaceCollection.model_validate(response.json()["data"])
            places += [
                Place(
                    id=f.id,
                    name=f.properties.name,
                    lon=f.geometry.coordinates[0],
                    lat=f.geometry.coordinates[1],
                    municipio=f.properties.municipio,
                    seccion=f.properties.seccion,
                    coordinates=f.properties.coordinates,
                )
                for f in collection.features
            ]
            pages, contract, page = collection.pages, collection.contract_version, page + 1
    return sorted(places, key=lambda p: p.id), contract


def write_places_snapshot(catalog: Catalog) -> None:
    pipeline = places_pipeline(catalog)
    category = str(pipeline.category)
    places, contract = fetch_places(category)
    out = io.StringIO()
    out.write(
        "# Generado por scripts/export_dcat_sdm.py --refresh-places: no se edita a mano.\n"
        f"# api: {API_BASE}/places?category={category}\n"
        f"# contract: {contract}\n"
        f"# read_on: {date.today().isoformat()}\n"
        f"# dataset_id: {pipeline.dataset_id}\n"
    )
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(PLACES_COLUMNS)
    for p in places:
        writer.writerow(
            [p.id, p.name, p.lon, p.lat, p.municipio or "", p.seccion or "", p.coordinates]
        )
    PLACES_SNAPSHOT.write_text(out.getvalue(), encoding="utf-8")
    print(f"wrote {PLACES_SNAPSHOT.relative_to(ROOT)} ({len(places)} places)")


def outputs(ctx: Context) -> list[tuple[Path, str]]:
    return [
        (DCAT_TARGET, render_dcat(ctx)),
        (SDM_DATASETS_TARGET, render_sdm_datasets(ctx)),
        (SDM_PLACES_TARGET, render_sdm_places(ctx)),
    ]


def stale_outputs(ctx: Context) -> list[Path]:
    return [
        path
        for path, content in outputs(ctx)
        if not path.exists() or path.read_text(encoding="utf-8") != content
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DCAT-AP 3.0.1 and Smart Data Models files")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="fail if a file is stale (offline)")
    mode.add_argument(
        "--refresh-places", action="store_true", help="re-read the pharmacies from the API"
    )
    args = parser.parse_args(argv)
    catalog = load_catalog(include_drafts=False)
    if args.refresh_places:
        try:
            write_places_snapshot(catalog)
        except httpx.HTTPError as exc:
            print(f"could not read {API_BASE}/places: {exc}", file=sys.stderr)
            return 2
    ctx = load_context(catalog)
    if args.check:
        stale = stale_outputs(ctx)
        if stale:
            print("stale (run scripts/export_dcat_sdm.py):", [p.name for p in stale])
            return 1
        return 0
    for path, content in outputs(ctx):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)} ({len(content.encode()) / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
