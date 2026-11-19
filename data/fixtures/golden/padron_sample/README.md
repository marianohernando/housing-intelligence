# padron_sample — fixture del padrón municipal de Madrid

Filas reales del padrón del Ayuntamiento de Madrid (datos.madrid.es, CC BY 4.0, 1 oct 2026): las
dos primeras secciones censales de Centro, Chamartín y Tetuán, con todas las edades. Las líneas se
copian tal cual salvo una cosa (D-247): un barrio que `admin_sample` no tiene pasa, con su nombre,
a uno de ese distrito que sí tiene (El Viso → Nueva España, Bellas Vistas → Castillejos y
Berruguete → Almenara), para que los totales por barrio casen con la geografía de muestra. Los
totales por distrito no cambian.

Regenerar con `uv run python scripts/build_padron_fixture.py` (requiere Bronze descargado): hace
ese mismo cambio.
