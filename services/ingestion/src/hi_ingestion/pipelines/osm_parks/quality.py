"""QA for parks: a plausible number, valid places, edge points, nothing closed to the public and
every park an official source lists (D-222 §5) actually published."""

from collections.abc import Sequence

from hi_contracts.catalog.pipeline import OsmParksPipeline
from hi_ingestion.pipelines.osm_parks.parks import EDGE_POINTS
from hi_ingestion.pipelines.places.normalize import Places
from hi_ingestion.pipelines.places.quality import CheckResult, QualityReport

MAX_QUARANTINE_RATIO = 0.02


def run_parks_quality(
    places: Places, spec: OsmParksPipeline, included: Sequence[str] = ()
) -> QualityReport:
    frame = places.frame
    attributes = list(frame["attributes"]) if len(frame) else []
    kept = len(frame) + len(places.quarantine)
    published = (
        {str(i) for i, a in zip(frame["external_id"], attributes, strict=True) if "inclusion" in a}
        if len(frame)
        else set()
    )
    missing = sorted(set(included) - published)
    return QualityReport(
        [
            CheckResult(
                "park_count_plausible",
                True,
                spec.min_parks <= len(frame) <= spec.max_parks,
                {"parks": len(frame), "min": spec.min_parks, "max": spec.max_parks},
            ),
            CheckResult(
                "ids_unique",
                True,
                bool(frame["external_id"].is_unique) if len(frame) else True,
            ),
            CheckResult(
                "every_park_has_its_edge",
                True,
                all(len(a.get(EDGE_POINTS) or []) >= 3 for a in attributes),
            ),
            CheckResult(
                "minimum_size",
                True,
                all(float(a["area_ha"]) >= spec.min_area_ha for a in attributes),
                {"min_area_ha": spec.min_area_ha},
            ),
            CheckResult(
                "open_to_the_public",
                True,
                not any(a.get("access") in spec.access_denied for a in attributes),
            ),
            CheckResult(
                "every_inclusion_published",
                True,
                not missing,
                {"included": len(included), "missing": missing},
            ),
            CheckResult(
                "quarantine_ratio",
                True,
                len(places.quarantine) <= MAX_QUARANTINE_RATIO * max(kept, 1),
                {"quarantined": len(places.quarantine), "max_ratio": MAX_QUARANTINE_RATIO},
            ),
        ]
    )
