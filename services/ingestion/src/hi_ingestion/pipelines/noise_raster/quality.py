"""QA for the noise grid: every declared index, one grid, plausible levels and not empty."""

from hi_contracts.catalog.pipeline import NoiseRasterPipeline
from hi_ingestion.pipelines.noise_raster.normalize import NoiseResult
from hi_ingestion.pipelines.places.quality import CheckResult, QualityReport


def run_noise_quality(result: NoiseResult, spec: NoiseRasterPipeline) -> QualityReport:
    missing = sorted(set(spec.layers) - set(result.found))
    cells = result.cells_with_level()
    too_loud = {name: db for name, db in result.max_db.items() if db > spec.max_db}
    return QualityReport(
        [
            CheckResult("every_layer_found", True, not missing, {"missing": missing}),
            CheckResult(
                "one_grid_as_declared",
                True,
                result.grid is not None and result.problems.empty,
                {"problems": result.problems.to_dict("records")},  # pyright: ignore[reportUnknownMemberType]
            ),
            CheckResult(
                "levels_are_decibels",
                True,
                result.grid is not None and not too_loud,
                {"max_db": result.max_db, "limit": spec.max_db},
            ),
            CheckResult(
                "not_empty",
                True,
                bool(cells) and min(cells.values()) >= spec.min_cells_with_level,
                {"cells_with_level": cells, "min": spec.min_cells_with_level},
            ),
        ]
    )
