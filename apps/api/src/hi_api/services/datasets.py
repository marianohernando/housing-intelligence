"""Datasets behind the product: every dataset with a last valid version (QA passed)."""

from sqlalchemy import Connection, text

from hi_contracts.public import DatasetList, DatasetRef

_DATASETS = text(
    """
    SELECT d.dataset_id, d.name, d.owner, coalesce(d.portal_url, d.landing_url) AS url,
           d.is_cm_open_data, s.license_name, v.version_label
      FROM dataset_registry d
      JOIN source_registry s ON s.source_id = d.source_id
      JOIN dataset_version v ON v.dataset_id = d.dataset_id AND v.is_last_valid
     WHERE (NOT :cm_only OR d.is_cm_open_data)
     ORDER BY d.is_cm_open_data DESC, d.dataset_id
    """
)


def dataset_list(conn: Connection, *, cm_only: bool) -> DatasetList:
    refs = [
        DatasetRef.model_validate(
            {
                "dataset_id": r["dataset_id"],
                "name": r["name"],
                "publisher": r["owner"],
                "is_cm_open_data": r["is_cm_open_data"],
                "url": r["url"],
                "version": r["version_label"],
                "license": r["license_name"],
            }
        )
        for r in conn.execute(_DATASETS, {"cm_only": cm_only}).mappings().all()
    ]
    return DatasetList(
        total=len(refs),
        cm_open_data_count=sum(r.is_cm_open_data for r in refs),
        datasets=refs,
    )
