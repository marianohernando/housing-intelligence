"""Versioned corrections to registered places, each backed by an official source (D-218 §10).

A correction never invents a value: it says which record, what to use instead, why, and where an
official source publishes it (URL, date consulted and the exact text). The ingestion applies it
with lineage: the file is an input of the register's run and the place says it was corrected.
A corrected name is the source's own text (D-221): only case and quotation marks may differ.
"""

import re
import unicodedata
from datetime import date
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator

from hi_contracts.catalog.dataset import DATASET_ID_PATTERN


class OfficialSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    publisher: str = Field(min_length=3)
    url: HttpUrl
    consulted: date
    says: str = Field(min_length=3, description="The text of the source the correction uses")


class AddressFix(BaseModel):
    """Address to geocode instead of the register's, when the register gives no usable one."""

    model_config = ConfigDict(extra="forbid")

    street: str = Field(min_length=2)
    number: str = Field(pattern=r"^\d+[A-Za-z]?$")


class DirectoryFix(BaseModel):
    """The directory entry that is this place, when no address rule can tell (D-218 §3)."""

    model_config = ConfigDict(extra="forbid")

    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    entry_id: str = Field(min_length=1)


_QUOTES = str.maketrans("", "", "\"'«»“”‘’")


def _as_said(text: str) -> str:
    """For comparing a name with its source: composed accents, without case, quotation marks
    or extra spaces."""
    return " ".join(unicodedata.normalize("NFC", text).translate(_QUOTES).split()).casefold()


def _says(name: str, says: str) -> bool:
    """The name is whole words of the source's text, in the same order."""
    return re.search(rf"(?<!\w){re.escape(_as_said(name))}(?!\w)", _as_said(says)) is not None


class PlaceCorrection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    entity_id: str = Field(min_length=1)
    reason: str = Field(min_length=10)
    source: OfficialSource
    address: AddressFix | None = None
    directory: DirectoryFix | None = None
    name: str | None = Field(
        default=None,
        min_length=3,
        description="The name to show, as the source writes it (tildes included, D-221)",
    )

    @field_validator("name")
    @classmethod
    def _composed(cls, name: str | None) -> str | None:
        return " ".join(unicodedata.normalize("NFC", name).split()) if name is not None else None

    @model_validator(mode="after")
    def _fixes(self) -> Self:
        key = f"{self.dataset_id}/{self.entity_id}"
        if self.address is not None and self.directory is not None:
            raise ValueError(f"{key}: give an address or a directory entry, not both")
        if self.address is None and self.directory is None and self.name is None:
            raise ValueError(f"{key}: nothing to correct")
        if self.name is not None and not _says(self.name, self.source.says):
            raise ValueError(f"{key}: the name must be the text the source says")
        return self


class PlaceCorrections(BaseModel):
    model_config = ConfigDict(extra="forbid")

    corrections: list[PlaceCorrection]

    @model_validator(mode="after")
    def _unique(self) -> Self:
        keys = [(c.dataset_id, c.entity_id) for c in self.corrections]
        if len(keys) != len(set(keys)):
            raise ValueError("one correction per record")
        return self

    def for_dataset(self, dataset_id: str) -> list[PlaceCorrection]:
        return [c for c in self.corrections if c.dataset_id == dataset_id]


class ParkInclusion(BaseModel):
    """An OSM area that OSM does not tag as a park but an official source lists as a public park
    (D-222 §5): the Casa de Campo is `landuse=forest`. Never from memory."""

    model_config = ConfigDict(extra="forbid")

    osm_id: str = Field(pattern=r"^(way|relation)/\d+$")
    reason: str = Field(min_length=10)
    source: OfficialSource


class ParkInclusions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    parks: list[ParkInclusion]

    @model_validator(mode="after")
    def _unique(self) -> Self:
        ids = [p.osm_id for p in self.parks]
        if len(ids) != len(set(ids)):
            raise ValueError("one inclusion per OSM area")
        return self
