"""Coverage bounds for Comunidad de Madrid and lat/lon sanity checks."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BBox:
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float

    def contains(self, lon: float, lat: float) -> bool:
        return self.min_lon <= lon <= self.max_lon and self.min_lat <= lat <= self.max_lat

    def contains_bbox(self, other: "BBox") -> bool:
        return self.contains(other.min_lon, other.min_lat) and self.contains(
            other.max_lon, other.max_lat
        )


# Comunidad de Madrid envelope (EPSG:4326) padded ~1 km over the official limits.
COMUNIDAD_MADRID_BBOX = BBox(min_lon=-4.58, min_lat=39.88, max_lon=-3.05, max_lat=41.17)


def is_within_madrid(lon: float, lat: float) -> bool:
    return COMUNIDAD_MADRID_BBOX.contains(lon, lat)


def looks_lat_lon_swapped(x: float, y: float) -> bool:
    """True when (x, y) only fits Madrid if read as (lat, lon)."""
    return not is_within_madrid(x, y) and is_within_madrid(y, x)
