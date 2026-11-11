"""Load and cross-validate data/catalog/{sources,datasets,features}/*.yaml."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, TypeAdapter, ValidationError

from hi_contracts.catalog import DatasetSpec, FeatureSpec, MetricSpec, PipelineSpec, SourceSpec

DEFAULT_CATALOG_DIR = Path(__file__).resolve().parents[5] / "data" / "catalog"
DRAFTS_DIRNAME = "_drafts"


class CatalogError(ValueError):
    """Raised when catalog files are invalid or inconsistent."""


PIPELINE_ADAPTER: TypeAdapter[PipelineSpec] = TypeAdapter(PipelineSpec)


@dataclass(frozen=True)
class Catalog:
    sources: dict[str, SourceSpec]
    datasets: dict[str, DatasetSpec]
    drafts: dict[str, DatasetSpec]
    features: dict[str, FeatureSpec]
    paths: dict[str, Path] = field(default_factory=dict[str, Path])
    metrics: dict[str, MetricSpec] = field(default_factory=dict[str, MetricSpec])
    pipelines: dict[str, PipelineSpec] = field(default_factory=dict[str, PipelineSpec])


def _read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        msg = f"{path}: expected a mapping at top level"
        raise CatalogError(msg)
    return data  # pyright: ignore[reportUnknownVariableType]


def _load_dir[M: BaseModel](
    directory: Path, model: type[M], id_field: str, errors: list[str], paths: dict[str, Path]
) -> dict[str, M]:
    items: dict[str, M] = {}
    if not directory.exists():
        return items
    for path in sorted(directory.glob("*.yaml")):
        try:
            spec = model.model_validate(_read_yaml(path))
        except (ValidationError, CatalogError, yaml.YAMLError) as exc:
            errors.append(f"{path.name}: {exc}")
            continue
        item_id = str(getattr(spec, id_field))
        if path.stem != item_id:
            errors.append(f"{path.name}: file name must equal {id_field} '{item_id}'")
        if item_id in items:
            errors.append(f"{path.name}: duplicated {id_field} '{item_id}'")
        items[item_id] = spec
        paths[item_id] = path
    return items


def _load_pipelines(directory: Path, errors: list[str]) -> dict[str, PipelineSpec]:
    pipelines: dict[str, PipelineSpec] = {}
    for path in sorted(directory.glob("*.yaml")) if directory.exists() else []:
        try:
            spec = PIPELINE_ADAPTER.validate_python(_read_yaml(path))
        except (ValidationError, CatalogError, yaml.YAMLError) as exc:
            errors.append(f"{path.name}: {exc}")
            continue
        if path.stem != spec.dataset_id:
            errors.append(f"{path.name}: file name must equal dataset_id '{spec.dataset_id}'")
        pipelines[spec.dataset_id] = spec
    return pipelines


def _cross_check_metrics(
    datasets: dict[str, DatasetSpec],
    metrics: dict[str, MetricSpec],
    pipelines: dict[str, PipelineSpec],
    errors: list[str],
) -> None:
    for metric in metrics.values():
        if metric.dataset_id not in datasets:
            errors.append(f"{metric.metric_id}: unknown curated dataset '{metric.dataset_id}'")
    for dataset_id, pipeline in pipelines.items():
        if dataset_id not in datasets:
            errors.append(f"pipeline {dataset_id}: no curated dataset with that id")
        for metric_id in pipeline.metric_ids():
            metric = metrics.get(metric_id)
            if metric is None:
                errors.append(f"pipeline {dataset_id}: unknown metric '{metric_id}'")
            elif metric.dataset_id != dataset_id:
                errors.append(
                    f"pipeline {dataset_id}: metric '{metric_id}' belongs to {metric.dataset_id}"
                )


def load_catalog(
    catalog_dir: Path = DEFAULT_CATALOG_DIR, *, include_drafts: bool = True
) -> Catalog:
    errors: list[str] = []
    paths: dict[str, Path] = {}
    sources = _load_dir(catalog_dir / "sources", SourceSpec, "source_id", errors, paths)
    datasets = _load_dir(catalog_dir / "datasets", DatasetSpec, "dataset_id", errors, paths)
    drafts = (
        _load_dir(
            catalog_dir / "datasets" / DRAFTS_DIRNAME, DatasetSpec, "dataset_id", errors, paths
        )
        if include_drafts
        else {}
    )
    features = _load_dir(catalog_dir / "features", FeatureSpec, "feature_id", errors, paths)
    metrics = _load_dir(catalog_dir / "metrics", MetricSpec, "metric_id", errors, paths)
    pipelines = _load_pipelines(catalog_dir / "pipelines", errors)
    _cross_check_metrics(datasets, metrics, pipelines, errors)

    for dataset_id in datasets.keys() & drafts.keys():
        errors.append(f"{dataset_id}: exists both as curated dataset and as draft")
    for dataset in [*datasets.values(), *drafts.values()]:
        if dataset.source_id not in sources:
            errors.append(f"{dataset.dataset_id}: unknown source_id '{dataset.source_id}'")
        for feature_id in dataset.feeds_features:
            if feature_id not in features:
                errors.append(f"{dataset.dataset_id}: feeds unknown feature '{feature_id}'")
    primaries: dict[str, str] = {}
    for feature in features.values():
        binding = feature.gap_row
        if binding and binding.role == "primary":
            if binding.row in primaries:
                errors.append(
                    f"{feature.feature_id}: gap row '{binding.row}' already has its primary "
                    f"indicator ({primaries[binding.row]})"
                )
            primaries[binding.row] = feature.feature_id
        for src in feature.sources:
            if src.dataset_id not in datasets:
                errors.append(f"{feature.feature_id}: unknown curated dataset '{src.dataset_id}'")

    if errors:
        raise CatalogError("Invalid catalog:\n  " + "\n  ".join(errors))
    return Catalog(sources, datasets, drafts, features, paths, metrics, pipelines)
