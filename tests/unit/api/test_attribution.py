"""What each dataset's licence asks to show (DatasetRef.attribution_text)."""

from hi_api.services.attribution import GEOCODER_SOURCE, attribution_text
from hi_ingestion.pipelines.places.geocoder import SOURCE_ID


def test_the_geocoder_source_is_the_one_the_places_pipeline_records() -> None:
    assert GEOCODER_SOURCE == SOURCE_ID


def test_a_dataset_shows_its_source_and_the_geocoder_only_when_it_used_it() -> None:
    row = {
        "attribution_text": "Fuente: Comunidad de Madrid, CC BY 4.0.",
        "geocoded": False,
        "geocoder_attribution": (
            "Geocodificación: © Instituto Geográfico Nacional (CartoCiudad), CC BY 4.0 scne.es."
        ),
    }
    assert attribution_text(row) == "Fuente: Comunidad de Madrid, CC BY 4.0."
    assert attribution_text(row | {"geocoded": True}) == (
        "Fuente: Comunidad de Madrid, CC BY 4.0. Geocodificación: © Instituto Geográfico Nacional "
        "(CartoCiudad), CC BY 4.0 scne.es."
    )
    assert attribution_text(row | {"attribution_text": None}) is None
