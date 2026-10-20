from datetime import UTC, datetime

from hypothesis import given
from hypothesis import strategies as st

from hi_contracts.catalog.candidate import CandidateRecord
from hi_contracts.catalog.enums import Domain, GeoResolution, Priority
from hi_domain.catalog.scoring import score_candidate

NOW = datetime(2026, 10, 20, tzinfo=UTC)


def _cand(title: str, **kw: object) -> CandidateRecord:
    base: dict[str, object] = {
        "candidate_id": "comunidad_madrid_ckan:x",
        "source_id": "comunidad_madrid_ckan",
        "external_id": "x",
        "name": "x",
        "title": title,
        "formats": ["CSV"],
        "license_id": "cc-by",
        "modified_at": datetime(2026, 8, 1, tzinfo=UTC),
    }
    return CandidateRecord.model_validate(base | kw)


def test_rent_by_postcode_is_core_p1() -> None:
    s = score_candidate(_cand("Alquiler medio mensual de viviendas por código postal"), NOW)
    assert s.domain is Domain.HOUSING
    assert s.geo_resolution is GeoResolution.CODIGO_POSTAL
    assert s.priority_draft is Priority.P1


def test_title_subject_wins_ties() -> None:
    s = score_candidate(
        _cand("Afiliados a la Seguridad Social por 1.000 habitantes. Municipios"), NOW
    )
    assert s.domain is Domain.EMPLOYMENT


def test_statistical_tables_are_not_points() -> None:
    c = _cand("Población reclusa por centros penitenciarios", extra={"organization": "estadistica"})
    assert score_candidate(c, NOW).geo_resolution is not GeoResolution.POINT


def test_gtfs_is_point_data() -> None:
    s = score_candidate(
        _cand("GTFS Red de Metro", source_id="crtm_open_data", license_id="CRTM-LDA"), NOW
    )
    assert s.domain is Domain.TRANSPORT
    assert s.geo_resolution is GeoResolution.POINT


def test_unrelated_dataset_is_low_priority() -> None:
    s = score_candidate(_cand("Explotaciones apícolas"), NOW)
    assert s.priority_draft is Priority.P3


@given(
    st.text(max_size=120),
    st.sampled_from(["comunidad_madrid_ckan", "datos_gob_es", "crtm_open_data", "zz"]),
)
def test_scores_are_bounded_and_never_p0(title: str, source_id: str) -> None:
    s = score_candidate(_cand(title or "x", source_id=source_id), NOW)
    for value in s.scorecard.model_dump(exclude={"notes", "reviewed_by", "reviewed_at"}).values():
        assert value is None or 0 <= value <= 5
    assert s.priority_draft is not Priority.P0
    assert 0 <= s.composite <= 5


@given(st.text(max_size=80))
def test_housing_keyword_in_title_never_lowers_impact(title: str) -> None:
    base = score_candidate(_cand(title or "x"), NOW).scorecard.product_impact or 0
    boosted = score_candidate(_cand(f"Vivienda {title}"), NOW).scorecard.product_impact or 0
    assert boosted >= min(base, 5)
