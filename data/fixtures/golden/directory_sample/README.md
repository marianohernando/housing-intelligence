# directory_sample — fixtures de directorios oficiales (D-218)

Filas reales de la provincia de Madrid de los directorios del Ministerio de Sanidad
(reutilización autorizada citando la fuente y la fecha de actualización), con solo las columnas
que lee el pipeline: nunca teléfonos ni correos.
- `ms_catalogo_nacional_hospitales.xlsx`: Catálogo Nacional de Hospitales 2025 (actualizado a
  31/12/2024), hoja «DIRECTORIO DE HOSPITALES».
- `ms_catalogo_centros_atencion_primaria.xlsx`: Catálogo de Centros de Atención Primaria del SNS
  2026 (actualizado a 31/12/2025), hoja «Catálogo - 2026».

Regenerar con `uv run python scripts/build_directory_fixtures.py` (requiere Bronze descargado).
