# places_sample — fixtures de equipamientos

Filas reales de los registros de centros educativos, sanitarios y de atención social de la
Comunidad de Madrid (CC BY 4.0) cuyas coordenadas caen dentro de `admin_sample`, más casos
límite: un centro dado de baja, una fila sin coordenadas y un subtipo protegido
(pisos tutelados), que el pipeline debe excluir.
Las columnas de contacto (teléfono, email, fax, web), NIF y titulares se guardan como
`[redactado]`: la columna existe para probar que el pipeline la ignora, pero el repo no copia
datos de personas.
Regenerar con `uv run python scripts/build_places_fixtures.py` (requiere Bronze descargado).

D-237: aparcamientos del Ayuntamiento de Madrid (`ayto_aparcamientos_*`, datos.madrid.es, CC BY 4.0, sin
teléfono, fax ni correo) y de disuasión del CRTM (`crtm_aparcamientos_disuasion`, con dos que
comparten `IDFEMPLAZAMIENTO`), y estaciones de calidad del aire de las redes de la Comunidad
(`cm_calidad_aire_estaciones`) y del Ayuntamiento (`ayto_calidad_aire_estaciones`): filas reales
copiadas a mano de los ficheros del 14 nov.
