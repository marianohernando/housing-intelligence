"""GET /api/v1/gaps on the fixture database: real rows, regional reference, provenance."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from hi_api.deps import get_engine
from hi_api.main import app
from hi_contracts.catalog.enums import GapRowKey
from hi_contracts.public.responses import (
    DatasetListResponse,
    GapImpactResponse,
    GapRowMapResponse,
    ZoneGapListResponse,
)

pytestmark = pytest.mark.db


@pytest.fixture
def client(migrated_engine: Engine, features_computed: None) -> TestClient:
    app.dependency_overrides[get_engine] = lambda: migrated_engine
    return TestClient(app)


def test_municipio_list_has_real_rows_against_the_region(
    client: TestClient, migrated_engine: Engine
) -> None:
    response = client.get("/api/v1/gaps/municipio/28079")
    assert response.status_code == 200
    body = ZoneGapListResponse.model_validate(response.json())
    assert body.data.zone.name == "Madrid"
    assert body.data.zone.admin_unit_id == "ES.28.MUN.28079"
    rows = {r.row.value: r for r in body.data.rows}
    assert {"colegio", "centro_salud"} <= set(rows)
    with migrated_engine.connect() as conn:
        region = conn.execute(
            text(
                "SELECT value FROM feature_value "
                "WHERE feature_id = 'centros_salud_a_pie_por_10000_hab' "
                "AND territory_level = 'ccaa' AND territory_code = '28'"
            )
        ).scalar_one()
    health = rows["centro_salud"]
    assert health.reference == pytest.approx(region, rel=1e-3)
    assert health.indicator.value is not None
    assert health.ratio_to_reference == pytest.approx(health.indicator.value / region, rel=1e-2)
    assert health.proxy_note
    assert body.meta.methodology_version == body.data.method.version
    cm = [d for d in body.data.datasets if d.is_cm_open_data]
    assert {d.dataset_id for d in cm} >= {"cm_centros_sanitarios", "cm_centros_educativos"}
    assert all(d.url and d.url.host == "datos.comunidad.madrid" for d in cm)


def test_madrid_district_has_real_rows_against_the_region(client: TestClient) -> None:
    """D-200: Madrid capital by district, with the padrón as its population (D-209)."""
    response = client.get("/api/v1/gaps/distrito/2807906")
    assert response.status_code == 200
    payload = ZoneGapListResponse.model_validate(response.json())
    assert payload.data.zone.municipio_ine == "28079"
    assert payload.data.zone.admin_unit_id == "ES.28.DIS.2807906"
    rows = {r.row.value: r for r in payload.data.rows}
    assert {"colegio", "centro_salud"} <= set(rows)
    warned = {w.split(" row ")[1].split()[0] for w in payload.warnings}
    assert warned == {k.value for k in GapRowKey} - set(rows)  # one per row not computed yet
    for key, row in rows.items():
        assert row.indicator.level.value == "distrito"
        assert (row.indicator.value is None) == (key == "vivienda")  # see the SIN DATOS test
        assert row.reference is not None
        # D-213: compared with the urban municipios (Madrid is urban), or with the whole region
        # when the urban ones have none of it in the sample
        assert row.reference_label in {
            "Otros municipios urbanos de la Comunidad de Madrid",
            "Comunidad de Madrid",
        }
    datasets = {d.dataset_id: d for d in rows["colegio"].datasets}
    assert datasets["ayto_padron_municipal"].is_cm_open_data is False  # the district population
    assert datasets["cm_poblacion_edad_nacionalidad_sexo"].is_cm_open_data  # the reference
    assert datasets["cm_centros_educativos"].is_cm_open_data


@pytest.mark.parametrize(("level", "code"), [("municipio", "28079"), ("distrito", "2807906")])
def test_rows_carry_walking_minutes_as_extra_indicators(
    client: TestClient, level: str, code: str
) -> None:
    """GAP-001 F1: features bound with `role: extra` show up next to the row's main indicator."""
    body = ZoneGapListResponse.model_validate(client.get(f"/api/v1/gaps/{level}/{code}").json())
    rows = {r.row.value: r for r in body.data.rows}
    expected = {"colegio": "min_a_pie_colegio", "centro_salud": "min_a_pie_centro_salud"}
    for row_key, feature_id in expected.items():
        extras = {e.feature_id: e for e in rows[row_key].extra_indicators}
        assert feature_id in extras
        walk = extras[feature_id]
        assert walk.unit == "min"
        assert walk.level.value == level
        assert (walk.value is None) == (walk.null_reason is not None)  # unknown is never 0
        assert "osm_red_peatonal" in walk.datasets
        assert "osm_red_peatonal" in {d.dataset_id for d in rows[row_key].datasets}
    assert "osm_red_peatonal" in {d.dataset_id for d in body.data.datasets}


def test_new_rows_by_municipio_and_district_with_their_extras(client: TestClient) -> None:
    """GAP-001 F3a: escuela infantil, mayores and farmacia, in a municipio and in a district.
    The official CM pharmacy ratio is only published by municipio."""
    new_rows = {"escuela_infantil", "mayores", "farmacia"}
    madrid = ZoneGapListResponse.model_validate(client.get("/api/v1/gaps/municipio/28079").json())
    district = ZoneGapListResponse.model_validate(
        client.get("/api/v1/gaps/distrito/2807906").json()
    )
    for body in (madrid, district):
        rows = {r.row.value: r for r in body.data.rows}
        assert new_rows <= set(rows)
        for key in new_rows:
            assert rows[key].reference is not None
            assert rows[key].proxy_note
    madrid_extras = {
        e.feature_id
        for r in madrid.data.rows
        if r.row.value == "farmacia"
        for e in r.extra_indicators
    }
    district_extras = {
        e.feature_id
        for r in district.data.rows
        if r.row.value == "farmacia"
        for e in r.extra_indicators
    }
    assert {"min_a_pie_farmacia", "farmacias_por_10000_hab_oficial"} <= madrid_extras
    assert "min_a_pie_farmacia" in district_extras
    assert "farmacias_por_10000_hab_oficial" not in district_extras
    madrid_rows = {r.row.value: r for r in madrid.data.rows}
    mayores = {e.feature_id for e in madrid_rows["mayores"].extra_indicators}
    assert {"min_a_pie_mayores", "plazas_residencia_por_100_mayores"} <= mayores
    cm = {d.dataset_id for d in madrid_rows["farmacia"].datasets if d.is_cm_open_data}
    assert {"cm_oficinas_farmacia", "cm_farmacias_municipios"} <= cm


def test_housing_row_by_municipio_and_explicit_sin_datos_by_district(client: TestClient) -> None:
    """GAP-001 F3b: the CM publishes no housing tables by district, so the row is there with
    SIN_DATOS and its reason (never 0, never absent); its district extras still show."""
    madrid = ZoneGapListResponse.model_validate(client.get("/api/v1/gaps/municipio/28079").json())
    rows = {r.row.value: r for r in madrid.data.rows}
    assert set(rows) == {k.value for k in GapRowKey}
    assert madrid.warnings == []
    housing = rows["vivienda"]
    assert housing.indicator.value is not None
    assert housing.indicator.confidence <= 0.8  # two sources, different universes and years
    assert {"viviendas_alquiler_pct", "tamano_medio_hogar"} <= {
        e.feature_id for e in housing.extra_indicators
    }
    nursery = {e.feature_id for e in rows["escuela_infantil"].extra_indicators}
    assert {"unidades_infantil_por_1000_ninos", "nacimientos_por_1000_hab"} <= nursery
    cm = {d.dataset_id for r in madrid.data.rows for d in r.datasets if d.is_cm_open_data}
    assert {
        "cm_viviendas_superficie",
        "cm_hogares_tamano_censo_2021",
        "cm_viviendas_tenencia_censo_2021",
        "cm_unidades_escolares",
        "cm_nacidos_vivos_municipios",
    } <= cm

    district = ZoneGapListResponse.model_validate(
        client.get("/api/v1/gaps/distrito/2807906").json()
    )
    by_key = {r.row.value: r for r in district.data.rows}
    assert set(by_key) == {k.value for k in GapRowKey}
    housing = by_key["vivienda"]
    assert housing.status.value == "SIN_DATOS"
    assert housing.indicator.value is None
    assert housing.indicator.null_reason is not None
    assert housing.indicator.null_reason.value == "SOURCE_MISSING"
    assert housing.ratio_to_reference is None
    assert {e.feature_id for e in housing.extra_indicators} == {"tamano_medio_hogar"}
    mayores = {e.feature_id for e in by_key["mayores"].extra_indicators}
    assert {"min_a_pie_mayores", "plazas_residencia_por_100_mayores"} <= mayores


def test_municipio_rows_never_cite_the_district_population(client: TestClient) -> None:
    body = ZoneGapListResponse.model_validate(client.get("/api/v1/gaps/municipio/28079").json())
    assert "ayto_padron_municipal" not in {d.dataset_id for d in body.data.datasets}


def test_dataset_list_counts_cm_open_data(client: TestClient) -> None:
    every = DatasetListResponse.model_validate(client.get("/api/v1/datasets").json()).data
    cm = DatasetListResponse.model_validate(
        client.get("/api/v1/datasets", params={"cm_only": True}).json()
    ).data
    assert every.total >= cm.total == cm.cm_open_data_count > 0
    assert all(d.is_cm_open_data and d.version for d in cm.datasets)
    assert every.cm_open_data_count == cm.total


def test_every_dataset_carries_the_attribution_its_licence_asks_for(client: TestClient) -> None:
    every = DatasetListResponse.model_validate(client.get("/api/v1/datasets").json()).data
    by_id = {d.dataset_id: d for d in every.datasets}
    hospitals = by_id["ms_catalogo_nacional_hospitales"].attribution_text or ""
    assert "Ministerio de Sanidad" in hospitals and "actualizado a" in hospitals
    assert all(d.attribution_text for d in every.datasets)  # every source used declares one


def test_unknown_zone_is_404_and_unsupported_level_is_422(client: TestClient) -> None:
    assert client.get("/api/v1/gaps/municipio/28999").status_code == 404
    assert client.get("/api/v1/gaps/h3_r9/89390cb1b0bffff").status_code == 422
    assert client.get("/api/v1/gaps/planeta/1").status_code == 422


def test_level_without_computed_indicators_returns_no_rows(
    client: TestClient, migrated_engine: Engine
) -> None:
    """Rows not computed at a level are absent (not SIN_DATOS). The section does have walking
    minutes, but an extra indicator never makes a row on its own."""
    with migrated_engine.connect() as conn:
        walk = conn.execute(
            text(
                "SELECT count(*) FROM feature_value WHERE feature_id = 'min_a_pie_colegio' "
                "AND territory_level = 'seccion_censal' AND territory_code = '2807901006'"
            )
        ).scalar_one()
    assert walk == 1
    response = client.get("/api/v1/gaps/seccion_censal/2807901006")  # in the admin fixture
    assert response.status_code == 200
    payload = ZoneGapListResponse.model_validate(response.json())
    assert payload.data.zone.name == "Sección 01-006 · Madrid"
    assert payload.data.rows == []
    assert len(payload.warnings) == len(GapRowKey)
    assert all("seccion_censal level" in w for w in payload.warnings)


def test_row_map_agrees_with_each_zone_list(client: TestClient) -> None:
    """GAP-001 F4: the map colour of every zone is the status of its row in /gaps/{level}/{code}."""
    for level, row in [("municipio", "colegio"), ("distrito", "centro_salud")]:
        response = client.get("/api/v1/gaps", params={"level": level, "row": row})
        assert response.status_code == 200
        body = GapRowMapResponse.model_validate(response.json())
        assert body.meta.methodology_version == body.data.method.version
        assert body.meta.data_version
        assert body.data.zones, (level, row)
        assert body.data.datasets
        for zone in body.data.zones:
            listed = ZoneGapListResponse.model_validate(
                client.get(f"/api/v1/gaps/{level}/{zone.code}").json()
            )
            same = next(r for r in listed.data.rows if r.row.value == row)
            assert zone.status == same.status
            assert zone.value == same.indicator.value
            assert zone.ratio_to_reference == same.ratio_to_reference
            assert zone.name == listed.data.zone.name
            assert zone.admin_unit_id == listed.data.zone.admin_unit_id
            assert zone.reference == same.reference
            assert zone.reference_label == same.reference_label
            assert zone.reliable == same.reliable
            assert body.data.reference == (same.regional_reference or same.reference)


def test_row_map_keeps_sin_datos_and_flags_rows_not_computed(client: TestClient) -> None:
    housing = GapRowMapResponse.model_validate(
        client.get("/api/v1/gaps", params={"level": "distrito", "row": "vivienda"}).json()
    )
    assert housing.data.zones
    assert {z.status.value for z in housing.data.zones} == {"SIN_DATOS"}
    assert housing.data.counts.sin_datos == len(housing.data.zones)
    assert all(z.null_reason is not None and z.value is None for z in housing.data.zones)
    sections = client.get("/api/v1/gaps", params={"level": "seccion_censal", "row": "colegio"})
    assert sections.status_code == 200
    body = GapRowMapResponse.model_validate(sections.json())
    assert body.data.zones == []
    assert body.warnings == [
        "INSUFFICIENT_DATA: row colegio not computed at seccion_censal level yet"
    ]


def test_row_map_rejects_unknown_rows_and_levels(client: TestClient) -> None:
    assert client.get("/api/v1/gaps", params={"level": "municipio", "row": "x"}).status_code == 422
    barrio = client.get("/api/v1/gaps", params={"level": "barrio", "row": "colegio"})
    assert barrio.status_code == 422
    assert barrio.json()["detail"]["code"] == "OUT_OF_COVERAGE"
    assert client.get("/api/v1/gaps", params={"level": "municipio"}).status_code == 422


def test_rows_compare_with_municipios_of_the_same_type(
    client: TestClient, migrated_engine: Engine
) -> None:
    """D-213: the reference is the rate of the municipios of the zone's type (Ley 45/2007), from
    the counts each feature row keeps; the region stays as context. The value per count comes
    from the region (2SFCA rows keep facility-equivalents, D-217). The housing row is used
    because the sample's walking network only covers Madrid: the 2SFCA rows of Ajalvir have
    no streets to place people on and are SIN DATOS there."""
    feature = "viviendas_grandes_por_100_hogares_grandes"
    with migrated_engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT territory_level, territory_code, value, inputs->'counts' AS counts "
                "FROM feature_value WHERE feature_id = :f "
                "AND territory_level IN ('municipio', 'ccaa')"
            ),
            {"f": feature},
        ).mappings()
        by_code = {(r["territory_level"], r["territory_code"]): r for r in rows}
    region = by_code[("ccaa", "28")]
    per_rate = region["value"] / (region["counts"]["numerator"] / region["counts"]["denominator"])
    # In the sample La Acebeda is rural (70 inhabitants); Ajalvir and Madrid are urban, and each
    # is compared with the other one (its own counts are left out).
    other = by_code[("municipio", "28079")]["counts"]
    rate = other["numerator"] / other["denominator"]
    body = ZoneGapListResponse.model_validate(client.get("/api/v1/gaps/municipio/28002").json())
    housing = next(r for r in body.data.rows if r.row.value == "vivienda")
    assert housing.reference_label == "Otros municipios urbanos de la Comunidad de Madrid"
    assert housing.reference == pytest.approx(per_rate * rate, rel=1e-3)
    assert housing.regional_reference is not None
    assert "en toda la Comunidad" in housing.explanation
    assert body.data.method.version == "gap-0.3"
    assert body.data.method.confidence_level == 0.95


def test_rows_carry_the_people_they_serve(client: TestClient, migrated_engine: Engine) -> None:
    """D-229: each row says who it serves in the zone, from its indicator's denominator."""
    madrid = ZoneGapListResponse.model_validate(client.get("/api/v1/gaps/municipio/28079").json())
    rows = {r.row.value: r for r in madrid.data.rows}
    with migrated_engine.connect() as conn:
        population = conn.execute(
            text(
                "SELECT value FROM feature_value WHERE feature_id = 'poblacion_total' "
                "AND territory_level = 'municipio' AND territory_code = '28079'"
            )
        ).scalar_one()
    health = rows["centro_salud"].people
    assert health is not None and health.label == "personas"
    assert health.count == pytest.approx(population, rel=1e-6)  # the same census population
    nursery = rows["escuela_infantil"].people
    assert nursery is not None and nursery.label == "niños de 0 a 4 años"
    assert 0 < nursery.count < health.count
    housing = rows["vivienda"].people
    assert housing is not None and housing.label == "hogares de 4 o más personas"
    district = ZoneGapListResponse.model_validate(
        client.get("/api/v1/gaps/distrito/2807906").json()
    )
    by_key = {r.row.value: r for r in district.data.rows}
    assert by_key["vivienda"].people is None  # no counts by district: unknown, never 0
    assert by_key["colegio"].people is not None


def _zones_of_the_search(client: TestClient, row: str, madrid_level: str) -> dict[str, str]:
    """code -> level of every zone the impact counts for a row, and its status."""
    municipios = GapRowMapResponse.model_validate(
        client.get("/api/v1/gaps", params={"level": "municipio", "row": row}).json()
    ).data.zones
    zones = {z.code: ("municipio", z.status.value) for z in municipios}
    if madrid_level == "distrito":
        del zones["28079"]
        districts = GapRowMapResponse.model_validate(
            client.get("/api/v1/gaps", params={"level": "distrito", "row": row}).json()
        ).data.zones
        zones |= {z.code: ("distrito", z.status.value) for z in districts}
    return {code: f"{level}:{status}" for code, (level, status) in zones.items()}


def test_impact_ranks_every_falta_zone_by_the_people_affected(client: TestClient) -> None:
    """D-229: the zones of the search (Madrid by district when the row has district values),
    the FALTA ones ranked by people, each with the same people as its own list."""
    response = client.get("/api/v1/gaps/impact")
    assert response.status_code == 200
    body = GapImpactResponse.model_validate(response.json())
    assert body.meta.methodology_version == body.data.version == "impact-0.1"
    assert body.data.method.version == "gap-0.3"
    rows = {r.row.value: r for r in body.data.rows}
    assert set(rows) == {k.value for k in GapRowKey}
    assert rows["vivienda"].madrid_level.value == "municipio"  # no housing tables by district
    assert rows["colegio"].madrid_level.value == "distrito"
    assert body.data.datasets
    for key, impact in rows.items():
        zones = _zones_of_the_search(client, key, impact.madrid_level.value)
        assert impact.zones == len(zones)
        falta = {code for code, state in zones.items() if state.endswith(":FALTA")}
        assert {z.code for z in impact.ranking} == falta
        assert impact.people_total > 0
        assert impact.share_in_falta == pytest.approx(impact.people_in_falta / impact.people_total)
        assert impact.summary.startswith(("En la Comunidad de Madrid", "Ninguna zona"))
        for zone in impact.ranking:
            listed = ZoneGapListResponse.model_validate(
                client.get(f"/api/v1/gaps/{zone.level.value}/{zone.code}").json()
            )
            same = next(r for r in listed.data.rows if r.row.value == key)
            assert same.status.value == "FALTA"
            assert same.people is not None and same.people.count == zone.people
            assert zone.p_value is None or zone.p_value < 0.025
            assert zone.explanation.startswith("Viven aquí")


def test_small_zones_say_why_they_cannot_be_compared(client: TestClient) -> None:
    """Fase de mejora (zonas pequeñas): La Acebeda has 1 household of 4 or more and 0 children
    of 0 to 4. Housing is not comparable (its denominator is a count below the 3,69 floor of
    D-213), and the nursery row says nobody of that age lives there, not «no data»."""
    body = ZoneGapListResponse.model_validate(client.get("/api/v1/gaps/municipio/28001").json())
    rows = {r.row.value: r for r in body.data.rows}
    housing = rows["vivienda"]
    assert housing.reliable is False and housing.status.value != "FALTA"
    assert housing.comparison_group is None
    assert housing.explanation.startswith("No comparable: aquí viven muy pocos hogares")
    nursery = rows["escuela_infantil"]
    assert nursery.status.value == "SIN_DATOS"
    assert nursery.indicator.null_reason is not None
    assert nursery.indicator.null_reason.value == "NOT_APPLICABLE"
    assert nursery.explanation.startswith("No viven niños de 0 a 4 años en esta zona")
    ajalvir = ZoneGapListResponse.model_validate(client.get("/api/v1/gaps/municipio/28002").json())
    without_streets = next(r for r in ajalvir.data.rows if r.row.value == "escuela_infantil")
    assert without_streets.indicator.null_reason is not None
    assert without_streets.indicator.null_reason.value == "SOURCE_NO_COVERAGE"  # people, no streets


def test_every_dataset_says_where_it_is_published(client: TestClient) -> None:
    """Fase de mejora 4: the padrón and OSM are not «en el portal de datos» of the CM; each
    dataset names the portal or site where it opens (`source_name`)."""
    every = DatasetListResponse.model_validate(client.get("/api/v1/datasets").json()).data
    by_id = {d.dataset_id: d for d in every.datasets}
    assert by_id["ayto_padron_municipal"].source_name == (
        "Portal de Datos Abiertos del Ayuntamiento de Madrid"
    )
    assert (by_id["osm_red_peatonal"].source_name or "").startswith("OpenStreetMap")
    cm = [d for d in every.datasets if d.is_cm_open_data]
    assert {d.source_name for d in cm} == {"Portal de Datos Abiertos de la Comunidad de Madrid"}
    madrid = ZoneGapListResponse.model_validate(client.get("/api/v1/gaps/municipio/28079").json())
    assert all(d.source_name for d in madrid.data.datasets)


def test_the_bed_datasets_are_served_as_regional_context(client: TestClient) -> None:
    """Fase de mejora 4: the two CM bed datasets are counted, so the API serves them: hospitals
    and installed beds per 1.000 inhabitants of the region, for the hospital note."""
    for feature_id, dataset_id in (
        ("camas_instaladas_por_1000_hab", "cm_dotacion_camas"),
        ("hospitales_total", "cm_hospitales_datos_asistenciales"),
    ):
        response = client.get(f"/api/v1/features/{feature_id}/values", params={"level": "ccaa"})
        assert response.status_code == 200, feature_id
        data = response.json()["data"]
        assert data["values"][0]["value"] > 0
        assert dataset_id in data["lineage"]["dataset_versions"]
