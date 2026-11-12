"""GET /api/v1/places: facilities as GeoJSON points, typed (places v1, 12 Nov, D-216).

Until 12 Nov the properties were free-form. They are now a contract so the web can show every
facility of a zone, filter it with the same criterion as the list of what is missing
(`gap_rows`) and show its capacity when the source publishes it.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from hi_contracts.catalog.dataset import DATASET_ID_PATTERN
from hi_contracts.catalog.enums import PlaceCategory
from hi_contracts.public.gaps import GapRowKey

PLACES_CONTRACT_VERSION = "places-1"

Ownership = Literal["publica", "concertada", "privada"]
CoordinatesOrigin = Literal["source", "geocoded"]


class PlaceCapacity(BaseModel):
    """How much the place can serve, as its source publishes it (never estimated)."""

    model_config = ConfigDict(extra="forbid")

    value: float = Field(ge=0, examples=[1300])
    unit: str = Field(examples=["camas", "plazas autorizadas"])
    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)


class PlaceProperties(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(examples=["Centro de salud (Madrid)", "AMOROS"])
    category: PlaceCategory
    subcategory: str = Field(examples=["COLEGIO DE EDUCACIÓN INFANTIL Y PRIMARIA"])
    municipio: str | None = Field(default=None, pattern=r"^28\d{3}$")
    seccion: str | None = Field(default=None, examples=["ES.28.SEC.2807905001"])
    ownership: Ownership | None = Field(
        default=None,
        description="Educational centres only: titularidad of the register (None elsewhere)",
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
