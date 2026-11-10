# Gate 01 — limitaciones conocidas (2026-10-22)

- Alcance: 10 datasets de la Comunidad de Madrid en producción local. Son la geografía canónica, 6 tablas estadísticas (población, hogares, viviendas por superficie, renta y alquiler por municipio y por código postal) y 3 registros de equipamientos.
- Siguen sin pipeline los P0 de transporte (5 GTFS del CRTM) y el panel de indicadores de distritos y barrios del Ayuntamiento. Catastro tampoco está ingerido.
- Las zonas estadísticas de la Comunidad se guardan como observaciones, pero no tienen geometría publicada, así que no se pueden pintar.
- El alquiler por código postal se guarda por código, sin polígono de código postal (card DATA-013).
- Equipamientos sin coordenadas o con coordenadas fuera de la región quedan en cuarentena: 55 educativos, 11 sanitarios y 46 sociales.
- Por protección de personas vulnerables (D-186), del registro social solo se mapean servicios para mayores, y del sanitario solo centros de salud, consultorios y hospitales.
- `cm_centros_sanitarios` se actualiza a diario en origen. Al volver a descargarlo, el pipeline crea una versión nueva validada; eso es lo esperado.
- El entorno remoto en Supabase no está cargado todavía: falta la contraseña de la base de datos (OPS-001). Migración y sincronización están preparadas y simuladas.
