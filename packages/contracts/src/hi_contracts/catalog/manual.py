"""Tables typed by hand from an official page that publishes no file (D-241: Plan Vive).

They live in data/catalog/manual/. Every entry quotes the page (`says`, its exact text), and the
contract rejects an entry whose name, figure or stage the quote does not contain: nothing is
typed from memory. An entry the page does not complete is not loaded; it is listed in
`excluded` with the reason, so it is never lost in silence.
"""

from datetime import date
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from hi_contracts.catalog.corrections import is_quoted

INE_MUNICIPIO = r"^28\d{3}$"
MADRID_DISTRICT = r"^28079\d{2}$"


def spanish_count(value: int) -> str:
    """How a Spanish page writes a whole number: 1616 -> «1.616»."""
    return f"{value:,}".replace(",", ".")


class DistrictPlacement(BaseModel):
    """A Madrid district the entry is in, with the official text that places it there."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(pattern=MADRID_DISTRICT)
    says: str = Field(min_length=3)


class PlacementSource(BaseModel):
    """Where the districts of an entry come from, when the page does not name them."""

    model_config = ConfigDict(extra="forbid")

    publisher: str = Field(min_length=3)
    url: HttpUrl
    consulted: date


class ZoneItem(BaseModel):
    """One entry of the page: what it counts in a municipio, where, and at which stage."""

    model_config = ConfigDict(extra="forbid")

    municipio_ine: str = Field(pattern=INE_MUNICIPIO)
    municipio: str = Field(min_length=2, description="as the page writes it")
    item: str = Field(pattern=r"^[a-z0-9_]+$")
    name: str = Field(min_length=2, description="where it is, as the page writes it")
    value: int = Field(gt=0)
    stage: str = Field(min_length=3, description="as the page writes it («Construcción»)")
    says: str = Field(min_length=10, description="the page's text for this entry")
    districts: list[DistrictPlacement] = Field(default_factory=list[DistrictPlacement])
    district_source: PlacementSource | None = None
    note: str | None = Field(default=None, min_length=10, description="shown with the entry")

    @model_validator(mode="after")
    def _the_page_says_it(self) -> Self:
        for label, text in (
            ("municipio", self.municipio),
            ("name", self.name),
            ("stage", self.stage),
            ("value", spanish_count(self.value)),
        ):
            if not is_quoted(text, self.says):
                msg = f"{self.item}: the quoted text does not say its {label} ({text!r})"
                raise ValueError(msg)
        if self.districts and (self.district_source is None or self.municipio_ine != "28079"):
            msg = f"{self.item}: districts are Madrid's and need their district_source"
            raise ValueError(msg)
        return self


class ExcludedItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    municipio: str = Field(min_length=2)
    reason: str = Field(min_length=10)


class ZoneItemsTable(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=3)
    publisher: str = Field(min_length=3)
    url: HttpUrl
    consulted: date
    unit: str = Field(min_length=2)
    items: list[ZoneItem] = Field(min_length=1)
    excluded: list[ExcludedItem] = Field(default_factory=list[ExcludedItem])

    @model_validator(mode="after")
    def _one_entry_per_item(self) -> Self:
        ids = [i.item for i in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("one entry per item")
        return self
