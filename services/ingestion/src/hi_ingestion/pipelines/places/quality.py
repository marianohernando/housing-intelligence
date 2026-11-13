"""QA for places: ids, coordinates, privacy allowlist and section assignment."""

from dataclasses import asdict, dataclass, field
from typing import Any

from hi_contracts.catalog.pipeline import PointsPipeline
from hi_domain.facilities import dependency
from hi_ingestion.pipelines.places.normalize import Places

MAX_QUARANTINE_RATIO = 0.12
PII_TERMS = ("telefono", "correo", "e_mail", "email", "nif", "fax", "web", "titulares")


@dataclass(frozen=True)
class CheckResult:
    name: str
    critical: bool
    passed: bool
    details: dict[str, Any] = field(default_factory=dict[str, Any])


@dataclass
class QualityReport:
    checks: list[CheckResult]

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks if c.critical)

    def to_dict(self) -> dict[str, Any]:
        return {"passed": self.passed, "checks": [asdict(c) for c in self.checks]}


def _directory_checks(places: Places, spec: PointsPipeline) -> list[CheckResult]:
    """D-218: one entry per place and one place per entry; how many matched, and whether the
    directory and the register agree on public or private (a wrong match would disagree)."""
    if not spec.directories:
        return []
    links = places.links
    reused = int(links.duplicated(["dataset_id", "external_id"]).sum()) + int(
        links.duplicated(["dataset_id", "canonical_place_id"]).sum()
    )
    attrs: list[dict[str, Any]] = places.frame["attributes"].tolist() if len(places.frame) else []
    pairs = [
        (a.get("dependency"), dependency(str(a["directory"].get("dependency") or "")))
        for a in attrs
        if isinstance(a.get("directory"), dict)
    ]
    compared = [(r, d) for r, d in pairs if r and d]
    disagree = sum(r != d for r, d in compared)
    loaded = set(places.directory_report)
    missing = sorted(link.dataset_id for link in spec.directories if link.dataset_id not in loaded)
    return [
        CheckResult("directory_one_to_one", True, reused == 0, {"reused": reused}),
        CheckResult("directory_loaded", False, not missing, {"missing_directories": missing}),
        CheckResult(
            "directory_dependency_agreement",
            False,
            disagree == 0,
            {"compared": len(compared), "disagree": disagree},
        ),
        CheckResult("directory_matches", False, True, places.directory_report),
    ]


def run_quality(places: Places, spec: PointsPipeline) -> QualityReport:
    frame = places.frame
    kept = len(frame) + len(places.quarantine)
    ratio = len(places.quarantine) / kept if kept else 0.0
    has_attrs = "attributes" in frame.columns
    attrs_list: list[dict[str, Any]] = frame["attributes"].tolist() if has_attrs else []
    attribute_keys = {k for attrs in attrs_list for k in attrs}
    leaked = sorted(k for k in attribute_keys if any(t in k for t in PII_TERMS))
    duplicated = int(frame["external_id"].duplicated().sum()) if len(frame) else 0
    checks = [
        CheckResult("has_places", True, len(frame) > 0, {"places": len(frame)}),
        CheckResult("unique_official_ids", True, duplicated == 0, {"duplicates": duplicated}),
        CheckResult(
            "coordinate_quarantine_ratio",
            True,
            ratio <= MAX_QUARANTINE_RATIO,
            {
                "quarantined": len(places.quarantine),
                "ratio": round(ratio, 4),
                "reasons": places.quarantine["reason"]
                .str.split(" \\(")
                .str[0]
                .value_counts()
                .to_dict(),
            },
        ),
        CheckResult("no_contact_or_tax_ids", True, not leaked, {"leaked_attributes": leaked}),
        CheckResult(
            "filters_applied",
            False,
            True,
            {"filtered_out": places.filtered_out, "source_rows": places.source_rows},
        ),
        CheckResult(
            "category_declared", True, bool(spec.category), {"category": spec.category.value}
        ),
        CheckResult(
            "coordinate_repairs",
            False,
            True,
            {
                "geocoded": int((places.repairs["origin"] == "geocoded").sum()),
                "kept_with_note": int((places.repairs["origin"] == "source").sum()),
                "rows": places.repairs.to_dict("records"),  # pyright: ignore[reportUnknownMemberType]
            },
        ),
        *_directory_checks(places, spec),
    ]
    return QualityReport(checks)
