"""D-253: services and supplies of a parcel (hi_domain.supplies) and the catalogue's cautions."""

import pytest

from hi_domain.parcels import CatalogEntry, ExistingBuilding, catalog_text, existing_text
from hi_domain.supplies import SIMULTANEITY, power_estimate, simultaneity


def test_the_simultaneity_is_table_1_of_itc_bt_10_and_its_formula_past_21() -> None:
    """As printed in the BOE supplement 224 of 18/09/2002, p. 68."""
    assert [simultaneity(n) for n in (1, 4, 10, 14, 19, 21)] == [1.0, 3.8, 8.5, 11.3, 14.3, 15.3]
    assert len(SIMULTANEITY) == 21
    assert simultaneity(26) == pytest.approx(17.8)  # 15,3 + 5 × 0,5
    assert simultaneity(164) == pytest.approx(86.8)
    with pytest.raises(ValueError, match="one home"):
        simultaneity(0)


def test_the_power_of_mendez_alvaro_passes_the_transformer_threshold() -> None:
    """13.121 m² / 80 ≈ 164 homes: 5,75 × 86,8 = 499,1 kW, over 100 kW (RD 1048/2013, 26.1)."""
    power = power_estimate(13121)
    assert power is not None
    assert (power.homes, power.simultaneity, power.kw) == (164, 86.8, 499.1)
    assert power.over_transformer_threshold
    small = power_estimate(224.4)  # Mayor 61: about 3 homes
    assert small is not None and (small.homes, small.kw) == (3, 17.3)
    assert not small.over_transformer_threshold
    assert power_estimate(None) is None and power_estimate(0) is None


@pytest.mark.parametrize(
    ("protection", "level"),
    [("Singular", 1), ("Integral", 1), ("Estructural", 2), ("Volumétrico", 2),
     ("Parcial", 3), ("Ambiental", 3), ("Otra", None), (None, None)],
)  # fmt: skip
def test_the_catalogue_levels_are_those_of_nnuu_4_3_4(
    protection: str | None, level: int | None
) -> None:
    assert CatalogEntry("1", None, protection, None).level == level


def test_what_a_catalogued_building_means_for_a_new_build_account() -> None:
    whole = catalog_text(CatalogEntry("00001", None, "Integral", None))
    assert "ni siquiera en ruina puede tener orden o licencia de demolición" in whole
    part = catalog_text(CatalogEntry("02933", None, "Parcial", None))
    assert part.startswith("Edificio catalogado por el Plan General, protección parcial (nº 02933)")
    assert "mantener esos elementos en el edificio nuevo" in part
    other = catalog_text(CatalogEntry(None, None, None, None))
    assert other.startswith("Edificio catalogado por el Plan General: las obras")


def test_what_is_built_is_said_with_its_figures_never_a_rule() -> None:
    mayor = existing_text(ExistingBuilding(376, 1890, 6))
    assert mayor == (
        "Hay un edificio de 376 m² construidos (de 1890), con 6 inmuebles en división horizontal. "
        "La calculadora es de obra nueva sobre suelo libre: no cuenta el derribo, el desalojo ni "
        "la compra a los propietarios de sus inmuebles."
    )
    assert existing_text(ExistingBuilding(6573)).endswith("no cuenta el derribo ni el desalojo.")


@pytest.mark.parametrize("status", ["Descatalogado", "Demolición total"])
def test_a_building_out_of_the_catalogue_is_never_said_protected(status: str) -> None:
    """Review of #110: the layer also gives «Descatalogado» and «Demolición total»."""
    text = catalog_text(CatalogEntry("01234", None, status, None))
    assert "protegido" not in text.split("catálogo de edificios protegidos")[1]
    assert text.startswith("El catálogo de edificios protegidos del Plan General lo da como «")
    assert CatalogEntry("01234", None, status, None).level is None
