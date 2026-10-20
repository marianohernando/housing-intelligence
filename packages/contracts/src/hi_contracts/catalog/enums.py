"""Controlled vocabularies shared by catalog YAML, DB check constraints and API."""

from enum import StrEnum


class TrustTier(StrEnum):
    A_OFFICIAL = "A_OFFICIAL"
    B_OPEN_STRUCTURED = "B_OPEN_STRUCTURED"
    C_COMMERCIAL_API = "C_COMMERCIAL_API"
    D_SCRAPED = "D_SCRAPED"


class LicenseStatus(StrEnum):
    CLEAR = "CLEAR"
    RESTRICTED = "RESTRICTED"
    PERMISSION_REQUIRED = "PERMISSION_REQUIRED"
    RESEARCH_ONLY = "RESEARCH_ONLY"
    REJECTED = "REJECTED"
    PENDING_REVIEW = "PENDING_REVIEW"


class DatasetStatus(StrEnum):
    DISCOVERED = "DISCOVERED"
    REVIEWED = "REVIEWED"
    INGESTING = "INGESTING"
    VALIDATED = "VALIDATED"
    PRODUCTION = "PRODUCTION"
    DEGRADED = "DEGRADED"
    RETIRED = "RETIRED"


class Priority(StrEnum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class ApiType(StrEnum):
    CKAN = "ckan"
    ARCGIS_HUB = "arcgis_hub"
    DCAT_APIDATA = "dcat_apidata"
    OGC_WFS = "ogc_wfs"
    DOWNLOAD = "download"
    NONE = "none"


class Domain(StrEnum):
    HOUSING = "housing"
    POPULATION = "population"
    INCOME = "income"
    EDUCATION = "education"
    HEALTH = "health"
    SOCIAL = "social"
    TRANSPORT = "transport"
    URBANISM = "urbanism"
    ENVIRONMENT = "environment"
    ECONOMY = "economy"
    EMPLOYMENT = "employment"
    SAFETY = "safety"
    GEOGRAPHY = "geography"
    OTHER = "other"


class GeoResolution(StrEnum):
    CCAA = "ccaa"
    PROVINCIA = "provincia"
    MUNICIPIO = "municipio"
    DISTRITO = "distrito"
    BARRIO = "barrio"
    SECCION_CENSAL = "seccion_censal"
    CODIGO_POSTAL = "codigo_postal"
    H3 = "h3"
    PARCELA = "parcela"
    EDIFICIO = "edificio"
    POINT = "point"
    LINE = "line"
    NONE = "none"
    UNKNOWN = "unknown"


class AdminLevel(StrEnum):
    CCAA = "ccaa"
    PROVINCIA = "provincia"
    MUNICIPIO = "municipio"
    DISTRITO = "distrito"
    BARRIO = "barrio"
    SECCION_CENSAL = "seccion_censal"


class PipelineStage(StrEnum):
    DISCOVER = "DISCOVER"
    FETCH = "FETCH"
    SNAPSHOT = "SNAPSHOT"
    SCHEMA_CHECK = "SCHEMA_CHECK"
    PARSE = "PARSE"
    NORMALIZE = "NORMALIZE"
    GEO_RESOLVE = "GEO_RESOLVE"
    ENTITY_RESOLUTION = "ENTITY_RESOLUTION"
    QUALITY_CHECK = "QUALITY_CHECK"
    PUBLISH_SILVER = "PUBLISH_SILVER"
    BUILD_FEATURES = "BUILD_FEATURES"


class RunStatus(StrEnum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class NullReason(StrEnum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    SOURCE_NO_COVERAGE = "SOURCE_NO_COVERAGE"
    SOURCE_MISSING = "SOURCE_MISSING"
    TEMPORARILY_UNAVAILABLE = "TEMPORARILY_UNAVAILABLE"
    STALE = "STALE"
    PARSE_ERROR = "PARSE_ERROR"
    ENTITY_NOT_RESOLVED = "ENTITY_NOT_RESOLVED"
    ESTIMATION_NOT_ALLOWED = "ESTIMATION_NOT_ALLOWED"
    UNKNOWN = "UNKNOWN"


class H3JoinMethod(StrEnum):
    CENTROID = "centroid"
    OVERLAP = "overlap"
    POPULATION_WEIGHTED = "population_weighted"
    NETWORK_ACCESS = "network_access"
