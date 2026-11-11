# Datasets que usa Vida Fácil

> Fichero generado: no se edita a mano. Se regenera con `uv run python pitch/build_datasets_cm.py`.
> Qué datasets se usan, qué alimentan y su Quality Gate salen de `data/catalog/` y `evidence/gate-01/`. El nombre oficial y la licencia salen de la API CKAN del portal (`pitch/portal_cm_snapshot.json`, leída el 2026-11-11).

**21 datasets del Portal de Datos Abiertos de la Comunidad de Madrid, 21 con Quality Gate 1 en PASS:** 15 publicados por la Comunidad y su Instituto de Estadística, y 6 del Consorcio Regional de Transportes que también tienen ficha en el portal (D-196).

Solo cuenta como «dataset CM» lo que tiene ficha en el portal (`hi_ingestion.catalog.provenance.is_cm_open_data`). El resto es complementario.

## Resumen

| # | Dataset | Publica | Gate 1 |
|---|---|---|---|
| 1 | [Alquiler del metro cuadrado medio mensual de viviendas habituales arrendadas por código postal para el municipio de Madrid](https://datos.comunidad.madrid/dataset/1934259) | Instituto de Estadística | PASS 2026-10-22 |
| 2 | [Alquiler del metro cuadrado mensual de viviendas arrendadas con valor catastral para municipios de más de 20.000 habitantes por tipo de vivienda. Municipios](https://datos.comunidad.madrid/dataset/alquiler_metro_cuadrado_mensual_viviendas_arrendadas_valor_catastral_municipios_mas_20000) | Instituto de Estadística | PASS 2026-10-22 |
| 3 | [Registro de centros de atención social](https://datos.comunidad.madrid/dataset/atencion_social_registro_centros) | Comunidad de Madrid | PASS 2026-10-22 |
| 4 | [Centros educativos de la comunidad de Madrid](https://datos.comunidad.madrid/dataset/centros_educativos) | Comunidad de Madrid | PASS 2026-10-22 |
| 5 | [Centros, servicios y establecimientos sanitarios](https://datos.comunidad.madrid/dataset/centros_servicios_establecimientos_sanitarios) | Comunidad de Madrid | PASS 2026-10-22 |
| 6 | [Recursos sanitarios. Farmacias. Municipios](https://datos.comunidad.madrid/dataset/farmacias) | Instituto de Estadística | PASS 2026-11-10 |
| 7 | [Hogares por tamaño del hogar. Censo 2021. Municipios](https://datos.comunidad.madrid/dataset/censo_2021_hogares_por_tamanyo) | Instituto de Estadística | PASS 2026-10-22 |
| 8 | [Nacidos vivos por lugar de residencia de la madre y sexo. Municipios](https://datos.comunidad.madrid/dataset/mnp_nacidos_vivos_por_residencia_y_sexo) | Instituto de Estadística | PASS 2026-11-10 |
| 9 | [Oficinas de farmacia](https://datos.comunidad.madrid/dataset/oficinas_farmacia) | Comunidad de Madrid | PASS 2026-11-10 |
| 10 | [Población censada por edad, nacionalidad y sexo. Censo anual. Municipios](https://datos.comunidad.madrid/dataset/poblacion_censada_por_edad_nacionalidad_y_sexo) | Instituto de Estadística | PASS 2026-10-22 |
| 11 | [Indicador de Renta Disponible Bruta Municipal. Municipios](https://datos.comunidad.madrid/dataset/irpf_indicador_renta) | Instituto de Estadística | PASS 2026-10-22 |
| 12 | [Secciones censales](https://datos.comunidad.madrid/dataset/secciones_censales) | Comunidad de Madrid | PASS 2026-10-20 |
| 13 | [Unidades escolares en centros no universitarios del régimen general por tipo de centro y enseñanza que imparten. Municipios](https://datos.comunidad.madrid/dataset/unidades_centros_no_universitarios_general_por_tipo_y_ensenanza) | Instituto de Estadística | PASS 2026-11-10 |
| 14 | [Censo anual Comunidad de Madrid. Viviendas por superficie agregada. Municipios](https://datos.comunidad.madrid/dataset/censo_anual_vivienda_por_superficie_agregada) | Instituto de Estadística | PASS 2026-10-22 |
| 15 | [Censo de vivienda y locales 2021. Viviendas familiares principales por régimen de tenencia. Municipios](https://datos.comunidad.madrid/dataset/censo_2021_viviendas_familiares_por_tenencia) | Instituto de Estadística | PASS 2026-11-10 |
| 16 | [Oferta planificada de la Red de Autobuses Urbanos del resto de municipios de la Comunidad de Madrid](https://datos.comunidad.madrid/dataset/red_de_autobuses_urbanos_resto_municipios_horarios_topologia) | Consorcio Regional de Transportes de Madrid | PASS 2026-11-10 |
| 17 | [Oferta planificada de la Red de Cercanías Madrid](https://datos.comunidad.madrid/dataset/red_de_cercanias_oferta_planificada_horarios_topologia) | Consorcio Regional de Transportes de Madrid | PASS 2026-11-10 |
| 18 | [Oferta planificada de la Red de Autobuses Urbanos de Madrid - EMT](https://datos.comunidad.madrid/dataset/red_de_autobuses_urbanos_emt_horarios_topologia) | Consorcio Regional de Transportes de Madrid | PASS 2026-11-10 |
| 19 | [Oferta planificada de la Red de Autobuses Interurbanos](https://datos.comunidad.madrid/dataset/red_de_autobuses_interurbanos_horarios_topologia) | Consorcio Regional de Transportes de Madrid | PASS 2026-11-10 |
| 20 | [Oferta planificada de la Red de Metro](https://datos.comunidad.madrid/dataset/red_de_metro_oferta_planificada_horarios_topologia) | Consorcio Regional de Transportes de Madrid | PASS 2026-11-10 |
| 21 | [Oferta planificada de la Red de Metro Ligero](https://datos.comunidad.madrid/dataset/red_de_metro_ligero_oferta_planificada_horarios_topologia) | Consorcio Regional de Transportes de Madrid | PASS 2026-11-10 |

## 1. Portal CM: publicados por la Comunidad de Madrid (15)

### Alquiler del metro cuadrado medio mensual de viviendas habituales arrendadas por código postal para el municipio de Madrid
- **Ficha:** https://datos.comunidad.madrid/dataset/1934259 · id `cm_alquiler_m2_codigo_postal_madrid` · publica: Instituto de Estadística
- **Licencia:** [Creative Commons Attribution](https://creativecommons.org/licenses/by/4.0/legalcode.es) (según el portal CM)
- **Qué alimenta:**
  - Métrica cargada: Alquiler mensual por metro cuadrado (códigos postales de Madrid) (`alquiler_m2_mensual_codigo_postal`)
  - Uso en la lista o en el buscador: **pendiente de A**
- **Quality Gate 1:** PASS · 2026-10-22 · 6/6 checks críticos · versión `2026-10-21-bc14c1e36441` · [quality_report.json](../evidence/gate-01/2026-10-22/cm_alquiler_m2_codigo_postal_madrid/quality_report.json)

### Alquiler del metro cuadrado mensual de viviendas arrendadas con valor catastral para municipios de más de 20.000 habitantes por tipo de vivienda. Municipios
- **Ficha:** https://datos.comunidad.madrid/dataset/alquiler_metro_cuadrado_mensual_viviendas_arrendadas_valor_catastral_municipios_mas_20000 · id `cm_alquiler_m2_municipios` · publica: Instituto de Estadística
- **Licencia:** [Creative Commons Attribution](https://creativecommons.org/licenses/by/4.0/legalcode.es) (según el portal CM)
- **Qué alimenta:**
  - Indicador por zona: Alquiler medio por metro cuadrado (viviendas habituales) (`alquiler_m2_mensual`, dato principal)
- **Quality Gate 1:** PASS · 2026-10-22 · 6/6 checks críticos · versión `2026-10-21-82cdb192ed1b` · [quality_report.json](../evidence/gate-01/2026-10-22/cm_alquiler_m2_municipios/quality_report.json)

### Registro de centros de atención social
- **Ficha:** https://datos.comunidad.madrid/dataset/atencion_social_registro_centros · id `cm_centros_atencion_social` · publica: Comunidad de Madrid
- **Licencia:** [Creative Commons Attribution](https://creativecommons.org/licenses/by/4.0/legalcode.es) (según el portal CM)
- **Qué alimenta:**
  - Indicador por zona: Plazas en residencias de mayores por cada 100 personas de 65 años o más (`plazas_residencia_por_100_mayores`, dato principal)
  - Puntos del mapa (mayores y atención social): `GET /api/v1/places?category=social`
- **Quality Gate 1:** PASS · 2026-10-22 · 5/5 checks críticos · versión `2026-10-21-9cadf73e6ea9` · 1.001 puntos · [quality_report.json](../evidence/gate-01/2026-10-22/cm_centros_atencion_social/quality_report.json)

### Centros educativos de la comunidad de Madrid
- **Ficha:** https://datos.comunidad.madrid/dataset/centros_educativos · id `cm_centros_educativos` · publica: Comunidad de Madrid
- **Licencia:** [Creative Commons Attribution](https://creativecommons.org/licenses/by/4.0/legalcode.es) (según el portal CM)
- **Qué alimenta:**
  - «Qué falta», fila «Colegios»: Centros educativos públicos por cada 1.000 menores de 15 años (`colegios_publicos_por_1000_menores`, dato principal)
  - Puntos del mapa (educación): `GET /api/v1/places?category=education`
- **Quality Gate 1:** PASS · 2026-10-22 · 5/5 checks críticos · versión `2026-10-21-27483ff8498b` · 3.851 puntos · [quality_report.json](../evidence/gate-01/2026-10-22/cm_centros_educativos/quality_report.json)

### Centros, servicios y establecimientos sanitarios
- **Ficha:** https://datos.comunidad.madrid/dataset/centros_servicios_establecimientos_sanitarios · id `cm_centros_sanitarios` · publica: Comunidad de Madrid
- **Licencia:** [Creative Commons Attribution](https://creativecommons.org/licenses/by/4.0/legalcode.es) (según el portal CM)
- **Qué alimenta:**
  - «Qué falta», fila «Centros de salud»: Centros de atención primaria por cada 10.000 habitantes (`centros_salud_por_10000_hab`, dato principal)
  - Puntos del mapa (salud): `GET /api/v1/places?category=health`
- **Quality Gate 1:** PASS · 2026-10-22 · 5/5 checks críticos · versión `2026-10-21-f2602e9e9275` · 1.543 puntos · [quality_report.json](../evidence/gate-01/2026-10-22/cm_centros_sanitarios/quality_report.json)

### Recursos sanitarios. Farmacias. Municipios
- **Ficha:** https://datos.comunidad.madrid/dataset/farmacias · id `cm_farmacias_municipios` · publica: Instituto de Estadística
- **Licencia:** [Creative Commons Attribution](https://creativecommons.org/licenses/by/4.0/legalcode.es) (según el portal CM)
- **Qué alimenta:**
  - Métrica cargada: Farmacias por cada 10.000 habitantes (`farmacias_por_10000_hab`)
  - Métrica cargada: Farmacias (`farmacias_total`)
  - Uso en la lista o en el buscador: **pendiente de A**
- **Quality Gate 1:** PASS · 2026-11-10 · 6/6 checks críticos · versión `2026-11-10-a2011625bc89` · 6.494 observaciones · [quality_report.json](../evidence/gate-01/2026-11-10/cm_farmacias_municipios/quality_report.json)

### Hogares por tamaño del hogar. Censo 2021. Municipios
- **Ficha:** https://datos.comunidad.madrid/dataset/censo_2021_hogares_por_tamanyo · id `cm_hogares_tamano_censo_2021` · publica: Instituto de Estadística
- **Licencia:** [Creative Commons Attribution](https://creativecommons.org/licenses/by/4.0/legalcode.es) (según el portal CM)
- **Qué alimenta:**
  - Indicador por zona: Porcentaje de hogares de cinco o más personas (`hogares_5_mas_pct`, dato principal)
  - Indicador por zona: Porcentaje de hogares de una persona (`hogares_unipersonales_pct`, dato principal)
  - Indicador por zona: Tamaño medio del hogar (aproximado) (`tamano_medio_hogar`, dato principal)
- **Quality Gate 1:** PASS · 2026-10-22 · 6/6 checks críticos · versión `2026-10-21-823dd42839c0` · [quality_report.json](../evidence/gate-01/2026-10-22/cm_hogares_tamano_censo_2021/quality_report.json)

### Nacidos vivos por lugar de residencia de la madre y sexo. Municipios
- **Ficha:** https://datos.comunidad.madrid/dataset/mnp_nacidos_vivos_por_residencia_y_sexo · id `cm_nacidos_vivos_municipios` · publica: Instituto de Estadística
- **Licencia:** [Creative Commons Attribution](https://creativecommons.org/licenses/by/4.0/legalcode.es) (según el portal CM)
- **Qué alimenta:**
  - Métrica cargada: Nacidos vivos (`nacidos_vivos`)
  - Uso en la lista o en el buscador: **pendiente de A**
- **Quality Gate 1:** PASS · 2026-11-10 · 6/6 checks críticos · versión `2026-11-10-9119056a0e09` · 22.538 observaciones · [quality_report.json](../evidence/gate-01/2026-11-10/cm_nacidos_vivos_municipios/quality_report.json)

### Oficinas de farmacia
- **Ficha:** https://datos.comunidad.madrid/dataset/oficinas_farmacia · id `cm_oficinas_farmacia` · publica: Comunidad de Madrid
- **Licencia:** [Creative Commons Attribution](https://creativecommons.org/licenses/by/4.0/legalcode.es) (según el portal CM)
- **Qué alimenta:**
  - Puntos del mapa (salud): `GET /api/v1/places?category=health`
  - Uso en la lista o en el buscador: **pendiente de A**
- **Quality Gate 1:** PASS · 2026-11-10 · 5/5 checks críticos · versión `2026-11-10-de61d48d7b4a` · 2.953 puntos · [quality_report.json](../evidence/gate-01/2026-11-10/cm_oficinas_farmacia/quality_report.json)

### Población censada por edad, nacionalidad y sexo. Censo anual. Municipios
- **Ficha:** https://datos.comunidad.madrid/dataset/poblacion_censada_por_edad_nacionalidad_y_sexo · id `cm_poblacion_edad_nacionalidad_sexo` · publica: Instituto de Estadística
- **Licencia:** [Creative Commons Attribution](https://creativecommons.org/licenses/by/4.0/legalcode.es) (según el portal CM)
- **Qué alimenta:**
  - «Qué falta», fila «Centros de salud»: Centros de atención primaria por cada 10.000 habitantes (`centros_salud_por_10000_hab`, denominador)
  - «Qué falta», fila «Colegios»: Centros educativos públicos por cada 1.000 menores de 15 años (`colegios_publicos_por_1000_menores`, denominador)
  - Indicador por zona: Plazas en residencias de mayores por cada 100 personas de 65 años o más (`plazas_residencia_por_100_mayores`, denominador)
  - Indicador por zona: Porcentaje de población menor de 15 años (`poblacion_0_14_pct`, dato principal)
  - Indicador por zona: Porcentaje de población de 65 años o más (`poblacion_65_mas_pct`, dato principal)
  - Indicador por zona: Población residente (`poblacion_total`, dato principal)
- **Quality Gate 1:** PASS · 2026-10-22 · 6/6 checks críticos · versión `2026-10-21-fd59e7826648` · [quality_report.json](../evidence/gate-01/2026-10-22/cm_poblacion_edad_nacionalidad_sexo/quality_report.json)

### Indicador de Renta Disponible Bruta Municipal. Municipios
- **Ficha:** https://datos.comunidad.madrid/dataset/irpf_indicador_renta · id `cm_renta_disponible_municipal` · publica: Instituto de Estadística
- **Licencia:** [Creative Commons Attribution](https://creativecommons.org/licenses/by/4.0/legalcode.es) (según el portal CM)
- **Qué alimenta:**
  - Indicador por zona: Renta disponible bruta per cápita (`renta_per_capita`, dato principal)
- **Quality Gate 1:** PASS · 2026-10-22 · 6/6 checks críticos · versión `2026-10-21-66a17af60f8e` · [quality_report.json](../evidence/gate-01/2026-10-22/cm_renta_disponible_municipal/quality_report.json)

### Secciones censales
- **Ficha:** https://datos.comunidad.madrid/dataset/secciones_censales · id `cm_secciones_censales` · publica: Comunidad de Madrid
- **Licencia:** [Creative Commons Attribution](https://creativecommons.org/licenses/by/4.0/legalcode.es) (según el portal CM)
- **Qué alimenta:**
  - Geografía de todas las zonas del mapa y de la lista de lo que falta
  - Indicador por zona: Superficie de la unidad administrativa (km²) (`admin_unit_area_km2`, dato principal)
- **Quality Gate 1:** PASS · 2026-10-20 · 10/10 checks críticos · versión `2026-10-20-37703ffcdfd0` · 179 municipios · 246 distritos censales · 131 barrios de Madrid · 4.417 secciones censales · 86.361 celdas H3 · [quality_report.json](../evidence/gate-01/2026-10-20/cm_secciones_censales/quality_report.json)

### Unidades escolares en centros no universitarios del régimen general por tipo de centro y enseñanza que imparten. Municipios
- **Ficha:** https://datos.comunidad.madrid/dataset/unidades_centros_no_universitarios_general_por_tipo_y_ensenanza · id `cm_unidades_escolares` · publica: Instituto de Estadística
- **Licencia:** [Creative Commons Attribution](https://creativecommons.org/licenses/by/4.0/legalcode.es) (según el portal CM)
- **Qué alimenta:**
  - Métrica cargada: Unidades escolares (`unidades_escolares`)
  - Uso en la lista o en el buscador: **pendiente de A**
- **Quality Gate 1:** PASS · 2026-11-10 · 6/6 checks críticos · versión `2026-11-10-bdf7c1ff864a` · 95.309 observaciones · [quality_report.json](../evidence/gate-01/2026-11-10/cm_unidades_escolares/quality_report.json)

### Censo anual Comunidad de Madrid. Viviendas por superficie agregada. Municipios
- **Ficha:** https://datos.comunidad.madrid/dataset/censo_anual_vivienda_por_superficie_agregada · id `cm_viviendas_superficie` · publica: Instituto de Estadística
- **Licencia:** [Creative Commons Attribution](https://creativecommons.org/licenses/by/4.0/legalcode.es) (según el portal CM)
- **Qué alimenta:**
  - Indicador por zona: Porcentaje de viviendas de menos de 60 m² (`viviendas_menos_60m2_pct`, dato principal)
- **Quality Gate 1:** PASS · 2026-10-22 · 6/6 checks críticos · versión `2026-10-21-1673f7e6ca4a` · [quality_report.json](../evidence/gate-01/2026-10-22/cm_viviendas_superficie/quality_report.json)

### Censo de vivienda y locales 2021. Viviendas familiares principales por régimen de tenencia. Municipios
- **Ficha:** https://datos.comunidad.madrid/dataset/censo_2021_viviendas_familiares_por_tenencia · id `cm_viviendas_tenencia_censo_2021` · publica: Instituto de Estadística
- **Licencia:** [Creative Commons Attribution](https://creativecommons.org/licenses/by/4.0/legalcode.es) (según el portal CM)
- **Qué alimenta:**
  - Métrica cargada: Viviendas principales por régimen de tenencia (`viviendas_por_tenencia`)
  - Uso en la lista o en el buscador: **pendiente de A**
- **Quality Gate 1:** PASS · 2026-11-10 · 6/6 checks críticos · versión `2026-11-10-048892fa99bc` · 567 observaciones · [quality_report.json](../evidence/gate-01/2026-11-10/cm_viviendas_tenencia_censo_2021/quality_report.json)

## 2. Portal CM: GTFS del CRTM con ficha en el portal (6)

### Oferta planificada de la Red de Autobuses Urbanos del resto de municipios de la Comunidad de Madrid
- **Ficha:** https://datos.comunidad.madrid/dataset/red_de_autobuses_urbanos_resto_municipios_horarios_topologia · id `crtm_gtfs_autobuses_urbanos` · publica: Consorcio Regional de Transportes de Madrid
- **Descarga:** https://www.arcgis.com/sharing/rest/content/items/357e63c2904f43aeb5d8a267a64346d8/data (fuente original; ficha en el portal CM, D-196)
- **Licencia:** [CRTM Licencia de datos abiertos (LDA)](https://www.crtm.es/licencia-de-uso) (según el portal CM)
- **Qué alimenta:**
  - Paradas y estaciones de autobuses urbanos del resto de municipios con su frecuencia de paso
  - Uso en la lista o en el buscador: **pendiente de A**
- **Quality Gate 1:** PASS · 2026-11-10 · 9/9 checks críticos · versión `2026-11-10-41f7f9c15b61` · 3.023 puntos · [quality_report.json](../evidence/gate-01/2026-11-10/crtm_gtfs_autobuses_urbanos/quality_report.json)

### Oferta planificada de la Red de Cercanías Madrid
- **Ficha:** https://datos.comunidad.madrid/dataset/red_de_cercanias_oferta_planificada_horarios_topologia · id `crtm_gtfs_cercanias` · publica: Consorcio Regional de Transportes de Madrid
- **Descarga:** https://www.arcgis.com/sharing/rest/content/items/1a25440bf66f499bae2657ec7fb40144/data (fuente original; ficha en el portal CM, D-196)
- **Licencia:** [CRTM Licencia de datos abiertos (LDA)](https://www.crtm.es/licencia-de-uso) (según el portal CM)
- **Qué alimenta:**
  - Paradas y estaciones de Cercanías con su frecuencia de paso
  - Uso en la lista o en el buscador: **pendiente de A**
- **Quality Gate 1:** PASS · 2026-11-10 · 9/9 checks críticos · versión `2026-11-10-1b018a22325c` · 93 puntos · [quality_report.json](../evidence/gate-01/2026-11-10/crtm_gtfs_cercanias/quality_report.json)

### Oferta planificada de la Red de Autobuses Urbanos de Madrid - EMT
- **Ficha:** https://datos.comunidad.madrid/dataset/red_de_autobuses_urbanos_emt_horarios_topologia · id `crtm_gtfs_emt` · publica: Consorcio Regional de Transportes de Madrid
- **Descarga:** https://www.arcgis.com/sharing/rest/content/items/868df0e58fca47e79b942902dffd7da0/data (fuente original; ficha en el portal CM, D-196)
- **Licencia:** [CRTM Licencia de datos abiertos (LDA)](https://www.crtm.es/licencia-de-uso) (según el portal CM)
- **Qué alimenta:**
  - Paradas y estaciones de autobuses EMT de Madrid con su frecuencia de paso
  - Uso en la lista o en el buscador: **pendiente de A**
- **Quality Gate 1:** PASS · 2026-11-10 · 9/9 checks críticos · versión `2026-11-10-8478ae5c9262` · 4.935 puntos · [quality_report.json](../evidence/gate-01/2026-11-10/crtm_gtfs_emt/quality_report.json)

### Oferta planificada de la Red de Autobuses Interurbanos
- **Ficha:** https://datos.comunidad.madrid/dataset/red_de_autobuses_interurbanos_horarios_topologia · id `crtm_gtfs_interurbanos` · publica: Consorcio Regional de Transportes de Madrid
- **Descarga:** https://www.arcgis.com/sharing/rest/content/items/885399f83408473c8d815e40c5e702b7/data (fuente original; ficha en el portal CM, D-196)
- **Licencia:** [CRTM Licencia de datos abiertos (LDA)](https://www.crtm.es/licencia-de-uso) (según el portal CM)
- **Qué alimenta:**
  - Paradas y estaciones de autobuses interurbanos con su frecuencia de paso
  - Uso en la lista o en el buscador: **pendiente de A**
- **Quality Gate 1:** PASS · 2026-11-10 · 9/9 checks críticos · versión `2026-11-10-5bbf3c95047c` · 6.645 puntos · [quality_report.json](../evidence/gate-01/2026-11-10/crtm_gtfs_interurbanos/quality_report.json)

### Oferta planificada de la Red de Metro
- **Ficha:** https://datos.comunidad.madrid/dataset/red_de_metro_oferta_planificada_horarios_topologia · id `crtm_gtfs_metro` · publica: Consorcio Regional de Transportes de Madrid
- **Descarga:** https://www.arcgis.com/sharing/rest/content/items/5c7f2951962540d69ffe8f640d94c246/data (fuente original; ficha en el portal CM, D-196)
- **Licencia:** [CRTM Licencia de datos abiertos (LDA)](https://www.crtm.es/licencia-de-uso) (según el portal CM)
- **Qué alimenta:**
  - Paradas y estaciones de metro con su frecuencia de paso
  - Uso en la lista o en el buscador: **pendiente de A**
- **Quality Gate 1:** PASS · 2026-11-10 · 9/9 checks críticos · versión `2026-11-10-cccabfd6f025` · 230 puntos · [quality_report.json](../evidence/gate-01/2026-11-10/crtm_gtfs_metro/quality_report.json)

### Oferta planificada de la Red de Metro Ligero
- **Ficha:** https://datos.comunidad.madrid/dataset/red_de_metro_ligero_oferta_planificada_horarios_topologia · id `crtm_gtfs_metro_ligero` · publica: Consorcio Regional de Transportes de Madrid
- **Descarga:** https://www.arcgis.com/sharing/rest/content/items/aaed26cc0ff64b0c947ac0bc3e033196/data (fuente original; ficha en el portal CM, D-196)
- **Licencia:** [CRTM Licencia de datos abiertos (LDA)](https://www.crtm.es/licencia-de-uso) (según el portal CM)
- **Qué alimenta:**
  - Paradas y estaciones de metro ligero con su frecuencia de paso
  - Uso en la lista o en el buscador: **pendiente de A**
- **Quality Gate 1:** PASS · 2026-11-10 · 9/9 checks críticos · versión `2026-11-10-599f9acfa270` · 56 puntos · [quality_report.json](../evidence/gate-01/2026-11-10/crtm_gtfs_metro_ligero/quality_report.json)

## 3. Fuentes complementarias en uso (1)

No cuentan como datos CM. Sirven para calcular, no sustituyen a una fuente regional.

### Red peatonal de OpenStreetMap (extracto Geofabrik de la Comunidad de Madrid)
- **Ficha:** https://download.geofabrik.de/europe/spain/madrid.html · id `osm_red_peatonal` · publica: OpenStreetMap contributors (extracto de Geofabrik)
- **Licencia:** [Open Database License (ODbL) 1.0](https://opendatacommons.org/licenses/odbl/1-0/) (según el registro de fuentes)
- **Qué alimenta:**
  - Red peatonal para medir la distancia a pie a cada servicio
  - Uso en la lista o en el buscador: **pendiente de A**
- **Quality Gate 1:** PASS · 2026-11-11 · 5/5 checks críticos · versión `2026-11-11-a3206c2d1d5f` · 57.658,8 km de calles y caminos · [quality_report.json](../evidence/gate-01/2026-11-11/osm_red_peatonal/quality_report.json)

## 4. En el catálogo, todavía sin ingerir (11)

Revisados y con licencia clara, pero sin Quality Gate: no se citan como usados. **Pendiente de A.**

| Dataset | Publica | ¿Portal CM? | Ficha |
|---|---|---|---|
| Arbolado en parques y zonas verdes de Madrid (detalle) | Ayuntamiento de Madrid | no | https://datos.madrid.es/dataset/300761-0-arbolado-especies |
| Censo de locales, sus actividades y terrazas de hostelería y restauración | Ayuntamiento de Madrid | no | https://datos.madrid.es/dataset/200085-0-censo-locales |
| Equipamientos y entidades de la ciudad de Madrid (que hay publicados en www.madrid.es) | Ayuntamiento de Madrid | no | https://datos.madrid.es/dataset/300331-0-equipamientos-municipales |
| Panel de indicadores de distritos y barrios de Madrid. Estudio sociodemográfico | Ayuntamiento de Madrid | no | https://datos.madrid.es/dataset/300087-0-indicadores-distritos |
| Barrios del Municipio de Madrid | Comunidad de Madrid | sí | https://datos.comunidad.madrid/dataset/barrios_municipio_madrid |
| Distritos del Municipio de Madrid | Comunidad de Madrid | sí | https://datos.comunidad.madrid/dataset/distritos_municipio_madrid |
| Covid 19 -TIA por Municipios y Distritos de Madrid | Comunidad de Madrid | sí | https://datos.comunidad.madrid/dataset/covid19_tia_muni_y_distritos |
| Parcelas publicadas en el Portal del Suelo 4.0 | Comunidad de Madrid | sí | https://datos.comunidad.madrid/dataset/parcelas_portal_suelo |
| Personas con discapacidad por edad y sexo. Municipios | Instituto de Estadística | sí | https://datos.comunidad.madrid/dataset/personas_discapacidad_por_edad_y_sexo |
| Número de transacciones inmobiliarias, por municipio. Vivienda libre y vivienda protegida. Comunidad de Madrid | Instituto de Estadística | sí | https://datos.comunidad.madrid/dataset/transacciones_inmobiliarias_municipio |
| Transacciones inmobiliarias de vivienda nueva y de segunda mano, por municipio. Comunidad de Madrid | Instituto de Estadística | sí | https://datos.comunidad.madrid/dataset/transacciones_vivienda_nueva_usada_municipio |
