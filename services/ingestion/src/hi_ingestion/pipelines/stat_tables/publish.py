"""Replace a dataset's observations atomically."""

import uuid
from typing import Any

import pandas as pd
from sqlalchemy import delete, insert
from sqlalchemy.orm import Session

from hi_db.models import MetricObservation

INSERT_CHUNK = 5000


def _clean(value: Any) -> Any:
    return None if value is None or (isinstance(value, float) and pd.isna(value)) else value


def replace_observations(
    session: Session, frame: pd.DataFrame, metric_ids: list[str], version_id: uuid.UUID
) -> int:
    session.execute(delete(MetricObservation).where(MetricObservation.metric_id.in_(metric_ids)))
    records: list[dict[str, Any]] = frame.to_dict("records")  # pyright: ignore[reportAssignmentType]
    rows = [
        {k: _clean(v) for k, v in r.items()} | {"dataset_version_id": version_id} for r in records
    ]
    for start in range(0, len(rows), INSERT_CHUNK):
        session.execute(insert(MetricObservation), rows[start : start + INSERT_CHUNK])
    return len(rows)
