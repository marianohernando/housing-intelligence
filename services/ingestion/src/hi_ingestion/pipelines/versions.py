"""dataset_version bookkeeping shared by every pipeline."""

import hashlib
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from hi_db.models import DatasetVersion
from hi_ingestion.pipelines.fetch import FetchedFile


def combined_checksum(files: list[FetchedFile]) -> str:
    joined = "|".join(f"{f.role}:{f.sha256}" for f in files)
    return hashlib.sha256(joined.encode()).hexdigest()


def find_version(session: Session, dataset_id: str, checksum: str) -> DatasetVersion | None:
    return session.scalar(
        select(DatasetVersion).where(
            DatasetVersion.dataset_id == dataset_id, DatasetVersion.checksum_sha256 == checksum
        )
    )


def is_current(
    session: Session, dataset_id: str, checksum: str, parser_version: str
) -> DatasetVersion | None:
    """Return the version if this exact content was already published by this parser."""
    existing = find_version(session, dataset_id, checksum)
    if existing and existing.is_last_valid and existing.parser_version == parser_version:
        return existing
    return None


def register_version(
    session: Session,
    primary: FetchedFile,
    checksum: str,
    *,
    parser_version: str,
    row_count: int,
    schema_hash: str,
    manifest_path: str,
) -> DatasetVersion:
    existing = find_version(session, primary.dataset_id, checksum)
    if existing is not None:  # same Bronze content, possibly a new parser: reprocess in place
        existing.parser_version = parser_version
        existing.quality_status = "PENDING"
        existing.schema_hash = schema_hash
        existing.row_count = row_count
        return existing
    version = DatasetVersion(
        dataset_id=primary.dataset_id,
        version_label=f"{datetime.now(UTC):%Y-%m-%d}-{checksum[:12]}",
        retrieved_at=datetime.fromisoformat(primary.retrieved_at),
        checksum_sha256=checksum,
        byte_size=primary.bytes,
        row_count=row_count,
        schema_hash=schema_hash,
        parser_version=parser_version,
        quality_status="PENDING",
        bronze_manifest_path=manifest_path,
    )
    session.add(version)
    session.flush()
    return version


def mark_last_valid(session: Session, version: DatasetVersion, quality_status: str) -> None:
    session.execute(
        update(DatasetVersion)
        .where(DatasetVersion.dataset_id == version.dataset_id, DatasetVersion.id != version.id)
        .values(is_last_valid=False)
    )
    version.is_last_valid = True
    version.quality_status = quality_status


def mark_failed(session: Session, version_id: object) -> None:
    session.execute(
        update(DatasetVersion)
        .where(DatasetVersion.id == version_id)
        .values(quality_status="FAILED")
    )
