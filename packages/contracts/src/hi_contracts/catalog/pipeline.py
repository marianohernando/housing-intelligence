"""Declarative pipeline specs: how a dataset's resource becomes Silver rows.

Pipelines live in data/catalog/pipelines/<dataset_id>.yaml. Code implements each `kind` once;
datasets only declare columns and mappings, so no dataset id or formula is hardcoded.
"""

import re
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


class CmMunicipioConceptPipeline(BaseModel):
    """Instituto de Estadística tables without a territory code (D-235): the municipio comes
    by name and what the row counts is in a free-text 'Concepto' column.

    Only the rows whose concept starts with one of the `concepts` are read, each with its value
    of `dimension` (e.g. the total and the cybercrime of the offences, so a feature can leave
    the second out). The source writes the names by hand (double spaces, «Rozas de Madrid»),
    so `municipios` maps each spelling to its INE code after collapsing the whitespace; a name
    that is not there goes to quarantine and fails the run, never dropped in silence. Rows
    whose status is in `excluded_statuses` (e.g. «Provisional») are left out and counted.
    """

    model_config = ConfigDict(extra="forbid")

    kind: Literal["cm_municipio_concept"]
    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    resource_role: str = "primary"
    csv: CsvFormat = Field(default_factory=CsvFormat)
    metric_id: str = Field(pattern=METRIC_ID_PATTERN)
    period_column: str = "Año"
    value_column: str = "Valor"
    unit_column: str | None = "Unidad"
    concept_column: str = "Concepto"
    dimension: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    concepts: dict[str, Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]*$")]] = Field(
        min_length=1, description="concept prefix -> value of `dimension` for its rows"
    )
    municipio_column: str = "Municipio"
    municipios: dict[str, Annotated[str, Field(pattern=r"^28\d{3}$")]] = Field(min_length=1)
    status_column: str | None = "Estado dato"
    excluded_statuses: list[str] = Field(default_factory=list[str])
    expected_municipios: int = Field(gt=0, description="municipios the table publishes")
    missing_markers: list[str] = Field(default_factory=lambda: list(DEFAULT_MISSING_MARKERS))

    @model_validator(mode="after")
    def _names_cover_the_expected_municipios(self) -> Self:
        codes = set(self.municipios.values())
        if len(codes) != self.expected_municipios:
            msg = (
                f"{self.dataset_id}: `municipios` names {len(codes)} municipios, "
                f"expected_municipios says {self.expected_municipios}"
            )
            raise ValueError(msg)
        if self.excluded_statuses and self.status_column is None:
            msg = f"{self.dataset_id}: excluded_statuses need a status_column"
            raise ValueError(msg)
        nested = [
            (a, b) for a in self.concepts for b in self.concepts if a != b and b.startswith(a)
        ]
        if nested:
            msg = f"{self.dataset_id}: a concept prefix starts another one: {nested[0]}"
            raise ValueError(msg)
        return self

    def concept_value(self, concept: str) -> str | None:
        """The `dimension` value of a row by its concept, or None when it is not read."""
        return next((v for prefix, v in self.concepts.items() if concept.startswith(prefix)), None)

    def metric_ids(self) -> list[str]:
        return [self.metric_id]


class AeatRentComparisonPipeline(BaseModel):
    """Agencia Tributaria, «Estadística de viviendas declaradas en IRPF»: the HTML table that
    compares the mean monthly rent and the mean m² of all leases with those of the leases
    signed in the year («nuevos contratos»), by municipio or by postcode (D-228).

    Rows look like «Alcalá de Henares-28005» (municipio) or «28001-Salamanca- Goya» (postcode);
    the first two numeric columns are the rents (all, new) and the next two the m² (all, new).
    Only the rows of the province in `province_prefix` are kept; the region's own row
    («Madrid, Comunidad de») becomes the ccaa observation.
    """

    model_config = ConfigDict(extra="forbid")

    kind: Literal["aeat_rent_comparison"]
    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    resource_role: str = "primary"
    level: Literal["municipio", "codigo_postal"]
    rent_metric_id: str = Field(pattern=METRIC_ID_PATTERN)
    area_metric_id: str = Field(pattern=METRIC_ID_PATTERN)
    province_prefix: str = Field(pattern=r"^\d{2}$")
    region_label: str | None = Field(
        default=None,
        description="Row of the region, e.g. «Madrid, Comunidad de» (municipio table only: in "
        "the postcode table it only adds up the municipios that have postcodes)",
    )
    contract_dim: str = "contratos"
    min_rows: int = Field(gt=0, description="fewer rows in scope -> the table changed or is cut")
    max_rows: int = Field(gt=0)

    @model_validator(mode="after")
    def _bounds(self) -> Self:
        if self.max_rows < self.min_rows:
            msg = f"{self.dataset_id}: max_rows must be >= min_rows"
            raise ValueError(msg)
        return self

    def metric_ids(self) -> list[str]:
        return [self.rent_metric_id, self.area_metric_id]


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

    Only the declared indicators are kept, at district level. A barrio row is kept, at barrio
    level and with the barrio's name, only for the indicators in `barrio_indicators` (D-232:
    the official barrio names come from here); the city row only for those in
    `city_indicators` (then it is the municipio, the value to compare the districts with).
    Every reference date is kept once: when two panel editions carry the same date, the latest
    edition wins (a revision).
    """

    model_config = ConfigDict(extra="forbid")

    kind: Literal["madrid_district_panel"]
    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    resource_role: str = "primary"
    csv: CsvFormat = Field(default_factory=lambda: CsvFormat(decimal=","))
    municipio_ine: str = Field(pattern=r"^28\d{3}$")
    indicators: dict[str, Annotated[str, Field(pattern=METRIC_ID_PATTERN)]] = Field(min_length=1)
    city_indicators: list[str] = Field(default_factory=list[str])
    barrio_indicators: list[str] = Field(default_factory=list[str])
    indicator_column: str = "indicador_completo"
    edition_column: str = "Periodo panel"
    district_column: str = "cod_distrito"
    district_name_column: str | None = "distrito"
    barrio_column: str = "cod_barrio"  # district + barrio digit: '11' (Palacio), '201' (Simancas)
    barrio_name_column: str = "barrio"
    period_column: str = "fecha_indicador"  # DD/MM/YYYY
    value_column: str = "valor_indicador"
    unit_column: str | None = "unidad_indicador"
    expected_districts: int = Field(gt=0)
    expected_barrios: int | None = Field(default=None, gt=0)
    missing_markers: list[str] = Field(default_factory=lambda: list(DEFAULT_MISSING_MARKERS))

    @model_validator(mode="after")
    def _city_and_barrio_indicators_are_declared(self) -> Self:
        for name, chosen in (
            ("city_indicators", self.city_indicators),
            ("barrio_indicators", self.barrio_indicators),
        ):
            unknown = sorted(set(chosen) - set(self.indicators))
            if unknown:
                msg = f"{name} must be declared indicators: {unknown}"
                raise ValueError(msg)
        if self.barrio_indicators and self.expected_barrios is None:
            msg = "barrio_indicators need expected_barrios: a panel short of barrios must fail"
            raise ValueError(msg)
        return self

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
    # Lets a register match an entry whose postal code differs from its own (D-218 §9)
    municipality_column: str | None = None
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
        optional = [self.dependency_column, self.capacity_column, self.municipality_column]
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


class StationTopologyPipeline(BaseModel):
    """A network topology layer of the CRTM (one station per row, ArcGIS JSON) kept in Silver
    only (DATA-019, D-223). It never creates places: a GTFS feed that declares it takes from it
    how accessible each of its stations is, matched by an official code.

    `step_free` reads the published accessibility grade: every grade the layer may carry is
    declared with its reading (yes, partial or no); a grade that is not declared is quarantined.
    """

    model_config = ConfigDict(extra="forbid")

    kind: Literal["station_topology"]
    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    resource_role: str = "primary"
    id_field: str
    operator_code_field: str
    name_field: str
    grade_field: str
    step_free: dict[str, Literal["yes", "partial", "no"]] = Field(min_length=1)
    min_rows: int = Field(gt=0, description="fewer stations -> the layer changed or is cut")
    max_rows: int = Field(gt=0)

    @model_validator(mode="after")
    def _rows_are_a_range(self) -> Self:
        if self.max_rows < self.min_rows:
            msg = f"{self.dataset_id}: max_rows must be >= min_rows"
            raise ValueError(msg)
        return self

    def metric_ids(self) -> list[str]:
        return []


class StationAccessibilityLink(BaseModel):
    """A GTFS feed's stations take their accessibility from a station topology (D-223). The key
    of a stop is group 1 of `stop_id_pattern`, compared with the topology's `match` column."""

    model_config = ConfigDict(extra="forbid")

    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    match: Literal["station_id", "operator_code"]
    stop_id_pattern: str

    @model_validator(mode="after")
    def _pattern_has_one_group(self) -> Self:
        try:
            groups = re.compile(self.stop_id_pattern).groups
        except re.error as exc:
            msg = f"{self.dataset_id}: invalid stop_id_pattern: {exc}"
            raise ValueError(msg) from exc
        if groups != 1:
            msg = f"{self.dataset_id}: stop_id_pattern needs exactly one group, it has {groups}"
            raise ValueError(msg)
        return self


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
    station_accessibility: StationAccessibilityLink | None = None

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


class OsmParksPipeline(BaseModel):
    """OpenStreetMap extract -> public parks as places (DATA-018, D-222).

    A park is an area tagged with one of `leisure` that is not closed to the public and has at
    least `min_area_ha`. Each becomes a place (a point inside it) that also keeps the points of
    its edge every `edge_step_m` metres: walking access is measured to the edge, not the centre.
    """

    model_config = ConfigDict(extra="forbid")

    kind: Literal["osm_parks"]
    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    resource_role: str = "primary"
    leisure: list[str] = Field(default_factory=lambda: ["park"], min_length=1)
    access_denied: list[str] = Field(default_factory=lambda: ["no", "private", "customers"])
    min_area_ha: float = Field(gt=0)
    edge_step_m: float = Field(default=50.0, gt=0)
    subcategory: str = "Parque"
    min_parks: int = Field(gt=0, description="below this the extract is truncated")
    max_parks: int = Field(gt=0)

    def metric_ids(self) -> list[str]:
        return []


PipelineSpec = Annotated[
    CmStatTablePipeline
    | CmPostcodeConceptPipeline
    | CmMunicipioConceptPipeline
    | AeatRentComparisonPipeline
    | MadridPadronPipeline
    | MadridDistrictPanelPipeline
    | PointsPipeline
    | GtfsFeedPipeline
    | OsmWalkNetworkPipeline
    | OsmParksPipeline
    | FacilityDirectoryPipeline
    | StationTopologyPipeline,
    Field(discriminator="kind"),
]
