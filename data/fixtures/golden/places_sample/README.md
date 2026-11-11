# places_sample — fixtures de equipamientos

Filas reales de los registros de centros educativos, sanitarios y de atención social de la
Comunidad de Madrid (CC BY 4.0) cuyas coordenadas caen dentro de `admin_sample`, más casos
límite: un centro dado de baja, una fila sin coordenadas y un subtipo protegido
(pisos tutelados), que el pipeline debe excluir.
Las columnas de contacto (teléfono, email, fax, web), NIF y titulares se guardan como
`[redactado]`: la columna existe para probar que el pipeline la ignora, pero el repo no copia
datos de personas.
Regenerar con `uv run python scripts/build_places_fixtures.py` (requiere Bronze descargado).
