# Slides — Vida Fácil (contenido, dirección visual y capturas)

## Qué es este fichero
Las 4 slides que piden las bases (§8, resumen en `docs/09_datamad/24_bases_oficiales_2026.md`), en su orden.
- **Entrega:** PDF (y PPTX de respaldo) antes de las 14:00 del 26 nov. Se sube como tarde a las 13:30 (`docs/09_datamad/25_plan_competicion.md` §9).
- **24 nov:** solo maquetar con capturas reales de la demo desplegada.
- **Estado:** borrador del 11 nov. Lo marcado «pendiente de A/B/C» se cierra en el freeze del 23 nov.
- **Reordenación del 23 nov** (decisión de Mariano sobre el informe del jurado simulado del 21 nov). En la formación del 5 nov se describió al ganador de 2024 como un buscador de pisos con el ambulatorio y el metro cerca y un perfil ponderado, hecho con scraping, y se le llamó «calderilla». Por eso el pitch abre con lo que eso no hacía:
  - «qué le falta a cada zona», para ayuntamientos;
  - la ficha de la parcela exacta, para inversores;
  - la API abierta;
  - todo con datos abiertos descargados de sus portales, sin scraping.

  El buscador para personas queda como la base, comparado en voz alta con lo de 2024: los 179 municipios, sin scraping, con el trayecto al trabajo y con «qué falta». Las 4 slides siguen el formato de las bases. Lema nuevo: «La zona que te conviene, y lo que le falta». El guion, en `pitch/guion.md` (545 palabras).

> Las decisiones del 11 nov están registradas como D-199 a D-207 (`docs/00_index/01_decisions_log.md`). El brief de diseño (`DISENO_VIDA_FACIL.md`, adoptado por D-201) sigue fuera del repo: se cita como documento interno, no como evidencia pública.

## El mensaje (del documento de la idea del 31 oct; solo el mensaje)
- **Tesis:** «Otros te enseñan lo que hay. Nosotros te enseñamos lo que falta.»
- **Tres usuarios:**
  - personas (gratis): «¿Dónde vivo mejor con lo que necesito?»;
  - ayuntamientos (planifican): «¿Qué le falta a cada zona y dónde invierto primero?»;
  - empresas (pagan): «¿Qué hace falta aquí?».
- **Modelo:** las empresas pagan por saber qué falta, y eso financia que sea gratis para las personas. Nunca se venden datos de personas: solo se ven zonas, siempre sumadas y anónimas.
- **Desde el 19 nov** (decisión de Mariano, `pitch/modelo_negocio.md`): también es gratis para los ayuntamientos, y las empresas que pagan son los inversores y los promotores privados.
- **Desde el 23 nov** (decisión de Mariano, `pitch/modelo_negocio.md`): gratis siempre, para todos, los datos, las zonas, «Qué falta», cada ficha de parcela y la API. De pago, el plan empresarial (carteras de parcelas, avisos de suelo nuevo y la API y el MCP a gran volumen con clave) y los informes personalizados (estudios de suelo a medida).

**Del PDF no se usa:**
- ninguna de sus cifras de ejemplo: zonas del Reality Check, 4.000–4.500 €/mes ni «10 conjuntos de datos»;
- el barrio de ejemplo con coworking, gimnasio y «lo que la gente dice que necesita». La necesidad declarada es un siguiente paso y nunca se simula (D-194);
- su estilo visual;
- el nombre «Housing Intelligence»: en todo lo que se ve, un solo nombre, «Vida Fácil» (jurado simulado del 12 nov). «Housing Intelligence» queda solo como nombre del repositorio.

---

## Slide 1 · Título, integrantes y descripción breve
**Texto:**
- **Vida Fácil** (logotipo de texto, Plus Jakarta Sans 700).
- *La zona que te conviene, y lo que le falta* (lema, en violeta, en dos líneas: el corte va tras la coma). **Desde el 23 nov** (decisión de Mariano), en lugar del lema anterior (D-199).
- Descripción, desde el 23 nov: «Para ayuntamientos, qué le falta a cada zona de la Comunidad de Madrid. Para inversores, la ficha de una parcela exacta. Para todos, una API abierta. Con datos abiertos descargados de sus portales, sin scraping.» (revisión del #122, R-03: antes, «con datos oficiales por API», que no vale para OpenStreetMap ni para lo que se descarga). Antes: «El mapa de lo que falta en cada zona de la Comunidad de Madrid: para elegir dónde vivir y para decidir dónde invertir.»
- Integrantes: equipo de una persona. En el PDF va el nombre completo, que el build toma de `DECK_INTEGRANTES` (`pitch/deck/README.md`). Decisión de Mariano (11 nov): en el repo público solo «Mariano»; el nombre completo va solo en el PDF del deck y en el formulario.
- Pie: «Código abierto (Apache-2.0) · Datos abiertos de la Comunidad de Madrid». El «DATAMAD 2026» ya va arriba, en la línea pequeña sobre el nombre.

**Composición:**
- Mitad izquierda: título, lema y descripción sobre `--bg`.
- Mitad derecha: captura **C5** (zona en 3D) dentro de una tarjeta de cristal grande, con el contorno violeta de la zona visible. **Rehecha por P el 23 nov en producción, con el deploy-46 (`dpl_GyEfen16H6Kxbcng13cABR124UY6`, código `542283b8`)** (`pitch/capturas/C5.png`, 1440 × 900): Chamartín en 3D, con las etiquetas de la estación de Chamartín, el centro de salud Potosí, el metro de Concha Espina y el colegio Padre Poveda, y la tarjeta «Lo que le falta a esta zona» (escuelas infantiles y centros de mayores JUSTO, colegios CUBIERTO). El recorte (`deck.css`, desde x 525 y desde arriba) enseña las pestañas «Qué falta», «Cómo lo calculamos» e «Inversores». Antes, la de B del 11 nov (`evidence/map-004/2026-11-11/prod_c5_chamartin_3d_desktop.png`), con «Datos: 21 conjuntos…», el logo antiguo y sin la pestaña «Inversores».
- Sin más elementos.

**Fuentes en la slide:** ninguna cifra.

---

## Slide 2 · Problema y datasets usados (con enlaces)
### Columna izquierda: el problema
Título: **«Nadie te dice qué le falta a cada zona»**.

Desde el 23 nov, en el orden del pitch:

| Quién | Qué le pasa hoy |
|---|---|
| Ayuntamientos | Los datos llegan sueltos: cuesta ver dónde falta una escuela infantil o un centro de salud frente al resto de la región. |
| Promotores e inversores | Eligen suelo sin ver la demanda. (Antes: «Empresas: abren por intuición, sin saber qué hace falta en la zona.», que no era el cliente que paga; juez B2 del jurado simulado.) |
| Personas | El precio en un sitio, los colegios en otro y el transporte en otro: nadie les dice qué zona va con su vida. |

Cierre de la columna: «Otros te enseñan lo que hay. Nosotros, lo que falta.»

### Columna derecha: los datos
Titular: **«39 conjuntos de datos del Portal de Datos Abiertos de la Comunidad de Madrid, todos con control de calidad superado»**. Fuente: `pitch/datasets_cm.md`, regenerado el 19 nov, con 39 en Gate 1 PASS, y producción: `GET /api/v1/datasets?cm_only=true` da `cm_open_data_count: 39`, y 59 conjuntos en total (comprobado por D el 19 nov, tras el despliegue de `396d8f6`). El número de la slide lo pone `pitch/deck/build.py` desde el mismo catálogo. Se revisa el 23 nov regenerando `datasets_cm.md`. **Cambio de maquetación del 19 nov, para que lo vea Mariano:** con los 3 nuevos (el Catastro por uso, por municipio y por distrito, y los visados de obra; D-247 y D-248), «Vivienda» pasa a 12 y ocupa una línea más. Para que «Apoyo (no CM)» siga dentro de la tarjeta, las filas de la tabla tienen 2 px menos de margen arriba y abajo, y la tabla y la línea de apoyo, 8 y 4 px menos de separación (`pitch/deck/deck.css`). La letra no cambia. Comprobado a 1920 × 1080.
- **De dónde salen los 12 desde el 12 nov** (Gate 1 en `evidence/gate-01/2026-11-14/` y, el del suelo, en `evidence/gate-01/2026-11-18/`):
  - D-235, contexto de la zona: las infracciones penales conocidas (`cm_infracciones_penales_municipios`) y la antigüedad de las viviendas (`cm_viviendas_antiguedad`). Con ellos, 29;
  - D-237, entorno: los aparcamientos de disuasión del Consorcio (`crtm_aparcamientos_disuasion`) y las 3 fichas de la red de calidad del aire de la Comunidad (`cm_calidad_aire_estaciones`, `cm_calidad_aire_horario_2025` y `cm_calidad_aire_zonas`);
  - D-241, vivienda nueva: las compraventas de vivienda nueva y usada (`cm_transacciones_nueva_usada`) y el valor tasado por antigüedad (`cm_valor_tasado_vivienda_antiguedad`);
  - D-246, suelo público para vivienda: las parcelas del Portal del Suelo 4.0 (`cm_parcelas_portal_suelo`), en producción desde el 18 nov. Con él, 36;
  - D-247 y D-248, la versión para inversores: el Catastro por uso de la Comunidad, por municipio y por distrito (`cm_catastro_unidades_urbanas_uso` y `cm_catastro_inmuebles_distrito_uso`), y los visados de obra (`cm_visados_presupuesto_obra`), en producción desde el 19 nov. Con ellos, 39.
- **Matiz, si preguntan:**
  - Los 12 nuevos no cambian el % de encaje ni «Qué falta»: 9 son contexto de la zona y se ven en su vista, y 3 son de la versión para inversores.
  - Las 3 topologías se usan con «Sin escaleras».
  - Los dos de camas (Dotación de camas y Hospitales y datos asistenciales) dan el total de la región: demuestran que el portal no publica camas por hospital, y por eso las de cada hospital salen del Catálogo Nacional de Hospitales (D-217 §4, D-218). La web los enseña bajo la nota del hospital (D-231, en producción).

Cada nombre lleva el hipervínculo a su ficha en el PDF. La tabla sale de `dataset_rows()` de `pitch/deck/build.py`, la misma función que pinta la slide:

| Tema | Datasets (nombre corto → ficha del portal) |
|---|---|
| Población y territorio (5) | [Secciones censales](https://datos.comunidad.madrid/dataset/secciones_censales) · [Población por edad](https://datos.comunidad.madrid/dataset/poblacion_censada_por_edad_nacionalidad_y_sexo) · [Hogares por tamaño](https://datos.comunidad.madrid/dataset/censo_2021_hogares_por_tamanyo) · [Nacidos vivos](https://datos.comunidad.madrid/dataset/mnp_nacidos_vivos_por_residencia_y_sexo) · [Renta disponible](https://datos.comunidad.madrid/dataset/irpf_indicador_renta) |
| Vivienda (12) | [Viviendas por superficie](https://datos.comunidad.madrid/dataset/censo_anual_vivienda_por_superficie_agregada) · [Viviendas por tenencia](https://datos.comunidad.madrid/dataset/censo_2021_viviendas_familiares_por_tenencia) · [Alquiler por municipio](https://datos.comunidad.madrid/dataset/alquiler_metro_cuadrado_mensual_viviendas_arrendadas_valor_catastral_municipios_mas_20000) · [Alquiler por código postal](https://datos.comunidad.madrid/dataset/1934259) · [Valor tasado de la vivienda](https://datos.comunidad.madrid/dataset/1004050) · [Valor tasado por antigüedad](https://datos.comunidad.madrid/dataset/valor_tasado_por_antiguedad) · [Viviendas por antigüedad](https://datos.comunidad.madrid/dataset/censo_anual_vivienda_por_antiguedad) · [Compraventas nueva y usada](https://datos.comunidad.madrid/dataset/transacciones_vivienda_nueva_usada_municipio) · [Suelo público (Portal del Suelo)](https://datos.comunidad.madrid/dataset/parcelas_portal_suelo) · [Catastro por uso](https://datos.comunidad.madrid/dataset/unidades_urbanas_por_uso) · [Catastro por distrito](https://datos.comunidad.madrid/dataset/catastro_inmuebles_por_distrito_y_uso) · [Visados de obra](https://datos.comunidad.madrid/dataset/1006022) |
| Servicios (8) | [Centros educativos](https://datos.comunidad.madrid/dataset/centros_educativos) · [Unidades escolares](https://datos.comunidad.madrid/dataset/unidades_centros_no_universitarios_general_por_tipo_y_ensenanza) · [Centros sanitarios](https://datos.comunidad.madrid/dataset/centros_servicios_establecimientos_sanitarios) · [Camas por dependencia](https://datos.comunidad.madrid/dataset/1912720) · [Hospitales](https://datos.comunidad.madrid/dataset/1912744) · [Centros de atención social](https://datos.comunidad.madrid/dataset/atencion_social_registro_centros) · [Oficinas de farmacia](https://datos.comunidad.madrid/dataset/oficinas_farmacia) · [Farmacias por municipio](https://datos.comunidad.madrid/dataset/farmacias) |
| Transporte (CRTM) (10) | [Metro](https://datos.comunidad.madrid/dataset/red_de_metro_oferta_planificada_horarios_topologia) · [Metro Ligero](https://datos.comunidad.madrid/dataset/red_de_metro_ligero_oferta_planificada_horarios_topologia) · [Cercanías](https://datos.comunidad.madrid/dataset/red_de_cercanias_oferta_planificada_horarios_topologia) · [EMT](https://datos.comunidad.madrid/dataset/red_de_autobuses_urbanos_emt_horarios_topologia) · [Autobuses urbanos](https://datos.comunidad.madrid/dataset/red_de_autobuses_urbanos_resto_municipios_horarios_topologia) · [Interurbanos](https://datos.comunidad.madrid/dataset/red_de_autobuses_interurbanos_horarios_topologia) · [Accesibilidad del metro](https://datos.comunidad.madrid/dataset/red_de_metro_lineas_estaciones_accesos_vestibulos_andenes) · [Accesibilidad del Metro Ligero](https://datos.comunidad.madrid/dataset/red_de_metro_ligero_tranvia_lineas_estaciones_accesos_vestibulos_andenes) · [Accesibilidad de Cercanías](https://datos.comunidad.madrid/dataset/red_de_cercanias_lineas_estaciones_accesos_vestibulos_andenes) · [Aparcamientos de disuasión](https://datos.comunidad.madrid/dataset/aparcamientos_disuasion) |
| Contexto de la zona (4) | [Aire: estaciones](https://datos.comunidad.madrid/dataset/calidad_aire_estaciones) · [Aire: datos horarios](https://datos.comunidad.madrid/dataset/calidad_aire_datos_historico) · [Aire: zonas](https://datos.comunidad.madrid/dataset/calidad_aire_zonas) · [Infracciones penales](https://datos.comunidad.madrid/dataset/hechos_conocidos_penales_por_tipologia_municipios_mayores_20000_por_municipio) |

- **Grupos:** salen del campo `domain` del catálogo (`THEMES` en `build.py`). «Población y territorio» junta geografía, población y renta, y «Contexto de la zona», el aire y las infracciones, para que las 39 quepan en la slide (5 + 12 + 8 + 10 + 4 = 39; la tabla de arriba es la que pinta `dataset_rows()` el 23 nov). Los enlaces salen de `portal_url` (`services/ingestion/src/hi_ingestion/catalog/provenance.py`), igual que en `datasets_cm.md`.
- **Línea pequeña bajo la tabla:** «Apoyo (no CM): OpenStreetMap, Ayuntamiento, Sanidad, Vivienda y Hacienda.». Son los 20 conjuntos complementarios de `pitch/datasets_cm.md` §3: el Ayuntamiento de Madrid (padrón, panel de distritos, ruido, aire, aparcamientos, locales, y la edificabilidad de VEDA y el estado de los ámbitos del Plan General), OpenStreetMap (calles, parques, ocio y la M-40), el Ministerio de Sanidad (hospitales y centros de salud), el Ministerio de Vivienda (alquiler del SERPAVI, D-242) y la Agencia Tributaria (contratos nuevos, D-228). El Plan Vive de la Comunidad cuenta también como complementario: es una página web, no una ficha del portal (D-241).
- **Pie:** «Lista completa, con licencias y control de calidad: github.com/marianohernando/housing-intelligence → `pitch/datasets_cm.md`».

**Composición:** dos tarjetas de cristal, la del problema al 40 % del ancho y la de los datos al 60 %. Cada tema de la tabla lleva su icono de línea. La cifra («39») va grande en violeta; el build la calcula del catálogo.

**Líneas de MELODA, desde el 23 nov** (P6 del informe del jurado simulado; decisión de Mariano; la frase, del coordinador), bajo la de apoyo: «MELODA: 16 sobre 49 de media; 1 de 5 en actualización. Las 10 fichas del Consorcio sacan 8 en este portal, frente a 24,7 de media en el portal del Consorcio (281 conjuntos).», con el enlace a spain.meloda.org. Cifras comprobadas contra `pitch/meloda_cm_snapshot.json` (los 39 emparejados por la URL de su ficha: media 15,97 y `d6_frequency` 1 en los 39) y `pitch/datasets_cm.md`, «Reutilización según MELODA» (16,0; las 10 fichas del Consorcio, 8; el portal del Consorcio, 24,7 de media en 281 conjuntos, sin emparejar uno a uno: pregunta 62). Son las del bloque 5 del guion. **Medido el 23 nov a 1920 × 1080** (`build.py` en borrador, vista previa a 100 ppp): para que las dos líneas quepan dentro de la tarjeta, la tarjeta de datos tiene 24 px de margen arriba y abajo (antes 36), la cifra grande 100 px (antes 120), las filas 3 px (antes 5), y la tabla y la línea de apoyo 6 px de separación (antes 12 y 10) (`pitch/deck/deck.css`). La letra de la tabla no cambia; la de MELODA es de 22 px, el mínimo del build, para que quepa «(281 conjuntos)» (revisión del #122, R-07). En la slide 4, el recuadro «Probada con 8 personas» baja a 24 px (antes 26) para que no suba sobre el paso 3.

---

## Slide 3 · Resultados: utilidad, impacto y viabilidad
Tres tarjetas de cristal en fila y, debajo, una banda con los enlaces.

**Composición desde el 23 nov** (decisión de Mariano; `pitch/deck/deck.html`). Las columnas van en el orden del pitch:
1. **«Impacto · ayuntamientos» → «Qué falta en cada zona»:** los cuatro estados; «**25.551** niños de 0 a 4 años viven en 3 distritos donde faltan escuelas infantiles.»; «Dónde invertir primero: Puente de Vallecas (57 por cada 100 de los municipios parecidos), Carabanchel y Villaverde.»; y «Cada falta, con su fuente y su probabilidad.». Antes iba en el centro y decía «viven donde faltan escuelas infantiles», que se podía oír como «25.551 niños sin escuela».
2. **«Utilidad» → «La parcela exacta y la zona que te conviene»:**
   - «**Inversores:** busca tu parcela en Madrid capital y calcula si sale, con la demanda de su zona.» (la línea que hasta el 22 nov iba al pie de «Viabilidad», con «Ya está»);
   - «**Personas:** en 179 municipios, sin scraping, con el trayecto al trabajo y lo que le falta a cada zona.» (revisión del #122, R-06: la slide no nombra al ganador de 2024, que puede estar en la sala y del que no hay fuente pública; el guion lo cita como algo contado en la formación);
   - la cita de la segunda ronda, «Ha mejorado un montón… ahora sí que te arroja cosas interesantes.», firmada «P6, segunda prueba con usuarios, 23 nov», sin nombre (A4, del jurado simulado, vio flojas las del 14 nov);
   - las miniaturas C2 y C3. **C3 se RECAPTURA tras el despliegue del 23 nov**; la ruta no cambia hasta entonces.
3. **«Viabilidad» → «Se sostiene»:** «Gratis siempre: datos, zonas, «Qué falta», cada ficha de parcela y la API.», «Pagarán las empresas: plan empresarial e informes a medida.», «Solo zonas, nunca datos de personas.», «Coste de infraestructura: 0 € hoy; unos 45 $/mes para poder cobrar.» (revisión del #122, R-08) y «API y MCP abiertos y gratuitos, sin clave.». Al pie, con el borde violeta: «**Ninguna cifra la genera una IA:** salen de cálculos deterministas sobre datos oficiales, cada una con su fuente.».
- **Pie:** «Demo pública con datos reales (datos del 19 nov). Niños de 0 a 4 años: padrón del Ayuntamiento de Madrid.» (antes, «(12 nov)»; la API está en `data_version 2026-11-19`).
- **Medido el 23 nov a 1920 × 1080** (`build.py` en borrador sin fallos, vista previa a 100 ppp): para que quepan las tres columnas, la letra de las viñetas y de la línea del pie de «Viabilidad» baja de 26 a 24 px (`pitch/deck/deck.css`), por encima del mínimo de 22 px que comprueba el build. Las tres tarjetas acaban encima de la banda de enlaces, y en «Utilidad» las miniaturas quedan justo bajo la cita.

Lo que sigue es el detalle de cada parte, con su historia; los textos de la slide son los de arriba.

### Utilidad, personas: la base
**Va con buscador:** producción lo tiene encendido desde el 11 nov y verificado (`NEXT_PUBLIC_FEATURE_SEARCH=true`; `evidence/gate-06/2026-11-11-deploy/deploy-12-buscador.md`, PR #11: smoke 7/7, axe AA sin fallos, consola limpia). La **versión sin buscador** queda de reserva, sin «próximamente», por si el 24 nov la demo vuelve a enseñar «Muy pronto»:
- Título: «Mira qué tienes cerca de casa».
- «Minutos a pie, por la calle, hasta el colegio, el centro de salud o la parada de autobús más cercanos.» (desde el 23 nov sin la farmacia: a un ciudadano no le sirve, segunda prueba de P6) (CORE-005, D-211; en la web: `evidence/map-004/2026-11-11/c4_que_falta_completa_desktop.png`).
- «Cada dato con su fuente y su fiabilidad.»
- Captura: la tarjeta de zona con «A pie: N min» (recorte de C5) en lugar de C2 y C3.

Versión con buscador (la que vale):
- **Título de la tarjeta, hasta el 22 nov:** «Encuentra la zona que te conviene», con las palabras de la web desde D-245. Debajo, una línea: «Cada zona, en palabras y con su %, con hechos que se pueden comprobar y su fiabilidad.»
- Cuentan su hogar, su alquiler máximo y dónde trabajan. Reciben «Zonas que te convienen» («os» con más de una persona): cada una con su banda en palabras («Muy buena opción», «Buena opción», «Opción regular» o «Poco recomendable») y su precio al mes; en escritorio, también el **% de encaje**, pequeño. La tarjeta enseña lo esencial y, en «Ver más», el % y hechos que se entienden, cada uno con su nivel de confianza en palabras. Lo que marcan primero pesa más, cada minuto cuenta y lo que no tiene datos nunca cuenta como 0 (D-215, D-243, D-245; `pitch/metodologia.md` §1.3).
- **Caso demo real** (`data/fixtures/contracts/scenario_state.familia_castellana.fixture.json`): pareja con 2 hijos de 4 y 8 años, 1.500 €/mes, colegio a 10 min como requisito y trabajo en la Castellana. Resultado en producción el 15 nov (`POST /api/v1/search` con ese fixture y la web, `fit-0.9`, D-243), con las palabras de la web comprobadas por D el 18 nov (`55651c2`):
  - «Hemos encontrado 42 zonas para vosotros»: **42 de las 199 zonas** cumplen todo, 157 no y ninguna sale sin datos. Eran 27, y 15 sin datos, hasta que el alquiler de referencia del Ministerio rellenó los pueblos (D-242);
  - todas cumplen lo que pide la familia; el % dice cuánto le conviene todo lo demás: 12 «Muy buena opción» (90 % o más), 5 «Buena opción», 13 «Opción regular» y 12 «Poco recomendable»;
  - **arriba, Puente de Vallecas y Latina, las dos «Muy buena opción · 94 %»**. La web pone 1.ª a Puente de Vallecas, porque a igual % tiene más cerca los servicios del día a día. La lista ya no dice «Empatan»: lo dice la tarjeta, en «Ver más» («Igual de buena que Latina (94 %).»). Siguen Usera y Moratalaz (93 %); Tetuán, Ciudad Lineal y Villaverde (92 %), y Carabanchel, Coslada y Leganés (90 %);
  - la tarjeta de Puente de Vallecas: «Unos 1.129 € al mes» («Precio orientativo»), colegio a unos 4 min, «41 min en transporte público hasta Paseo de la Castellana (Azca), llegando a las 9:00» y «No le falta nada de lo que buscáis.». En «Ver más», «Tiene lo que pedís. Aun así, comparado con municipios parecidos, aquí faltan escuelas infantiles.»: la familia no marca escuela infantil, así que esa falta no le baja el %; si la marcara, se quedaría en el 89 %;
  - **antes** (`fit-0.6`, 12 nov): Latina 1.ª al 98 %, con cuatro empatadas.
- **«¿Queréis ver más zonas?»** (Reality Check; antes «¿Y si cambias algo?»): cuántas zonas aparecen al cambiar una sola condición. En el caso demo:
  - «+5 min a pie hasta colegio con primaria · saldrían 49 más: 91 zonas en total»;
  - «+150 €/mes · saldrían 3 más: 45 zonas en total»;
  - «Lo que más limita vuestra búsqueda es: Colegio con primaria a 10 min andando como mucho»;
  - en «Casi valen» (antes «Casi encajan») se quedan, por el presupuesto, Chamartín, Arganzuela, Centro, Chamberí y Retiro. Sin %: la web dice cuánto se pasan (Chamartín, «Se pasa unos 90 € al mes de vuestro presupuesto»).

  Capturas **C2** (las dos primeras filas de «Zonas que os convienen») y **C3** (este bloque, con su primera opción), rehechas por D en producción el 18 nov, con la claridad en el móvil ya desplegada (`55651c2`, `pitch/capturas/`). **C3, rehecha por P el 23 nov en producción, con el deploy-46 (`dpl_GyEfen16H6Kxbcng13cABR124UY6`, código `542283b8`):** las mismas cifras («42 zonas», «saldrían 49 más: 91 zonas en total», «saldrían 3 más: 45 zonas en total») y, en el pie de datos, «Datos: 39 conjuntos…» (antes, «35»). El recorte va 15 px más a la derecha, como la tarjeta (`deck.css`).
- **Coste:** alquiler medio por m² × m² del hogar (77 m² para 4 personas, Censo 2021 del INE). Es orientativo y tira a la baja: son contratos vigentes declarados en el IRPF, no anuncios (D-214). En la slide no va ninguna cifra de coste sin la palabra «unos».
- **Trabajo:** cuenta los minutos de puerta a puerta en transporte público para llegar a las 9:00, con los horarios publicados de las 6 redes del CRTM (CORE-009, D-220). En producción desde el 12 nov. **Límite que se dice si preguntan:** son horarios programados de un día laborable, no tiempos reales, y en 45–50 zonas de la Sierra Norte y del sureste no se llega a las 9:00 (D-220 §6).
- **«Sin escaleras»** (opcional, D-223): quien lo marca ve los minutos andando hasta la estación de metro, Metro Ligero o Cercanías que el CRTM da como totalmente accesible. Nunca se deduce de nada ni se etiqueta a nadie, y la tarjeta dice lo que no mide (autobuses, aceras y portales). En producción desde el 12 nov (despliegue de `2761696`). En la slide va una línea, solo si cabe.
- **Seguridad: no va en la slide.** No puntúa (D-224, D-226), y si preguntan la respuesta es la 36 de `pitch/preguntas.md`.
- **Antes de maquetar** se vuelven a comprobar las cifras en la demo, por si cambian los datos. Capturas C1, C2 y C3: las rehízo D en producción el 18 nov con `fit-0.9` y la claridad en el móvil (`55651c2`), a 1440 × 900; C6, a 390 × 844 (`pitch/capturas/`).

### Impacto: ayuntamientos que deciden dónde invertir (columna izquierda desde el 23 nov)
**Fase de mejora (12–14 nov)**, ya en `deck.html`; la frase de la cifra cambia el 23 nov (abajo):
- **Cifra de impacto (A, D-229, `impact-0.1`):** «**25.551** niños de 0 a 4 años viven donde faltan escuelas infantiles», en grande, y debajo «Dónde invertir primero: Puente de Vallecas (57 por cada 100 de los municipios parecidos), Carabanchel y Villaverde». Sustituye al ejemplo largo y a «179 municipios y 21 distritos de Madrid».
  - **Desde el 23 nov:** «**25.551** niños de 0 a 4 años viven en 3 distritos donde faltan escuelas infantiles.», para que no se oiga como «niños sin escuela», y debajo «Cada falta, con su fuente y su probabilidad.». Es una señal para priorizar: con Holm sobre los 21 distritos solo aguanta Puente de Vallecas (p = 0,00114 frente a 0,00238), y sobre las 199 zonas ninguna (pregunta 46; decisión de Mariano: se mantiene la cifra, con la respuesta preparada).
  - Fuente: `GET /api/v1/gaps/impact` y `evidence/gate-04/2026-11-12/impact-cifras.txt`, con los datos del 12 nov; las mismas cifras con los del 19 nov (API leída el 21 nov). Son el 9,8 % de los niños de esa edad: Puente de Vallecas 9.433, Carabanchel 9.150 y Villaverde 6.968, del padrón de cada distrito. Puente de Vallecas tiene ratio 0,571, con p = 0,00114.
  - En el pie: «Niños de 0 a 4 años: padrón del Ayuntamiento de Madrid».
  - En producción desde el 12 nov (`GET /api/v1/gaps/impact`, comprobado: 25.551 de 260.310, 3 zonas). Si cambian los datos, se cambia la cifra. El ranking también se ve en la web, en «Dónde invertir primero» («Qué falta» sin zona): Puente de Vallecas 9.433 (57 por cada 100), Carabanchel 9.150 (68) y Villaverde 6.968 (61).
  - Las demás filas (farmacias y mayores) van en la pregunta 47, no en la slide. La vivienda, desde el 23 nov, es contexto y no una falta (pregunta 63).
- **Desde el 23 nov, la cita es la de la segunda ronda** (P6, 23 nov): «Ha mejorado un montón… ahora sí que te arroja cosas interesantes.», en la columna «Utilidad». Las de abajo, del 14 nov, quedan en la pregunta 43.
- **Citas de la prueba con usuarios (14 nov), aprobadas por Mariano, hasta el 22 nov:** «Se valora mucho la cercanía al puesto de trabajo.» y «Muy chula la web, funciona bien.».
  - Van firmadas «Prueba con usuarios, 14 nov» y sin nombre, como se prometió a los usuarios.
  - Las dos son de usuarios, así que van juntas en la tarjeta de utilidad, en el sitio de la viñeta «¿Salen pocas?…», que ya enseña la captura C3.
  - No hubo cita de un técnico municipal: la tarjeta de impacto se queda sin cita.
  - Si llegan citas mejores, se cambian.
- **Relato de la prueba con usuarios** (va en la slide 4 y en el cierre del guion; la versión larga, en la pregunta 43):
  - **Quién:** 7 personas que buscan casa, del 13 al 15 nov. Seis de 26 a 55 años (P1 a P6) y una persona mayor. Sin nombres, como se les prometió. Con el inversor que probó la ficha de la parcela el 19 nov (P7, pregunta 61) son **8 personas**, la cifra de la slide 4 y del guion desde el 23 nov. El 23 nov P6 repitió la prueba (segunda ronda): es la misma persona, así que el recuento no cambia.
  - **Qué pidieron y qué hicimos** (todo en producción desde el 14 nov):
    - buscar solo en una parte de la región, que lo pidieron 4 de las 6 → «¿Dónde?», con Madrid capital por sus 131 barrios (D-238);
    - «me salían sitios muy lejos» → «Tardar como mucho N min» hasta el trabajo, y una ayuda que dice qué transporte cuenta (PR #53);
    - quien va en autobús quería ver sus paradas → «Parada de autobús a unos 2 min andando · Metro o Cercanías a unos 8 min» (D-233);
    - con mucho presupuesto salían siempre pueblos en orden alfabético → desempate por los servicios del día a día más cerca, con el aviso cuando muchas encajan igual de bien (D-239, D-243);
    - el % no cuadraba con «Qué falta» y empataban muchas zonas → la fórmula «cerca y plazas», elegida con el banco de pruebas (D-243, `pitch/banco_formula.md`);
    - no se distinguían los hospitales públicos de los privados → cada hospital lo dice (D-239).
  - **Qué no entra antes del freeze:** los proyectos futuros y filtrar pisos por metros u obra nueva (preguntas 49 y 50).
  - **La persona mayor** la probó el 15 nov en el móvil y le costó: la letra y los botones, pequeños; palabras técnicas; y demasiado a la vez. **Lo que se cambió por eso está en producción desde el 15 nov** (D-244 y D-245, despliegues de `e0417ae`, `c0e9d11` y `55651c2`; comprobado por D el 18 nov):
    - letra de 16 px o más y botones de 44 px o más en todo el móvil: medido a 390 y a 360 px en todas las pantallas, 0 textos y 0 botones por debajo (`evidence/gate-06/2026-11-15-ux-1/ux-movil-1.md` y `2026-11-16-ux-2/ux-movil-2.md`);
    - lenguaje llano;
    - una portada que dice para qué sirve;
    - «Somos mayores», con «¿Cerca de dónde queréis vivir?»;
    - una lista con 4 cosas por fila en el móvil, en vez de 7 a 9;
    - una tarjeta con lo esencial y lo demás en «Ver más»;
    - «No sabemos si…» cuando falta el dato.
  - **En la slide 4**, el recuadro dice «un móvil más sencillo». **La persona mayor no ha vuelto a probarla todavía** (la segunda ronda, de momento, es solo la de P6): se dice lo que se ha cambiado y medido, nunca que a ella ya le resulta fácil.
  - Fuentes: D-233, D-238 («cuatro personas pidieron buscar solo en una parte de la región»), D-239, D-244, D-245, `trabajo.max_min` y `trabajo.ayuda` en `pitch/textos_web.md`, y las notas de Mariano, que no se versionan.

- Para cada zona, la lista **FALTA / JUSTO / CUBIERTO / SIN DATOS**. Tiene 6 filas, por municipio y por los 21 distritos (D-194; GAP-001 F1–F3b). Desde el 12 nov (D-217, `gap-0.3`) las cinco de servicios miden **lo que la gente tiene a 15 minutos andando, repartido entre todos los que lo comparten** (2SFCA; en llano, `pitch/metodologia.md` §1.4):
  - escuela infantil: escuelas infantiles al alcance a pie por cada 1.000 niños de 0 a 4 años (cada escuela cuenta como una: nadie publica sus plazas);
  - colegio: aulas de primaria, públicas y concertadas, al alcance a pie por cada 1.000 niños de 5 a 14 años;
  - centro de salud: centros de salud del SERMAS al alcance a pie por cada 10.000 habitantes (los consultorios cuentan para los minutos, no como capacidad);
  - mayores: plazas en hogares, clubes y centros de día al alcance a pie por cada 100 personas de 65 o más;
  - farmacia: farmacias al alcance a pie por cada 10.000 habitantes;
  - vivienda (no va a pie): viviendas de más de 90 m² por cada 100 hogares de 4 o más personas; por distrito, SIN DATOS, porque la CM no lo publica a ese nivel. **Desde el despliegue del 23 nov es contexto, no una falta** (D-254, `gap-0.4`): en los pueblos las segundas residencias inflaban la referencia rural (pregunta 63).

  Fuente: `gap_row` de los YAML en `data/catalog/features/` (D-217 §3) y `evidence/gate-04/2026-11-12/gap-status-gap03.md`. Cada fila lleva su fuente, su fiabilidad y los minutos a pie.
- **Con qué se compara (D-213, refinada por D-217):** con los demás municipios de su tipo, urbanos o rurales (Ley 45/2007), sin contarse a sí misma. FALTA exige menos del 80 % de esa referencia y que la diferencia no se explique por el tamaño de la zona (prueba exacta de Poisson). Un pueblo demasiado pequeño se compara junto con sus vecinos parecidos; si ni así se puede, nunca sale FALTA. Detalle y fuentes en `pitch/metodologia.md` §1.4.
- **Ejemplo de la slide: Puente de Vallecas (distrito 2807913), escuelas infantiles.** Comprobado en producción el 12 nov: `GET /api/v1/gaps/distrito/2807913` (`method.version: gap-0.3`, `data_version: 2026-11-12`), fila `escuela_infantil`:
  - **FALTA:** valor 2,781 (`escuelas_infantiles_a_pie_por_1000_ninos`); referencia 4,87, «Otros municipios urbanos de la Comunidad de Madrid»; ratio 0,571; `reliable: true`; `comparison_group: null` (los distritos no se agrupan). En toda la Comunidad, 4,721.
  - **Texto de la API (`explanation`):** «2,8 escuelas infantiles al alcance a pie por cada 1.000 niños de 0 a 4 años; en los demás municipios urbanos de la Comunidad de Madrid, 4,9 (en toda la Comunidad, 4,7)».
  - **Por qué se entiende en una frase:** la escuela infantil más cercana está cerca (la mitad de la zona la tiene a 6 min o menos: `min_a_pie_escuela_infantil` = 6,258), pero son pocas para tantos niños. Contar centros por habitante da casi lo mismo (2,708, `escuelas_infantiles_por_1000_ninos`): no es un efecto del método.
  - **Las demás filas de la zona:** colegio, centro de salud, mayores y farmacia, CUBIERTO (farmacia: 4,5 frente a 3,1); vivienda, SIN DATOS (desde el 23 nov, contexto).
  - **Otros distritos con FALTA en esa fila:** Villaverde (2,984; ratio 0,613) y Carabanchel (3,322; 0,682) (`GET /api/v1/gaps?level=distrito&row=escuela_infantil`, 12 nov). Centro (0,661) y Vicálvaro (0,647) tienen un ratio parecido y salen JUSTO: con menos niños, la diferencia podría ser casualidad. Sirve para la pregunta de estadística (UCM).
  - **Si preguntan por un municipio:** Parla, farmacias, FALTA: 2,029 frente a 4,175 (ratio 0,486). La estadística oficial de farmacias por habitante también da 2,04 (`GET /api/v1/gaps/municipio/28106`, 12 nov).
  - **Ya no vale «Madrid tiene un tercio menos de centros de atención primaria»** (D-217 §7): con gap-0.3, Madrid capital sale JUSTO en centros de salud (0,3603 frente a 0,3799; ratio 0,9484, `evidence/gate-04/2026-11-12/gap-status-gap03.md`).
  - Captura **C4**: desde el 12 nov no va en la slide 3. Queda de reserva (`deck_c4_puente_de_vallecas_escuelas_infantiles_1440.png`, de B, con las mismas cifras que producción).
- **Escala:**
  - 179 municipios (`evidence/gate-01/2026-10-20/cm_secciones_censales/row_counts.json`) + 21 distritos de Madrid capital (D-200, D-209; DATA-012 hecha);
  - 3.866 centros educativos, 553 centros sanitarios (276 centros de salud, 151 consultorios, 85 hospitales y 41 centros de salud mental; sin las clínicas privadas, D-216; con los 4 centros de salud corregidos por D-218 §10), 1.014 servicios para mayores y 2.957 farmacias (`evidence/gate-01/2026-11-12/cm_*/row_counts.json`, campo `places`);
  - 14.982 paradas y estaciones con su frecuencia: suma de `places` en `evidence/gate-01/2026-11-10/crtm_gtfs_*/row_counts.json`.

### Viabilidad: se sostiene
- **Quién paga desde el 23 nov** (decisión de Mariano; `pitch/modelo_negocio.md`): en la slide, «Gratis siempre: datos, zonas, «Qué falta», cada ficha de parcela y la API.» y «Pagarán las empresas: plan empresarial e informes a medida.». El plan empresarial: carteras de parcelas, avisos de suelo nuevo, volumen con clave y MCP remoto; los informes: estudios de suelo a medida. Nada de lo de pago existe todavía. Los precios no van en la slide (pregunta 6).
- **Quién pagaba del 19 al 22 nov** (sustituido): en la slide, «Gratis para personas y ayuntamientos. Pagarán inversores y promotores.».
  - **Los ayuntamientos**, gratis: ven qué le falta a su municipio frente a municipios parecidos y a cuánta gente afecta («Qué falta», en producción en los 179 municipios y los 21 distritos de Madrid). La columna «Impacto · ayuntamientos» de la misma slide lo enseña.
  - **Los inversores y promotores privados** pagarán con un plan de precios. «Pagarán» porque hoy no se cobra: su versión está en la web desde el 19 nov (D-247 y D-248; desde la tarde, con «Busca tu parcela», D-250), de acceso libre durante el concurso, sin cuentas ni cobro («Plan Inversor (acceso libre durante el concurso)», D-248 §1). Evidencia: `evidence/gate-06/2026-11-19-deploy/deploy-37-396d8f6-inversores.md` (PR #96) y `deploy-39-79020a1-parcela.md` (PR #102).
  - **Los precios no van en la slide** porque son hipótesis por validar: plan Inversor de unos 99–199 €/mes, Equipo de unos 399 €/mes y estudio a medida de 490–1.500 €. Si preguntan, pregunta 6 de `pitch/preguntas.md`.
- **Privacidad:**
  - solo agregados por zona y nunca datos personales;
  - se excluyen equipamientos que expondrían a personas vulnerables (D-186);
  - la base de la demo está cerrada a accesos directos (D-197);
  - los fixtures no llevan datos de contacto (D-198).
- **Coste:** la base de la demo cabe en el plan gratuito de Supabase: 100 MB de 500 (`evidence/gate-06/2026-11-11/supabase-sync-demo.txt`, D-188). La web y la API van en el plan gratuito Hobby de Vercel: 0 €/mes y sin dominio propio (`infra/deploy/README.md` y `evidence/gate-06/2026-11-11-deploy/deploy-1-production.md`). Límite: Hobby solo admite uso no comercial; para cobrar a empresas habría que pasar a un plan de pago.
- **En la slide, el coste:** «Coste de infraestructura: 0 € hoy; unos 45 $/mes para poder cobrar» (desde el 23 nov; antes, «0 € hoy; unos 45 $/mes para uso comercial») (Vercel Pro 20 $ y Supabase Pro desde 25 $, precios del 12 nov en `pitch/modelo_negocio.md`). El plan gratuito de Vercel no admite uso comercial.
- **Reproducible y abierto:**
  - en la slide, desde el 23 nov por la tarde: «API y MCP abiertos y gratuitos, sin clave.», con el MCP en remoto (D-255). Por la mañana: «API abierta y gratuita; MCP de código abierto.», porque el MCP solo funcionaba en local (jueces B1 y A5 del jurado simulado). Del 19 al 22 nov: «Código abierto, y API y MCP gratis.» (decisión de Mariano, transmitida por datamad-10; antes, «Código abierto: cualquiera puede repetir los cálculos.»). Dice lo mismo que la frase del bloque 4 del guion, «La API y el MCP para agentes de IA son gratis para todos.». La API y el MCP, en `/desarrolladores` (D-249) y en las preguntas 1 y 2. **Medido a 1920 × 1080** (D, 19 nov, `build.py` en borrador sin fallos): cabe en una línea, sin desborde, y las tres tarjetas acaban a 834 px, por encima de la banda de enlaces (858); con la viñeta anterior, a 842;
  - Apache-2.0 (`LICENSE`, D-191);
  - `make` como entrada única;
  - añadir un dataset es añadir un YAML de pipeline (`data/catalog/pipelines/`);
  - cada dato con su lineage y su control de calidad (`evidence/gate-01/`).

- **La línea del pie de «Viabilidad», desde el 23 nov:** «**Ninguna cifra la genera una IA:** salen de cálculos deterministas sobre datos oficiales, cada una con su fuente.» (formación del 5 nov: «yo necesito el número»; `CLAUDE.md` §3, IA). La de inversores pasa a la columna «Utilidad», sin «Ya está». Lo que sigue es su historia.
- **La línea de inversores, del 18 al 22 nov al pie de «Viabilidad»** (la idea de pasar de dónde vivir a dónde construir, aprobada por Mariano el 18 nov; desde el 19 nov dice lo que ya está, y no el cruce con la vivienda que falta, que todavía no existe: revisión del #98). En la slide, al pie de la tarjeta, con el borde violeta de las citas: «**Ya está**, para inversores: busca tu parcela en Madrid capital y calcula si sale, con la demanda de su zona.» (aprobada por Mariano el 19 nov por la tarde). Ocupa el sitio de la miniatura C7, que no cabía con él (ver «Capturas necesarias»). **En la slide no se nombra ninguna empresa.**
  - **Con la búsqueda por parcela en producción (19 nov, D-250):** «Madrid capital» porque la búsqueda llega a toda la ciudad; el contexto completo del barrio es el del piloto (los 108 barrios dentro de la M-40), y fuera la ficha da las cifras del distrito o de la ciudad (pregunta 6). «Calcula si sale», y no «mira», porque el semáforo necesita el precio del suelo (revisión del #103). Dice lo mismo que el bloque 4 del guion: «buscar una parcela de Madrid capital y calcular si una promoción sale, con la demanda de la zona».
  - **Medida a 1920 × 1080** (D, 19 nov, `build.py` en borrador sin fallos): 3 líneas, sin desborde, y las tres tarjetas acaban a 834 px, con la banda a 858. Era una propuesta de D; con «mira si una promoción sale» pasaba a 4 líneas y quedaba muy justa (841 px).
  - **Antes, el 19 nov por la mañana:** «**Ya está**, para inversores (piloto en Madrid): viabilidad sobre una parcela, con el contexto de su barrio.», genérica a propósito hasta que la búsqueda por parcela estuviera en producción.
  - **Tiene que caber en 3 líneas a 1920 × 1080**, como la del 18 nov: con la viñeta anterior del código abierto (2 líneas), cuatro alargaban las tarjetas hasta meterlas bajo la banda de enlaces (medido el 19 nov). Por eso no lleva «y promotores» ni «libre durante el concurso»: lo dice la línea de «Quién paga» («Pagarán») y, si preguntan, la pregunta 6.
  - **Antes, el 18 nov:** «Ya enseñamos el suelo público para vivienda. **Siguiente paso:** dónde construir, según la vivienda que falta.». El suelo público sigue en la web (D-246) y está dentro de la versión para inversores.
  - **Lo que todavía no hace:** cruzar cada parcela con la vivienda que le falta a cada zona y para quién (Housing Gap: `docs/03_intelligence/16_housing_gap_product_recommender.md` y `51_housing_gap_math_spec.md`; capa PRO: `docs/01_product/05_pro_layer.md`). En los 21 distritos de Madrid, la fila «vivienda» de «Qué falta» salía SIN DATOS (`GET /api/v1/gaps?level=distrito&row=vivienda`, 19 nov), y desde el 23 nov es contexto (pregunta 63). El análisis por parcela quedó fuera del concurso con D-192 y entró el 19 nov con D-250, sin el Housing Gap. Es un plan: se dice en futuro.
  - **Hoy, en producción desde el 18 nov** (D-246, despliegue de `747cb65` y sync: `evidence/gate-06/2026-11-18-deploy/deploy-36-747cb65-suelo.md`, PR #90): el suelo público para vivienda del Portal del Suelo 4.0 de la Comunidad ([ficha del portal](https://datos.comunidad.madrid/dataset/parcelas_portal_suelo)), en «Vivienda nueva y lo que viene» de cada municipio o distrito. En producción el 18 nov (API, leída por D): 291 parcelas en 29 municipios y 394.298 m² edificables. Está en `pitch/datasets_cm.md`. Desde el 19 nov ya no tiene frase propia en el bloque 4 del guion ni en la slide 3: queda dentro de la versión para inversores. Sin captura de la capa.
  - **La validación de mercado, solo en las respuestas** (pregunta 60): Nestra (España) y Sitescope (Polonia) ya venden el «¿se puede construir?» a promotores. En sus webs, ninguna lo cruza con la demanda de los hogares. Ese es el hueco de Vida Fácil.

### Banda de enlaces (con QR)
- Demo: https://vidafacil-madrid.vercel.app (verificada el 11 nov con el buscador encendido: smoke 7/7, `evidence/gate-06/2026-11-11-deploy/deploy-12-buscador.md`, PR #11).
- Código: https://github.com/marianohernando/housing-intelligence

---

## Slide 4 · Pantallazo del sistema
**Composición:**
- Captura **C1** (mapa con la búsqueda del caso demo, 1440 px) a sangre en un marco de cristal. **Rehecha por P el 23 nov en producción, con el deploy-46 (`dpl_GyEfen16H6Kxbcng13cABR124UY6`, código `542283b8`):** el lema nuevo, la pestaña «Inversores» y «Datos: 39 conjuntos…» (antes, el lema anterior y «35»).
- Encima, abajo a la derecha, la captura **C6** (móvil, 390 px) en un marco de teléfono sencillo, sin marca de fabricante.
- Tres pasos numerados, con números que apuntan a la captura:
  1. «Cuéntanos tu hogar, tu presupuesto y dónde trabajas»: tarjeta «Tu búsqueda».
  2. «Mira las zonas que te convienen y por qué»: cabecera de la tarjeta de zona (nombre y «Distrito de Madrid · Muy buena opción»).
  3. «Entra en una zona y mira qué le falta, con su fuente»: «No le falta nada de lo que buscáis.» en la tarjeta.
- Bajo los tres pasos, con un borde violeta como las citas de la slide 3, **desde el 23 nov:** «**Probada con 8 personas.** Siete que buscan casa, una de ellas mayor, y un inversor. Se hizo lo que pidieron: barrios, un límite de tiempo al trabajo, letra y botones más grandes en el móvil y los servicios de la parcela.» (revisión del #122, R-09: lo que se hizo, no un resultado validado). Las 8 son las 7 que buscan casa (P1 a P6 y una persona mayor, 13–15 nov) y el inversor (P7, 19 nov). Del 19 al 22 nov decía «Probada con 7 personas», sin el inversor. Se ve durante el cierre del guion (bloque 6), que lo resume en voz alta. Medido el 23 nov a 1920 × 1080: el recuadro acaba a la altura del móvil. Las paradas de autobús, que también pidieron, salen del recuadro para que quepa la persona mayor: siguen en la pregunta 43.
- Pie: «Demo en vivo: vidafacil-madrid.vercel.app».

**Fuentes en la slide:** ninguna cifra nueva salvo las 8 personas (relato de la slide 3). Si la captura muestra cifras, son las de la API en ese momento.

**C1 rehecha el 18 nov** (D, producción con `55651c2`, `pitch/capturas/C1.png`): el caso de ejemplo con la tarjeta esencial de Puente de Vallecas («Muy buena opción», «Unos 1.129 € al mes», sus minutos a pie y «No le falta nada de lo que buscáis.»), el contorno de la zona en el mapa y «¿Dónde?» en «Tu búsqueda» (D-238). Marcadores (`.s4 .m1`–`.m3`): 1 en «Tu búsqueda» (`top: 340px`), 2 en la cabecera de la tarjeta (`top: 136px`) y 3 en «No le falta nada de lo que buscáis.» (`top: 428px`). **C6 rehecha el 18 nov** a 390 × 844 (`pitch/capturas/C6.png`): la lista del móvil, «Zonas que os convienen», con «Hemos encontrado 42 zonas para vosotros.» y 5 filas con la zona, su banda y su precio al mes. **Desde el 23 nov, C1 y C6 son las del deploy-46** (P, `542283b8`; ver «Capturas necesarias»), con el lema nuevo y la pestaña «Inversores»; los marcadores 2 y 3 se movieron con la tarjeta.

---

## Dirección visual (brief de diseño, no el PDF)
Fuente única: `DISENO_VIDA_FACIL.md`. Los valores de la tabla son los que B ya validó en AA en la web (`apps/web/src/styles/tokens.css` en `claude/s1-web`, commit `4402edd`, PR #2). Si cambian antes del 24 nov, mandan los de la web.

| Elemento | Valor |
|---|---|
| Formato | 16:9, 1920 × 1080, márgenes de 96 px y rejilla de 12 columnas |
| Fondo | `--bg #F6F5FC`, lavanda muy claro |
| Texto | `--ink #141B3D` (navy) y `--ink-soft #5A6080` para lo secundario |
| Acento | `--violet #6A5AE0` para cifras clave y formas; `--violet-strong #4B3BBF` para texto y enlaces violetas (AA); `--violet-soft #ECE9FD` para chips |
| Tarjetas | Cristal: blanco al 82 % + desenfoque de 18 px + borde `rgba(255,255,255,.6)` + sombra `0 8px 32px rgba(20,27,61,.08)` y radio de 22 px |
| Estados de «qué falta» | FALTA `#A61E33` (texto) / `#C93A52` (icono) · JUSTO `#7E4C00` / `#A86A00` · CUBIERTO `#17634A` / `#23805F` · SIN DATOS `#4F546A` / `#6E7389`, con borde discontinuo. **Siempre con texto e icono**, nunca solo color |
| Tipografía | Plus Jakarta Sans 600/700 en títulos (56–64 pt) e Inter 400/500 en el texto (≥ 24 pt, para que se lea en proyector) |
| Iconos | De línea, del mismo grosor que en la web |
| Idioma | Español llano, sin anglicismos («Qué falta», «Cómo lo calculamos»; nunca «Análisis» ni «Metodología») |

**Lo que no puede salir en ninguna slide:**
- Nada de los mockups que no sea estilo. Llevan «Madrid 360», chips de discapacidad, un icono de usuario, foto de zona y «92/100» con barras; todo eso está descartado (D-199, D-202 y D-205; `CLAUDE.md` §13).
- Notas sobre 100 o barras de puntuación: el encaje es un % con hechos debajo.
- Fotos de zonas.
- Etiquetas como «peligroso» ni datos de nacionalidad.
- Capturas de mockups: solo de la demo real.

**Contraste:** se comprueba AA en cada slide exportada, también el texto sobre cristal. Si no llega, se sube la opacidad del cristal.

---

## Capturas necesarias
**Capturas rehechas el 23 nov, tras el despliegue del día:** C5 (slide 1), C1 (slide 4) y C3 (slide 3), por P en producción, con el deploy-46 (`dpl_GyEfen16H6Kxbcng13cABR124UY6`, código `542283b8`), a 1440 × 900 y densidad 1, como las anteriores. Se hicieron con Playwright y el Chrome instalado (WebGL por software), después de calentar la portada, la búsqueda de ejemplo y Chamartín. Las cifras que citan las slides no han cambiado: 42 zonas (157 no cumplen y 0 sin datos), «Unos 1.129 € al mes», colegio a unos 4 min, 41 min hasta la Castellana, «saldrían 49 más: 91 zonas en total» y «saldrían 3 más: 45 zonas en total». Un texto sí cambia: bajo el precio, la tarjeta ya no dice «Precio orientativo», sino «Precio de los contratos de alquiler de 2024: un anuncio de hoy suele pedir más.». Por esa nota, «No le falta nada de lo que buscáis.» baja a y 646, y el marcador 3 de la slide 4 baja con ella (`deck.css`). En las imágenes no hay datos de personas: el único sitio es el lugar de trabajo del ejemplo, el Paseo de la Castellana (Azca).

Se hacen el 24 nov sobre la demo desplegada, con el caso demo precargado, a 1440 × 900 (escritorio) y 390 × 844 (móvil) y con densidad 2×. Se guardan en `pitch/capturas/` con estos nombres. B puede adelantarlas en `evidence/map-004/<fecha>/`.

`pitch/deck/build.py` usa la captura de `pitch/capturas/` si hay una con el mismo id y, si no, la de la evidencia:
- **C1, C2, C3, C5 y C6** están en `pitch/capturas/`. C2 la rehízo D en producción el 18 nov (`55651c2`); C1, C3, C5 y C6, P el 23 nov, con el deploy-46 (`542283b8`).
- **C4 y C7** son de B (`evidence/map-004/2026-11-11/prod_*` y, la C4, `evidence/map-004/2026-11-12/deck/`). La C5 de B del 11 nov queda en la evidencia como respaldo de `build.py`. C4 y C7 no van en ninguna slide: quedan de reserva.

**Recaptura tras gap-0.3 (12 nov).** Las del 11 nov son anteriores a gap-0.3 y D-216. B ya rehízo C3 y C4 (PR #17, `evidence/map-004/2026-11-12/deck/`, en local a 1440 px con datos reales y las mismas cifras que producción), y el deck las toma de ahí (el #17 se fusionó el 12 nov). Con ellas y `DECK_INTEGRANTES`, `build.py --final` genera sin fallos (12 nov). Las demás valen como borrador, pero se rehacen antes del 24 nov:

| Id | Qué cambia | Dónde |
|---|---|---|
| C3 | Rehecha por D el 18 nov en producción (`55651c2`, `pitch/capturas/C3.png`): «¿Queréis ver más zonas?», «Hemos encontrado 42 zonas para vosotros», «+5 min a pie hasta colegio con primaria · saldrían 49 más: 91 zonas en total» y «+150 €/mes · saldrían 3 más: 45 zonas en total» | Portada → «Ejemplo: pareja con 2 hijos…» → «Ver todas las opciones» |
| C4 | Hecha por B: `deck_c4_puente_de_vallecas_escuelas_infantiles_1440.png`, la fila de escuelas infantiles de **Puente de Vallecas** en FALTA (2,8 frente a 4,9) con «A pie: 6 min». El hueco enseña las dos cifras | `/que-falta?zona=distrito/2807913` |
| C5 | Rehecha por P el 23 nov con el deploy-46 (`pitch/capturas/C5.png`): «Lo que le falta a esta zona» con escuelas infantiles y centros de mayores JUSTO y colegios CUBIERTO, y la pestaña «Inversores» | `/zona/distrito/2807905` (Chamartín en 3D) |
| C1, C2 | Rehechas por D el 18 nov en producción (`55651c2`, `pitch/capturas/`): C1, el mapa con la tarjeta esencial de Puente de Vallecas («Muy buena opción», «Unos 1.129 € al mes» y «No le falta nada de lo que buscáis.»); C2, «Zonas que os convienen» con Puente de Vallecas y Latina, «Muy buena opción · 94 %» | Portada → «Ejemplo: pareja con 2 hijos…», la lista y la tarjeta de la 1.ª |
| C6 | Rehecha por P el 23 nov en producción, con el deploy-46 (`542283b8`), a 390 × 844 (`pitch/capturas/C6.png`): la cabecera con la pestaña «Inversores» y la lista del móvil con 5 filas esenciales | Portada → «Ejemplo: pareja con 2 hijos…», en el móvil |
| C7 | Desde el 18 nov no va en la slide 3: su sitio lo ocupa la línea del pie de «Viabilidad» (desde el 19 nov, la versión para inversores). Queda de reserva | `/como-lo-calculamos` |

| Id | Pantalla y estado | Tamaño | Slide | Estado |
|---|---|---|---|---|
| C1 | «Mapa» con «Tu búsqueda» rellena con el caso demo, coropleta de encaje y tarjeta de zona abierta | 1440 | 4 | **Rehecha por P en producción el 23 nov** (deploy-46, `542283b8`; `pitch/capturas/C1.png`): el lema nuevo, la pestaña «Inversores», la tarjeta esencial de Puente de Vallecas («Muy buena opción», «Unos 1.129 € al mes», la nota del precio de 2024, sus minutos a pie, 41 min hasta la Castellana y «No le falta nada de lo que buscáis.»), la leyenda con 42 / 157 / 0 zonas y «Datos: 39 conjuntos…». Marcadores de la slide 4 (`.s4 .m1`–`.m3`): 1 en «Tu búsqueda» (`top: 340px`), 2 en la cabecera de la tarjeta (`left: 703px`, `top: 136px`) y 3 en «No le falta nada de lo que buscáis.» (`left: 703px`, `top: 458px`) |
| C2 | Recorte de «Zonas que os convienen»: las dos primeras filas, Puente de Vallecas y Latina, «Muy buena opción · 94 %» y «Unos … € al mes» | 1440 | 3 | Rehecha por D en producción el 18 nov (`55651c2`, `pitch/capturas/C2.png`). El recorte tiene la proporción del hueco |
| C3 | Bloque «¿Queréis ver más zonas?» con cifras reales de la API | 1440 | 3 | **Rehecha por P en producción el 23 nov** (deploy-46, `542283b8`; `pitch/capturas/C3.png`), abierta con «Ver todas las opciones»: «Hemos encontrado 42 zonas para vosotros», «+5 min a pie hasta colegio con primaria · saldrían 49 más: 91 zonas en total», «+150 €/mes · saldrían 3 más: 45 zonas en total» y «Datos: 39 conjuntos…» en el pie. El recorte (x 1010–1380, y 100–372) enseña el titular y la primera opción |
| C4 | Pestaña «Qué falta» de la zona del ejemplo (**Puente de Vallecas**): 6 filas con valor, referencia, confianza, minutos a pie y datasets enlazados | 1440 | 3 | Hecha por B el 12 nov (`evidence/map-004/2026-11-12/deck/deck_c4_puente_de_vallecas_escuelas_infantiles_1440.png`, PR #17; la página entera, en `deck_c4_puente_de_vallecas_que_falta_1440.png`). El hueco enseña las dos cifras de la fila de escuelas infantiles: 2,8 en Puente de Vallecas y 4,9 en los otros municipios urbanos |
| C5 | Zona en 3D: inclinación de unos 60°, contorno violeta y etiquetas de colegios, centros de salud y estaciones | 1440 | 1 | **Rehecha por P en producción el 23 nov** (deploy-46, `542283b8`; `pitch/capturas/C5.png`): Chamartín en 3D, con su contorno violeta y las etiquetas de estación, centro de salud, metro y colegio; la pestaña «Inversores»; y «Lo que le falta a esta zona». El recorte empieza en x 525 y arriba, con las pestañas. Sustituye a la de B del 11 nov (`evidence/map-004/2026-11-11/prod_c5_chamartin_3d_desktop.png`) |
| C6 | Móvil: la lista «Zonas que os convienen» con sus filas esenciales | 390 | 4 | **Rehecha por P en producción el 23 nov** (deploy-46, `542283b8`; `pitch/capturas/C6.png`, 390 × 844, el mismo tamaño que la anterior): la cabecera con «Mapa», «Qué falta», «Cómo lo calculamos» e «Inversores», «Hemos encontrado 42 zonas para vosotros.» y 5 filas, de Puente de Vallecas a Tetuán, todas «Muy buena opción», con unos 1.129, 1.101, 1.019, 1.083 y 1.488 € al mes (las mismas cifras que la del 18 nov). El puntero se aparta antes de capturar, para que ninguna fila salga resaltada |
| C7 | «Cómo lo calculamos» o panel de procedencia de un dato, con el enlace a la ficha del portal | 1440 | — (reserva) | Hecha por B en producción (`prod_c7_como_lo_calculamos_desktop.png`). **Desde el 18 nov no va en la slide 3:** el siguiente paso no cabía con ella en «Viabilidad», y a 100 px de alto no se leía. Además enseña un texto anterior de «Cómo lo calculamos». Si vuelve, se rehace en producción |
| C8 | Inversores, «Busca tu parcela» en el móvil: la cabecera con la pestaña «Inversores» marcada (D-251), «Plan Inversor (acceso libre durante el concurso)», el título, la frase de lo que hace y la caja de la referencia catastral | 390 | — (reserva) | **Rehecha por D en producción el 20 nov** (con D-253, despliegue de `a669057`): `pitch/capturas/C8.png`, 780 × 1.688 (390 px a 2×). Para las preguntas 6 y 60. La línea del pie de la slide 3 va sin captura: no cabe con ella |
| C9 | Inversores, el arriba de la ficha de Méndez Álvaro 47 en el móvil: la pestaña «Inversores», barrio de Atocha (distrito de Arganzuela), la referencia catastral, el aviso «Esto es un primer filtro de minutos, gratis y con fuentes…», «Guardar como PDF» y «Llévate esta ficha (PDF) a tu consultora…» | 390 | — (reserva) | **Rehecha por D en producción el 20 nov:** `pitch/capturas/C9.png`, 780 × 1.688. Para las preguntas 6 y 61. Una de las 4 parcelas de demostración |
| C10 | Inversores, la ficha entera de Almería 1, reducida a 900 px de ancho: arriba, el primer filtro y los avisos del ámbito sin terminar y del edificio existente; la edificabilidad «Sin dato» con los 32.697 m² como referencia; «Servicios y suministros» (sin urbanizar); la calculadora sin escenarios hasta poner los m²; «Lo que añade un estudio completo»; y las fuentes | 1440 | — (reserva) | **Rehecha por D en producción el 20 nov:** `pitch/capturas/C10.jpg`, 900 × 9.186 (desde 1440 px). Para las preguntas 6 y 61: no damos una cifra donde el planeamiento no está desarrollado. Para una slide, se recorta a una sección |
| C11 | Inversores, «4. Servicios y suministros» de Méndez Álvaro 47 en el móvil: «solar» como condición legal, las obras de urbanización del APR.02.06 finalizadas, la potencia (unas 164 viviendas, al menos 499,1 kW, «Supuesto»), el aviso del centro de transformación y de quién paga la extensión de red, el enlace al mapa de capacidad de la CNMC y el agua de Canal de Isabel II | 390 | — (reserva) | **Hecha por D en producción el 20 nov:** `pitch/capturas/C11.png`, 708 × 4.246 (la sección, a 2×). Para las preguntas 6 y 61 |
| QR | Códigos QR de la demo (https://vidafacil-madrid.vercel.app) y del repo | — | 3 | Se generan el 24 nov, cuando la demo esté verificada |

**C8 a C11, rehechas una sola vez el 20 nov** con D-253 en producción (datamad-10, 19 nov), solo con las parcelas de demostración: enseñan la pestaña «Inversores», el primer filtro y los servicios. Las de C en `evidence/gate-06/2026-11-19-deploy/deploy-39/` son anteriores a D-251 y D-252 y ya no valen. **Si el sábado 21 la web deja una sola vez** «Llévate esta ficha (PDF) a tu consultora…» (hoy sale bajo «Guardar como PDF» y al final de «Lo que añade un estudio completo»), C9 o C10 pueden enseñar la que se quite: se revisa entonces.

## Checklist del 24 nov (maquetar)
La maqueta ya está hecha en `pitch/deck/`: HTML a 16:9 y `build.py`, que genera el PDF y comprueba el contraste y los tamaños. Sus pasos están en `pitch/deck/README.md`; los de aquí siguen valiendo.

1. Rebase de `hi-coord` y `uv run python pitch/build_datasets_cm.py --refresh-portal`. Si cambia el total de datasets CM o algún grupo, actualizar la slide 2.
2. Cerrar todas las marcas «pendiente de A/B/C» de este fichero. Lo que no exista se quita de la slide; no se dibuja.
3. Hacer las capturas C1–C7 sobre la demo desplegada (consola sin errores) y generar los QR.
4. Maquetar con los tokens de arriba, exportar a PDF con hipervínculos activos y guardar también el PPTX.
5. Comprobar contraste AA y leer cada slide a 3 m (proyector). Mariano revisa el 24 (`docs/09_datamad/25_plan_competicion.md` §5).
