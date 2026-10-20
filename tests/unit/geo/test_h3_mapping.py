import h3
from hypothesis import given, settings
from hypothesis import strategies as st
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

from hi_domain.geo.h3_mapping import cell_centroid, cell_polygon, cells_for_polygon

SOL = (-3.7035, 40.4169)


def test_cell_polygon_contains_its_centroid() -> None:
    cell = h3.latlng_to_cell(SOL[1], SOL[0], 9)
    poly = cell_polygon(cell)
    assert poly.is_valid
    lng, lat = cell_centroid(cell)
    assert poly.contains(Polygon.from_bounds(lng - 1e-6, lat - 1e-6, lng + 1e-6, lat + 1e-6))


def test_overlap_is_superset_of_center_and_full() -> None:
    square = box(-3.71, 40.41, -3.70, 40.42)
    center = cells_for_polygon(square, 9, "center")
    overlap = cells_for_polygon(square, 9, "overlap")
    full = cells_for_polygon(square, 9, "full")
    assert full <= center <= overlap


@settings(max_examples=25, deadline=None)
@given(
    st.floats(-4.4, -3.2),
    st.floats(40.0, 41.0),
    st.floats(0.002, 0.02),
)
def test_overlap_cells_fully_cover_polygon(lon: float, lat: float, size: float) -> None:
    square = box(lon, lat, lon + size, lat + size)
    cells = cells_for_polygon(square, 9, "overlap")
    assert all(h3.get_resolution(c) == 9 for c in cells)
    covered = unary_union([cell_polygon(c) for c in cells])
    assert square.difference(covered).area <= square.area * 1e-6
