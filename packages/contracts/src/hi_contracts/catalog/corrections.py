"""Versioned corrections to registered places, each backed by an official source (D-218 §10).

A correction never invents a value: it says which record, what to use instead, why, and where an
official source publishes it (URL, date consulted and the exact text). The ingestion applies it
with lineage: the file is an input of the register's run and the place says it was corrected.
"""

from datetime import date
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

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


class PlaceCorrection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    entity_id: str = Field(min_length=1)
    reason: str = Field(min_length=10)
    source: OfficialSource
    address: AddressFix | None = None
    directory: DirectoryFix | None = None

    @model_validator(mode="after")
    def _one_fix(self) -> Self:
        if (self.address is None) == (self.directory is None):
            msg = f"{self.dataset_id}/{self.entity_id}: give exactly one of address or directory"
            raise ValueError(msg)
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
