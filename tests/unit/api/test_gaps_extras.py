"""Extra indicators of the per-zone list (GAP-001 F1), without a database."""

from typing import Any

from hi_api.services.gaps import extras_at, merged_versions, split_bound
from hi_contracts.catalog.enums import TerritoryLevel


def _feature(feature_id: str, row: str, role: str) -> dict[str, Any]:
    return {"feature_id": feature_id, "gap_row": {"row": row, "role": role}}


def _value(versions: dict[str, str], value: float | None = 1.0) -> dict[str, Any]:
    reason = None if value is not None else "no_coverage"
    return {"value": value, "null_reason": reason, "inputs": {"dataset_versions": versions}}


def test_split_bound_separates_roles_and_orders_extras_by_feature_id() -> None:
    primaries, extras = split_bound(
        [
            _feature("z_walk", "colegio", "extra"),
            _feature("colegios", "colegio", "primary"),
            _feature("a_walk", "colegio", "extra"),
            _feature("salud_walk", "centro_salud", "extra"),
        ]
    )
    assert list(primaries) == ["colegios"]
    assert [f["feature_id"] for f in extras["colegio"]] == ["a_walk", "z_walk"]
    assert [f["feature_id"] for f in extras["centro_salud"]] == ["salud_walk"]


def test_extras_at_keeps_unknown_values_and_leaves_out_the_ones_not_computed() -> None:
    walk, pct = _feature("walk", "colegio", "extra"), _feature("pct", "colegio", "extra")
    values = {
        ("walk", "distrito"): _value({"osm": "v1"}, value=None),  # computed, no data
        ("pct", "municipio"): _value({"osm": "v1"}),  # computed at another level only
    }
    extras = extras_at(TerritoryLevel.DISTRITO, [walk, pct], values)
    assert [e.feature["feature_id"] for e in extras] == ["walk"]
    assert extras[0].value["value"] is None
    assert extras[0].value["null_reason"] == "no_coverage"  # unknown, never 0


def test_merged_versions_adds_the_extras_and_the_zone_value_wins_a_clash() -> None:
    row = _value({"centros": "zone", "padron": "p1"})
    reference = _value({"centros": "region", "censo": "c1"})
    extra = _value({"centros": "walk", "osm": "o1"})
    assert merged_versions(row, reference, [extra]) == {
        "centros": "zone",
        "padron": "p1",
        "censo": "c1",
        "osm": "o1",
    }
    assert merged_versions(row, None, []) == {"centros": "zone", "padron": "p1"}
