"""Pipeline constants. Changing any of them requires bumping PARSER_VERSION."""

PARSER_VERSION = "admin_boundaries-1.1.0"
SECTIONS_DATASET = "cm_secciones_censales"
BARRIOS_DATASET = "cm_barrios_madrid"
SOURCE_CRS = "EPSG:25830"
WGS84 = "EPSG:4326"
H3_RESOLUTIONS = (8, 9)
MIN_OVERLAP_SHARE = 1e-3  # drop H3/section slivers below 0.1 % of the cell
AREA_TOLERANCE = 0.01  # computed vs declared area, and children vs parent
MAX_QUARANTINE_RATIO = 0.005
MADRID_MUNICIPIO = "28079"
# Full-region expectations (only enforced when the input is the complete seccionado).
FULL_RUN_MIN_SECTIONS = 4000
EXPECTED_MUNICIPIOS = 179
EXPECTED_MADRID_DISTRICTS = 21
EXPECTED_MADRID_BARRIOS = 131
INSERT_CHUNK = 5000
# Official spellings (DATA-022). The section CSV writes '/' or 0xD0 where the Ñ goes and drops
# accents, so names come from the latest valid version of these tables (admin_names.py).
MUNICIPIO_NAMES_DATASET = "cm_poblacion_edad_nacionalidad_sexo"
MADRID_DISTRICT_NAMES_DATASET = "ayto_panel_indicadores_distritos_barrios"
CENSAL_DISTRICT_NAME = "{municipio} — distrito censal {number}"
