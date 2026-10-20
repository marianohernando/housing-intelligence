# pyright: reportAttributeAccessIssue=false
# geoalchemy2 registers create/drop_geospatial_* on alembic.op at runtime.
"""Foundation: source/dataset registries, ingestion runs and canonical geography (admin units, H3).

Revision ID: 0001
Revises: none
Create Date: 2026-10-20 10:26:32.126623+00:00
"""

from collections.abc import Sequence

import geoalchemy2  # noqa: F401  (registers geospatial alembic ops)
import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Idempotent: no-op on Supabase, where extensions already live in schema `extensions`.
    op.execute("CREATE SCHEMA IF NOT EXISTS extensions")
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA extensions")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions")
    op.create_geospatial_table(
        "h3_cell",
        sa.Column("h3_index", sa.Text(), nullable=False),
        sa.Column("resolution", sa.SmallInteger(), nullable=False),
        sa.Column(
            "geom_4326",
            Geometry(
                geometry_type="POLYGON",
                srid=4326,
                dimension=2,
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                nullable=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "centroid_4326",
            Geometry(
                geometry_type="POINT",
                srid=4326,
                dimension=2,
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                nullable=False,
            ),
            nullable=False,
        ),
        sa.CheckConstraint("resolution IN (7, 8, 9, 10)", name=op.f("ck_h3_cell_resolution")),
        sa.PrimaryKeyConstraint("h3_index", name=op.f("pk_h3_cell")),
    )
    op.create_geospatial_index(
        "ix_h3_cell_geom_4326",
        "h3_cell",
        ["geom_4326"],
        unique=False,
        postgresql_using="gist",
        postgresql_ops={},
    )
    op.create_index("ix_h3_cell_resolution", "h3_cell", ["resolution"], unique=False)
    op.create_table(
        "source_registry",
        sa.Column("source_id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("source_type", sa.Text(), nullable=False),
        sa.Column("api_type", sa.Text(), nullable=False),
        sa.Column("base_url", sa.Text(), nullable=True),
        sa.Column("catalog_url", sa.Text(), nullable=True),
        sa.Column("license_name", sa.Text(), nullable=True),
        sa.Column("license_url", sa.Text(), nullable=True),
        sa.Column("license_status", sa.Text(), nullable=False),
        sa.Column("attribution_text", sa.Text(), nullable=True),
        sa.Column("commercial_use", sa.Boolean(), nullable=True),
        sa.Column("redistribution_allowed", sa.Boolean(), nullable=True),
        sa.Column("trust_tier", sa.Text(), nullable=False),
        sa.Column("default_confidence", sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column("update_frequency", sa.Text(), nullable=True),
        sa.Column("geographic_scope", sa.Text(), nullable=True),
        sa.Column("terms_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "api_type IN ('ckan', 'arcgis_hub', 'dcat_apidata', 'ogc_wfs', 'download', 'none')",
            name=op.f("ck_source_registry_api_type"),
        ),
        sa.CheckConstraint(
            "license_status IN ('CLEAR', 'RESTRICTED', 'PERMISSION_REQUIRED', 'RESEARCH_ONLY', 'REJECTED', 'PENDING_REVIEW')",
            name=op.f("ck_source_registry_license_status"),
        ),
        sa.CheckConstraint(
            "trust_tier IN ('A_OFFICIAL', 'B_OPEN_STRUCTURED', 'C_COMMERCIAL_API', 'D_SCRAPED')",
            name=op.f("ck_source_registry_trust_tier"),
        ),
        sa.PrimaryKeyConstraint("source_id", name=op.f("pk_source_registry")),
    )
    op.create_table(
        "dataset_registry",
        sa.Column("dataset_id", sa.Text(), nullable=False),
        sa.Column("source_id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("domain", sa.Text(), nullable=False),
        sa.Column("owner", sa.Text(), nullable=False),
        sa.Column("format", sa.Text(), nullable=False),
        sa.Column("geography", sa.Text(), nullable=False),
        sa.Column("geo_resolution", sa.Text(), nullable=False),
        sa.Column("temporal_resolution", sa.Text(), nullable=True),
        sa.Column("refresh_policy", sa.Text(), nullable=False),
        sa.Column("landing_url", sa.Text(), nullable=True),
        sa.Column("license_status", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("priority", sa.Text(), nullable=False),
        sa.Column(
            "scorecard",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("catalog_yaml_path", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "license_status IN ('CLEAR', 'RESTRICTED', 'PERMISSION_REQUIRED', 'RESEARCH_ONLY', 'REJECTED', 'PENDING_REVIEW')",
            name=op.f("ck_dataset_registry_license_status"),
        ),
        sa.CheckConstraint(
            "priority IN ('P0', 'P1', 'P2', 'P3')", name=op.f("ck_dataset_registry_priority")
        ),
        sa.CheckConstraint(
            "status IN ('DISCOVERED', 'REVIEWED', 'INGESTING', 'VALIDATED', 'PRODUCTION', 'DEGRADED', 'RETIRED')",
            name=op.f("ck_dataset_registry_status"),
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["source_registry.source_id"],
            name=op.f("fk_dataset_registry_source_id_source_registry"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("dataset_id", name=op.f("pk_dataset_registry")),
    )
    op.create_index(
        op.f("ix_dataset_registry_source_id"), "dataset_registry", ["source_id"], unique=False
    )
    op.create_table(
        "dataset_version",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("dataset_id", sa.Text(), nullable=False),
        sa.Column("version_label", sa.Text(), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_modified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("checksum_sha256", sa.Text(), nullable=False),
        sa.Column("byte_size", sa.BigInteger(), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("schema_hash", sa.Text(), nullable=True),
        sa.Column("parser_version", sa.Text(), nullable=False),
        sa.Column("quality_status", sa.Text(), nullable=True),
        sa.Column("bronze_manifest_path", sa.Text(), nullable=False),
        sa.Column("is_last_valid", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["dataset_id"],
            ["dataset_registry.dataset_id"],
            name=op.f("fk_dataset_version_dataset_id_dataset_registry"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_dataset_version")),
        sa.UniqueConstraint(
            "dataset_id",
            "checksum_sha256",
            name=op.f("uq_dataset_version_dataset_id_checksum_sha256"),
        ),
    )
    op.create_index(
        op.f("ix_dataset_version_dataset_id"), "dataset_version", ["dataset_id"], unique=False
    )
    op.create_geospatial_table(
        "geo_admin_unit",
        sa.Column("admin_unit_id", sa.Text(), nullable=False),
        sa.Column("level", sa.Text(), nullable=False),
        sa.Column("code_official", sa.Text(), nullable=False),
        sa.Column("code_source", sa.Text(), nullable=True),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("parent_admin_unit_id", sa.Text(), nullable=True),
        sa.Column(
            "geom_4326",
            Geometry(
                geometry_type="MULTIPOLYGON",
                srid=4326,
                dimension=2,
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                nullable=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "geom_25830",
            Geometry(
                geometry_type="MULTIPOLYGON",
                srid=25830,
                dimension=2,
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                nullable=False,
            ),
            nullable=False,
        ),
        sa.Column("area_m2", sa.Float(), nullable=False),
        sa.Column("source_id", sa.Text(), nullable=False),
        sa.Column("dataset_version_id", sa.UUID(), nullable=False),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "level IN ('ccaa', 'provincia', 'municipio', 'distrito', 'barrio', 'seccion_censal')",
            name=op.f("ck_geo_admin_unit_level"),
        ),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_version.id"],
            name=op.f("fk_geo_admin_unit_dataset_version_id_dataset_version"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["parent_admin_unit_id"],
            ["geo_admin_unit.admin_unit_id"],
            name=op.f("fk_geo_admin_unit_parent_admin_unit_id_geo_admin_unit"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["source_registry.source_id"],
            name=op.f("fk_geo_admin_unit_source_id_source_registry"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("admin_unit_id", name=op.f("pk_geo_admin_unit")),
        sa.UniqueConstraint(
            "level", "code_official", name=op.f("uq_geo_admin_unit_level_code_official")
        ),
    )
    op.create_index(
        op.f("ix_geo_admin_unit_dataset_version_id"),
        "geo_admin_unit",
        ["dataset_version_id"],
        unique=False,
    )
    op.create_geospatial_index(
        "ix_geo_admin_unit_geom_25830",
        "geo_admin_unit",
        ["geom_25830"],
        unique=False,
        postgresql_using="gist",
        postgresql_ops={},
    )
    op.create_geospatial_index(
        "ix_geo_admin_unit_geom_4326",
        "geo_admin_unit",
        ["geom_4326"],
        unique=False,
        postgresql_using="gist",
        postgresql_ops={},
    )
    op.create_index(
        op.f("ix_geo_admin_unit_parent_admin_unit_id"),
        "geo_admin_unit",
        ["parent_admin_unit_id"],
        unique=False,
    )
    op.create_table(
        "ingestion_run",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("dataset_id", sa.Text(), nullable=False),
        sa.Column("dataset_version_id", sa.UUID(), nullable=True),
        sa.Column("correlation_id", sa.Text(), nullable=False),
        sa.Column("stage", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "metrics",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("error", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "stage IN ('DISCOVER', 'FETCH', 'SNAPSHOT', 'SCHEMA_CHECK', 'PARSE', 'NORMALIZE', 'GEO_RESOLVE', 'ENTITY_RESOLUTION', 'QUALITY_CHECK', 'PUBLISH_SILVER', 'BUILD_FEATURES')",
            name=op.f("ck_ingestion_run_stage"),
        ),
        sa.CheckConstraint(
            "status IN ('RUNNING', 'SUCCESS', 'FAILED', 'SKIPPED')",
            name=op.f("ck_ingestion_run_status"),
        ),
        sa.ForeignKeyConstraint(
            ["dataset_id"],
            ["dataset_registry.dataset_id"],
            name=op.f("fk_ingestion_run_dataset_id_dataset_registry"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_version.id"],
            name=op.f("fk_ingestion_run_dataset_version_id_dataset_version"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ingestion_run")),
    )
    op.create_index(
        op.f("ix_ingestion_run_correlation_id"), "ingestion_run", ["correlation_id"], unique=False
    )
    op.create_index(
        op.f("ix_ingestion_run_dataset_id"), "ingestion_run", ["dataset_id"], unique=False
    )
    op.create_table(
        "h3_cell_admin_unit",
        sa.Column("h3_index", sa.Text(), nullable=False),
        sa.Column("admin_unit_id", sa.Text(), nullable=False),
        sa.Column("method", sa.Text(), nullable=False),
        sa.Column("overlap_share", sa.Float(), nullable=False),
        sa.CheckConstraint(
            "method IN ('centroid', 'overlap', 'population_weighted', 'network_access')",
            name=op.f("ck_h3_cell_admin_unit_method"),
        ),
        sa.CheckConstraint(
            "overlap_share > 0 AND overlap_share <= 1.000001",
            name=op.f("ck_h3_cell_admin_unit_overlap_share"),
        ),
        sa.ForeignKeyConstraint(
            ["admin_unit_id"],
            ["geo_admin_unit.admin_unit_id"],
            name=op.f("fk_h3_cell_admin_unit_admin_unit_id_geo_admin_unit"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["h3_index"],
            ["h3_cell.h3_index"],
            name=op.f("fk_h3_cell_admin_unit_h3_index_h3_cell"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "h3_index", "admin_unit_id", "method", name=op.f("pk_h3_cell_admin_unit")
        ),
    )
    op.create_index(
        op.f("ix_h3_cell_admin_unit_admin_unit_id"),
        "h3_cell_admin_unit",
        ["admin_unit_id"],
        unique=False,
    )


def downgrade() -> None:
    # Extensions are shared infrastructure and are intentionally not dropped.
    op.drop_index(op.f("ix_h3_cell_admin_unit_admin_unit_id"), table_name="h3_cell_admin_unit")
    op.drop_table("h3_cell_admin_unit")
    op.drop_index(op.f("ix_ingestion_run_dataset_id"), table_name="ingestion_run")
    op.drop_index(op.f("ix_ingestion_run_correlation_id"), table_name="ingestion_run")
    op.drop_table("ingestion_run")
    op.drop_index(op.f("ix_geo_admin_unit_parent_admin_unit_id"), table_name="geo_admin_unit")
    op.drop_geospatial_index(
        "ix_geo_admin_unit_geom_4326",
        table_name="geo_admin_unit",
        postgresql_using="gist",
        column_name="geom_4326",
    )
    op.drop_geospatial_index(
        "ix_geo_admin_unit_geom_25830",
        table_name="geo_admin_unit",
        postgresql_using="gist",
        column_name="geom_25830",
    )
    op.drop_index(op.f("ix_geo_admin_unit_dataset_version_id"), table_name="geo_admin_unit")
    op.drop_geospatial_table("geo_admin_unit")
    op.drop_index(op.f("ix_dataset_version_dataset_id"), table_name="dataset_version")
    op.drop_table("dataset_version")
    op.drop_index(op.f("ix_dataset_registry_source_id"), table_name="dataset_registry")
    op.drop_table("dataset_registry")
    op.drop_table("source_registry")
    op.drop_index("ix_h3_cell_resolution", table_name="h3_cell")
    op.drop_geospatial_index(
        "ix_h3_cell_geom_4326",
        table_name="h3_cell",
        postgresql_using="gist",
        column_name="geom_4326",
    )
    op.drop_geospatial_table("h3_cell")
