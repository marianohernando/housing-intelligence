"""DATA-022 on the fixtures: official spellings land in geo_admin_unit with their run recorded."""

from pathlib import Path

import pytest
from sqlalchemy import Engine, text

from hi_domain.geo.names import invalid_name_chars
from hi_ingestion.pipelines.admin_boundaries.official_names import apply_official_names

pytestmark = pytest.mark.db


def test_official_names_replace_the_csv_spelling(
    fixtures_ingested: None, migrated_engine: Engine, tmp_path: Path
) -> None:
    summary = apply_official_names(migrated_engine, evidence_root=tmp_path)
    assert summary.status == "SUCCESS", summary.quality
    assert summary.quality["passed"]
    assert summary.evidence_dir is not None
    assert (summary.evidence_dir / "changes.json").exists()
    with migrated_engine.connect() as conn:
        names = dict(
            conn.execute(
                text(
                    "SELECT admin_unit_id, name FROM geo_admin_unit "
                    "WHERE level IN ('municipio', 'distrito', 'barrio') AND name IS NOT NULL"
                )
            ).all()
        )
        recorded = conn.execute(
            text(
                "SELECT metrics FROM ingestion_run WHERE correlation_id = :c "
                "AND stage = 'NORMALIZE'"
            ),
            {"c": summary.correlation_id},
        ).scalar_one()
    assert names["ES.28.MUN.28001"] == "Acebeda (La)"  # CSV: "ACEBEDA, LA"
    assert names["ES.28.DIS.2800101"] == "Acebeda (La) — distrito censal 01"
    assert names["ES.28.DIS.2807905"] == "Chamartín"
    assert {u: invalid_name_chars(n) for u, n in names.items() if invalid_name_chars(n)} == {}
    assert recorded["step"] == "official_names"
    assert set(recorded["names_from"]) == {
        "cm_poblacion_edad_nacionalidad_sexo",
        "ayto_panel_indicadores_distritos_barrios",
    }


def test_second_run_changes_nothing(fixtures_ingested: None, migrated_engine: Engine) -> None:
    apply_official_names(migrated_engine, evidence_root=None)
    again = apply_official_names(migrated_engine, evidence_root=None)
    assert again.status == "SUCCESS"
    assert again.counts["changes"] == 0
