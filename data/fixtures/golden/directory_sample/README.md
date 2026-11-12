# directory_sample — fixtures de directorios oficiales (D-218)

Filas reales de la provincia de Madrid de los directorios del Ministerio de Sanidad
(reutilización autorizada citando la fuente y la fecha de actualización), con solo las columnas
que lee el pipeline: nunca teléfonos ni correos.
- `ms_catalogo_nacional_hospitales.xlsx`: Catálogo Nacional de Hospitales 2025 (actualizado a
  31/12/2024), hoja «DIRECTORIO DE HOSPITALES».

Regenerar con `uv run python scripts/build_directory_fixtures.py` (requiere Bronze descargado).
