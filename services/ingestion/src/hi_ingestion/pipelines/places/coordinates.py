"""Repair of missing or incoherent coordinates against the declared location (D-216).

A register row declares where it is twice: its coordinates and its address (municipio, and in
Madrid the district). When they disagree, or the coordinates are missing, the address is
geocoded with the official geocoder and accepted only at portal level inside the declared
municipio. Pure logic: the locator and the geocoder are injected, so tests need no network.
"""

import unicodedata
from collections.abc import Callable
from dataclasses import dataclass

SOURCE = "source"
GEOCODED = "geocoded"
# An address point is not the register's own survey: 0.8 at the exact portal; 0.6 at the
# nearest portal the geocoder knows on the same street, up to 10 numbers away (about 5 plots,
# 50-100 m in a town, i.e. one or two minutes on foot). Farther, or no number, is rejected.
EXACT_PORTAL_CONFIDENCE = 0.8
NEAR_PORTAL_CONFIDENCE = 0.6
MAX_PORTAL_GAP = 10


@dataclass(frozen=True)
class Located:
    """Where a point falls in the canonical geography."""

    municipio: str | None  # INE code, e.g. 28079
    district: str | None  # Madrid district admin code 2807901..2807921, else None


@dataclass(frozen=True)
class GeocodeHit:
    lon: float
    lat: float
    municipio: str  # INE code the geocoder reports
    match: str  # "portal" is the only accepted level
    portal: int | None = None  # the house number the point belongs to


@dataclass(frozen=True)
class Declared:
    municipio: str | None
    district: str | None
    address: str | None
    number: int | None = None  # house number in the address; None -> never geocoded


@dataclass(frozen=True)
class Resolution:
    lon: float | None
    lat: float | None
    origin: str  # SOURCE or GEOCODED; meaningless when quarantined
    quarantine_reason: str | None = None
    note: str | None = None  # kept as-is but worth reporting (e.g. a district label)
    confidence: float = 1.0

    @property
    def accepted(self) -> bool:
        return self.lon is not None and self.lat is not None


Locate = Callable[[float, float], Located]
Geocode = Callable[[str], GeocodeHit | None]


def _usable(hit: GeocodeHit | None, declared: Declared) -> GeocodeHit | None:
    if hit is None or hit.match != "portal" or hit.portal is None or declared.number is None:
        return None
    if declared.municipio and hit.municipio != declared.municipio:
        return None
    return hit if abs(hit.portal - declared.number) <= MAX_PORTAL_GAP else None


def _geocoded(hit: GeocodeHit, declared: Declared, note: str) -> Resolution:
    exact = hit.portal == declared.number
    confidence = EXACT_PORTAL_CONFIDENCE if exact else NEAR_PORTAL_CONFIDENCE
    where = "" if exact else f" (nearest portal {hit.portal} for number {declared.number})"
    return Resolution(hit.lon, hit.lat, GEOCODED, note=note + where, confidence=confidence)


def _missing(declared: Declared, geocode: Geocode) -> Resolution:
    hit = _usable(geocode(declared.address), declared) if declared.address else None
    if hit is None:
        return Resolution(
            None, None, SOURCE, "missing coordinates; address not found at portal level"
        )
    return _geocoded(hit, declared, "coordinates missing in the source")


def _wrong_municipio(
    declared: Declared, located: Located, lonlat: tuple[float, float], geocode: Geocode
) -> Resolution:
    hit = _usable(geocode(declared.address), declared) if declared.address else None
    if hit is None:
        reason = (
            f"coordinates in municipio {located.municipio}, register says {declared.municipio}; "
            "address not found at portal level"
        )
        return Resolution(None, None, SOURCE, reason)
    note = f"source coordinates fell in municipio {located.municipio} {lonlat}"
    return _geocoded(hit, declared, note)


def _wrong_district(
    declared: Declared,
    located: Located,
    lonlat: tuple[float, float],
    locate: Locate,
    geocode: Geocode,
) -> Resolution:
    hit = _usable(geocode(declared.address), declared) if declared.address else None
    if hit is not None and locate(hit.lon, hit.lat).district == declared.district:
        return _geocoded(hit, declared, f"source coordinates fell in district {located.district}")
    evidence = (
        "the address is not found at portal level"
        if hit is None
        else "the address does not contradict the coordinates"
    )
    note = (
        f"register says district {declared.district}, the official geography puts it in "
        f"{located.district}; {evidence}, kept"
    )
    return Resolution(lonlat[0], lonlat[1], SOURCE, note=note)


def resolve(
    lonlat: tuple[float, float] | None, declared: Declared, locate: Locate, geocode: Geocode
) -> Resolution:
    """Source coordinates when coherent; the geocoded address when it fixes them; else reject.

    Coordinates outside the declared municipio are wrong, so they are replaced or quarantined.
    A different Madrid district is weaker evidence (labels can follow administrative areas), so
    the coordinates are only replaced when the address lands in the declared district.
    """
    if lonlat is None:
        return _missing(declared, geocode)
    located = locate(*lonlat)
    if declared.municipio and located.municipio and located.municipio != declared.municipio:
        return _wrong_municipio(declared, located, lonlat, geocode)
    if declared.district and located.district and located.district != declared.district:
        return _wrong_district(declared, located, lonlat, locate, geocode)
    return Resolution(lonlat[0], lonlat[1], SOURCE)


def house_number(raw: str) -> int | None:
    """«37», «83-85», «5 BIS» -> first number; «S/N» or empty -> None."""
    digits = ""
    for char in raw.strip():
        if char.isdigit():
            digits += char
        elif digits:
            break
    return int(digits) if digits else None


def fold_name(name: str) -> str:
    """«Álamo (El)», «El Álamo» and «EL ALAMO» -> «el alamo»."""
    text = unicodedata.normalize("NFKD", name.strip().casefold())
    text = "".join(c for c in text if not unicodedata.combining(c))
    if text.endswith(")") and " (" in text:
        base, article = text[:-1].rsplit(" (", 1)
        text = f"{article} {base}"
    return " ".join(text.replace("-", " ").split())
