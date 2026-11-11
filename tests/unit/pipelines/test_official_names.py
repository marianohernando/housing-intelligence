"""DATA-022: official spellings replace the broken names of the section CSV."""

from hi_ingestion.pipelines.admin_boundaries.official_names import Unit, plan_names

MUN = "municipio"
DIS = "distrito"


def _units() -> list[Unit]:
    return [
        Unit("ES.28.MUN.28121", MUN, "28121", "REDUE/A", None),
        Unit("ES.28.MUN.28004", MUN, "28004", "ALAMO, EL", None),
        Unit("ES.28.MUN.28079", MUN, "28079", "MADRID", None),
        Unit(
            "ES.28.DIS.2812101", DIS, "2812101", "REDUE/A — distrito censal 01", "ES.28.MUN.28121"
        ),
        Unit("ES.28.DIS.2807919", DIS, "2807919", "Vicalvaro", "ES.28.MUN.28079"),
        Unit("ES.28.BAR.280795", "barrio", "280795", "Castellana", "ES.28.DIS.2807904"),
    ]


MUNICIPIOS = {
    "ES.28.MUN.28121": ["Redueña"],
    "ES.28.MUN.28004": ["Álamo (El)"],
    "ES.28.MUN.28079": ["Madrid"],
}
DISTRICTS = {"ES.28.DIS.2807919": ["Vicálvaro"]}


def test_official_spellings_replace_the_broken_ones() -> None:
    units = _units()
    plan = plan_names(units, MUNICIPIOS, DISTRICTS)
    assert plan.passed, plan.checks()
    assert plan.names["ES.28.MUN.28121"] == "Redueña"
    assert plan.names["ES.28.MUN.28004"] == "Álamo (El)"
    assert plan.names["ES.28.DIS.2812101"] == "Redueña — distrito censal 01"
    assert plan.names["ES.28.DIS.2807919"] == "Vicálvaro"
    assert plan.names["ES.28.BAR.280795"] == "Castellana"  # barrios keep their source name
    changed = {c["admin_unit_id"] for c in plan.changes(units)}
    assert changed == {
        "ES.28.MUN.28121",
        "ES.28.MUN.28004",
        "ES.28.MUN.28079",
        "ES.28.DIS.2812101",
        "ES.28.DIS.2807919",
    }


def test_municipio_without_official_name_blocks_the_update() -> None:
    plan = plan_names(
        _units(), {k: v for k, v in MUNICIPIOS.items() if "28121" not in k}, DISTRICTS
    )
    assert not plan.passed
    assert plan.missing == ["ES.28.MUN.28121"]
    # The district keeps the broken name and the spelling check catches it too.
    assert plan.invalid["ES.28.DIS.2812101"] == ["/"]


def test_madrid_district_without_name_blocks_the_update() -> None:
    plan = plan_names(_units(), MUNICIPIOS, {})
    assert not plan.passed
    assert plan.missing == ["ES.28.DIS.2807919"]


def test_two_names_for_one_unit_is_a_conflict() -> None:
    municipios = MUNICIPIOS | {"ES.28.MUN.28004": ["Álamo (El)", "El Álamo"]}
    plan = plan_names(_units(), municipios, DISTRICTS)
    assert not plan.passed
    assert plan.conflicts == {"ES.28.MUN.28004": ["El Álamo", "Álamo (El)"]}


def test_a_broken_official_name_is_never_published() -> None:
    plan = plan_names(_units(), MUNICIPIOS | {"ES.28.MUN.28121": ["REDUEÐA"]}, DISTRICTS)
    assert not plan.passed
    assert plan.invalid["ES.28.MUN.28121"] == ["Ð"]
    assert plan.invalid["ES.28.DIS.2812101"] == ["Ð"]
