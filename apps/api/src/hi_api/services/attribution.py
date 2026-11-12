"""The text a dataset's licence asks to show next to its data (DatasetRef.attribution_text).

It comes from the source catalogue (`source_registry.attribution_text`). Datasets with places
located by the geocoder (D-216: origin «geocoded») also carry the geocoder's own attribution
(CartoCiudad, CC BY 4.0 scne.es). Each query selects `attribution_text`, `geocoded` and
`geocoder_attribution` for its dataset rows, with GEOCODER_SOURCE bound as :geocoder.
"""

from typing import Any

from sqlalchemy import RowMapping

# hi_ingestion.pipelines.places.geocoder.SOURCE_ID (the API image does not ship hi_ingestion)
GEOCODER_SOURCE = "ign_cartociudad"
# hi_ingestion.catalog.provenance.CM_SOURCE_ID: a CM open-data dataset's `url` opens in the CM
# portal, so that is the site its `source_name` names (D-231), whoever produces it (the CRTM)
CM_SOURCE = "comunidad_madrid_ckan"
SOURCE_NAME_SQL = (
    "CASE WHEN d.is_cm_open_data THEN "
    "(SELECT c.name FROM source_registry c WHERE c.source_id = :cm_source) "
    "ELSE s.name END AS source_name"
)


def attribution_text(row: RowMapping | dict[str, Any]) -> str | None:
    parts = [row["attribution_text"], row["geocoder_attribution"] if row["geocoded"] else None]
    text = " ".join(str(p).strip() for p in parts if p)
    return text or None
