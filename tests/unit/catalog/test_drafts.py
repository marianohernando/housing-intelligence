from datetime import UTC, datetime

from hi_contracts.catalog import DatasetSpec
from hi_contracts.catalog.candidate import CandidateRecord, CandidateResource
from hi_domain.catalog.scoring import score_candidate
from hi_ingestion.catalog_harvester.drafts import _deep_merge, draft_dataset_id, to_draft


def _cand(**kw: object) -> CandidateRecord:
    base: dict[str, object] = {
        "candidate_id": "comunidad_madrid_ckan:1934259",
        "source_id": "comunidad_madrid_ckan",
        "external_id": "1934259",
        "name": "estadistica_1934259",
        "title": "Alquiler del metro cuadrado medio mensual por código postal",
        "formats": ["CSV", "JSON"],
        "license_id": "cc-by",
        "landing_url": "https://datos.comunidad.madrid/dataset/1934259",
        "resources": [
            CandidateResource(name="csv", format="CSV", url="https://datos.comunidad.madrid/x.csv"),
            CandidateResource(name="bad", format="CSV", url="not a url"),
        ],
        "modified_at": datetime(2026, 8, 1, tzinfo=UTC),
    }
    return CandidateRecord.model_validate(base | kw)


def test_draft_is_a_valid_dataset_spec_and_never_p0() -> None:
    draft = to_draft(score_candidate(_cand()))
    spec = DatasetSpec.model_validate(draft)
    assert spec.priority != "P0"
    assert spec.status == "DISCOVERED"
    assert spec.license_status == "CLEAR"
    assert len(spec.resources) == 1  # invalid URL dropped


def test_draft_ids_are_stable_and_valid() -> None:
    scored = score_candidate(_cand())
    assert draft_dataset_id(scored) == draft_dataset_id(scored)
    assert draft_dataset_id(scored).startswith("cm_ie1934259_")


def test_unknown_license_needs_review() -> None:
    draft = to_draft(score_candidate(_cand(license_id=None, source_id="datos_gob_es")))
    assert draft["license_status"] == "PENDING_REVIEW"


def test_deep_merge_keeps_unrelated_keys() -> None:
    merged = _deep_merge(
        {"geo": {"resolution": "unknown", "crs": "x"}, "a": 1}, {"geo": {"resolution": "point"}}
    )
    assert merged == {"geo": {"resolution": "point", "crs": "x"}, "a": 1}
