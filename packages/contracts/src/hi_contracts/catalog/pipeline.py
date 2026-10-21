"""Declarative pipeline specs: how a dataset's resource becomes Silver rows.

Pipelines live in data/catalog/pipelines/<dataset_id>.yaml. Code implements each `kind` once;
datasets only declare columns and mappings, so no dataset id or formula is hardcoded.
"""

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


class PointsPipeline(BaseModel):
    """Point facilities with projected coordinates -> place_master."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["points_csv"]
    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    resource_role: str = "primary"
    csv: CsvFormat = Field(default_factory=CsvFormat)
    category: PlaceCategory
    id_column: str
    name_column: str | None = None  # None -> "<subcategory> (<municipio>)"
    subcategory_column: str
    # Only rows whose column values are in the allowlist enter the product (all filters apply).
    row_filters: dict[str, list[str]] = Field(default_factory=dict[str, list[str]])
    x_column: str
    y_column: str
    crs: str = Field(default="EPSG:25830", pattern=r"^EPSG:\d{4,5}$")
    municipio_code_column: str | None = None
    status_column: str | None = None
    active_values: list[str] = Field(default_factory=list[str])
    group_by_id: bool = False
    grouped_list_columns: list[str] = Field(default_factory=list[str])
    attribute_columns: list[str] = Field(default_factory=list[str])  # explicit allowlist (no PII)

    @model_validator(mode="after")
    def _status_needs_values(self) -> Self:
        if self.status_column and not self.active_values:
            msg = f"{self.dataset_id}: status_column requires active_values"
            raise ValueError(msg)
        return self

    def metric_ids(self) -> list[str]:
        return []


PipelineSpec = Annotated[
    CmStatTablePipeline | CmPostcodeConceptPipeline | PointsPipeline, Field(discriminator="kind")
]
