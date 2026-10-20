"""Heuristic first-pass scorecard for harvested candidates (docs/02_data/38).

Only criteria that metadata can support are scored automatically; the rest stay None
(needs human review). Drafts can never be P0: P0 requires a reviewed scorecard.
"""

import re
import unicodedata
from dataclasses import dataclass
from datetime import UTC, datetime

from hi_contracts.catalog.candidate import CandidateRecord
from hi_contracts.catalog.dataset import Scorecard
from hi_contracts.catalog.enums import Domain, GeoResolution, Priority

SCORING_VERSION = "heuristic-v2"

DOMAIN_KEYWORDS: dict[Domain, tuple[str, ...]] = {
    Domain.HOUSING: (
        "vivienda", "alquiler", "hipoteca", "compraventa", "transacciones inmobiliarias",
        "inmobiliari", "parque residencial", "vivienda protegida", "vpo", "valor tasado",
        "arrendad", "edificios destinados a vivienda", "residencial",
    ),
    Domain.POPULATION: (
        "poblacion", "padron", "censo", "hogares", "habitantes", "nacimientos", "defunciones",
        "migraciones", "movimiento natural", "extranjeros", "estructura de edad", "piramide",
    ),
    Domain.INCOME: ("renta", "ingresos", "irpf", "salario", "pobreza", "desigualdad", "gini"),
    Domain.EMPLOYMENT: ("paro", "desempleo", "afiliacion", "afiliados", "empleo", "contratos"),
    Domain.EDUCATION: (
        "centros educativos", "colegio", "escuela", "instituto", "universidad", "alumnado",
        "alumnos", "escolarizacion", "educacion infantil", "centros docentes",
    ),
    Domain.HEALTH: (
        "centros sanitarios", "centro de salud", "hospital", "farmacia", "zona basica de salud",
        "atencion primaria", "establecimientos sanitarios",
    ),
    Domain.SOCIAL: (
        "atencion social", "servicios sociales", "residencia", "mayores", "dependencia",
        "discapacidad", "centros de dia", "teleasistencia",
    ),
    Domain.TRANSPORT: (
        "transporte", "gtfs", "metro", "autobus", "cercanias", "paradas", "estaciones",
        "movilidad", "trafico", "aparcamiento", "bicicleta", "interurbano", "tren",
    ),
    Domain.URBANISM: (
        "urbanismo", "planeamiento", "parcela", "suelo", "edificabilidad", "licencias",
        "catastr", "edificios", "construccion", "callejero", "portal del suelo",
    ),
    Domain.ENVIRONMENT: (
        "calidad del aire", "contaminacion", "ruido", "zonas verdes", "arbolado", "parques",
        "temperatura", "emisiones", "medio ambiente", "residuos", "agua", "isla de calor",
    ),
    Domain.ECONOMY: (
        "empresas", "comercio", "locales", "actividad economica", "establecimientos",
        "turismo", "terrazas", "mercados",
    ),
    Domain.SAFETY: ("seguridad", "delitos", "accidentes", "siniestralidad", "criminalidad"),
    Domain.GEOGRAPHY: (
        "limites", "secciones censales", "seccionado", "cartografia", "delimitacion",
    ),
}  # fmt: skip

# Product impact by domain for the residential-intelligence core (docs/02_data/08, START_HERE §5).
DOMAIN_IMPACT: dict[Domain, int] = {
    Domain.HOUSING: 5, Domain.POPULATION: 5, Domain.INCOME: 5, Domain.TRANSPORT: 5,
    Domain.GEOGRAPHY: 5, Domain.EDUCATION: 4, Domain.HEALTH: 4, Domain.SOCIAL: 4,
    Domain.URBANISM: 4, Domain.ENVIRONMENT: 3, Domain.ECONOMY: 3, Domain.EMPLOYMENT: 3,
    Domain.SAFETY: 3, Domain.OTHER: 1,
}  # fmt: skip

# DATAMAD bases §6/§10: the Comunidad de Madrid portal is the scored source.
SOURCE_DATAMAD: dict[str, int] = {
    "comunidad_madrid_ckan": 5,
    "crtm_open_data": 4,
    "ayuntamiento_madrid_ckan": 3,
    "datos_gob_es": 2,
}

AREA_RULES: tuple[tuple[re.Pattern[str], int, GeoResolution], ...] = (
    (re.compile(r"seccion(es)? censal"), 5, GeoResolution.SECCION_CENSAL),
    (re.compile(r"barrio"), 4, GeoResolution.BARRIO),
    (re.compile(r"codigo postal|codigos postales"), 4, GeoResolution.CODIGO_POSTAL),
    (re.compile(r"distrito|zona basica"), 4, GeoResolution.DISTRITO),
    (re.compile(r"municipi"), 3, GeoResolution.MUNICIPIO),
    (re.compile(r"comunidad de madrid|regional|autonomic"), 1, GeoResolution.CCAA),
)  # fmt: skip
PARCEL_TITLE = re.compile(r"parcela|catastr|callejero|portal del suelo")
POINT_TITLE = re.compile(
    r"localizacion|ubicacion|geolocaliz|directorio|registro de|gtfs|paradas|estaciones|"
    r"red de (metro|autobus|cercanias|metro ligero|tranvia)|mapa de"
)
FACILITY_TITLE = re.compile(
    r"\bcentros?\b|establecimientos|farmacias|equipamientos|instalaciones|puntos de|"
    r"aparcamientos|arbolado|zonas verdes|parques"
)
GEO_FORMATS = {
    "GEOJSON", "SHP", "KML", "KMZ", "WFS", "WMS", "FEATURE SERVICE", "FEATURE LAYER",
    "GTFS", "GPKG", "FILE GEODATABASE",
}  # fmt: skip
STATISTICAL_ORGS = {"estadistica"}

FORMAT_EASE: dict[str, int] = {
    "GEOJSON": 5, "CSV": 5, "JSON": 5, "SHP": 4, "ZIP": 4, "KML": 4, "GTFS": 4,
    "CSV COLLECTION": 4, "FEATURE SERVICE": 4, "FEATURE LAYER": 4, "XLSX": 3, "XLS": 3,
    "ODS": 3, "XML": 3, "WFS": 3, "WMS": 2, "HTML": 1, "PDF": 1, "DOCX": 1,
}  # fmt: skip

LICENSE_CLARITY: dict[str, int] = {
    "cc-by": 5, "cc-zero": 5, "odc-by": 5, "odc-pddl": 5, "crtm-lda": 5, "other-pd": 4,
    "cc-by-sa": 4, "odc-odbl": 4, "other-open": 3, "other-at": 3, "uk-ogl": 3,
    "cc-nc": 1, "other-nc": 1, "notspecified": 1, "other-closed": 0,
}  # fmt: skip
OPEN_LICENSE_THRESHOLD = 4

COMPOSITE_WEIGHTS: dict[str, int] = {
    "product_impact": 3, "datamad_relevance": 2, "geographic_granularity": 2,
    "freshness": 1, "license_clarity": 1, "ingestion_ease": 1,
}  # fmt: skip


@dataclass(frozen=True)
class ScoredCandidate:
    candidate: CandidateRecord
    domain: Domain
    matched_keywords: tuple[str, ...]
    geo_resolution: GeoResolution
    scorecard: Scorecard
    composite: float
    priority_draft: Priority


def normalize_text(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", ascii_text.lower())


def detect_domain(title: str, tags: str, body: str) -> tuple[Domain, tuple[str, ...], bool]:
    """Weighted keyword match: title x3, tags x2, description x1.

    Ties go to the keyword that appears first in the title (the subject of the dataset).
    Returns (domain, matched keywords, strong) where strong means title or tags matched.
    """
    best: tuple[int, int, Domain, tuple[str, ...], bool] = (0, 0, Domain.OTHER, (), False)
    for domain, keywords in DOMAIN_KEYWORDS.items():
        hits = tuple(k for k in keywords if k in title or k in tags or k in body)
        if not hits:
            continue
        weight = sum(3 if k in title else 2 if k in tags else 1 for k in hits)
        positions = [title.find(k) for k in hits if k in title]
        first = -min(positions) if positions else -10_000
        strong = any(k in title or k in tags for k in hits)
        if (weight, first) > best[:2]:
            best = (weight, first, domain, hits, strong)
    return best[2], best[3], best[4]


def detect_granularity(title: str, tags: str, formats: list[str]) -> tuple[int, GeoResolution]:
    if PARCEL_TITLE.search(title):
        return 5, GeoResolution.PARCELA
    if POINT_TITLE.search(title):
        return 5, GeoResolution.POINT
    for pattern, score, resolution in AREA_RULES:
        if pattern.search(title):
            return score, resolution
    has_geo_format = any(f.upper() in GEO_FORMATS for f in formats)
    if has_geo_format and FACILITY_TITLE.search(title):
        return 5, GeoResolution.POINT
    for pattern, score, resolution in AREA_RULES:
        if pattern.search(tags):
            return score, resolution
    return 2, GeoResolution.UNKNOWN


def freshness_score(modified_at: datetime | None, now: datetime) -> int | None:
    if modified_at is None:
        return None
    reference = modified_at if modified_at.tzinfo else modified_at.replace(tzinfo=UTC)
    age_days = (now - reference).days
    for limit, score in ((365, 5), (730, 4), (1095, 3), (1825, 2)):
        if age_days <= limit:
            return score
    return 1


def ingestion_ease(formats: list[str]) -> int | None:
    scores = [FORMAT_EASE[f.upper()] for f in formats if f.upper() in FORMAT_EASE]
    return max(scores) if scores else None


def license_clarity(license_id: str | None) -> int | None:
    if license_id is None:
        return None
    return LICENSE_CLARITY.get(license_id.lower(), 2)


def composite_score(card: Scorecard) -> float:
    values = card.model_dump()
    scored = [(values[k], w) for k, w in COMPOSITE_WEIGHTS.items() if values[k] is not None]
    if not scored:
        return 0.0
    return round(sum(v * w for v, w in scored) / sum(w for _, w in scored), 3)


def draft_priority(card: Scorecard) -> Priority:
    impact = card.product_impact or 0
    if (
        impact >= 4
        and (card.geographic_granularity or 0) >= 3
        and (card.license_clarity or 0) >= OPEN_LICENSE_THRESHOLD
        and (card.datamad_relevance or 0) >= 4
    ):
        return Priority.P1
    if impact >= 3:
        return Priority.P2
    return Priority.P3


def score_candidate(candidate: CandidateRecord, now: datetime | None = None) -> ScoredCandidate:
    now = now or datetime.now(UTC)
    title = normalize_text(candidate.title)
    tags = normalize_text(" ".join(candidate.tags))
    body = normalize_text(candidate.description[:600])
    domain, hits, strong = detect_domain(title, tags, body)
    granularity, resolution = detect_granularity(title, tags, candidate.formats)
    if candidate.extra.get("organization") in STATISTICAL_ORGS and resolution in {
        GeoResolution.POINT,
        GeoResolution.PARCELA,
    }:
        granularity, resolution = 2, GeoResolution.UNKNOWN  # statistical tables are not points
    if not hits:
        impact = 1
    else:
        impact = DOMAIN_IMPACT[domain] if strong else max(1, DOMAIN_IMPACT[domain] - 1)
    datamad = SOURCE_DATAMAD.get(candidate.source_id, 1)
    card = Scorecard(
        datamad_relevance=min(datamad, 2) if impact <= 2 else datamad,
        product_impact=impact,
        geographic_granularity=granularity,
        freshness=freshness_score(candidate.modified_at, now),
        license_clarity=license_clarity(candidate.license_id),
        ingestion_ease=ingestion_ease(candidate.formats),
        notes=f"{SCORING_VERSION}; keywords={list(hits)}; strong={strong}",
    )
    return ScoredCandidate(
        candidate=candidate,
        domain=domain,
        matched_keywords=hits,
        geo_resolution=resolution,
        scorecard=card,
        composite=composite_score(card),
        priority_draft=draft_priority(card),
    )
