"""D-248: the construction cost per m² that the building permits declare, as a versioned table
(data/catalog/manual/pem_visados_cm.yaml), the manual-table pattern of D-241.

Unlike Plan Vive, nothing here is typed by hand: scripts/pem_visados_cm.py reads the official CSV
of the Comunidad de Madrid portal once and writes each year's budget, area and their ratio, with
the file's checksum. The contract checks the arithmetic (the ratio is the budget over the area),
so an edited figure no longer matches its pieces.
"""

from datetime import date
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

PermitKind = Literal["viviendas_en_bloque", "unifamiliar_adosada", "unifamiliar_aislada"]


class PermitFigures(BaseModel):
    """One kind of building in one year: budget of works (PEM), area to build and their ratio."""

    model_config = ConfigDict(extra="forbid")

    pem_miles_eur: int = Field(gt=0, description="thousands of euros")
    superficie_m2: int = Field(gt=0)
    pem_eur_m2: int = Field(gt=0)
    provisional: bool

    @model_validator(mode="after")
    def _ratio_of_its_pieces(self) -> Self:
        if self.pem_eur_m2 != round(self.pem_miles_eur * 1000 / self.superficie_m2):
            raise ValueError("pem_eur_m2 is the budget over the area, rounded to the euro")
        return self


class PermitYear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    year: int = Field(ge=1990, le=2100)
    viviendas_en_bloque: PermitFigures
    unifamiliar_adosada: PermitFigures
    unifamiliar_aislada: PermitFigures

    def figures(self) -> dict[str, PermitFigures]:
        return {
            "viviendas_en_bloque": self.viviendas_en_bloque,
            "unifamiliar_adosada": self.unifamiliar_adosada,
            "unifamiliar_aislada": self.unifamiliar_aislada,
        }


class PermitDefault(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: PermitKind
    year: int


class PermitBudgetTable(BaseModel):
    """«Visados, superficie y presupuesto de dirección de obra de edificios…» (CM portal),
    recomputed from its CSV on `consulted`."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=10)
    publisher: str = Field(min_length=3)
    source: str = Field(min_length=10, description="the statistic, as the portal names it")
    license: str = Field(min_length=3)
    portal_id: str = Field(min_length=1)
    url: HttpUrl
    csv_url: HttpUrl
    updated: str = Field(description="«Fecha Actualización» of the portal, as written")
    metadata_modified: date
    consulted: date
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$", description="of the CSV read")
    territory: str = Field(min_length=10)
    method: str = Field(min_length=10)
    default: PermitDefault
    series: list[PermitYear] = Field(min_length=1)

    @model_validator(mode="after")
    def _one_row_per_year_and_the_default_in_it(self) -> Self:
        years = [y.year for y in self.series]
        if len(years) != len(set(years)):
            raise ValueError("one entry per year")
        if self.default.year not in years:
            raise ValueError("the default year is one of the series")
        return self
