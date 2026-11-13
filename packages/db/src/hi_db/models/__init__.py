"""ORM models. Import every module here so Base.metadata is complete for Alembic."""

from hi_db.models.features import FeatureRegistry, FeatureValue
from hi_db.models.geo import GeoAdminUnit, H3Cell, H3CellAdminUnit
from hi_db.models.metrics import MetricObservation, MetricRegistry
from hi_db.models.places import PlaceMaster, PlaceSourceAlias
from hi_db.models.registry import DatasetRegistry, DatasetVersion, IngestionRun, SourceRegistry
from hi_db.models.transit import CommuteTime, TransitHub

__all__ = [
    "CommuteTime",
    "DatasetRegistry",
    "DatasetVersion",
    "FeatureRegistry",
    "FeatureValue",
    "GeoAdminUnit",
    "H3Cell",
    "H3CellAdminUnit",
    "IngestionRun",
    "MetricObservation",
    "MetricRegistry",
    "PlaceMaster",
    "PlaceSourceAlias",
    "SourceRegistry",
    "TransitHub",
]
