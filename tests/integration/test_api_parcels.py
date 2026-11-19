"""D-250 on the fixture database: the barrio around a parcel, read only with PostGIS. In a pilot
barrio the sheet brings its whole investor sheet (D-248); outside the pilot, its district's
figures and a note; on a point of no barrio, no context and a warning. No upstream is called:
the parcel itself comes from a stub, placed inside a fixture barrio."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from hi_api.deps import get_engine
from hi_api.main import app
from hi_api.services import investors, parcel_sheet
from hi_api.services.parcels import to_lonlat
from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.pro.investors import Buildability, BuildabilityKind, ParcelBlock
from hi_contracts.public.responses import ParcelSheetResponse

pytestmark = pytest.mark.db
PILOT = (("28079011", "Palacio", "Centro"), ("28079016", "Sol", "Centro"))
RC = "1111111VK1111A"  # made up

_INSIDE = text(
    """
    SELECT ST_X(p) AS x, ST_Y(p) AS y
      FROM (SELECT ST_PointOnSurface(geom_25830) AS p FROM geo_admin_unit
             WHERE level = 'barrio' AND code_official = :code) s
    """
)


@pytest.fixture
def client(
    migrated_engine: Engine, features_computed: None, monkeypatch: pytest.MonkeyPatch
) -> Iterator[TestClient]:
    monkeypatch.setattr(investors, "PILOT_BARRIOS", PILOT)
    app.dependency_overrides[get_engine] = lambda: migrated_engine
    parcel_sheet.CACHE.clear()
    yield TestClient(app)
    app.dependency_overrides.pop(get_engine, None)


def stub_parcel_at(monkeypatch: pytest.MonkeyPatch, engine: Engine, barrio: str | None) -> None:
    """The parcel the lookup finds: inside `barrio` of the fixture, or far from any (None)."""
    if barrio is None:
        lon, lat = -3.60, 40.40
    else:
        with engine.connect() as conn:
            point = conn.execute(_INSIDE, {"code": barrio}).mappings().one()
        lon, lat = to_lonlat(point["x"], point["y"])
    parcel = ParcelBlock.model_validate(
        {
            "rc14": RC,
            "address": "Calle de Prueba 1, 28001 Madrid",
            "lat": lat,
            "lon": lon,
            "area_m2": 500,
            "rustic": False,
            "is_vacant": True,
            "horizontal_division": False,
            "units": None,
            "built_m2": 0,
            "current_use": None,
            "official_url": None,
            "observed_at": "2026-11-19",
        }
    )
    built = Buildability(value_m2=None, kind=BuildabilityKind.SIN_DATO, source="x")

    async def parts(
        rc14: str, lookup: parcel_sheet.Lookup, deadline: float | None = None
    ) -> parcel_sheet.Parts:
        return parcel_sheet.Parts(parcel, None, built, [])

    monkeypatch.setattr(parcel_sheet, "live_parts", parts)


def get(client: TestClient) -> ParcelSheetResponse:
    response = client.get("/api/v1/investors/parcels", params={"rc": RC})
    assert response.status_code == 200, response.text
    return ParcelSheetResponse.model_validate(response.json())


def test_a_parcel_in_a_pilot_barrio_brings_its_investor_sheet(
    client: TestClient, migrated_engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    stub_parcel_at(monkeypatch, migrated_engine, "28079011")
    body = get(client)
    sheet = body.data
    assert sheet.barrio is not None and sheet.barrio.code == "28079011"
    assert sheet.district is not None and sheet.district.code == "2807901"
    context = sheet.context
    assert context is not None and context.in_pilot and context.level is TerritoryLevel.BARRIO
    assert context.note is None
    assert context.sheet.zone.code == "28079011"
    assert sheet.defaults == context.sheet.defaults  # the calculator starts from the barrio's
    assert body.meta.data_version is not None
    assert "context" not in sheet.degraded


def test_outside_the_pilot_the_context_is_the_district_and_says_so(
    client: TestClient, migrated_engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(investors, "PILOT_BARRIOS", PILOT[1:])  # Palacio out
    stub_parcel_at(monkeypatch, migrated_engine, "28079011")
    sheet = get(client).data
    context = sheet.context
    assert context is not None and not context.in_pilot
    assert context.level is TerritoryLevel.DISTRITO
    assert context.sheet.zone.level is TerritoryLevel.DISTRITO
    assert context.sheet.zone.code == "2807901"
    assert context.note is not None and "fuera del piloto" in context.note
    assert sheet.barrio is not None and sheet.barrio.code == "28079011"
    # No figure of the barrio: each comes from the district or the city
    for figure in context.sheet.demand.model_dump().values():
        assert figure["source"]["level"] in {None, "distrito", "municipio"}


def test_a_point_in_no_barrio_has_no_context_and_a_warning(
    client: TestClient, migrated_engine: Engine, monkeypatch: pytest.MonkeyPatch
) -> None:
    stub_parcel_at(monkeypatch, migrated_engine, None)
    body = get(client)
    assert body.data.context is None and body.data.barrio is None
    assert "OUT_OF_COVERAGE: the point is in no barrio" in body.warnings
    assert body.data.defaults.pem_m2.value is not None
