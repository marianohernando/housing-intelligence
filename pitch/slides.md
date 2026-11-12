# Slides — Vida Fácil (contenido, dirección visual y capturas)

## Qué es este fichero
Las 4 slides que piden las bases (§8, resumen en `docs/09_datamad/24_bases_oficiales_2026.md`), en su orden.
- **Entrega:** PDF (y PPTX de respaldo) antes de las 14:00 del 26 nov. Se sube como tarde a las 13:30 (`docs/09_datamad/25_plan_competicion.md` §9).
- **24 nov:** solo maquetar con capturas reales de la demo desplegada.
- **Estado:** borrador del 11 nov. Lo marcado «pendiente de A/B/C» se cierra en el freeze del 23 nov.

> Las decisiones del 11 nov están registradas como D-199 a D-207 (`docs/00_index/01_decisions_log.md`). El brief de diseño (`DISENO_VIDA_FACIL.md`, adoptado por D-201) sigue fuera del repo: se cita como documento interno, no como evidencia pública.

## El mensaje (del documento de la idea del 31 oct; solo el mensaje)
- **Tesis:** «Otros te enseñan lo que hay. Nosotros te enseñamos lo que falta.»
- **Tres usuarios:**
  - personas (gratis): «¿Dónde vivo mejor con lo que necesito?»;
  - ayuntamientos (planifican): «¿Qué le falta a cada zona y dónde invierto primero?»;
  - empresas (pagan): «¿Qué hace falta aquí?».
- **Modelo:** las empresas pagan por saber qué falta, y eso financia que sea gratis para las personas. Nunca se venden datos de personas: solo se ven zonas, siempre sumadas y anónimas.

**Del PDF no se usa:**
- ninguna de sus cifras de ejemplo: zonas del Reality Check, 4.000–4.500 €/mes ni «10 conjuntos de datos»;
- el barrio de ejemplo con coworking, gimnasio y «lo que la gente dice que necesita». La necesidad declarada es un siguiente paso y nunca se simula (D-194);
- su estilo visual;
- el nombre «Housing Intelligence»: en todo lo que se ve, un solo nombre, «Vida Fácil» (jurado simulado del 12 nov). «Housing Intelligence» queda solo como nombre del repositorio.

---

## Slide 1 · Título, integrantes y descripción breve
**Texto:**
- **Vida Fácil** (logotipo de texto, Plus Jakarta Sans 700).
- *Encuentra tu sitio en Madrid* (lema, en violeta).
- Descripción, una frase: «El mapa de lo que falta en cada zona de la Comunidad de Madrid: para elegir dónde vivir y para decidir dónde invertir.»
- Integrantes: equipo de una persona. En el PDF va el nombre completo, que el build toma de `DECK_INTEGRANTES` (`pitch/deck/README.md`). Decisión de Mariano (11 nov): en el repo público solo «Mariano»; el nombre completo va solo en el PDF del deck y en el formulario.
- Pie: «Código abierto (Apache-2.0) · Datos abiertos de la Comunidad de Madrid». El «DATAMAD 2026» ya va arriba, en la línea pequeña sobre el nombre.

**Composición:**
- Mitad izquierda: título, lema y descripción sobre `--bg`.
- Mitad derecha: captura **C5** (zona en 3D) dentro de una tarjeta de cristal grande, con el contorno violeta de la zona visible. Es la captura de producción de B con `gap-0.2` (`evidence/map-004/2026-11-11/prod_c5_chamartin_3d_desktop.png`, Chamartín), recortada para enseñar el mapa 3D y la tarjeta «Qué falta aquí». El recorte deja fuera el título de la barra de barrios, que en esa captura aún dice «Barrios de la zona»: es de antes del despliegue del PR #9.
- Sin más elementos.

**Fuentes en la slide:** ninguna cifra.

---

## Slide 2 · Problema y datasets usados (con enlaces)
### Columna izquierda: el problema
Título: **«Nadie te dice qué le falta a cada zona»**.

| Quién | Qué le pasa hoy |
|---|---|
| Personas | El precio en un sitio, los colegios en otro y el transporte en otro: nadie les dice qué zona va con su vida. |
| Ayuntamientos | Los datos llegan sueltos: cuesta ver dónde falta una escuela infantil o un centro de salud frente al resto de la región. |
| Empresas | Abren por intuición, sin saber qué hace falta en la zona. |

Cierre de la columna: «Otros te enseñan lo que hay. Nosotros, lo que falta.»

### Columna derecha: los datos
Titular: **«26 conjuntos de datos del Portal de Datos Abiertos de la Comunidad de Madrid, todos con control de calidad superado»**. Fuente: `pitch/datasets_cm.md`, regenerado el 12 nov, con 26 en Gate 1 PASS. Los cinco nuevos son del 12 nov: los dos de camas (`evidence/gate-01/2026-11-12/cm_dotacion_camas/` y `cm_hospitales_datos_asistenciales/`) y las tres topologías del CRTM con la accesibilidad de las estaciones (`crtm_topologia_metro/`, `crtm_topologia_metro_ligero/` y `crtm_topologia_cercanias/`, D-223). La web en producción dice lo mismo: `GET /api/v1/datasets?cm_only=true` da `cm_open_data_count: 26` (12 nov). Se revisa el 23 nov regenerando `datasets_cm.md`.
- **Matiz, si preguntan:** 24 alimentan la lista de lo que falta o el buscador. Las 3 topologías se usan con «sin escaleras», en producción desde el 12 nov. Los dos de camas (Dotación de camas y Hospitales y datos asistenciales) dan el total de la región y demuestran que el portal no publica camas por hospital: por eso las camas de cada hospital salen del Catálogo Nacional de Hospitales (D-217 §4, D-218). Su uso en pantalla está **pendiente de A** (`pitch/datasets_cm.md`).

Cada nombre lleva el hipervínculo a su ficha en el PDF:

| Tema | Datasets (nombre corto → ficha del portal) |
|---|---|
| Geografía (1) | [Secciones censales](https://datos.comunidad.madrid/dataset/secciones_censales) |
| Población y hogares (3) | [Población por edad](https://datos.comunidad.madrid/dataset/poblacion_censada_por_edad_nacionalidad_y_sexo) · [Hogares por tamaño (Censo 2021)](https://datos.comunidad.madrid/dataset/censo_2021_hogares_por_tamanyo) · [Nacidos vivos](https://datos.comunidad.madrid/dataset/mnp_nacidos_vivos_por_residencia_y_sexo) |
| Vivienda (4) | [Viviendas por superficie](https://datos.comunidad.madrid/dataset/censo_anual_vivienda_por_superficie_agregada) · [Viviendas por régimen de tenencia (Censo 2021)](https://datos.comunidad.madrid/dataset/censo_2021_viviendas_familiares_por_tenencia) · [Alquiler €/m² por municipio](https://datos.comunidad.madrid/dataset/alquiler_metro_cuadrado_mensual_viviendas_arrendadas_valor_catastral_municipios_mas_20000) · [Alquiler €/m² por código postal (Madrid)](https://datos.comunidad.madrid/dataset/1934259) |
| Renta (1) | [Renta disponible bruta municipal](https://datos.comunidad.madrid/dataset/irpf_indicador_renta) |
| Servicios (8) | [Centros educativos](https://datos.comunidad.madrid/dataset/centros_educativos) · [Unidades escolares](https://datos.comunidad.madrid/dataset/unidades_centros_no_universitarios_general_por_tipo_y_ensenanza) · [Centros sanitarios](https://datos.comunidad.madrid/dataset/centros_servicios_establecimientos_sanitarios) · [Camas por dependencia](https://datos.comunidad.madrid/dataset/1912720) · [Hospitales y datos asistenciales](https://datos.comunidad.madrid/dataset/1912744) · [Centros de atención social](https://datos.comunidad.madrid/dataset/atencion_social_registro_centros) · [Oficinas de farmacia](https://datos.comunidad.madrid/dataset/oficinas_farmacia) · [Farmacias por municipio](https://datos.comunidad.madrid/dataset/farmacias) |
| Transporte (9, del CRTM con ficha en el portal) | [Metro](https://datos.comunidad.madrid/dataset/red_de_metro_oferta_planificada_horarios_topologia) · [Metro Ligero](https://datos.comunidad.madrid/dataset/red_de_metro_ligero_oferta_planificada_horarios_topologia) · [Cercanías](https://datos.comunidad.madrid/dataset/red_de_cercanias_oferta_planificada_horarios_topologia) · [EMT](https://datos.comunidad.madrid/dataset/red_de_autobuses_urbanos_emt_horarios_topologia) · [Autobuses urbanos](https://datos.comunidad.madrid/dataset/red_de_autobuses_urbanos_resto_municipios_horarios_topologia) · [Interurbanos](https://datos.comunidad.madrid/dataset/red_de_autobuses_interurbanos_horarios_topologia) · [Accesibilidad del metro](https://datos.comunidad.madrid/dataset/red_de_metro_lineas_estaciones_accesos_vestibulos_andenes) · [Accesibilidad del Metro Ligero](https://datos.comunidad.madrid/dataset/red_de_metro_ligero_tranvia_lineas_estaciones_accesos_vestibulos_andenes) · [Accesibilidad de Cercanías](https://datos.comunidad.madrid/dataset/red_de_cercanias_lineas_estaciones_accesos_vestibulos_andenes) |

- **Grupos:** salen del campo `domain` del catálogo. Los enlaces salen de `portal_url` (`services/ingestion/src/hi_ingestion/catalog/provenance.py`), igual que en `datasets_cm.md`.
- **Línea pequeña bajo la tabla:**
  - «Complementan, sin contar como datos CM: red peatonal de OpenStreetMap (ODbL)» (`pitch/datasets_cm.md` §3). Si el 24 nov la web ya enseña las zonas verdes, va «red peatonal y parques de OpenStreetMap» (D-222);
  - «+ Ayuntamiento de Madrid (población y hogares por distrito)»: en uso desde DATA-012 (D-209; `pitch/datasets_cm.md` §3);
  - «+ Ministerio de Sanidad (nombre y camas de cada hospital, nombre de cada centro de salud)»: Catálogo Nacional de Hospitales 2025 y Catálogo de Centros de Atención Primaria del SNS 2026, reutilizables con cita y fecha (D-218; `pitch/datasets_cm.md` §3).
- **Pie:** «Lista completa, con licencias y control de calidad: github.com/marianohernando/housing-intelligence → `pitch/datasets_cm.md`».

**Composición:** dos tarjetas de cristal, la del problema al 40 % del ancho y la de los datos al 60 %. Cada tema de la tabla lleva su icono de línea. La cifra («26») va grande en violeta; el build la calcula del catálogo.

---

## Slide 3 · Resultados: utilidad, impacto y viabilidad
Tres tarjetas de cristal en fila y, debajo, una banda con los enlaces.

### Utilidad: personas que buscan dónde vivir
**Va con buscador:** producción lo tiene encendido desde el 11 nov y verificado (`NEXT_PUBLIC_FEATURE_SEARCH=true`; `evidence/gate-06/2026-11-11-deploy/deploy-12-buscador.md`, PR #11: smoke 7/7, axe AA sin fallos, consola limpia). La **versión sin buscador** queda de reserva, sin «próximamente», por si el 24 nov la demo vuelve a enseñar «Muy pronto»:
- Título: «Mira qué tienes cerca de casa».
- «Minutos a pie, por la calle, hasta el colegio, el centro de salud o la farmacia más cercanos.» (CORE-005, D-211; en la web: `evidence/map-004/2026-11-11/c4_que_falta_completa_desktop.png`).
- «Cada dato con su fuente y su fiabilidad.»
- Captura: la tarjeta de zona con «A pie: N min» (recorte de C5) en lugar de C2 y C3.

Versión con buscador (la que vale):
- Cuentan su hogar, su alquiler máximo y dónde trabajan. Reciben zonas con su **% de encaje** y, debajo, hechos que se entienden, cada uno con su nivel de confianza en palabras. Lo que marcan primero pesa más, y lo que no tiene datos nunca cuenta como 0 (D-215; `pitch/metodologia.md` §1.3).
- **Caso demo real** (`data/fixtures/contracts/scenario_state.familia_castellana.fixture.json`): pareja con 2 hijos de 4 y 8 años, 1.500 €/mes, colegio a 10 min como requisito y trabajo en la Castellana. Resultado en producción el 12 nov, tras el despliegue de `28a0f2f` (`POST /api/v1/search` con ese fixture, `fit-0.3`, con el trabajo en minutos de transporte público de D-220). Es igual que en la base local de A (`evidence/gate-04/2026-11-12/golden-search-commute.txt`, `golden_family`):
  - encajan **33 de las 199 zonas**, y en 15 falta algún dato;
  - 1.ª **Fuencarral-El Pardo, 100 %**, con «29 min en transporte público hasta Paseo de la Castellana (Azca), llegando a las 9:00», colegio a 9 min y ≈ 1.107 €/mes por 77 m² (con el alquiler de contratos nuevos de D-228, unos **[1.270 €: pendiente de A]**; las cifras de este caso se vuelven a comprobar cuando A lo despliegue). Después, Ciudad Lineal (33 min) y Hortaleza (32 min), **empatadas al 99 %**: no se presenta un orden entre ellas. Puente de Vallecas, 7.ª (98 %);
  - antes, con la distancia en línea recta (`fit-0.1`), salía 1.ª Ciudad Lineal (99 %).
  - Cambia respecto al 11 nov (32 zonas y Ciudad Lineal ≈ 1.075 €/mes): D-216 sacó del registro los 1.001 «centros polivalentes» (clínicas privadas), que también ponderaban el alquiler por distrito. Con eso, Salamanca cabe en 1.500 €/mes y encaja (94 %): es la zona 33.
- **«¿Y si cambias algo?»** (Reality Check): cuántas zonas aparecen al cambiar una sola condición. En el caso demo lo que más limita es el colegio a 10 min: «+5 min a pie hasta colegio con primaria: saldrían 50 zonas, 17 más». Subir 150 €/mes ya no añade ninguna (`added_zones: 0`), y la web no enseña las opciones que no suman (`relaxOptions` en `apps/web/src/lib/fit.ts`). Casi encajan San Sebastián de los Reyes, Tres Cantos y Moncloa-Aravaca, que solo fallan por el colegio (producción, 12 nov). Captura **C3**: la de B (PR #17).
- **Coste:** alquiler medio por m² × m² del hogar (77 m² para 4 personas, Censo 2021 del INE). Es orientativo y tira a la baja: son contratos vigentes declarados en el IRPF, no anuncios (D-214). En la slide no va ninguna cifra de coste sin la palabra «unos».
- **Trabajo:** cuenta los minutos de puerta a puerta en transporte público para llegar a las 9:00, con los horarios publicados de las 6 redes del CRTM (CORE-009, D-220). En producción desde el 12 nov. **Límite que se dice si preguntan:** son horarios programados de un martes, no tiempos reales, y en 45–50 zonas de la Sierra Norte y del sureste no se llega a las 9:00 (D-220 §6).
- **«Sin escaleras»** (opcional, D-223): quien lo marca ve los minutos andando hasta la estación de metro, Metro Ligero o Cercanías que el CRTM da como totalmente accesible. Nunca se deduce de nada ni se etiqueta a nadie, y la tarjeta dice lo que no mide (autobuses, aceras y portales). En producción desde el 12 nov (despliegue de `2761696`). En la slide va una línea, solo si cabe.
- **Seguridad: no va en la slide.** No puntúa (D-224, D-226), y si preguntan la respuesta es la 36 de `pitch/preguntas.md`.
- **Antes de maquetar** se vuelven a comprobar las cifras en la demo, por si cambian los datos. Capturas: C1 y C2, las de B con `fit-0.2` (PR #19); C3, la de B del 12 nov (PR #17).

### Impacto: ayuntamientos que deciden dónde invertir
- Para cada zona, la lista **FALTA / JUSTO / CUBIERTO / SIN DATOS**. Tiene 6 filas, por municipio y por los 21 distritos (D-194; GAP-001 F1–F3b). Desde el 12 nov (D-217, `gap-0.3`) las cinco de servicios miden **lo que la gente tiene a 15 minutos andando, repartido entre todos los que lo comparten** (2SFCA; en llano, `pitch/metodologia.md` §1.4):
  - escuela infantil: escuelas infantiles al alcance a pie por cada 1.000 niños de 0 a 4 años (cada escuela cuenta como una: nadie publica sus plazas);
  - colegio: aulas de primaria, públicas y concertadas, al alcance a pie por cada 1.000 niños de 5 a 14 años;
  - centro de salud: centros de salud del SERMAS al alcance a pie por cada 10.000 habitantes (los consultorios cuentan para los minutos, no como capacidad);
  - mayores: plazas en hogares, clubes y centros de día al alcance a pie por cada 100 personas de 65 o más;
  - farmacia: farmacias al alcance a pie por cada 10.000 habitantes;
  - vivienda (no va a pie): viviendas de más de 90 m² por cada 100 hogares de 4 o más personas; por distrito, SIN DATOS, porque la CM no lo publica a ese nivel.

  Fuente: `gap_row` de los YAML en `data/catalog/features/` (D-217 §3) y `evidence/gate-04/2026-11-12/gap-status-gap03.md`. Cada fila lleva su fuente, su fiabilidad y los minutos a pie.
- **Con qué se compara (D-213, refinada por D-217):** con los demás municipios de su tipo, urbanos o rurales (Ley 45/2007), sin contarse a sí misma. FALTA exige menos del 80 % de esa referencia y que la diferencia no se explique por el tamaño de la zona (prueba exacta de Poisson). Un pueblo demasiado pequeño se compara junto con sus vecinos parecidos; si ni así se puede, nunca sale FALTA. Detalle y fuentes en `pitch/metodologia.md` §1.4.
- **Ejemplo de la slide: Puente de Vallecas (distrito 2807913), escuelas infantiles.** Comprobado en producción el 12 nov: `GET /api/v1/gaps/distrito/2807913` (`method.version: gap-0.3`, `data_version: 2026-11-12`), fila `escuela_infantil`:
  - **FALTA:** valor 2,781 (`escuelas_infantiles_a_pie_por_1000_ninos`); referencia 4,87, «Otros municipios urbanos de la Comunidad de Madrid»; ratio 0,571; `reliable: true`; `comparison_group: null` (los distritos no se agrupan). En toda la Comunidad, 4,721.
  - **Texto de la API (`explanation`):** «2,8 escuelas infantiles al alcance a pie por cada 1.000 niños de 0 a 4 años; en los demás municipios urbanos de la Comunidad de Madrid, 4,9 (en toda la Comunidad, 4,7)».
  - **Por qué se entiende en una frase:** la escuela infantil más cercana está cerca (desde la mitad de las calles, a 6 min o menos: `min_a_pie_escuela_infantil` = 6,258), pero son pocas para tantos niños. Contar centros por habitante da casi lo mismo (2,708, `escuelas_infantiles_por_1000_ninos`): no es un efecto del método.
  - **Las demás filas de la zona:** colegio, centro de salud, mayores y farmacia, CUBIERTO (farmacia: 4,5 frente a 3,1); vivienda, SIN DATOS.
  - **Otros distritos con FALTA en esa fila:** Villaverde (2,984; ratio 0,613) y Carabanchel (3,322; 0,682) (`GET /api/v1/gaps?level=distrito&row=escuela_infantil`, 12 nov). Centro (0,661) y Vicálvaro (0,647) tienen un ratio parecido y salen JUSTO: con menos niños, la diferencia podría ser casualidad. Sirve para responder a Escot.
  - **Si preguntan por un municipio:** Parla, farmacias, FALTA: 2,029 frente a 4,175 (ratio 0,486). La estadística oficial de farmacias por habitante también da 2,04 (`GET /api/v1/gaps/municipio/28106`, 12 nov).
  - **Ya no vale «Madrid tiene un tercio menos de centros de atención primaria»** (D-217 §7): con gap-0.3, Madrid capital sale JUSTO en centros de salud (0,3603 frente a 0,3799; ratio 0,9484, `evidence/gate-04/2026-11-12/gap-status-gap03.md`).
  - Captura **C4**: la de B (PR #17), `deck_c4_puente_de_vallecas_escuelas_infantiles_1440.png`, con las mismas cifras que producción.
- **Escala:**
  - 179 municipios (`evidence/gate-01/2026-10-20/cm_secciones_censales/row_counts.json`) + 21 distritos de Madrid capital (D-200, D-209; DATA-012 hecha);
  - 3.866 centros educativos, 553 centros sanitarios (276 centros de salud, 151 consultorios, 85 hospitales y 41 centros de salud mental; sin las clínicas privadas, D-216; con los 4 centros de salud corregidos por D-218 §10), 1.014 servicios para mayores y 2.957 farmacias (`evidence/gate-01/2026-11-12/cm_*/row_counts.json`, campo `places`);
  - 14.982 paradas y estaciones con su frecuencia: suma de `places` en `evidence/gate-01/2026-11-10/crtm_gtfs_*/row_counts.json`.

### Viabilidad: se sostiene
- **Quién paga:** las empresas, por análisis agregados y API. Para las personas es gratis (modelo del documento de la idea, sin cifras).
- **Privacidad:**
  - solo agregados por zona y nunca datos personales;
  - se excluyen equipamientos que expondrían a personas vulnerables (D-186);
  - la base de la demo está cerrada a accesos directos (D-197);
  - los fixtures no llevan datos de contacto (D-198).
- **Coste:** la base de la demo cabe en el plan gratuito de Supabase: 100 MB de 500 (`evidence/gate-06/2026-11-11/supabase-sync-demo.txt`, D-188). La web y la API van en el plan gratuito Hobby de Vercel: 0 €/mes y sin dominio propio (`infra/deploy/README.md` y `evidence/gate-06/2026-11-11-deploy/deploy-1-production.md`). Límite: Hobby solo admite uso no comercial; para cobrar a empresas habría que pasar a un plan de pago.
- **Reproducible y abierto:**
  - Apache-2.0 (`LICENSE`, D-191);
  - `make` como entrada única;
  - añadir un dataset es añadir un YAML de pipeline (`data/catalog/pipelines/`);
  - cada dato con su lineage y su control de calidad (`evidence/gate-01/`).

### Banda de enlaces (con QR)
- Demo: https://vidafacil-madrid.vercel.app (verificada el 11 nov con el buscador encendido: smoke 7/7, `evidence/gate-06/2026-11-11-deploy/deploy-12-buscador.md`, PR #11).
- Código: https://github.com/marianohernando/housing-intelligence

---

## Slide 4 · Pantallazo del sistema
**Composición:**
- Captura **C1** (mapa con la búsqueda del caso demo, 1440 px) a sangre en un marco de cristal.
- Encima, abajo a la derecha, la captura **C6** (móvil, 390 px) en un marco de teléfono sencillo, sin marca de fabricante.
- Tres notas de cristal numeradas que apuntan a la captura:
  1. «Cuéntanos tu hogar, tu presupuesto y dónde trabajas»: tarjeta «Tu búsqueda».
  2. «Zonas que encajan, con el porqué»: cabecera de la tarjeta de zona (% de encaje y hechos).
  3. «Qué falta en cada zona, con su fuente»: mini lista «Qué falta aquí» de la tarjeta.
- Pie: «Demo en vivo: vidafacil-madrid.vercel.app».

**Fuentes en la slide:** ninguna cifra nueva. Si la captura muestra cifras, son las de la API en ese momento.

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
Se hacen el 24 nov sobre la demo desplegada, con el caso demo precargado, a 1440 × 900 (escritorio) y 390 × 844 (móvil) y con densidad 2×. Se guardan en `pitch/capturas/` con estos nombres. B puede adelantarlas en `evidence/map-004/<fecha>/`.

El deck usa las capturas de producción del 11 nov. `pitch/deck/build.py` las toma de la evidencia si no hay una con el mismo id en `pitch/capturas/`:
- C4–C7 son de B (`evidence/map-004/2026-11-11/prod_*`), con `gap-0.2`. Se hicieron antes de desplegar el PR #9, así que algunos textos son anteriores. Los recortes los dejan fuera; ver cada fila.
- C1–C3 son de C (`evidence/gate-06/2026-11-11-deploy/prod-buscador-*`, PR #11, fusionado el 12 nov).

**Recaptura tras gap-0.3 (12 nov).** Las del 11 nov son anteriores a gap-0.3 y D-216. B ya rehízo C3 y C4 (PR #17, `evidence/map-004/2026-11-12/deck/`, en local a 1440 px con datos reales y las mismas cifras que producción), y el deck las toma de ahí (el #17 se fusionó el 12 nov). Con ellas y `DECK_INTEGRANTES`, `build.py --final` genera sin fallos (12 nov). Las demás valen como borrador, pero se rehacen antes del 24 nov:

| Id | Qué cambia | Dónde |
|---|---|---|
| C3 | Hecha por B: `deck_c3_y_si_cambias_1440.png`, con «Con tu búsqueda tal cual salen 33 zonas» y «+5 min a pie hasta colegio con primaria: saldrían 50 zonas, 17 más» | Portada → «Ver un ejemplo…» → «Ver todas las opciones» |
| C4 | Hecha por B: `deck_c4_puente_de_vallecas_escuelas_infantiles_1440.png`, la fila de escuelas infantiles de **Puente de Vallecas** en FALTA (2,8 frente a 4,9) con «A pie: 6 min». El hueco enseña las dos cifras | `/que-falta?zona=distrito/2807913` |
| C5 | Estados de Chamartín con gap-0.3: centro de salud y colegio CUBIERTO, mayores JUSTO (C6, el móvil, no enseña estados) | Zona Chamartín en 3D |
| C1, C2 | Hechas por B con `fit-0.2` (PR #19): `deck_c1_busqueda_1440.png` y `deck_c2_tarjeta_zona_1440.png`, con Fuencarral-El Pardo 1.ª (100 %) y «29 min en transporte público hasta Paseo de la Castellana (Azca), llegando a las 9:00». Son locales con datos reales, y producción da las mismas cifras desde el 12 nov (`fit-0.3`): no hace falta rehacerlas | Portada → «Ver un ejemplo…» y tarjeta de la 1.ª |
| C7 | «Cómo lo calculamos» ya explica el 2SFCA; el hueco puede volver a enseñar las reglas | `/como-lo-calculamos` |

| Id | Pantalla y estado | Tamaño | Slide | Estado |
|---|---|---|---|---|
| C1 | «Mapa» con «Tu búsqueda» rellena con el caso demo, coropleta de encaje y tarjeta de zona abierta | 1440 | 4 | Hecha por B con `fit-0.2` (`evidence/map-004/2026-11-12/deck/deck_c1_busqueda_1440.png`, PR #19): caso de la Castellana con Fuencarral-El Pardo 1.ª (100 %), como en producción desde el 12 nov |
| C2 | Recorte de la tarjeta de zona: % de encaje + 3–5 hechos con confianza + mini «Qué falta aquí» | 1440 | 3 | Hecha por B con `fit-0.2` (`evidence/map-004/2026-11-12/deck/deck_c2_tarjeta_zona_1440.png`, PR #19). El hueco de la slide 3 enseña la cabecera: «100 % de encaje» y «La 1.ª que más encaja» |
| C3 | Bloque «¿Y si cambias algo?» con cifras reales de la API | 1440 | 3 | Hecha por B el 12 nov (`evidence/map-004/2026-11-12/deck/deck_c3_y_si_cambias_1440.png`, PR #17). El hueco enseña «salen 33 zonas» y la opción «+5 min…: saldrían 50 zonas, 17 más». La del 11 nov decía 49 y ya no vale |
| C4 | Pestaña «Qué falta» de la zona del ejemplo (**Puente de Vallecas**): 6 filas con valor, referencia, confianza, minutos a pie y datasets enlazados | 1440 | 3 | Hecha por B el 12 nov (`evidence/map-004/2026-11-12/deck/deck_c4_puente_de_vallecas_escuelas_infantiles_1440.png`, PR #17; la página entera, en `deck_c4_puente_de_vallecas_que_falta_1440.png`). El hueco enseña las dos cifras de la fila de escuelas infantiles: 2,8 en Puente de Vallecas y 4,9 en los otros municipios urbanos |
| C5 | Zona en 3D: inclinación de unos 60°, contorno violeta y etiquetas de colegios, centros de salud y estaciones | 1440 | 1 | Hecha por B en producción con `gap-0.2` (`prod_c5_chamartin_3d_desktop.png`, Chamartín). El recorte deja fuera el título de la barra, «Barrios de la zona», que hoy se llama «Ir a un barrio»; se ven solo los barrios |
| C6 | Móvil: mapa a pantalla completa con la hoja inferior de la tarjeta de zona | 390 | 4 | Hecha por B en producción (`prod_c5_chamartin_3d_mobile.png`). No enseña estados |
| C7 | «Cómo lo calculamos» o panel de procedencia de un dato, con el enlace a la ficha del portal | 1440 | 3 (Viabilidad) | Hecha por B en producción (`prod_c7_como_lo_calculamos_desktop.png`). El hueco enseña «Cómo sale el % de encaje»: la primera de las «Tres reglas» aún compara con toda la Comunidad, también en producción. Cuando B la cambie (`pitch/metodologia.md` 1.1), se puede rehacer y volver a enseñar las reglas |
| QR | Códigos QR de la demo (https://vidafacil-madrid.vercel.app) y del repo | — | 3 | Se generan el 24 nov, cuando la demo esté verificada |

## Checklist del 24 nov (maquetar)
La maqueta ya está hecha en `pitch/deck/`: HTML a 16:9 y `build.py`, que genera el PDF y comprueba el contraste y los tamaños. Sus pasos están en `pitch/deck/README.md`; los de aquí siguen valiendo.

1. Rebase de `hi-coord` y `uv run python pitch/build_datasets_cm.py --refresh-portal`. Si cambia el total de datasets CM o algún grupo, actualizar la slide 2.
2. Cerrar todas las marcas «pendiente de A/B/C» de este fichero. Lo que no exista se quita de la slide; no se dibuja.
3. Hacer las capturas C1–C7 sobre la demo desplegada (consola sin errores) y generar los QR.
4. Maquetar con los tokens de arriba, exportar a PDF con hipervínculos activos y guardar también el PPTX.
5. Comprobar contraste AA y leer cada slide a 3 m (proyector). Mariano revisa el 24 (`docs/09_datamad/25_plan_competicion.md` §5).
