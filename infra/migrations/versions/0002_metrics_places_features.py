# pyright: reportAttributeAccessIssue=false
# geoalchemy2 registers create/drop_geospatial_* on alembic.op at runtime.
"""Metric registry and observations, canonical places with aliases, feature registry and values.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-21 23:41:02.127099+00:00
"""

from collections.abc import Sequence

import geoalchemy2  # noqa: F401  (registers geospatial alembic ops)
import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "feature_registry",
        sa.Column("feature_id", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("human_name", sa.Text(), nullable=False),
        sa.Column("domain", sa.Text(), nullable=False),
        sa.Column("unit", sa.Text(), nullable=False),
        sa.Column("direction", sa.Text(), nullable=False),
        sa.Column("geo_level", sa.Text(), nullable=False),
        sa.Column("spec", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("feature_id", name=op.f("pk_feature_registry")),
    )
    op.create_table(
        "metric_registry",
        sa.Column("metric_id", sa.Text(), nullable=False),
        sa.Column("human_name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("domain", sa.Text(), nullable=False),
        sa.Column("unit", sa.Text(), nullable=False),
        sa.Column("direction", sa.Text(), nullable=False),
        sa.Column("aggregation_method", sa.Text(), nullable=False),
        sa.Column("geo_resolution_min", sa.Text(), nullable=False),
        sa.Column("temporal_resolution", sa.Text(), nullable=False),
        sa.Column("dataset_id", sa.Text(), nullable=False),
        sa.Column(
            "dimensions",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("null_policy", sa.Text(), nullable=False),
        sa.Column("public_visible", sa.Boolean(), nullable=False),
        sa.Column("pro_visible", sa.Boolean(), nullable=False),
        sa.Column("sensitive", sa.Boolean(), nullable=False),
        sa.Column("methodology_version", sa.Text(), nullable=False),
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
            "aggregation_method IN ('sum', 'mean', 'weighted_mean', 'count', 'none')",
            name=op.f("ck_metric_registry_aggregation_method"),
        ),
        sa.CheckConstraint(
            "direction IN ('higher_is_better', 'lower_is_better', 'neutral', 'target_range')",
            name=op.f("ck_metric_registry_direction"),
        ),
        sa.CheckConstraint(
            "geo_resolution_min IN ('ccaa', 'municipio', 'distrito', 'barrio', 'seccion_censal', 'codigo_postal', 'zona_estadistica', 'h3_r8', 'h3_r9')",
            name=op.f("ck_metric_registry_geo_resolution_min"),
        ),
        sa.ForeignKeyConstraint(
            ["dataset_id"],
            ["dataset_registry.dataset_id"],
            name=op.f("fk_metric_registry_dataset_id_dataset_registry"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("metric_id", name=op.f("pk_metric_registry")),
    )
    op.create_index(
        op.f("ix_metric_registry_dataset_id"), "metric_registry", ["dataset_id"], unique=False
    )
    op.create_table(
        "feature_value",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("feature_id", sa.Text(), nullable=False),
        sa.Column("feature_version", sa.Integer(), nullable=False),
        sa.Column("territory_level", sa.Text(), nullable=False),
        sa.Column("territory_code", sa.Text(), nullable=False),
        sa.Column("admin_unit_id", sa.Text(), nullable=True),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("null_reason", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column(
            "inputs",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "null_reason IS NULL OR null_reason IN ('NOT_APPLICABLE', 'SOURCE_NO_COVERAGE', 'SOURCE_MISSING', 'TEMPORARILY_UNAVAILABLE', 'STALE', 'PARSE_ERROR', 'ENTITY_NOT_RESOLVED', 'ESTIMATION_NOT_ALLOWED', 'UNKNOWN')",
            name=op.f("ck_feature_value_null_reason"),
        ),
        sa.CheckConstraint(
            "territory_level IN ('ccaa', 'municipio', 'distrito', 'barrio', 'seccion_censal', 'codigo_postal', 'zona_estadistica', 'h3_r8', 'h3_r9')",
            name=op.f("ck_feature_value_territory_level"),
        ),
        sa.CheckConstraint(
            "(value IS NULL) <> (null_reason IS NULL)",
            name=op.f("ck_feature_value_value_xor_null_reason"),
        ),
        sa.CheckConstraint(
            "confidence >= 0 AND confidence <= 1", name=op.f("ck_feature_value_confidence_range")
        ),
        sa.ForeignKeyConstraint(
            ["admin_unit_id"],
            ["geo_admin_unit.admin_unit_id"],
            name=op.f("fk_feature_value_admin_unit_id_geo_admin_unit"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["feature_id"],
            ["feature_registry.feature_id"],
            name=op.f("fk_feature_value_feature_id_feature_registry"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_feature_value")),
        sa.UniqueConstraint(
            "feature_id",
            "feature_version",
            "territory_level",
            "territory_code",
            "period_start",
            name=op.f(
                "uq_feature_value_feature_id_feature_version_territory_level_territory_code_period_start"
            ),
        ),
    )
    op.create_index(
        op.f("ix_feature_value_admin_unit_id"), "feature_value", ["admin_unit_id"], unique=False
    )
    op.create_index(
        "ix_feature_value_lookup",
        "feature_value",
        ["feature_id", "territory_level", "period_start"],
        unique=False,
    )
    op.create_table(
        "metric_observation",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("metric_id", sa.Text(), nullable=False),
        sa.Column("territory_level", sa.Text(), nullable=False),
        sa.Column("territory_code", sa.Text(), nullable=False),
        sa.Column("territory_name", sa.Text(), nullable=True),
        sa.Column("admin_unit_id", sa.Text(), nullable=True),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column(
            "dims",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("dims_key", sa.Text(), server_default=sa.text("''"), nullable=False),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("null_reason", sa.Text(), nullable=True),
        sa.Column("unit", sa.Text(), nullable=True),
        sa.Column("raw_value", sa.Text(), nullable=True),
        sa.Column("dataset_version_id", sa.UUID(), nullable=False),
        sa.CheckConstraint(
            "null_reason IS NULL OR null_reason IN ('NOT_APPLICABLE', 'SOURCE_NO_COVERAGE', 'SOURCE_MISSING', 'TEMPORARILY_UNAVAILABLE', 'STALE', 'PARSE_ERROR', 'ENTITY_NOT_RESOLVED', 'ESTIMATION_NOT_ALLOWED', 'UNKNOWN')",
            name=op.f("ck_metric_observation_null_reason"),
        ),
        sa.CheckConstraint(
            "territory_level IN ('ccaa', 'municipio', 'distrito', 'barrio', 'seccion_censal', 'codigo_postal', 'zona_estadistica', 'h3_r8', 'h3_r9')",
            name=op.f("ck_metric_observation_territory_level"),
        ),
        sa.CheckConstraint(
            "(value IS NULL) <> (null_reason IS NULL)",
            name=op.f("ck_metric_observation_value_xor_null_reason"),
        ),
        sa.ForeignKeyConstraint(
            ["admin_unit_id"],
            ["geo_admin_unit.admin_unit_id"],
            name=op.f("fk_metric_observation_admin_unit_id_geo_admin_unit"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_version.id"],
            name=op.f("fk_metric_observation_dataset_version_id_dataset_version"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["metric_id"],
            ["metric_registry.metric_id"],
            name=op.f("fk_metric_observation_metric_id_metric_registry"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_metric_observation")),
        sa.UniqueConstraint(
            "metric_id",
            "territory_level",
            "territory_code",
            "period_start",
            "dims_key",
            name=op.f(
                "uq_metric_observation_metric_id_territory_level_territory_code_period_start_dims_key"
            ),
        ),
    )
    op.create_index(
        op.f("ix_metric_observation_admin_unit_id"),
        "metric_observation",
        ["admin_unit_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_metric_observation_dataset_version_id"),
        "metric_observation",
        ["dataset_version_id"],
        unique=False,
    )
    op.create_index(
        "ix_metric_observation_lookup",
        "metric_observation",
        ["metric_id", "territory_level", "period_start"],
        unique=False,
    )
    op.create_geospatial_table(
        "place_master",
        sa.Column(
            "canonical_place_id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("canonical_name", sa.Text(), nullable=False),
        sa.Column("category", sa.Text(), nullable=False),
        sa.Column("subcategory", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column(
            "geom_4326",
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
        sa.Column(
            "geom_25830",
            Geometry(
                geometry_type="POINT",
                srid=25830,
                dimension=2,
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                nullable=False,
            ),
            nullable=False,
        ),
        sa.Column("municipio_ine", sa.Text(), nullable=True),
        sa.Column("seccion_admin_unit_id", sa.Text(), nullable=True),
        sa.Column("h3_r9", sa.Text(), nullable=True),
        sa.Column("official_source_id", sa.Text(), nullable=False),
        sa.Column("official_dataset_id", sa.Text(), nullable=False),
        sa.Column("official_entity_id", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column(
            "attributes",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("dataset_version_id", sa.UUID(), nullable=False),
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
            "category IN ('education', 'health', 'social', 'transport', 'commerce', 'culture', 'sport', 'administration', 'green', 'other')",
            name=op.f("ck_place_master_category"),
        ),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'INACTIVE', 'CLOSED', 'UNKNOWN')",
            name=op.f("ck_place_master_status"),
        ),
        sa.ForeignKeyConstraint(
            ["dataset_version_id"],
            ["dataset_version.id"],
            name=op.f("fk_place_master_dataset_version_id_dataset_version"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["official_dataset_id"],
            ["dataset_registry.dataset_id"],
            name=op.f("fk_place_master_official_dataset_id_dataset_registry"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["official_source_id"],
            ["source_registry.source_id"],
            name=op.f("fk_place_master_official_source_id_source_registry"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["seccion_admin_unit_id"],
            ["geo_admin_unit.admin_unit_id"],
            name=op.f("fk_place_master_seccion_admin_unit_id_geo_admin_unit"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("canonical_place_id", name=op.f("pk_place_master")),
        sa.UniqueConstraint(
            "official_dataset_id",
            "official_entity_id",
            name=op.f("uq_place_master_official_dataset_id_official_entity_id"),
        ),
    )
    op.create_index(
        "ix_place_master_category", "place_master", ["category", "subcategory"], unique=False
    )
    op.create_geospatial_index(
        "ix_place_master_geom_25830",
        "place_master",
        ["geom_25830"],
        unique=False,
        postgresql_using="gist",
        postgresql_ops={},
    )
    op.create_geospatial_index(
        "ix_place_master_geom_4326",
        "place_master",
        ["geom_4326"],
        unique=False,
        postgresql_using="gist",
        postgresql_ops={},
    )
    op.create_index(op.f("ix_place_master_h3_r9"), "place_master", ["h3_r9"], unique=False)
    op.create_index(
        op.f("ix_place_master_seccion_admin_unit_id"),
        "place_master",
        ["seccion_admin_unit_id"],
        unique=False,
    )
    op.create_geospatial_table(
        "place_source_alias",
        sa.Column("dataset_id", sa.Text(), nullable=False),
        sa.Column("external_id", sa.Text(), nullable=False),
        sa.Column("canonical_place_id", sa.UUID(), nullable=False),
        sa.Column("source_id", sa.Text(), nullable=False),
        sa.Column("source_name", sa.Text(), nullable=True),
        sa.Column("source_address", sa.Text(), nullable=True),
        sa.Column(
            "source_geom",
            Geometry(
                geometry_type="POINT",
                srid=4326,
                dimension=2,
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=True,
        ),
        sa.Column("match_method", sa.Text(), nullable=False),
        sa.Column("match_score", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["canonical_place_id"],
            ["place_master.canonical_place_id"],
            name=op.f("fk_place_source_alias_canonical_place_id_place_master"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["dataset_id"],
            ["dataset_registry.dataset_id"],
            name=op.f("fk_place_source_alias_dataset_id_dataset_registry"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["source_registry.source_id"],
            name=op.f("fk_place_source_alias_source_id_source_registry"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("dataset_id", "external_id", name=op.f("pk_place_source_alias")),
    )
    op.create_index(
        op.f("ix_place_source_alias_canonical_place_id"),
        "place_source_alias",
        ["canonical_place_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_place_source_alias_canonical_place_id"), table_name="place_source_alias")
    op.drop_geospatial_table("place_source_alias")
    op.drop_index(op.f("ix_place_master_seccion_admin_unit_id"), table_name="place_master")
    op.drop_index(op.f("ix_place_master_h3_r9"), table_name="place_master")
    op.drop_geospatial_index(
        "ix_place_master_geom_4326",
        table_name="place_master",
        postgresql_using="gist",
        column_name="geom_4326",
    )
    op.drop_geospatial_index(
        "ix_place_master_geom_25830",
        table_name="place_master",
        postgresql_using="gist",
        column_name="geom_25830",
    )
    op.drop_index("ix_place_master_category", table_name="place_master")
    op.drop_geospatial_table("place_master")
    op.drop_index("ix_metric_observation_lookup", table_name="metric_observation")
    op.drop_index(op.f("ix_metric_observation_dataset_version_id"), table_name="metric_observation")
    op.drop_index(op.f("ix_metric_observation_admin_unit_id"), table_name="metric_observation")
    op.drop_table("metric_observation")
    op.drop_index("ix_feature_value_lookup", table_name="feature_value")
    op.drop_index(op.f("ix_feature_value_admin_unit_id"), table_name="feature_value")
    op.drop_table("feature_value")
    op.drop_index(op.f("ix_metric_registry_dataset_id"), table_name="metric_registry")
    op.drop_table("metric_registry")
    op.drop_table("feature_registry")
