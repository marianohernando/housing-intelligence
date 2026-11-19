"""Versioned inputs a run reads instead of the network: tables typed by hand from an official
page that publishes no file (D-241: Plan Vive), the points of the Portal del Suelo parcels of
Madrid, read once from the CM map layer (D-246, `ParcelPointsTable`), and the pilot barrios of
the investor version, inside the M-40 of OpenStreetMap (D-247, `PilotZonesTable`).

They live in data/catalog/manual/. Every typed entry quotes the page (`says`, its exact text),
and the contract rejects an entry whose name, figure or stage the quote does not contain:
nothing is typed from memory. An entry the page does not complete is not loaded; it is listed
in `excluded` with the reason, so it is never lost in silence.
"""

import hashlib
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


# EPSG:25830 bounds of the Comunidad de Madrid, with a margin: a point outside is not one of
# its parcels (a swapped or degree-valued coordinate).
REGION_X = (350_000, 510_000)
REGION_Y = (4_400_000, 4_570_000)


class ParcelPoint(BaseModel):
    """A point inside one parcel of the layer, in metres (EPSG:25830)."""

    model_config = ConfigDict(extra="forbid")

    ref: str = Field(pattern=r"^[0-9A-Z]{9}$", description="the portal's referencia_codigo")
    x: int = Field(ge=REGION_X[0], le=REGION_X[1])
    y: int = Field(ge=REGION_Y[0], le=REGION_Y[1])


class ParcelPointsTable(BaseModel):
    """D-246: where the parcels of a municipio are, read once from the CM's own map layer and
    versioned, so the run that places them in districts and barrios needs no network. The
    point is inside the parcel's polygon (not its centroid, which can fall outside it)."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=3)
    publisher: str = Field(min_length=3)
    url: HttpUrl
    layer: str = Field(min_length=3)
    crs: str = Field(pattern=r"^EPSG:25830$")
    consulted: date
    method: str = Field(min_length=10)
    municipio_ine: str = Field(pattern=INE_MUNICIPIO)
    points: list[ParcelPoint] = Field(min_length=1)

    @model_validator(mode="after")
    def _one_point_per_parcel(self) -> Self:
        refs = [p.ref for p in self.points]
        if len(refs) != len(set(refs)):
            raise ValueError("one point per parcel")
        return self


class PilotRing(BaseModel):
    """The closed polygon of a ring road, in metres (EPSG:25830), with the checksum of its
    coordinates: a hand edit that changes one vertex no longer matches it."""

    model_config = ConfigDict(extra="forbid")

    ways: int = Field(gt=0, description="OSM ways of the road that close the ring")
    area_km2: float = Field(gt=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    coordinates: list[tuple[int, int]] = Field(min_length=4)

    @model_validator(mode="after")
    def _closed_and_unchanged(self) -> Self:
        if self.coordinates[0] != self.coordinates[-1]:
            raise ValueError("the ring is closed: its last vertex is its first")
        for x, y in self.coordinates:
            if not (REGION_X[0] <= x <= REGION_X[1] and REGION_Y[0] <= y <= REGION_Y[1]):
                msg = f"vertex ({x}, {y}) is outside the Comunidad de Madrid"
                raise ValueError(msg)
        if ring_checksum(self.coordinates) != self.sha256:
            raise ValueError("the ring's coordinates do not match its sha256")
        return self


def ring_checksum(coordinates: list[tuple[int, int]]) -> str:
    """sha256 of the vertices as «x,y» lines: the same ring always gives the same checksum."""
    text = "\n".join(f"{x},{y}" for x, y in coordinates)
    return hashlib.sha256(text.encode()).hexdigest()


class PilotBarrio(BaseModel):
    """A barrio and where it is from the ring: `margin_m` is the distance from its centroid to
    the ring, positive inside and negative outside, and `area_inside_pct` the share of its
    surface inside. A barrio on the edge (`PilotZonesTable.on_edge`) carries the note of the
    person who reviewed it (`review`)."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(pattern=r"^28079\d{3}$")
    name: str = Field(min_length=2)
    distrito: str = Field(min_length=2)
    margin_m: int
    area_inside_pct: int = Field(ge=0, le=100)
    review: str | None = Field(default=None, min_length=10)


class PilotZonesTable(BaseModel):
    """D-247: the barrios of the pilot of the investor version, Madrid inside the M-40. A barrio
    is in when its centroid is inside the ring of the road (OpenStreetMap, ODbL), read once by
    scripts/m40_barrios.py and versioned with its query, the OSM timestamp and the ring's
    checksum. The barrios on the edge, in or out (a centroid nearer the ring than `edge_m`, or
    a barrio the ring crosses: between `crossing_pct` and 100 - `crossing_pct` % of it inside),
    are reviewed by hand: the contract rejects one without its note, so an edge barrio never
    enters or leaves in silence."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=3)
    publisher: str = Field(min_length=3)
    license: str = Field(min_length=3)
    url: HttpUrl
    query: str = Field(min_length=10, description="the Overpass query, as sent")
    osm_timestamp: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
    consulted: date
    crs: str = Field(pattern=r"^EPSG:25830$")
    method: str = Field(min_length=10)
    municipio_ine: str = Field(pattern=INE_MUNICIPIO)
    edge_m: int = Field(gt=0, description="a centroid nearer the ring than this is reviewed")
    crossing_pct: int = Field(ge=0, lt=50, description="a barrio the ring crosses is reviewed")
    ring: PilotRing
    barrios: list[PilotBarrio] = Field(min_length=1, description="inside: the pilot")
    reviewed_outside: list[PilotBarrio] = Field(
        default_factory=list[PilotBarrio], description="outside, on the edge: reviewed, not in"
    )
    outside: int = Field(ge=0, description="the other barrios of the municipio, off the edge")

    def on_edge(self, barrio: PilotBarrio) -> bool:
        crossed = self.crossing_pct < barrio.area_inside_pct < 100 - self.crossing_pct
        return abs(barrio.margin_m) < self.edge_m or crossed

    @model_validator(mode="after")
    def _sides_and_reviews(self) -> Self:
        codes = [b.code for b in [*self.barrios, *self.reviewed_outside]]
        if len(codes) != len(set(codes)):
            raise ValueError("one entry per barrio")
        if any(not c.startswith(self.municipio_ine) for c in codes):
            raise ValueError("every barrio is of the table's municipio")
        for barrio in self.barrios:
            if barrio.margin_m <= 0:
                msg = f"{barrio.code}: a pilot barrio has its centroid inside the ring"
                raise ValueError(msg)
        for barrio in self.reviewed_outside:
            if barrio.margin_m > 0 or not self.on_edge(barrio):
                msg = f"{barrio.code}: reviewed_outside lists the outside barrios on the edge"
                raise ValueError(msg)
        for barrio in [*self.barrios, *self.reviewed_outside]:
            if self.on_edge(barrio) and barrio.review is None:
                msg = f"{barrio.code} ({barrio.name}) is on the edge of the ring: review it"
                raise ValueError(msg)
        return self

    def codes(self) -> list[str]:
        return [b.code for b in self.barrios]
