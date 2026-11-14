"""GET /api/v1/places: facilities as GeoJSON points, typed (places v1, 12 Nov, D-216).

Until 12 Nov the properties were free-form. They are now a contract so the web can show every
facility of a zone, filter it with the same criterion as the list of what is missing
(`gap_rows`) and show its capacity when the source publishes it.

D-218 (additive, still places-1): hospitals carry their installed beds from the Catálogo
Nacional de Hospitales in `capacity`, with `dependency` and `kind`; hospitals and primary care
centres carry their institutional name when the official directory gives one.

D-239 (additive, still places-1): `dependency` on the place itself, for every health place of
the CM register, so a hospital the catalogue could not be matched to (no beds) says it too.
«publica» is the network of the Servicio Madrileño de Salud, also its hospitals run by a private
company, which say so in `management` («Hospital público · gestión privada»).
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from hi_contracts.catalog.dataset import DATASET_ID_PATTERN
from hi_contracts.catalog.enums import PlaceCategory
from hi_contracts.public.gaps import GapRowKey

PLACES_CONTRACT_VERSION = "places-1"

Ownership = Literal["publica", "concertada", "privada"]
Dependency = Literal["publica", "privada"]
Management = Literal["publica", "privada"]
CoordinatesOrigin = Literal["source", "geocoded"]


class PlaceCapacity(BaseModel):
    """How much the place can serve, as its source publishes it (never estimated)."""

    model_config = ConfigDict(extra="forbid")

    value: float = Field(ge=0, examples=[1300])
    unit: str = Field(examples=["camas instaladas", "plazas autorizadas"])
    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    dependency: Dependency | None = Field(
        default=None,
        description="Hospitals (D-218): who runs it, from the CM register; mutuas count as "
        "private. Kept as the register says it: the public network is `dependency` of the place "
        "(D-239)",
    )
    kind: str | None = Field(
        default=None,
        examples=["Hospital general"],
        description="Hospitals (D-218): the register's type (general, especializado, ...)",
    )


class PlaceProperties(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        examples=["Hospital Universitario La Paz", "Centro de salud Abrantes", "AMOROS"],
        description="Institutional name; '<type> (<municipio>)' when no official one is known",
    )
    category: PlaceCategory
    subcategory: str = Field(examples=["COLEGIO DE EDUCACIÓN INFANTIL Y PRIMARIA"])
    municipio: str | None = Field(default=None, pattern=r"^28\d{3}$")
    seccion: str | None = Field(default=None, examples=["ES.28.SEC.2807905001"])
    ownership: Ownership | None = Field(
        default=None,
        description="Educational centres only: titularidad of the register (None elsewhere)",
    )
    dependency: Dependency | None = Field(
        default=None,
        description="Health places (D-239): 'publica' for the network of the Servicio Madrileño "
        "de Salud (the CM register's dependencia funcional, or a network hospital a private "
        "company runs), 'privada' for the rest; mutuas count as private (None elsewhere)",
    )
    management: Management | None = Field(
        default=None,
        description="Hospitals (D-239): who runs it. 'privada' for a private hospital and for a "
        "hospital of the public network run by a private company by concession or concierto "
        "singular (a versioned list with its official source), 'publica' for the rest of the "
        "public ones (None elsewhere)",
    )
    gap_rows: list[GapRowKey] = Field(
        default_factory=list[GapRowKey],
        description="Rows of the list of what is missing that count this place (same filters)",
    )
    capacity: PlaceCapacity | None = None
    coordinates: CoordinatesOrigin = Field(
        default="source",
        description="'geocoded' when the register's coordinates were missing or wrong (D-216)",
    )
    confidence: float = Field(ge=0, le=1, description="1 for the register's own coordinates")


class PointGeometry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["Point"] = "Point"
    coordinates: tuple[float, float] = Field(description="[lon, lat], WGS84")


class PlaceFeature(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["Feature"] = "Feature"
    id: str
    geometry: PointGeometry
    properties: PlaceProperties


class PlaceCollection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["FeatureCollection"] = "FeatureCollection"
    contract_version: str = PLACES_CONTRACT_VERSION
    features: list[PlaceFeature]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    pages: int = Field(ge=1)
