from hypothesis import given
from hypothesis import strategies as st

from hi_domain.geo.bounds import COMUNIDAD_MADRID_BBOX, is_within_madrid, looks_lat_lon_swapped

GOLDEN_POINTS = {
    "sol": (-3.7035, 40.4169),
    "aranjuez": (-3.6025, 40.0333),
    "alcala_de_henares": (-3.3643, 40.4818),
}

madrid_lon = st.floats(COMUNIDAD_MADRID_BBOX.min_lon, COMUNIDAD_MADRID_BBOX.max_lon)
madrid_lat = st.floats(COMUNIDAD_MADRID_BBOX.min_lat, COMUNIDAD_MADRID_BBOX.max_lat)


def test_golden_points_inside_madrid() -> None:
    for lon, lat in GOLDEN_POINTS.values():
        assert is_within_madrid(lon, lat)


def test_barcelona_outside_madrid() -> None:
    assert not is_within_madrid(2.1734, 41.3851)


def test_swapped_coordinates_detected() -> None:
    lon, lat = GOLDEN_POINTS["sol"]
    assert looks_lat_lon_swapped(lat, lon)
    assert not looks_lat_lon_swapped(lon, lat)


@given(madrid_lon, madrid_lat)
def test_points_in_bbox_are_never_flagged_as_swapped(lon: float, lat: float) -> None:
    assert is_within_madrid(lon, lat)
    assert not looks_lat_lon_swapped(lon, lat)
