"""Pieces shared by the search result and the per-zone list: zones, datasets, indicator values."""

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from hi_contracts.catalog.dataset import DATASET_ID_PATTERN
from hi_contracts.catalog.enums import NullReason, TerritoryLevel

Confidence = float  # 0..1, see `confidence` fields; 0 means unknown


class ZoneRef(BaseModel):
    """A zone the product talks about. `code` is the INE code (municipio, sección) or H3 index."""

    model_config = ConfigDict(extra="forbid")

    level: TerritoryLevel
    code: str = Field(min_length=1, examples=["28079", "2807901124"])
    admin_unit_id: str | None = Field(
        default=None,
        description="geo_admin_unit id for /api/v1/geo/admin-units; None for H3 cells",
        examples=["ES.28.MUN.28079"],
    )
    name: str = Field(examples=["Madrid"])
    municipio_ine: str | None = Field(default=None, pattern=r"^28\d{3}$")
    municipio_name: str | None = None
    center_lon: float | None = Field(default=None, ge=-4.58, le=-3.05)
    center_lat: float | None = Field(default=None, ge=39.88, le=41.17)


class DatasetRef(BaseModel):
    """Provenance of a result: the dataset, who publishes it and where to open it."""

    model_config = ConfigDict(extra="forbid")

    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    name: str
    publisher: str
    is_cm_open_data: bool = Field(
        description="Published in the Comunidad de Madrid open data portal (counts for DATAMAD)"
    )
    url: HttpUrl | None = Field(default=None, description="Portal page (CM portal when it exists)")
    version: str | None = Field(default=None, description="dataset_version label used")
    license: str | None = None


class IndicatorValue(BaseModel):
    """One measured value with its unit, confidence and the reason when it is missing."""

    model_config = ConfigDict(extra="forbid")

    feature_id: str
    label: str = Field(description="Plain-language name")
    value: float | None
    unit: str
    confidence: Confidence = Field(ge=0, le=1)
    null_reason: NullReason | None = Field(
        default=None, description="Why value is missing; never 0 for unknown"
    )
    level: TerritoryLevel = Field(description="Level the value was computed at")
    datasets: list[str] = Field(default_factory=list[str], description="dataset_id values")


class DatasetList(BaseModel):
    """Datasets behind the product (GET /api/v1/datasets): the footer counter and provenance."""

    model_config = ConfigDict(extra="forbid")

    total: int = Field(ge=0)
    cm_open_data_count: int = Field(ge=0, description="Published in the CM open data portal")
    datasets: list[DatasetRef]
