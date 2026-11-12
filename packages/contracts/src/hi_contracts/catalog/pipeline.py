"""Declarative pipeline specs: how a dataset's resource becomes Silver rows.

Pipelines live in data/catalog/pipelines/<dataset_id>.yaml. Code implements each `kind` once;
datasets only declare columns and mappings, so no dataset id or formula is hardcoded.
"""

from string import Formatter
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hi_contracts.catalog.dataset import DATASET_ID_PATTERN
from hi_contracts.catalog.enums import PlaceCategory, TerritoryLevel
from hi_contracts.catalog.metric import METRIC_ID_PATTERN

DEFAULT_MISSING_MARKERS = ("-", ".", "..", "...", "")


class CsvFormat(BaseModel):
    model_config = ConfigDict(extra="forbid")

    separator: str = ";"
    encodings: list[str] = Field(default_factory=lambda: ["utf-8-sig", "latin-1"])
    decimal: str = "."


class MetricSplit(BaseModel):
    """One source column decides which metric a row belongs to (e.g. 'Medida')."""

    model_config = ConfigDict(extra="forbid")

    column: str
    metrics: dict[str, Annotated[str, Field(pattern=METRIC_ID_PATTERN)]]


class CmStatTablePipeline(BaseModel):
    """Instituto de Estadística long tables: Año | Tipo territorio | Código | ... | Valor."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["cm_stat_table"]
    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    resource_role: str = "primary"
    csv: CsvFormat = Field(default_factory=CsvFormat)
    metric_id: str | None = Field(default=None, pattern=METRIC_ID_PATTERN)
    metric_split: MetricSplit | None = None
    period_column: str = "Año"
    # Older years are left out to fit the storage budget; counted as out_of_window, never hidden.
    period_min: int | None = Field(default=None, ge=1900, le=2100)
    value_column: str = "Valor"
    unit_column: str | None = "Unidad"
    territory_type_column: str = "Tipo territorio"
    territory_code_column: str = "Código territorio"
    territory_name_column: str = "Territorio"
    territory_types: dict[str, TerritoryLevel]
    dimension_columns: dict[str, str] = Field(default_factory=dict[str, str])
    missing_markers: list[str] = Field(default_factory=lambda: list(DEFAULT_MISSING_MARKERS))

    @model_validator(mode="after")
    def _one_metric_source(self) -> Self:
        if (self.metric_id is None) == (self.metric_split is None):
            msg = f"{self.dataset_id}: declare exactly one of metric_id or metric_split"
            raise ValueError(msg)
        return self

    def metric_ids(self) -> list[str]:
        if self.metric_split:
            return sorted(set(self.metric_split.metrics.values()))
        return [self.metric_id] if self.metric_id else []


class CmPostcodeConceptPipeline(BaseModel):
    """Tables where the postcode is embedded in a free-text 'Concepto' column."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["cm_postcode_concept"]
    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    resource_role: str = "primary"
    csv: CsvFormat = Field(default_factory=CsvFormat)
    metric_id: str = Field(pattern=METRIC_ID_PATTERN)
    period_column: str = "Año"
    value_column: str = "Valor"
    concept_column: str = "Concepto"
    postcode_pattern: str = r"c[oó]digo postal (\d{5})"
    missing_markers: list[str] = Field(default_factory=lambda: list(DEFAULT_MISSING_MARKERS))

    def metric_ids(self) -> list[str]:
        return [self.metric_id]


class MadridPadronPipeline(BaseModel):
    """Ayuntamiento de Madrid padrón: one row per census section and single year of age.

    Districts get the CM census 5-year age bands plus their total, so ratios over this
    population compare like with like. The count columns (nationality x sex) are only summed.
    """

    model_config = ConfigDict(extra="forbid")

    kind: Literal["madrid_padron"]
    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    resource_role: str = "primary"
    csv: CsvFormat = Field(default_factory=CsvFormat)
    metric_id: str = Field(pattern=METRIC_ID_PATTERN)
    municipio_ine: str = Field(pattern=r"^28\d{3}$")
    district_column: str
    district_name_column: str | None = None
    age_column: str
    count_columns: list[str] = Field(min_length=1)
    period_column: str
    expected_districts: int = Field(gt=0)
    # Its municipio total (every dimension 'total') is compared with the padrón total; warning only.
    census_metric_id: str | None = Field(default=None, pattern=METRIC_ID_PATTERN)

    def metric_ids(self) -> list[str]:
        return [self.metric_id]


class MadridDistrictPanelPipeline(BaseModel):
    """Ayuntamiento de Madrid district panel: one row per indicator, territory and panel year.

    Only the declared indicators are kept, at district level: barrio rows and the city row are
    outside the scope; every panel year is kept (each one carries its own reference date).
    """

    model_config = ConfigDict(extra="forbid")

    kind: Literal["madrid_district_panel"]
    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    resource_role: str = "primary"
    csv: CsvFormat = Field(default_factory=lambda: CsvFormat(decimal=","))
    municipio_ine: str = Field(pattern=r"^28\d{3}$")
    indicators: dict[str, Annotated[str, Field(pattern=METRIC_ID_PATTERN)]] = Field(min_length=1)
    indicator_column: str = "indicador_completo"
    district_column: str = "cod_distrito"
    district_name_column: str | None = "distrito"
    barrio_column: str = "cod_barrio"
    period_column: str = "fecha_indicador"  # DD/MM/YYYY
    value_column: str = "valor_indicador"
    unit_column: str | None = "unidad_indicador"
    expected_districts: int = Field(gt=0)
    missing_markers: list[str] = Field(default_factory=lambda: list(DEFAULT_MISSING_MARKERS))

    def metric_ids(self) -> list[str]:
        return sorted(set(self.indicators.values()))


def _template_columns(template: str | None) -> list[str]:
    if not template:
        return []
    return [field for _, field, _, _ in Formatter().parse(template) if field]


class DirectoryLink(BaseModel):
    """A register's places are matched against an official directory to take its name and
    capacity (D-218). Only the declared subcategories are matched."""

    model_config = ConfigDict(extra="forbid")

    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    # register subcategory -> the directory's kind for it; the postcode-only rule needs it
    kinds: dict[str, str] = Field(min_length=1)
    # register subcategory -> words before the directory name when it is a bare place name
    # (primary care: «ABRANTES» -> «Centro de salud Abrantes»); absent -> the name as published
    name_prefix: dict[str, str] = Field(default_factory=dict[str, str])

    @model_validator(mode="after")
    def _prefixes_name_matched_subcategories(self) -> Self:
        unknown = sorted(set(self.name_prefix) - set(self.kinds))
        if unknown:
            msg = f"{self.dataset_id}: name_prefix for subcategories it does not match: {unknown}"
            raise ValueError(msg)
        return self


class FacilityDirectoryPipeline(BaseModel):
    """An official directory of facilities (one XLSX sheet) kept in Silver only (D-218).

    It never creates places: the register's own pipeline matches its places against the
    directory (entity resolution with a declared method) to take the institutional name and the
    published capacity. Contact columns (phone, email) are never read.
    """

    model_config = ConfigDict(extra="forbid")

    kind: Literal["facility_directory"]
    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    resource_role: str = "primary"
    sheet: str
    id_column: str
    name_column: str
    address_column: str
    postal_code_column: str
    kind_column: str
    dependency_column: str | None = None
    capacity_column: str | None = None
    capacity_unit: str | None = None
    # Only rows of the region: e.g. «Cód. Provincia» in ["28"]
    scope_column: str
    scope_values: list[str] = Field(min_length=1)
    min_rows: int = Field(gt=0, description="fewer rows in scope -> the sheet changed or is cut")
    max_rows: int = Field(gt=0)

    @model_validator(mode="after")
    def _capacity_has_a_unit(self) -> Self:
        if (self.capacity_column is None) != (self.capacity_unit is None):
            msg = f"{self.dataset_id}: declare capacity_column and capacity_unit together"
            raise ValueError(msg)
        if self.max_rows < self.min_rows:
            msg = f"{self.dataset_id}: max_rows must be >= min_rows"
            raise ValueError(msg)
        return self

    def kept_columns(self) -> list[str]:
        optional = [self.dependency_column, self.capacity_column]
        return [
            self.id_column,
            self.name_column,
            self.address_column,
            self.postal_code_column,
            self.kind_column,
            self.scope_column,
            *[c for c in optional if c],
        ]

    def metric_ids(self) -> list[str]:
        return []


class PointsPipeline(BaseModel):
    """Point facilities with projected coordinates -> place_master."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["points_csv"]
    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    resource_role: str = "primary"
    csv: CsvFormat = Field(default_factory=CsvFormat)
    category: PlaceCategory
    id_column: str
    name_column: str | None = None  # None -> name_template or "<subcategory> (<municipio>)"
    # e.g. "Farmacia · {VIA} {NUMERO}" when the register has no name column; fields are columns
    name_template: str | None = None
    subcategory_column: str | None = None
    subcategory_value: str | None = None  # registers with a single kind of place
    # Only rows whose column values are in the allowlist enter the product (all filters apply).
    row_filters: dict[str, list[str]] = Field(default_factory=dict[str, list[str]])
    x_column: str
    y_column: str
    crs: str = Field(default="EPSG:25830", pattern=r"^EPSG:\d{4,5}$")
    municipio_code_column: str | None = None
    # Declared location, to repair missing or incoherent coordinates (D-216): the municipio by
    # name when the register has no INE code, and the Madrid district code ("01".."21").
    municipio_name_column: str | None = None
    district_code_column: str | None = None
    # Postal address for the official geocoder, e.g. "{VIA} {NUMERO}, {CP} {MUNICIPIO}".
    address_template: str | None = None
    address_number_column: str | None = None  # house number: no number -> never geocoded
    address_street_column: str | None = None  # the geocoder must match this street
    status_column: str | None = None
    active_values: list[str] = Field(default_factory=list[str])
    group_by_id: bool = False
    grouped_list_columns: list[str] = Field(default_factory=list[str])
    attribute_columns: list[str] = Field(default_factory=list[str])  # explicit allowlist (no PII)
    # Postal code of the address: the directories match on it (D-218)
    postal_code_column: str | None = None
    # Who runs the place, as the register words it -> attributes.dependency publica|privada
    dependency_column: str | None = None
    directories: list[DirectoryLink] = Field(default_factory=list[DirectoryLink])

    @model_validator(mode="after")
    def _directories_need_an_address(self) -> Self:
        if not self.directories:
            return self
        if not (self.postal_code_column and self.address_street_column):
            msg = (
                f"{self.dataset_id}: directories need postal_code_column and address_street_column"
            )
            raise ValueError(msg)
        matched = [s for link in self.directories for s in link.kinds]
        if len(matched) != len(set(matched)):
            msg = f"{self.dataset_id}: a subcategory is matched against two directories"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _status_needs_values(self) -> Self:
        if self.status_column and not self.active_values:
            msg = f"{self.dataset_id}: status_column requires active_values"
            raise ValueError(msg)
        if (self.subcategory_column is None) == (self.subcategory_value is None):
            msg = (
                f"{self.dataset_id}: declare exactly one of subcategory_column or subcategory_value"
            )
            raise ValueError(msg)
        if self.name_column and self.name_template:
            msg = f"{self.dataset_id}: declare name_column or name_template, not both"
            raise ValueError(msg)
        return self

    def name_template_columns(self) -> list[str]:
        return _template_columns(self.name_template)

    def address_template_columns(self) -> list[str]:
        return _template_columns(self.address_template)

    def metric_ids(self) -> list[str]:
        return []


Weekday = Literal["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
CLOCK_PATTERN = r"^([01]\d|2[0-3]):[0-5]\d$"


class GtfsFeedPipeline(BaseModel):
    """Static GTFS feed -> one transport place per stop or parent station, with service levels.

    Service is measured on one reference day: the median (by active trips) of the feed's
    `reference_weekday` dates inside its own validity window, so the result never depends on
    the day the pipeline runs.
    """

    model_config = ConfigDict(extra="forbid")

    kind: Literal["gtfs_feed"]
    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    resource_role: str = "primary"
    mode: str = Field(pattern=r"^[a-z_]+$", description="place subcategory, e.g. metro, emt")
    reference_weekday: Weekday = "tuesday"
    peak_start: str = Field(default="07:00", pattern=CLOCK_PATTERN)
    peak_end: str = Field(default="09:00", pattern=CLOCK_PATTERN)
    expand_frequencies: bool = Field(
        default=True,
        description="False when frequencies.txt only annotates trips already listed one by one",
    )

    @model_validator(mode="after")
    def _peak_is_a_window(self) -> Self:
        if self.peak_end <= self.peak_start:
            msg = f"{self.dataset_id}: peak_end must be after peak_start"
            raise ValueError(msg)
        return self

    def metric_ids(self) -> list[str]:
        return []


class OsmWalkNetworkPipeline(BaseModel):
    """OpenStreetMap extract -> undirected walkable street graph, kept in Silver only.

    A way is walkable when its `highway` value is listed or it explicitly allows people on foot;
    `foot=no`, or `access=no/private` without a foot permission, removes it. One-way rules apply
    to vehicles, so the graph is undirected. Only indicators computed on it reach the database.
    """

    model_config = ConfigDict(extra="forbid")

    kind: Literal["osm_walk_network"]
    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    resource_role: str = "primary"
    walkable_highways: list[str] = Field(min_length=1)
    foot_allowed: list[str] = Field(default_factory=lambda: ["yes", "designated", "permissive"])
    access_denied: list[str] = Field(default_factory=lambda: ["no", "private"])
    min_total_km: float = Field(gt=0, description="below this the extract is truncated")
    min_main_component_share: float = Field(default=0.9, gt=0, le=1)

    def metric_ids(self) -> list[str]:
        return []


PipelineSpec = Annotated[
    CmStatTablePipeline
    | CmPostcodeConceptPipeline
    | MadridPadronPipeline
    | MadridDistrictPanelPipeline
    | PointsPipeline
    | GtfsFeedPipeline
    | OsmWalkNetworkPipeline
    | FacilityDirectoryPipeline,
    Field(discriminator="kind"),
]
