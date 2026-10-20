"""Load and cross-validate data/catalog/{sources,datasets,features}/*.yaml."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ValidationError

from hi_contracts.catalog import DatasetSpec, FeatureSpec, SourceSpec

DEFAULT_CATALOG_DIR = Path(__file__).resolve().parents[5] / "data" / "catalog"
DRAFTS_DIRNAME = "_drafts"


class CatalogError(ValueError):
    """Raised when catalog files are invalid or inconsistent."""


@dataclass(frozen=True)
class Catalog:
    sources: dict[str, SourceSpec]
    datasets: dict[str, DatasetSpec]
    drafts: dict[str, DatasetSpec]
    features: dict[str, FeatureSpec]
    paths: dict[str, Path] = field(default_factory=dict[str, Path])


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


def load_catalog(catalog_dir: Path = DEFAULT_CATALOG_DIR) -> Catalog:
    errors: list[str] = []
    paths: dict[str, Path] = {}
    sources = _load_dir(catalog_dir / "sources", SourceSpec, "source_id", errors, paths)
    datasets = _load_dir(catalog_dir / "datasets", DatasetSpec, "dataset_id", errors, paths)
    drafts = _load_dir(
        catalog_dir / "datasets" / DRAFTS_DIRNAME, DatasetSpec, "dataset_id", errors, paths
    )
    features = _load_dir(catalog_dir / "features", FeatureSpec, "feature_id", errors, paths)

    for dataset_id in datasets.keys() & drafts.keys():
        errors.append(f"{dataset_id}: exists both as curated dataset and as draft")
    for dataset in [*datasets.values(), *drafts.values()]:
        if dataset.source_id not in sources:
            errors.append(f"{dataset.dataset_id}: unknown source_id '{dataset.source_id}'")
        for feature_id in dataset.feeds_features:
            if feature_id not in features:
                errors.append(f"{dataset.dataset_id}: feeds unknown feature '{feature_id}'")
    for feature in features.values():
        for src in feature.sources:
            if src.dataset_id not in datasets:
                errors.append(f"{feature.feature_id}: unknown curated dataset '{src.dataset_id}'")

    if errors:
        raise CatalogError("Invalid catalog:\n  " + "\n  ".join(errors))
    return Catalog(sources, datasets, drafts, features, paths)
