"""D-250: GET /api/v1/investors/parcels and /parcels/candidates without network nor database.

The answers of the Catastro, the Ayuntamiento and CartoCiudad are SYNTHETIC (respx): made-up
references and streets, shaped like the services' answers, never a saved answer (the Catastro's
licence does not allow redistributing them, and the repo is public). The database is unreachable
here (as in CI): the sheet comes without its barrio and says so.
"""

import logging
from collections.abc import Iterator
from typing import Any

import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from hi_api import privacy
from hi_api.main import app
from hi_api.services import parcel_sheet
from hi_api.services.parcels import (
    CALLEJERO,
    CARTOCIUDAD,
    CONDICIONES,
    COORDENADAS,
    PLANEAMIENTO,
    USER_AGENT,
    USOS_SUELO,
)
from hi_contracts.public.responses import ParcelCandidatesResponse, ParcelSheetResponse

client = TestClient(app)
RC = "1111111VK1111A"  # made up
DH_RC = "2222222VK2222B"
OTHER_RC = "3333333VK3333C"
DEMO_RC = "2122202VK4722A"  # one of the four saved demo sheets
POINT = {"x": 440000.5, "y": 4475000.5}
RAW_KEYS = ("bico", "lrcdnp", "rcdnp", "debi", "lcons", "loint", "ldt", "cuerr", "lerr")


@pytest.fixture(autouse=True)
def fresh(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    for name in ("PARCEL_UPSTREAMS", "PARCEL_GUARD_PER_MINUTE", "GEOCODER_GUARD_PER_MINUTE"):
        monkeypatch.delenv(name, raising=False)
    parcel_sheet.CACHE.clear()
    parcel_sheet.settings.cache_clear()
    parcel_sheet.guards.cache_clear()
    yield
    parcel_sheet.CACHE.clear()
    parcel_sheet.settings.cache_clear()
    parcel_sheet.guards.cache_clear()


# --- Synthetic answers, shaped like the services' ---


def location(street: str = "DE PRUEBA", number: str = "1", cm: str = "79") -> dict[str, Any]:
    return {
        "loine": {"cp": "28", "cm": cm},
        "cmc": "900" if cm == "79" else "123",
        "locs": {
            "lous": {
                "lourb": {
                    "dir": {"cv": "1", "tv": "CL", "nv": street, "pnp": number},
                    "dp": "28001",
                    "dm": "1",
                }
            }
        },
    }


def finca(rc: str, area: str, ltp: str | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {
        "dff": {"ss": area},
        "infgraf": {"igraf": f"https://www1.sedecatastro.gob.es/Cartografia/mapa.aspx?refcat={rc}"},
    }
    if ltp:
        body["ltp"] = ltp
    return body


def dnprc_single(
    rc: str = RC, use: str = "Residencial", built: str = "800", cm: str = "79"
) -> dict[str, Any]:
    bi = {
        "idbi": {"cn": "UR", "rc": {"pc1": rc[:7], "pc2": rc[7:]}},
        "dt": location(cm=cm),
        "ldt": "CL DE PRUEBA 1 28001 MADRID (MADRID)",
        "debi": {"luso": use, "sfc": built, "cpt": "100,000000", "ant": "1975"},
    }
    bico: dict[str, Any] = {"bi": bi, "finca": finca(rc, "500")}
    if built != "0":
        bico["lcons"] = [{"lcd": "VIVIENDA", "dfcons": {"stl": built}}]
    return {"consulta_dnprcResult": {"control": {"cudnp": 1, "cucons": 1}, "bico": bico}}


def dh_unit(car: str, use: str, built: str, floor: str, door: str) -> dict[str, Any]:
    dt = location()
    dt["locs"]["lous"]["lourb"]["loint"] = {"es": "1", "pt": floor, "pu": door}
    return {
        "rc": {"pc1": DH_RC[:7], "pc2": DH_RC[7:], "car": car, "cc1": "X", "cc2": "Y"},
        "dt": dt,
        "debi": {"luso": use, "sfc": built, "ant": "1920"},
    }


def dnprc_divided() -> dict[str, Any]:
    units = [
        dh_unit("0001", "Comercial", "50", "00", "01"),
        dh_unit("0002", "Residencial", "70", "01", "A"),
        dh_unit("0003", "Residencial", "60", "02", "B"),
    ]
    return {"consulta_dnprcResult": {"control": {"cudnp": 3}, "lrcdnp": {"rcdnp": units}}}


def dnprc_unit() -> dict[str, Any]:
    body = dnprc_single(DH_RC)
    body["consulta_dnprcResult"]["bico"]["finca"] = finca(
        DH_RC, "90", "Parcela con varios inmuebles (division horizontal)"
    )
    return body


def catastro_error(root: str, code: str, form: str = "list") -> dict[str, Any]:
    error = {"cod": code, "des": "MENSAJE DE ERROR SINTÉTICO"}
    errors: Any = [error] if form == "list" else {"err": [error]}
    return {root: {"control": {"cuerr": 1}, "lerr": errors}}


def cpmrc() -> dict[str, Any]:
    geo = {"xcen": str(POINT["x"]), "ycen": str(POINT["y"]), "srs": "EPSG:25830"}
    return {
        "Consulta_CPMRCResult": {"control": {"cucoor": 1}, "coordenadas": {"coord": [{"geo": geo}]}}
    }


def arcgis(attributes: dict[str, Any] | None) -> dict[str, Any]:
    return {"features": [] if attributes is None else [{"attributes": attributes}]}


USES_NZ8 = {
    "AMB_TX_ETIQ": "8.3.a",
    "AMB_TX_DENOM": "ZONA 8 GRADO 3º - NIVEL a",
    "ZURV_TX_NOMBRE": "",
    "UBOV_TX_ETIQ": "M00001",
    "USP_TX_DENOM": "RESIDENCIAL VIVIENDA UNIFAMILIAR  ",
}


def mock_catastro(router: respx.MockRouter, dnprc: Any = None) -> None:
    router.get(url__startswith=f"{CALLEJERO}/Consulta_DNPRC").mock(
        return_value=httpx.Response(200, json=dnprc or dnprc_single())
    )
    router.get(url__startswith=f"{COORDENADAS}/Consulta_CPMRC").mock(
        return_value=httpx.Response(200, json=cpmrc())
    )


def mock_sigma(router: respx.MockRouter, uses: Any = USES_NZ8, instrument: Any = None) -> None:
    router.get(url__startswith=USOS_SUELO).mock(return_value=httpx.Response(200, json=arcgis(uses)))
    router.get(url__startswith=PLANEAMIENTO).mock(
        return_value=httpx.Response(200, json=arcgis(instrument))
    )


def sheet_of(response: Any) -> ParcelSheetResponse:  # the test client's response
    assert response.status_code == 200, response.text
    return ParcelSheetResponse.model_validate(response.json())


def assert_transformed(response: Any) -> None:
    """Our fields only: no key of the Catastro's answers travels in our response."""
    body = response.text
    for key in RAW_KEYS:
        assert f'"{key}"' not in body


# --- A parcel by its reference ---


@respx.mock
def test_a_parcel_with_its_planning_and_an_assumed_buildability() -> None:
    mock_catastro(respx.mock)
    mock_sigma(respx.mock)
    response = client.get("/api/v1/investors/parcels", params={"rc": RC.lower()})
    body = sheet_of(response)
    sheet = body.data
    assert body.meta.methodology_version == "parcels-0.1"
    assert sheet.input.value == "rc"
    parcel = sheet.parcel
    assert parcel.rc14 == RC
    assert parcel.address == "Calle de Prueba 1, 28001 Madrid"
    assert (parcel.area_m2, parcel.built_m2, parcel.year_built) == (500, 800, 1975)
    assert parcel.is_vacant is False and parcel.horizontal_division is False
    assert parcel.lat is not None and 40.2 < parcel.lat < 40.7
    assert sheet.planning is not None
    assert sheet.planning.code == "8.3.a" and sheet.planning.kind.value == "norma_zonal"
    assert sheet.planning.use == "RESIDENCIAL VIVIENDA UNIFAMILIAR"
    assert sheet.planning.sheet_label == "Artículo 8.8.9 de las Normas Urbanísticas"
    assert sheet.planning.norma_zonal is not None
    assert sheet.planning.norma_zonal.name == "Edificación en vivienda unifamiliar"
    assert sheet.planning.notice.startswith("Información urbanística sin valor jurídico")
    built = sheet.buildability
    assert built.kind.value == "supuesto" and built.value_m2 == pytest.approx(350)
    assert built.article == "8.8.9" and built.editable is True
    # Without a database: no barrio, and it says so; the calculator still has its assumptions
    assert sheet.context is None and sheet.degraded == ["context"]
    assert "SOURCE_DEGRADED: context" in body.warnings
    assert sheet.defaults.pem_m2.value is not None
    assert sheet.defaults.sale_price_m2.value is None
    assert sheet.fallback is None
    assert response.headers["cache-control"] == "no-store"  # incomplete: not cached
    assert_transformed(response)


@respx.mock
def test_sources_carry_the_attributions_and_never_call_it_catastral_information() -> None:
    mock_catastro(respx.mock)
    mock_sigma(respx.mock)
    sheet = sheet_of(client.get("/api/v1/investors/parcels", params={"rc": RC})).data
    by_id = {s.source_id: s for s in sheet.sources}
    day = sheet.parcel.observed_at.strftime("%d/%m/%Y")
    assert by_id["catastro_ovc"].attribution == (
        "Elaborado por Vida Fácil a partir de datos de la Dirección General del Catastro "
        f"(Sede Electrónica del Catastro), consultados el {day}."
    )
    planning = by_id["ayuntamiento_madrid_urbanismo_sigma"].attribution
    assert planning.startswith("Origen de los datos: Ayuntamiento de Madrid")
    assert "sin valor jurídico" in planning
    assert "ayuntamiento_madrid_nnuu" in by_id  # the article of the assumption
    text = ParcelSheetResponse.model_validate(
        client.get("/api/v1/investors/parcels", params={"rc": RC}).json()
    ).model_dump_json()
    for forbidden in ("información catastral", "ficha catastral", "cartografía catastral"):
        assert forbidden not in text.lower()


@respx.mock
def test_the_requests_carry_a_generic_user_agent() -> None:
    mock_catastro(respx.mock)
    mock_sigma(respx.mock)
    sheet_of(client.get("/api/v1/investors/parcels", params={"rc": RC}))
    agents = {call.request.headers["user-agent"] for call in respx.calls}
    assert agents == {USER_AGENT}
    assert "@" not in USER_AGENT


@respx.mock
def test_a_building_in_horizontal_division_is_summarised_never_listed() -> None:
    dnprc = respx.get(url__startswith=f"{CALLEJERO}/Consulta_DNPRC")
    dnprc.side_effect = [
        httpx.Response(200, json=dnprc_divided()),
        httpx.Response(200, json=dnprc_unit()),
    ]
    respx.get(url__startswith=f"{COORDENADAS}/Consulta_CPMRC").mock(
        return_value=httpx.Response(200, json=cpmrc())
    )
    mock_sigma(respx.mock)
    response = client.get("/api/v1/investors/parcels", params={"rc": DH_RC})
    parcel = sheet_of(response).data.parcel
    assert parcel.horizontal_division is True and parcel.is_vacant is False
    assert parcel.area_m2 == 90  # from the unit's answer: the parcel's
    assert parcel.units is not None and parcel.units.total == 3
    assert [(u.use, u.count, u.built_m2) for u in parcel.units.by_use] == [
        ("Residencial", 2, 130),
        ("Comercial", 1, 50),
    ]
    assert (parcel.built_m2, parcel.year_built, parcel.current_use) == (180, 1920, "Residencial")
    # The second call asked for one unit (20 characters); no unit travels in the answer
    assert dnprc.calls[1].request.url.params["RefCat"] == f"{DH_RC}0001XY"
    assert f"{DH_RC}0001XY" not in response.text
    assert_transformed(response)


@respx.mock
def test_a_plot_with_nothing_built_is_a_solar() -> None:
    mock_catastro(
        respx.mock,
        dnprc_single(use="Obras de urbanización y jardineria, suelos sin edificar", built="0"),
    )
    mock_sigma(respx.mock)
    parcel = sheet_of(client.get("/api/v1/investors/parcels", params={"rc": RC})).data.parcel
    assert parcel.is_vacant is True and parcel.built_m2 == 0


@pytest.mark.parametrize(
    ("code", "status", "error"),
    [("3", 422, "OUT_OF_COVERAGE"), ("4", 422, "OUT_OF_COVERAGE"), ("5", 404, "NOT_FOUND")],
)
@respx.mock
def test_catastro_codes(code: str, status: int, error: str) -> None:
    respx.get(url__startswith=f"{CALLEJERO}/Consulta_DNPRC").mock(
        return_value=httpx.Response(200, json=catastro_error("consulta_dnprcResult", code))
    )
    respx.get(url__startswith=f"{COORDENADAS}/Consulta_CPMRC").mock(
        return_value=httpx.Response(200, json=cpmrc())
    )
    response = client.get("/api/v1/investors/parcels", params={"rc": OTHER_RC})
    assert response.status_code == status
    assert response.json()["detail"]["code"] == error


def test_a_malformed_reference_never_reaches_the_catastro() -> None:
    with respx.mock(assert_all_called=False) as router:
        response = client.get("/api/v1/investors/parcels", params={"rc": "12345"})
        assert response.status_code == 422
        assert response.json()["detail"]["code"] == "OUT_OF_COVERAGE"
        assert not router.calls


@respx.mock
def test_a_parcel_out_of_madrid_is_out_of_coverage() -> None:
    mock_catastro(respx.mock, dnprc_single(cm="123"))
    response = client.get("/api/v1/investors/parcels", params={"rc": OTHER_RC})
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "OUT_OF_COVERAGE"


@pytest.mark.parametrize(
    "params",
    [
        {},
        {"rc": RC, "address": "calle mayor 61"},
        {"lat": "40.4"},
        {"rc": RC, "lat": "40.4", "lon": "-3.7"},
    ],
)
def test_exactly_one_way_in(params: dict[str, str]) -> None:
    response = client.get("/api/v1/investors/parcels", params=params)
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)  # a validation error, as FastAPI's


# --- When a service fails ---


@respx.mock
def test_the_ayuntamiento_down_leaves_the_rest_of_the_sheet() -> None:
    mock_catastro(respx.mock)
    respx.get(url__startswith=USOS_SUELO).mock(side_effect=httpx.ReadTimeout("slow"))
    respx.get(url__startswith=PLANEAMIENTO).mock(side_effect=httpx.ReadTimeout("slow"))
    body = sheet_of(client.get("/api/v1/investors/parcels", params={"rc": RC}))
    sheet = body.data
    assert sheet.planning is None
    assert sheet.degraded == ["planning", "context"]
    assert "SOURCE_DEGRADED: planning" in body.warnings
    assert sheet.parcel.area_m2 == 500
    assert sheet.buildability.kind.value == "sin_dato"
    assert sheet.buildability.source.startswith("Sin la calificación del Ayuntamiento")


@respx.mock
def test_an_arcgis_error_is_the_ayuntamiento_failing() -> None:
    mock_catastro(respx.mock)
    respx.get(url__startswith=USOS_SUELO).mock(
        return_value=httpx.Response(200, json={"error": {"code": 500, "message": "x"}})
    )
    respx.get(url__startswith=PLANEAMIENTO).mock(
        return_value=httpx.Response(200, json=arcgis(None))
    )
    sheet = sheet_of(client.get("/api/v1/investors/parcels", params={"rc": RC})).data
    assert sheet.planning is None and "planning" in sheet.degraded


@respx.mock
def test_the_instrument_layer_failing_keeps_the_planning() -> None:
    mock_catastro(respx.mock)
    respx.get(url__startswith=USOS_SUELO).mock(
        return_value=httpx.Response(200, json=arcgis(USES_NZ8))
    )
    respx.get(url__startswith=PLANEAMIENTO).mock(side_effect=httpx.ConnectError("down"))
    sheet = sheet_of(client.get("/api/v1/investors/parcels", params={"rc": RC})).data
    assert sheet.planning is not None and sheet.planning.instrument is None
    assert "planning" not in sheet.degraded


@respx.mock
def test_an_area_brings_its_instrument_and_its_official_record() -> None:
    mock_catastro(respx.mock)
    uses = USES_NZ8 | {"AMB_TX_ETIQ": "APR.99.01", "AMB_TX_DENOM": "ÁMBITO DE PRUEBA"}
    record = "https://servpub.madrid.es/VSURB_WBVISOR/seguimiento/expPlaneamiento.iam?figura=X.1"
    instrument = {
        "EXP_TX_NUMERO": "000/0000/00000",
        "EXP_TX_DENOM": "Plan de prueba",
        "FIG_TX_ETIQ": "X.1",
        "ENLACE": record,
    }
    mock_sigma(respx.mock, uses, instrument)
    sheet = sheet_of(client.get("/api/v1/investors/parcels", params={"rc": RC})).data
    planning = sheet.planning
    assert planning is not None and planning.kind.value == "APR" and planning.norma_zonal is None
    assert planning.instrument is not None and str(planning.instrument.url) == record
    assert str(planning.sheet_url) == record and planning.sheet_label == "Ficha del expediente X.1"
    assert sheet.buildability.kind.value == "sin_dato"


@respx.mock
def test_norma_zonal_1_asks_for_its_z() -> None:
    mock_catastro(respx.mock)
    mock_sigma(respx.mock, USES_NZ8 | {"AMB_TX_ETIQ": "1.2", "AMB_TX_DENOM": "ZONA 1 GRADO 2º"})
    respx.get(url__startswith=CONDICIONES).mock(
        return_value=httpx.Response(200, json=arcgis({"COEF_Z": 4}))
    )
    built = sheet_of(client.get("/api/v1/investors/parcels", params={"rc": RC})).data.buildability
    assert built.kind.value == "supuesto" and built.value_m2 == pytest.approx(500 * 4 * 0.66)


@pytest.mark.parametrize(
    "failure",
    [
        httpx.Response(
            200, text="<html>Sistema no disponible</html>", headers={"content-type": "text/html"}
        ),
        httpx.Response(502),
        httpx.ConnectTimeout("down"),
    ],
)
def test_the_catastro_down_serves_the_demo_sheet_or_503(failure: Any) -> None:
    with respx.mock(assert_all_called=False) as router:
        route = router.get(url__startswith=CATASTRO_ROOT)
        if isinstance(failure, Exception):
            route.mock(side_effect=failure)
        else:
            route.mock(return_value=failure)
        demo = client.get("/api/v1/investors/parcels", params={"rc": DEMO_RC})
        sheet = sheet_of(demo).data
        assert sheet.fallback == "demo_snapshot"
        assert sheet.parcel.rc14 == DEMO_RC and sheet.buildability.value_m2 == 13121
        assert any(
            w.startswith("SOURCE_DEGRADED: served from the demo snapshot")
            for w in sheet_of(demo).warnings
        )
        other = client.get("/api/v1/investors/parcels", params={"rc": OTHER_RC})
        assert other.status_code == 503
        assert other.json()["detail"]["code"] == "SOURCE_DEGRADED"


CATASTRO_ROOT = "https://ovc.catastro.meh.es/"


def test_without_upstreams_only_the_demo_parcels_and_no_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PARCEL_UPSTREAMS", "false")
    parcel_sheet.settings.cache_clear()
    with respx.mock(assert_all_called=False) as router:
        for rc in parcel_sheet.demo_rcs():
            sheet = sheet_of(client.get("/api/v1/investors/parcels", params={"rc": rc})).data
            assert sheet.fallback == "demo_snapshot" and sheet.parcel.rc14 == rc
        other = client.get("/api/v1/investors/parcels", params={"rc": OTHER_RC})
        assert other.status_code == 503
        point = client.get("/api/v1/investors/parcels", params={"lat": "40.45", "lon": "-3.68"})
        address = client.get("/api/v1/investors/parcels", params={"address": "calle de prueba 1"})
        box = client.get("/api/v1/investors/parcels/candidates", params={"q": "calle de prueba"})
        assert [r.status_code for r in (point, address, box)] == [503, 503, 503]
        assert not router.calls


# --- A point on the map ---


@respx.mock
def test_a_point_gives_its_parcel() -> None:
    respx.get(url__startswith=f"{COORDENADAS}/Consulta_RCCOOR").mock(
        return_value=httpx.Response(
            200,
            json={
                "Consulta_RCCOORResult": {
                    "control": {"cucoor": 1},
                    "coordenadas": {"coord": [{"pc": {"pc1": RC[:7], "pc2": RC[7:]}}]},
                }
            },
        )
    )
    mock_catastro(respx.mock)
    mock_sigma(respx.mock)
    sheet = sheet_of(
        client.get("/api/v1/investors/parcels", params={"lat": "40.45", "lon": "-3.68"})
    ).data
    assert sheet.input.value == "point" and sheet.parcel.rc14 == RC


@respx.mock
def test_a_point_on_the_street_suggests_the_nearest_parcels() -> None:
    respx.get(url__startswith=f"{COORDENADAS}/Consulta_RCCOOR_Distancia").mock(
        return_value=httpx.Response(
            200,
            json={
                "Consulta_RCCOOR_DistanciaResult": {
                    "control": {"cucoor": 2},
                    "coordenadas_distancias": {
                        "coordd": [
                            {
                                "lpcd": [
                                    {
                                        "pc": {"pc1": RC[:7], "pc2": RC[7:]},
                                        "ldt": "CL DE PRUEBA 1",
                                        "dis": "4.59",
                                    },
                                    {
                                        "pc": {"pc1": OTHER_RC[:7], "pc2": OTHER_RC[7:]},
                                        "ldt": "CL DE PRUEBA 3",
                                        "dis": "4.76",
                                    },
                                ]
                            }
                        ]
                    },
                }
            },
        )
    )
    respx.get(url__regex=rf"^{COORDENADAS}/Consulta_RCCOOR\?").mock(
        return_value=httpx.Response(200, json=catastro_error("Consulta_RCCOORResult", "16"))
    )
    response = client.get("/api/v1/investors/parcels", params={"lat": "40.44", "lon": "-3.61"})
    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["code"] == "NOT_FOUND"
    assert [n["rc14"] for n in detail["details"]["nearest"]] == [RC, OTHER_RC]
    assert detail["details"]["nearest"][0]["distance_m"] == pytest.approx(4.59)


def test_a_point_out_of_madrid_never_reaches_the_catastro() -> None:
    with respx.mock(assert_all_called=False) as router:
        response = client.get("/api/v1/investors/parcels", params={"lat": "40.48", "lon": "-3.36"})
        assert response.status_code == 422
        assert response.json()["detail"]["code"] == "OUT_OF_COVERAGE"
        assert not router.calls


# --- An address ---


def portal(rc: str, number: int, address: str, kind: str = "portal") -> dict[str, Any]:
    return {
        "id": "X",
        "muniCode": "28079",
        "type": kind,
        "address": address,
        "postalCode": "28001",
        "lat": 40.41,
        "lng": -3.70,
        "portalNumber": number,
        "refCatastral": rc,
    }


@respx.mock
def test_an_address_with_one_portal_gives_its_parcel() -> None:
    respx.get(url__startswith=CARTOCIUDAD).mock(
        return_value=httpx.Response(200, json=[portal(RC, 1, "CALLE DE PRUEBA 1, Madrid")])
    )
    mock_catastro(respx.mock)
    mock_sigma(respx.mock)
    sheet = sheet_of(
        client.get("/api/v1/investors/parcels", params={"address": "calle de prueba 1"})
    ).data
    assert sheet.input.value == "address" and sheet.parcel.rc14 == RC
    assert "ign_cartociudad" in {s.source_id for s in sheet.sources}


@respx.mock
def test_an_address_with_several_portals_is_never_picked() -> None:
    respx.get(url__startswith=CARTOCIUDAD).mock(
        return_value=httpx.Response(
            200,
            json=[
                portal(RC, 1, "CALLE DE PRUEBA 1, Madrid"),
                portal(OTHER_RC, 1, "CALLE DE PRUEBAS 1, Madrid"),
                portal(DH_RC, 1, "CALLE DE OTRA 1, Getafe") | {"muniCode": "28065"},
            ],
        )
    )
    response = client.get("/api/v1/investors/parcels", params={"address": "calle de prueba 1"})
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "AMBIGUOUS_INPUT"
    assert [c["rc14"] for c in detail["details"]["candidates"]] == [RC, OTHER_RC]


@respx.mock
def test_cartociudad_down_falls_back_to_the_street_index() -> None:
    respx.get(url__startswith=CARTOCIUDAD).mock(side_effect=httpx.ConnectError("down"))
    respx.get(url__startswith=f"{CALLEJERO}/ObtenerNumerero").mock(
        return_value=httpx.Response(
            200, json=catastro_error("consulta_numereroResult", "43", "dict")
        )
    )
    response = client.get("/api/v1/investors/parcels", params={"address": "calle de prueba 999"})
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "NOT_FOUND"


def test_the_typed_address_is_never_logged(caplog: pytest.LogCaptureFixture) -> None:
    typed = "calle inventada 12345"
    with caplog.at_level(logging.INFO), respx.mock(assert_all_called=False) as router:
        router.get(url__startswith=CARTOCIUDAD).mock(return_value=httpx.Response(200, json=[]))
        client.get("/api/v1/investors/parcels", params={"address": typed})
        client.get("/api/v1/investors/parcels/candidates", params={"q": typed})
    # Ours and the upstream client's; httpx2 is the test client itself, not the API
    logged = "\n".join(r.getMessage() for r in caplog.records if r.name != "httpx2")
    assert "parcel input=address" in logged
    assert "inventada" not in logged and "12345" not in logged


def test_the_access_log_redacts_the_typed_address() -> None:
    record = logging.LogRecord(
        "uvicorn.access",
        logging.INFO,
        __file__,
        1,
        '%s - "%s %s HTTP/%s" %d',
        ("203.0.113.7:1", "GET", f"{privacy.PARCELS}?address=calle+mayor+61&x=1", "1.1", 200),
        None,
    )
    assert privacy.RedactTypedAddress().filter(record)
    line = record.getMessage()
    assert "mayor" not in line and "address=[redactado]&x=1" in line
    assert privacy.redact("/api/v1/investors/parcels/candidates?q=gran+via") == (
        "/api/v1/investors/parcels/candidates?q=[redactado]"
    )
    assert privacy.redact("/api/v1/gaps?q=1") == "/api/v1/gaps?q=1"


# --- The address box ---


@respx.mock
def test_candidates_are_portals_of_madrid_with_their_parcel() -> None:
    respx.get(url__startswith=CARTOCIUDAD).mock(
        return_value=httpx.Response(
            200,
            json=[
                portal(RC + "0001XY", 1, "CALLE DE PRUEBA 1, Madrid"),
                portal("", 3, "CALLE DE PRUEBA 3, Madrid"),
                portal(OTHER_RC, 0, "CALLE DE PRUEBA, Madrid", kind="callejero"),
            ],
        )
    )
    response = client.get("/api/v1/investors/parcels/candidates", params={"q": "calle de prueba"})
    assert response.status_code == 200, response.text
    body = ParcelCandidatesResponse.model_validate(response.json()).data
    assert [(c.rc14, c.address) for c in body.candidates] == [(RC, "Calle de Prueba 1, Madrid")]
    assert body.needs_number is False
    assert body.sources[0].attribution.startswith(
        "Geocodificación: © Instituto Geográfico Nacional"
    )


@respx.mock
def test_a_street_without_number_asks_for_it() -> None:
    respx.get(url__startswith=CARTOCIUDAD).mock(
        return_value=httpx.Response(
            200, json=[portal("", 0, "CALLE DE PRUEBA, Madrid", "callejero")]
        )
    )
    body = ParcelCandidatesResponse.model_validate(
        client.get("/api/v1/investors/parcels/candidates", params={"q": "calle de prueba"}).json()
    ).data
    assert body.candidates == [] and body.needs_number is True


def test_candidates_need_four_letters() -> None:
    assert (
        client.get("/api/v1/investors/parcels/candidates", params={"q": "may"}).status_code == 422
    )


# --- The guard on the upstream services ---


@respx.mock
def test_only_cache_misses_spend_the_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PARCEL_GUARD_PER_MINUTE", "2")
    parcel_sheet.settings.cache_clear()
    mock_catastro(respx.mock)
    mock_sigma(respx.mock)
    ip = {"X-Forwarded-For": "203.0.113.7"}
    for _ in range(5):  # the same parcel: one miss, then the cache
        sheet_of(client.get("/api/v1/investors/parcels", params={"rc": RC}, headers=ip))
    sheet_of(client.get("/api/v1/investors/parcels", params={"rc": OTHER_RC}, headers=ip))
    third = client.get("/api/v1/investors/parcels", params={"rc": DH_RC}, headers=ip)
    assert third.status_code == 429
    assert third.json()["detail"]["code"] == "RATE_LIMITED"
    assert 1 <= int(third.headers["retry-after"]) <= 60
    # Another client has its own budget; a demo parcel is served from its saved sheet
    other_ip = {"X-Forwarded-For": "198.51.100.4, 10.0.0.1"}
    sheet_of(client.get("/api/v1/investors/parcels", params={"rc": DH_RC}, headers=other_ip))
    demo = client.get("/api/v1/investors/parcels", params={"rc": DEMO_RC}, headers=ip)
    assert sheet_of(demo).data.fallback == "demo_snapshot"


# --- The demo sheets ---


def test_the_demo_sheets_are_our_fields_for_the_four_parcels() -> None:
    snapshot = parcel_sheet.demo_snapshot()
    assert parcel_sheet.demo_rcs() == [
        "2122202VK4722A",
        "3959601VK4735H",
        "0390314VK4709A",
        "9943003VK3794D",
    ]
    kinds = [d.buildability.kind.value for d in snapshot.parcels]
    assert kinds == ["oficial", "oficial", "sin_dato", "supuesto"]
    raw = parcel_sheet.DEMO_PATH.read_text(encoding="utf-8")
    for key in RAW_KEYS:
        assert f'"{key}"' not in raw
    divided = snapshot.parcels[3].parcel
    assert divided.horizontal_division and divided.units is not None
    assert all(set(u.model_dump()) == {"use", "count", "built_m2"} for u in divided.units.by_use)
