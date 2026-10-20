from shapely.geometry import GeometryCollection, LineString, MultiPolygon, Point, Polygon

from hi_domain.geo.geometry import to_multipolygon


def test_bowtie_is_repaired_into_valid_multipolygon() -> None:
    bowtie = Polygon([(0, 0), (2, 2), (2, 0), (0, 2)])
    assert not bowtie.is_valid
    fixed = to_multipolygon(bowtie)
    assert isinstance(fixed, MultiPolygon)
    assert fixed.is_valid
    assert fixed.area > 0


def test_non_polygonal_parts_are_dropped() -> None:
    mixed = GeometryCollection([Polygon([(0, 0), (1, 0), (1, 1)]), LineString([(0, 0), (5, 5)])])
    fixed = to_multipolygon(mixed)
    assert isinstance(fixed, MultiPolygon)
    assert len(fixed.geoms) == 1


def test_empty_or_point_returns_none() -> None:
    assert to_multipolygon(None) is None
    assert to_multipolygon(Polygon()) is None
    assert to_multipolygon(Point(0, 0)) is None
