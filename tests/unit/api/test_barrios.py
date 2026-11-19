"""The search inside a district (D-232): what a barrio says when it lacks data, and the trip it
borrows from its district. Pure parts of hi_api.services.barrios, no database."""

from hi_api.services.barrios import (
    DISTRICT_TRIP_CONFIDENCE,
    DISTRICT_TRIP_NOTE,
    RENT_MISSING,
    RENT_NOT_COMPUTED,
    barrio_warnings,
    borrowed_trips,
    rent_missing,
)
from hi_contracts.catalog.enums import NullReason, TerritoryLevel
from hi_contracts.public import IndicatorValue
from hi_domain.fit import Commute


def _rent(value: float | None, reason: NullReason | None = None) -> IndicatorValue:
    return IndicatorValue(
        feature_id="alquiler_m2_mensual",
        label="Alquiler",
        value=value,
        unit="EUR/m2/mes",
        confidence=0.6 if value is not None else 0.0,
        null_reason=reason,
        level=TerritoryLevel.BARRIO,
        datasets=["cm_alquiler_m2_codigo_postal_madrid"],
    )


def test_the_reason_for_no_rent_follows_the_null_reason_of_the_row() -> None:
    assert rent_missing(_rent(15.0)) is None
    assert rent_missing(None) == RENT_NOT_COMPUTED
    no_places = rent_missing(_rent(None, NullReason.SOURCE_NO_COVERAGE))
    assert no_places == RENT_MISSING[NullReason.SOURCE_NO_COVERAGE.value]
    assert "ningún colegio" in (no_places or "")
    unpublished = rent_missing(_rent(None, NullReason.SOURCE_MISSING))
    assert unpublished == RENT_MISSING[NullReason.SOURCE_MISSING.value]
    assert "no publica" in (unpublished or "")
    assert rent_missing(_rent(None, NullReason.STALE)) == "Sin datos de alquiler para este barrio"


def test_a_barrio_keeps_its_own_trip_and_borrows_only_what_it_lacks() -> None:
    own, district = Commute(30.0, 0.7), Commute(40.0, 0.6)
    by_zone = {
        0: {"BAR": own, "DIS": district},
        1: {"DIS": district},
        2: {"BAR": Commute(None, 0.5), "DIS": district},  # «no trip by 9:00» is the barrio's
        3: {},
    }
    trips, borrowed = borrowed_trips(by_zone, "BAR", "DIS")
    assert borrowed
    assert trips[0] == own
    assert trips[1] == Commute(40.0, 0.6 * DISTRICT_TRIP_CONFIDENCE, DISTRICT_TRIP_NOTE)
    assert trips[2].minutes is None and trips[2].note is None
    assert 3 not in trips  # nowhere to borrow from: the straight line, as in /search


def test_an_empty_or_unfed_district_never_answers_silently() -> None:
    assert any("no barrio of this district" in w for w in barrio_warnings(0, False, 0))
    capital = barrio_warnings(0, False, 0, whole_capital=True)  # `scope: madrid` (D-238)
    assert any("no barrio of Madrid capital" in w for w in capital)
    assert any("no indicator by barrio" in w for w in barrio_warnings(8, False, 0))
    assert any("2 barrios" in w for w in barrio_warnings(8, True, 2))
    assert barrio_warnings(8, True, 0) == []
