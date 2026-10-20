"""ingestion_run bookkeeping in short, independent transactions (survives pipeline rollback)."""

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Engine, update
from sqlalchemy.orm import Session

from hi_contracts.catalog.enums import PipelineStage, RunStatus
from hi_db.models import IngestionRun


class StageTracker:
    def __init__(self, engine: Engine, dataset_id: str, correlation_id: str | None = None) -> None:
        self.engine = engine
        self.dataset_id = dataset_id
        self.correlation_id = correlation_id or uuid.uuid4().hex
        self.version_id: uuid.UUID | None = None

    def record(
        self,
        stage: PipelineStage,
        status: RunStatus,
        metrics: dict[str, Any],
        error: str | None = None,
    ) -> None:
        with Session(self.engine) as session, session.begin():
            session.add(
                IngestionRun(
                    dataset_id=self.dataset_id,
                    dataset_version_id=self.version_id,
                    correlation_id=self.correlation_id,
                    stage=stage.value,
                    status=status.value,
                    finished_at=datetime.now(UTC),
                    metrics=metrics,
                    error=error,
                )
            )

    @contextmanager
    def stage(self, stage: PipelineStage) -> Iterator[dict[str, Any]]:
        metrics: dict[str, Any] = {}
        with Session(self.engine) as session, session.begin():
            run = IngestionRun(
                dataset_id=self.dataset_id,
                dataset_version_id=self.version_id,
                correlation_id=self.correlation_id,
                stage=stage.value,
                status=RunStatus.RUNNING.value,
            )
            session.add(run)
            session.flush()
            run_id = run.id
        try:
            yield metrics
        except Exception as exc:
            self._finish(run_id, RunStatus.FAILED, metrics, repr(exc))
            raise
        self._finish(run_id, RunStatus.SUCCESS, metrics, None)

    def _finish(
        self, run_id: uuid.UUID, status: RunStatus, metrics: dict[str, Any], error: str | None
    ) -> None:
        with Session(self.engine) as session, session.begin():
            session.execute(
                update(IngestionRun)
                .where(IngestionRun.id == run_id)
                .values(
                    status=status.value,
                    finished_at=datetime.now(UTC),
                    metrics=metrics,
                    error=error,
                    dataset_version_id=self.version_id,
                )
            )
