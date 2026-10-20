# admin_sample — fixture de integración

Subconjunto real de `cm_secciones_censales` (seccionado 2019) y `cm_barrios_madrid`:
secciones que contienen las zonas golden de Madrid (Sol, Plaza de Castilla) y sus vecinas,
más todas las secciones de La Acebeda (28001) y Ajalvir (28002).

Fuente: Comunidad de Madrid — Portal de Datos Abiertos (datos.comunidad.madrid), CC BY 4.0.
Regenerar con `uv run python scripts/build_admin_fixture.py` (requiere Bronze descargado).
