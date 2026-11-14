"""NO2 of a zone from one monitoring station (D-237): its own first, otherwise the nearest of
its air quality zone, always naming the station; never 0 when there is none."""

import math
from datetime import date

import pandas as pd

from hi_features import air, methods
from hi_features.methods import STATION_COLUMNS

Y = date(2025, 1, 1)
SETTINGS = methods.StationSettings(min_capture=0.85, own_confidence=0.9, nearest_confidence=0.6)


def _stations() -> pd.DataFrame:
    """FIXTURE: made-up stations in projected metres. A has two, the one at (1000, 0) nearer to
    its centre; B has none; C's only station lacks hours; the urban one is in zone 3; F has a
    traffic station of its own, the nearest to B of zone 5."""
    rows = [
        ("S1", "Uno", "A", "5", 1000.0, 0.0, 10.0, 0.98, False),
        ("S2", "Dos", "A", "5", 5000.0, 0.0, 40.0, 0.98, False),
        ("S3", "Tres", "C", "5", 9000.0, 0.0, 99.0, 0.50, False),
        ("S4", "Urbana", "D", "3", 2100.0, 3000.0, 30.0, 0.97, False),
        ("S5", "Avenida", "F", "5", 2000.0, 2500.0, 35.0, 0.97, True),
    ]
    return pd.DataFrame(rows, columns=STATION_COLUMNS)


def _run() -> dict[str, dict[str, object]]:
    centres = {
        "A": (0.0, 0.0),
        "B": (2000.0, 3000.0),
        "C": (9000.0, 0.0),
        "D": (2000.0, 3000.0),
        "F": (2000.0, 2600.0),
    }
    air = {"A": "5", "B": "5", "C": "5", "D": "3", "E": "5", "F": "5"}
    frame = methods.nearest_station_value(
        _stations(), centres, ["A", "B", "C", "D", "E", "F"], air, Y, SETTINGS
    )
    return {str(r["territory_code"]): r for r in frame.to_dict("records")}  # pyright: ignore[reportUnknownVariableType]


def test_a_zone_with_stations_takes_its_own_nearest_one() -> None:
    a = _run()["A"]
    assert a["value"] == 10.0 and a["confidence"] == 0.9
    assert a["detail"] == {
        "station": "Uno",
        "station_code": "S1",
        "own": True,
        "distance_km": 1.0,
        "traffic": False,
    }


def test_without_one_it_takes_the_nearest_of_its_air_zone_not_the_nearest_of_all() -> None:
    """B is 100 m from the urban station of zone 3, but it is in zone 5; there, the traffic
    station of F is nearer, but a borrowed station is a background one first (R-08)."""
    b = _run()["B"]
    assert b["detail"]["station"] == "Uno" and b["detail"]["own"] is False  # type: ignore[index]
    assert b["value"] == 10.0 and b["confidence"] == 0.6
    assert b["detail"]["distance_km"] == round(math.hypot(1000, 3000) / 1000, 1)  # type: ignore[index]


def test_a_station_without_enough_valid_hours_does_not_count() -> None:
    c = _run()["C"]
    assert c["detail"]["station"] == "Dos" and c["value"] == 40.0  # type: ignore[index]


def test_a_zone_without_centre_is_unknown_never_zero() -> None:
    e = _run()["E"]
    assert math.isnan(float(e["value"])) and e["null_reason"] == "SOURCE_NO_COVERAGE"  # type: ignore[arg-type]


def test_a_zone_keeps_its_own_traffic_station_and_says_so() -> None:
    f = _run()["F"]
    assert f["detail"]["station"] == "Avenida" and f["detail"]["traffic"] is True  # type: ignore[index]
    assert f["detail"]["own"] is True  # type: ignore[index]


def test_a_traffic_station_is_told_by_the_type_its_network_publishes() -> None:
    keys = ["estacion_tipo_estacion", "nom_tipo"]
    assert air.is_traffic({"estacion_tipo_estacion": "Tráfico"}, keys)
    assert air.is_traffic({"nom_tipo": "Urbana tráfico"}, keys)
    for kind in ("Fondo", "Industrial", "Suburbana", "Urbana fondo"):
        assert not air.is_traffic({"nom_tipo": kind}, keys)
    assert not air.is_traffic(None, keys)
