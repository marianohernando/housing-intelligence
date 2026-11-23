"""D-248 on the fixture database: the pilot list and a barrio's sheet, with line A's figures
(commerce, buildable area left, vacant land) missing, as until they are loaded: null with their
reason, never 0. The pilot is the fixture's two sample barrios of Centro."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, event

from hi_api.deps import get_engine
from hi_api.main import app
from hi_api.services import investors
from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.catalog.pipeline import PermitBudgetPipeline
from hi_contracts.pro.investors import ValueMark
from hi_contracts.public.responses import (
    DatasetListResponse,
    InvestorZoneListResponse,
    InvestorZoneResponse,
)
from hi_domain.viability_data import CRG_URL, PEM_EUR_M2, REFERENCE_PEM_EUR_M2
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.permits.run import run_permit_budget_pipeline

pytestmark = pytest.mark.db
PILOT = (("28079011", "Palacio", "Centro"), ("28079016", "Sol", "Centro"))


@pytest.fixture
def client(
    migrated_engine: Engine, features_computed: None, monkeypatch: pytest.MonkeyPatch
) -> TestClient:
    monkeypatch.setattr(investors, "PILOT_BARRIOS", PILOT)
    app.dependency_overrides[get_engine] = lambda: migrated_engine
    return TestClient(app)


def test_the_pilot_list_has_its_barrios_and_their_district(client: TestClient) -> None:
    response = client.get("/api/v1/investors/zones")
    assert response.status_code == 200, response.text
    body = InvestorZoneListResponse.model_validate(response.json())
    zones = {z.zone.code: z for z in body.data.zones}
    assert set(zones) == {"28079011", "28079016"}
    palacio = zones["28079011"]
    assert palacio.zone.admin_unit_id == "ES.28.BAR.28079011"
    assert palacio.district.code == "2807901"
    # Line A's figures (D-247), on the fixture database since #95
    assert palacio.commerce_per_1000 is not None
    assert palacio.remaining_m2 is not None  # a confirmed 0 when no area is left
    assert body.data.pilot == investors.PILOT_TEXT


def test_a_barrio_sheet_says_where_each_figure_comes_from(client: TestClient) -> None:
    response = client.get("/api/v1/investors/zones/ES.28.BAR.28079011")
    assert response.status_code == 200, response.text
    body = InvestorZoneResponse.model_validate(response.json())
    sheet = body.data
    assert sheet.zone.name and sheet.district.code == "2807901"
    for figure in [*sheet.demand.model_dump().values(), *sheet.prices.model_dump().values()]:
        assert figure["source"]["text"]
        assert (figure["value"] is None) == (figure["null_reason"] is not None)
    # Line A's figures (D-247): read by their id, each with its dataset; never 0 for unknown
    assert sheet.gaps is not None
    commerce = {f.feature_id: f for f in sheet.gaps.commerce}
    assert set(commerce) == set(investors.COMMERCE)
    for feature_id in ("comercio_proximidad_1000hab", "locales_abiertos_1000hab"):
        figure = commerce[feature_id]
        assert figure.value is not None and figure.null_reason is None
        assert "ayto_censo_locales_actividades" in figure.source.dataset_ids  # and the padrón
        assert figure.source.level is TerritoryLevel.BARRIO
    remaining = sheet.land.remaining_m2
    assert remaining.value is not None
    assert "ayto_edificabilidad_remanente_ambitos" in remaining.source.dataset_ids
    assert not any("not loaded" in w for w in body.warnings)
    # Defaults: data and assumptions marked as such
    # D-252: the default PEM is the CRG's assumption; the CM permits' PEM stays as the low
    # reference, a figure with its feature and dataset
    assert sheet.defaults.pem_m2.value == REFERENCE_PEM_EUR_M2
    assert sheet.defaults.pem_m2.mark is ValueMark.SUPUESTO
    assert str(sheet.defaults.pem_m2.source.url) == CRG_URL
    permits = sheet.defaults.pem_permits_m2
    assert permits is not None and permits.value == PEM_EUR_M2
    assert permits.mark is ValueMark.DATO
    assert sheet.defaults.cost_coefficient.mark is ValueMark.SUPUESTO
    assert sheet.defaults.sale_price_m2.mark is ValueMark.ESTIMACION  # D-234: shared out
    assert sum(p.pct for p in sheet.defaults.cost_parts) == pytest.approx(35.75)
    assert sheet.notices[0].startswith("No es una tasación")


def test_the_gaps_are_the_district_list(client: TestClient) -> None:
    sheet = InvestorZoneResponse.model_validate(
        client.get("/api/v1/investors/zones/ES.28.BAR.28079016").json()
    ).data
    district = client.get("/api/v1/gaps/distrito/2807901").json()["data"]
    assert sheet.gaps is not None
    assert [r.row.value for r in sheet.gaps.rows] == [r["row"] for r in district["rows"]]
    assert [r.status.value for r in sheet.gaps.rows] == [r["status"] for r in district["rows"]]


def test_a_barrio_out_of_the_pilot_is_not_found(client: TestClient) -> None:
    response = client.get("/api/v1/investors/zones/ES.28.BAR.28079191")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "NOT_FOUND"


def test_the_pem_comes_from_its_cm_dataset_once_loaded(
    client: TestClient, migrated_engine: Engine, tmp_path: Path
) -> None:
    """D-248: the versioned table loads as a CM dataset (it counts in /datasets) and the sheet
    takes the PEM from the Feature Store, with its dataset; the same figure as the fallback."""
    from hi_features.compute import compute, persist

    catalog = load_catalog()
    spec = catalog.pipelines["cm_visados_presupuesto_obra"]
    assert isinstance(spec, PermitBudgetPipeline)
    summary = run_permit_budget_pipeline(
        migrated_engine, catalog, spec, evidence_root=None, data_dir=tmp_path
    )
    assert summary.status == "SUCCESS"
    feature = catalog.features[investors.PEM]
    persist(migrated_engine, feature, compute(migrated_engine, feature))

    sheet = InvestorZoneResponse.model_validate(
        client.get("/api/v1/investors/zones/ES.28.BAR.28079011").json()
    ).data
    pem = sheet.defaults.pem_permits_m2  # D-252: the low reference, still the CM dataset
    assert pem is not None and pem.value == PEM_EUR_M2
    assert pem.feature_id == investors.PEM
    assert pem.source.dataset_ids == ["cm_visados_presupuesto_obra"]
    assert pem.source.level is TerritoryLevel.CCAA
    assert sheet.defaults.pem_m2.value == REFERENCE_PEM_EUR_M2  # the calculator's default
    listed = DatasetListResponse.model_validate(client.get("/api/v1/datasets").json()).data
    visados = [d for d in listed.datasets if d.dataset_id == "cm_visados_presupuesto_obra"]
    assert len(visados) == 1 and visados[0].is_cm_open_data


def test_the_pilot_list_takes_a_handful_of_queries_whatever_its_size(
    client: TestClient, migrated_engine: Engine
) -> None:
    """Review of #94: the list asked for each zone's name one at a time (~216 queries for the
    108 pilot barrios). Now a fixed number, with the gap maps cached as in GET /gaps."""
    client.get("/api/v1/investors/zones")  # warms the cached row maps
    statements: list[str] = []

    def count(*args: object) -> None:
        statements.append(str(args[2]))

    event.listen(migrated_engine, "before_cursor_execute", count)
    try:
        assert client.get("/api/v1/investors/zones").status_code == 200
    finally:
        event.remove(migrated_engine, "before_cursor_execute", count)
    assert len(statements) <= 8, statements
