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


# D-232: barrio names from the Ayuntamiento panel. The CM barrios table is older than the 2017
# reform: it calls 28079192 «Ambroz» and leaves 28079183, 28079193 and 28079194 unnamed.
def _barrios() -> list[Unit]:
    return [
        Unit("ES.28.BAR.28079192", "barrio", "28079192", "Ambroz", "ES.28.DIS.2807919"),
        Unit("ES.28.BAR.28079193", "barrio", "28079193", None, "ES.28.DIS.2807919"),
        Unit("ES.28.BAR.28079201", "barrio", "28079201", "Simancas", "ES.28.DIS.2807920"),
    ]


BARRIOS = {
    "ES.28.BAR.28079192": ["Valdebernardo"],
    "ES.28.BAR.28079193": ["Valderrivas"],
    "ES.28.BAR.28079201": ["Simancas"],
}


def test_barrios_take_the_name_the_ayuntamiento_publishes() -> None:
    units = _units() + _barrios()
    plan = plan_names(units, MUNICIPIOS, DISTRICTS, BARRIOS)
    assert plan.passed, plan.checks()
    assert plan.names["ES.28.BAR.28079192"] == "Valdebernardo"
    assert plan.names["ES.28.BAR.28079193"] == "Valderrivas"
    assert plan.names["ES.28.BAR.280795"] == "Castellana"  # not in the source: keeps its name
    changed = {c["admin_unit_id"] for c in plan.changes(units)}
    assert {"ES.28.BAR.28079192", "ES.28.BAR.28079193"} <= changed
    assert "ES.28.BAR.28079201" not in changed


def test_a_barrio_left_without_any_name_blocks_the_update() -> None:
    plan = plan_names(_units() + _barrios(), MUNICIPIOS, DISTRICTS, {})
    assert not plan.passed
    assert plan.unnamed == ["ES.28.BAR.28079193"]
    failed = {c["name"] for c in plan.checks() if not c["passed"]}
    assert failed == {"every_barrio_has_a_name"}


def test_two_names_for_one_barrio_is_a_conflict() -> None:
    barrios = BARRIOS | {"ES.28.BAR.28079192": ["Valdebernardo", "Ambroz"]}
    plan = plan_names(_units() + _barrios(), MUNICIPIOS, DISTRICTS, barrios)
    assert not plan.passed
    assert plan.conflicts == {"ES.28.BAR.28079192": ["Ambroz", "Valdebernardo"]}


def test_a_barrio_the_panel_does_not_name_keeps_its_name_and_a_broken_one_blocks() -> None:
    """Barrios out of the panel keep the CM name, so its spelling is still checked."""
    broken = Unit("ES.28.BAR.28079083", "barrio", "28079083", "PE/A GRANDE", "ES.28.DIS.2807908")
    plan = plan_names([*_units(), broken], MUNICIPIOS, DISTRICTS, BARRIOS)
    assert not plan.passed
    assert plan.invalid == {"ES.28.BAR.28079083": ["/"]}
