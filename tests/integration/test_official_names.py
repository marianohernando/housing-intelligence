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
    assert names["ES.28.BAR.28079055"] == "Nueva España"  # from the Ayuntamiento panel (D-232)
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


def test_a_broken_name_blocks_every_change(
    fixtures_ingested: None, migrated_engine: Engine
) -> None:
    def name_of(unit_id: str) -> str:
        with migrated_engine.connect() as conn:
            return conn.execute(
                text("SELECT name FROM geo_admin_unit WHERE admin_unit_id = :u"), {"u": unit_id}
            ).scalar_one()

    def set_name(unit_id: str, name: str) -> None:
        with migrated_engine.begin() as conn:
            conn.execute(
                text("UPDATE geo_admin_unit SET name = :n WHERE admin_unit_id = :u"),
                {"n": name, "u": unit_id},
            )

    def set_source_name(unit_id: str, name: str) -> None:
        """The barrio's name as the panel writes it (D-232: barrios take it from there)."""
        with migrated_engine.begin() as conn:
            conn.execute(
                text("UPDATE metric_observation SET territory_name = :n WHERE admin_unit_id = :u"),
                {"n": name, "u": unit_id},
            )

    with migrated_engine.connect() as conn:
        barrio, barrio_name = conn.execute(
            text("SELECT admin_unit_id, name FROM geo_admin_unit WHERE level = 'barrio' LIMIT 1")
        ).one()
    set_name("ES.28.MUN.28001", "ACEBEDA, LA")
    set_source_name(barrio, "PE/A GRANDE")
    try:
        failed = apply_official_names(migrated_engine, evidence_root=None)
        assert failed.status == "FAILED"
        invalid = next(c for c in failed.quality["checks"] if c["name"].startswith("names_use"))
        assert invalid["details"]["sample"] == {barrio: ["/"]}
        assert name_of("ES.28.MUN.28001") == "ACEBEDA, LA"  # nothing was written
    finally:
        set_source_name(barrio, barrio_name)
        assert apply_official_names(migrated_engine, evidence_root=None).status == "SUCCESS"
    assert name_of("ES.28.MUN.28001") == "Acebeda (La)"
