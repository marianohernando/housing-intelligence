"""Warnings for the rows a zone's list does not carry yet (no database needed)."""

from hi_api.services.gaps import missing_row_warnings
from hi_contracts.catalog.enums import GapRowKey, TerritoryLevel


def test_one_warning_per_expected_row_that_is_absent() -> None:
    present = {GapRowKey.COLEGIO, GapRowKey.CENTRO_SALUD}
    warnings = missing_row_warnings(present, TerritoryLevel.DISTRITO)
    assert warnings == [
        "INSUFFICIENT_DATA: row escuela_infantil not computed at distrito level yet",
        "INSUFFICIENT_DATA: row mayores not computed at distrito level yet",
        "INSUFFICIENT_DATA: row farmacia not computed at distrito level yet",
        "INSUFFICIENT_DATA: row vivienda not computed at distrito level yet",
    ]


def test_every_row_is_warned_when_none_is_computed() -> None:
    warnings = missing_row_warnings(set(), TerritoryLevel.SECCION_CENSAL)
    assert len(warnings) == len(GapRowKey)
    assert all("seccion_censal level" in w for w in warnings)


def test_no_warning_when_every_row_is_present() -> None:
    assert missing_row_warnings(set(GapRowKey), TerritoryLevel.MUNICIPIO) == []
