# Gate 01 — limitaciones conocidas (2026-11-10)

- **Alcance.** 21 datasets del Portal de Datos Abiertos de la Comunidad de Madrid en producción local:
  - geografía canónica;
  - 10 tablas estadísticas;
  - 4 registros de equipamientos (educativos, sanitarios, servicios para mayores y oficinas de farmacia);
  - 6 GTFS del CRTM. Se publican en datos.crtm.es y también tienen ficha en el portal CM, que va enlazada en cada dataset (`role: cm_portal`).
- **Nuevos desde el 22 oct.** DATA-007 (6 GTFS, D-196) y DATA-016 (farmacias por municipio, unidades escolares, nacidos vivos, viviendas por régimen de tenencia y oficinas de farmacia).
- **Unidades escolares.** Se cargan desde 2015 (`period_min`). Los años 1994–2014 quedan fuera por el presupuesto de almacenamiento del plan gratuito de Supabase y se cuentan como `out_of_window`. Las enseñanzas se solapan (los ciclos formativos y sus grados), así que «Total» no es la suma de los miembros. Las features deben elegir un nivel y no sumar. Es un proxy de capacidad (aulas), no de plazas.
- **Viviendas por régimen de tenencia** (Censo 2021): cubre 178 de 179 municipios.
- **Nacidos vivos.** Se guarda con la dimensión sexo, igual que la población. Nunca puede ser feature (test de D-189).
- **Oficinas de farmacia.** 4 registros sin coordenadas quedan en cuarentena. El nombre de los titulares (personas) nunca se guarda y el fixture lo redacta. El nombre del lugar se compone con la dirección.
- **Transporte.** Ver `evidence/gate-02/2026-11-10/known-limitations.md`: GTFS de metro vencido, headway de cercanías sin sentido, paradas fuera de la región.
- **Transacciones inmobiliarias** (DATA-017, backlog). Son trimestrales e identifican el municipio solo por su nombre, así que necesitan un tipo de pipeline nuevo.
- **Sigue igual que el 22 oct.** Zonas estadísticas sin geometría publicada, alquiler por código postal sin polígono (DATA-013), cuarentena de equipamientos sin coordenadas y `cm_centros_sanitarios` con actualización diaria en origen.
- **Entorno remoto (Supabase).** Sin cargar todavía: falta la contraseña de la base de datos (OPS-001).
