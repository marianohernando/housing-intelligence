"""A run that fails after registering its version must not be skipped by the next one.

Bug (board, A v8): a dataset already published reprocessed with a new parser registers the
same version row in place (same checksum, new parser, still last valid). If that run fails,
the next run used to see «same checksum and parser, last valid» and skip it, so the new parser
never published and the failure went unnoticed.
"""

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import Engine, text

from hi_contracts.catalog.pipeline import CsvFormat, FacilityDirectoryPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.common import RunSummary
from hi_ingestion.pipelines.directory.normalize import (
    Directory,
    normalize_directory,
    parse_sheet,
    write_directory_silver,
)
from hi_ingestion.pipelines.directory.quality import run_directory_quality
from hi_ingestion.pipelines.directory.run import PARSER_VERSION, run_directory_pipeline
from hi_ingestion.pipelines.fetch import FetchedFile, local_file
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline
from tests.integration.conftest import GOLDEN

pytestmark = pytest.mark.db
DATASET = "ms_catalogo_nacional_hospitales"
VERSION_SQL = text(
    "SELECT parser_version, quality_status, is_last_valid FROM dataset_version "
    "WHERE dataset_id = :ds AND checksum_sha256 = :checksum"
)


class NormalizeCrashError(RuntimeError):
    pass


def _spec() -> FacilityDirectoryPipeline:
    spec = load_catalog().pipelines[DATASET]
    assert isinstance(spec, FacilityDirectoryPipeline)
    return spec


def _source() -> FetchedFile:
    return local_file(DATASET, "primary", GOLDEN / "directory_sample" / f"{DATASET}.xlsx")


def _steps(parser_version: str, *, crash: bool = False, fail_quality: bool = False) -> Any:
    spec = _spec()

    def normalize(frame: Any) -> Directory:
        if crash:
            raise NormalizeCrashError("parser bug")
        return normalize_directory(frame, spec)

    def quality(directory: Directory) -> dict[str, Any]:
        report = run_directory_quality(directory, spec).to_dict()
        return {**report, "passed": False} if fail_quality else report

    return PipelineSteps[Directory](
        parser_version=parser_version,
        csv=CsvFormat(),
        resource_role=spec.resource_role,
        normalize=normalize,
        quarantine=lambda directory: directory.quarantine,
        quality=quality,
        counts=lambda directory: {"entries": len(directory.frame)},
        write_silver=write_directory_silver,
        publish=lambda _session, directory, _version_id: {"entries": len(directory.frame)},
        parse=lambda path: parse_sheet(path, spec),
    )


def _run(engine: Engine, tmp_path: Path, steps: Any) -> RunSummary:
    return run_pipeline(
        engine, load_catalog(), DATASET, steps, _source(), evidence_root=None, data_dir=tmp_path
    )


def _version(engine: Engine, summary: RunSummary) -> dict[str, Any]:
    with engine.connect() as conn:
        row = conn.execute(VERSION_SQL, {"ds": DATASET, "checksum": summary.checksum}).one()
    return dict(row._mapping)


@pytest.fixture
def published_directory(
    published: RunSummary, migrated_engine: Engine, tmp_path: Path
) -> Iterator[RunSummary]:
    """The directory published with its real parser; restored after the test."""
    assert published.status == "SUCCESS"
    first = run_directory_pipeline(
        migrated_engine, load_catalog(), _spec(), _source(), evidence_root=None, data_dir=tmp_path
    )
    assert first.status in {"SUCCESS", "SKIPPED"}, first.quality
    yield first
    restored = run_directory_pipeline(
        migrated_engine, load_catalog(), _spec(), _source(), evidence_root=None, data_dir=tmp_path
    )
    assert restored.status in {"SUCCESS", "SKIPPED"}, restored.quality
    assert _version(migrated_engine, restored)["parser_version"] == PARSER_VERSION


def test_a_crash_after_registering_is_reprocessed_next_time(
    published_directory: RunSummary, migrated_engine: Engine, tmp_path: Path
) -> None:
    new_parser = f"{PARSER_VERSION}+crash-test"
    with pytest.raises(NormalizeCrashError):
        _run(migrated_engine, tmp_path, _steps(new_parser, crash=True))
    left = _version(migrated_engine, published_directory)
    assert left["parser_version"] == new_parser  # registered in place before the crash
    assert left["quality_status"] != "PASSED"
    again = _run(migrated_engine, tmp_path, _steps(new_parser))
    assert again.status == "SUCCESS", "the failed run was skipped as if it had published"
    assert _version(migrated_engine, again)["quality_status"] == "PASSED"


def test_a_quality_failure_is_reprocessed_next_time(
    published_directory: RunSummary, migrated_engine: Engine, tmp_path: Path
) -> None:
    new_parser = f"{PARSER_VERSION}+quality-test"
    failed = _run(migrated_engine, tmp_path, _steps(new_parser, fail_quality=True))
    assert failed.status == "FAILED"
    assert _version(migrated_engine, failed)["quality_status"] == "FAILED"
    again = _run(migrated_engine, tmp_path, _steps(new_parser))
    assert again.status == "SUCCESS"


def test_a_published_version_is_still_skipped(
    published_directory: RunSummary, migrated_engine: Engine, tmp_path: Path
) -> None:
    once = _run(migrated_engine, tmp_path, _steps(PARSER_VERSION))
    assert once.status in {"SUCCESS", "SKIPPED"}
    twice = _run(migrated_engine, tmp_path, _steps(PARSER_VERSION))
    assert twice.status == "SKIPPED"
    assert twice.checksum == once.checksum
