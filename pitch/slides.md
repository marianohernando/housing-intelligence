# Slides — Vida Fácil (contenido, dirección visual y capturas)

## Qué es este fichero
Las 4 slides que piden las bases (§8, resumen en `docs/09_datamad/24_bases_oficiales_2026.md`), en su orden.
- **Entrega:** PDF (y PPTX de respaldo) antes de las 14:00 del 26 nov. Se sube como tarde a las 13:30 (`docs/09_datamad/25_plan_competicion.md` §9).
- **24 nov:** solo maquetar con capturas reales de la demo desplegada.
- **Estado:** borrador del 11 nov. Lo marcado «pendiente de A/B/C» se cierra en el freeze del 23 nov.

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
- el nombre «Housing Intelligence», que solo puede ir en el pie como plataforma o equipo (`prompts/DECISIONES_11nov.md` §1).

---

## Slide 1 · Título, integrantes y descripción breve
**Texto:**
- **Vida Fácil** (logotipo de texto, Plus Jakarta Sans 700).
- *Encuentra tu sitio en Madrid* (lema, en violeta).
- Descripción, una frase: «El mapa de lo que falta en cada zona de la Comunidad de Madrid: para elegir dónde vivir y para decidir dónde invertir.»
- Integrantes: **lo rellena Mariano** (nombre y apellidos tal como en la inscripción).
- Pie: «DATAMAD 2026 · Datos abiertos de la Comunidad de Madrid · Código abierto (Apache-2.0) · Plataforma Housing Intelligence».

**Composición:**
- Mitad izquierda: título, lema y descripción sobre `--bg`.
- Mitad derecha: captura **C5** (zona en 3D) dentro de una tarjeta de cristal grande, con el contorno violeta de la zona visible.
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
Titular: **«21 conjuntos de datos del Portal de Datos Abiertos de la Comunidad de Madrid, todos con control de calidad superado»**. Fuente: `pitch/datasets_cm.md` y `evidence/gate-01/2026-11-10/real-run-quality.txt`. Se revisa el 23 nov regenerando `datasets_cm.md`.

Cada nombre lleva el hipervínculo a su ficha en el PDF:

| Tema | Datasets (nombre corto → ficha del portal) |
|---|---|
| Geografía (1) | [Secciones censales](https://datos.comunidad.madrid/dataset/secciones_censales) |
| Población y hogares (3) | [Población por edad](https://datos.comunidad.madrid/dataset/poblacion_censada_por_edad_nacionalidad_y_sexo) · [Hogares por tamaño (Censo 2021)](https://datos.comunidad.madrid/dataset/censo_2021_hogares_por_tamanyo) · [Nacidos vivos](https://datos.comunidad.madrid/dataset/mnp_nacidos_vivos_por_residencia_y_sexo) |
| Vivienda (4) | [Viviendas por superficie](https://datos.comunidad.madrid/dataset/censo_anual_vivienda_por_superficie_agregada) · [Viviendas por régimen de tenencia (Censo 2021)](https://datos.comunidad.madrid/dataset/censo_2021_viviendas_familiares_por_tenencia) · [Alquiler €/m² por municipio](https://datos.comunidad.madrid/dataset/alquiler_metro_cuadrado_mensual_viviendas_arrendadas_valor_catastral_municipios_mas_20000) · [Alquiler €/m² por código postal (Madrid)](https://datos.comunidad.madrid/dataset/1934259) |
| Renta (1) | [Renta disponible bruta municipal](https://datos.comunidad.madrid/dataset/irpf_indicador_renta) |
| Servicios (6) | [Centros educativos](https://datos.comunidad.madrid/dataset/centros_educativos) · [Unidades escolares](https://datos.comunidad.madrid/dataset/unidades_centros_no_universitarios_general_por_tipo_y_ensenanza) · [Centros sanitarios](https://datos.comunidad.madrid/dataset/centros_servicios_establecimientos_sanitarios) · [Centros de atención social](https://datos.comunidad.madrid/dataset/atencion_social_registro_centros) · [Oficinas de farmacia](https://datos.comunidad.madrid/dataset/oficinas_farmacia) · [Farmacias por municipio](https://datos.comunidad.madrid/dataset/farmacias) |
| Transporte (6, del CRTM con ficha en el portal) | [Metro](https://datos.comunidad.madrid/dataset/red_de_metro_oferta_planificada_horarios_topologia) · [Metro Ligero](https://datos.comunidad.madrid/dataset/red_de_metro_ligero_oferta_planificada_horarios_topologia) · [Cercanías](https://datos.comunidad.madrid/dataset/red_de_cercanias_oferta_planificada_horarios_topologia) · [EMT](https://datos.comunidad.madrid/dataset/red_de_autobuses_urbanos_emt_horarios_topologia) · [Autobuses urbanos](https://datos.comunidad.madrid/dataset/red_de_autobuses_urbanos_resto_municipios_horarios_topologia) · [Interurbanos](https://datos.comunidad.madrid/dataset/red_de_autobuses_interurbanos_horarios_topologia) |

- **Grupos:** salen del campo `domain` del catálogo. Los enlaces salen de `portal_url` (`services/ingestion/src/hi_ingestion/catalog/provenance.py`), igual que en `datasets_cm.md`.
- **Línea pequeña bajo la tabla:**
  - «Complementan, sin contar como datos CM: red peatonal de OpenStreetMap (ODbL)» (`pitch/datasets_cm.md` §3);
  - «+ Ayuntamiento de Madrid (distritos)»: **pendiente de A** (DATA-012). Se quita si no llega.
- **Pie:** «Lista completa, con licencias y control de calidad: github.com/marianohernando/housing-intelligence → `pitch/datasets_cm.md`».

**Composición:** dos tarjetas de cristal, la del problema al 40 % del ancho y la de los datos al 60 %. Cada tema de la tabla lleva su icono de línea. El «21» va grande en violeta.

---

## Slide 3 · Resultados: utilidad, impacto y viabilidad
Tres tarjetas de cristal en fila y, debajo, una banda con los enlaces.

### Utilidad: personas que buscan dónde vivir
- Cuentan su hogar, su alquiler máximo y dónde trabajan. Reciben zonas con su **% de encaje** y, debajo, hechos que se entienden, cada uno con su nivel de confianza en palabras.
  - Ejemplo de formato (`prompts/DISENO_VIDA_FACIL.md`): «Colegio público a 6 min andando».
  - Los hechos reales de la zona del caso demo: **pendiente de A** (CORE-005 y CORE-003) y **pendiente de B** (captura C2).
- **Reality Check:** si nada encaja, enseña cuántas zonas aparecen al relajar cada condición, con cifras reales de la API. Hoy solo existe el contrato (`packages/contracts/src/hi_contracts/public/search.py`, `7541527`); el cálculo está **pendiente de A** (CORE-003). Captura **C3**.
- **Caso demo:** pareja con 2 hijos que trabaja en la Castellana (`data/fixtures/contracts/scenario_state.familia_castellana.fixture.json`).

### Impacto: ayuntamientos que deciden dónde invertir
- Para cada zona, la lista **FALTA / JUSTO / CUBIERTO / SIN DATOS**. Tiene 6 filas: escuela infantil, colegio, centro de salud, mayores, farmacia y vivienda (D-194). Cada fila se compara con la referencia regional y lleva su fuente y su confianza.
- **Ejemplo real de hoy**, Móstoles en `GET /api/v1/gaps/municipio/28092` (`data/fixtures/contracts/zone_gap_list.mostoles.fixture.json`):
  - Centros de salud: **FALTA**. 0,47 centros de atención primaria por cada 10.000 habitantes; en el conjunto de la Comunidad, 0,59.
  - Colegios: **CUBIERTO**. 2,7 centros educativos públicos por cada 1.000 menores de 15 años; en la Comunidad, 2,2.
  - **Provisional:** los cortes `gap-0.1` y el filtro de colegios, que hoy incluye escuelas infantiles e institutos, cambian con GAP-001. La zona definitiva y sus cifras: **pendiente de A** (GAP-001). Puede ser un distrito de Madrid si DATA-012 llega. Captura **C4**.
- **Escala:**
  - 179 municipios (`evidence/gate-01/2026-10-20/cm_secciones_censales/row_counts.json`) + 21 distritos de Madrid capital (**pendiente de A**, DATA-012);
  - 3.851 centros educativos, 1.543 centros sanitarios, 1.001 servicios para mayores y 2.953 farmacias (`evidence/gate-01/*/cm_*/row_counts.json`, campo `places`);
  - 14.982 paradas y estaciones con su frecuencia: suma de `places` en `evidence/gate-01/2026-11-10/crtm_gtfs_*/row_counts.json`.

### Viabilidad: se sostiene
- **Quién paga:** las empresas, por análisis agregados y API. Para las personas es gratis (modelo del documento de la idea, sin cifras).
- **Privacidad:**
  - solo agregados por zona y nunca datos personales;
  - se excluyen equipamientos que expondrían a personas vulnerables (D-186);
  - la base de la demo está cerrada a accesos directos (D-197);
  - los fixtures no llevan datos de contacto (D-198).
- **Coste:** la base de la demo cabe en el plan gratuito de Supabase (perfil demo de 77 MB, D-188). El alojamiento de la web y la API está **pendiente de C** (OPS-001).
- **Reproducible y abierto:**
  - Apache-2.0 (`LICENSE`, D-191);
  - `make` como entrada única;
  - añadir un dataset es añadir un YAML de pipeline (`data/catalog/pipelines/`);
  - cada dato con su lineage y su control de calidad (`evidence/gate-01/`).

### Banda de enlaces (con QR)
- Demo: **pendiente de C** (URL estable el 17 nov).
- Código: https://github.com/marianohernando/housing-intelligence

---

## Slide 4 · Pantallazo del sistema
**Composición:**
- Captura **C1** (mapa con la búsqueda del caso demo, 1440 px) a sangre en un marco de cristal.
- Encima, abajo a la derecha, la captura **C6** (móvil, 390 px) en un marco de teléfono sencillo, sin marca de fabricante.
- Tres notas de cristal numeradas que apuntan a la captura:
  1. «Cuéntanos tu hogar, tu presupuesto y dónde trabajas»: tarjeta «Tu búsqueda».
  2. «Zonas que encajan, con el porqué»: tarjeta de zona.
  3. «Qué falta en cada zona, con su fuente»: mini lista o pestaña «Qué falta».
- Pie: «Demo en vivo: <URL> (pendiente de C)».

**Fuentes en la slide:** ninguna cifra nueva. Si la captura muestra cifras, son las de la API en ese momento.

---

## Dirección visual (brief de diseño, no el PDF)
Fuente única: `prompts/DISENO_VIDA_FACIL.md`. Los valores de la tabla son los que B ya validó en AA en la web (`apps/web/src/styles/tokens.css` en `claude/s1-web`, commit `4402edd`, PR #2). Si cambian antes del 24 nov, mandan los de la web.

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
- Nada de los mockups que no sea estilo. Llevan «Madrid 360», chips de discapacidad, un icono de usuario, foto de zona y «92/100» con barras; todo eso está descartado (`prompts/DECISIONES_11nov.md` §1, §5 y §8; `CLAUDE.md` §13).
- Notas sobre 100 o barras de puntuación: el encaje es un % con hechos debajo.
- Fotos de zonas.
- Etiquetas como «peligroso» ni datos de nacionalidad.
- Capturas de mockups: solo de la demo real.

**Contraste:** se comprueba AA en cada slide exportada, también el texto sobre cristal. Si no llega, se sube la opacidad del cristal.

---

## Capturas necesarias
Se hacen el 24 nov sobre la demo desplegada, con el caso demo precargado, a 1440 × 900 (escritorio) y 390 × 844 (móvil) y con densidad 2×. Se guardan en `pitch/capturas/` con estos nombres. B puede adelantarlas en `evidence/map-004/<fecha>/`.

| Id | Pantalla y estado | Tamaño | Slide | Estado |
|---|---|---|---|---|
| C1 | «Mapa» con «Tu búsqueda» rellena con el caso demo, coropleta de encaje y tarjeta de zona abierta | 1440 | 4 | **Pendiente de B** |
| C2 | Recorte de la tarjeta de zona: % de encaje + 3–5 hechos con confianza + mini «Qué falta aquí» | 1440 | 3 | **Pendiente de B** (y A para los hechos) |
| C3 | Bloque Reality Check con cifras reales de la API | 1440 | 3 | **Pendiente de A y B** |
| C4 | Pestaña «Qué falta» de la zona elegida: 6 filas con valor, referencia, confianza y datasets enlazados | 1440 | 3 | **Pendiente de A y B** |
| C5 | Zona en 3D: inclinación de unos 60°, contorno violeta y etiquetas de colegios, centros de salud y estaciones | 1440 | 1 | **Pendiente de B** |
| C6 | Móvil: mapa a pantalla completa con la hoja inferior de la tarjeta de zona | 390 | 4 | **Pendiente de B** |
| C7 | «Cómo lo calculamos» o panel de procedencia de un dato, con el enlace a la ficha del portal | 1440 | 2 (opcional) | **Pendiente de B** |
| QR | Códigos QR de la demo y del repo | — | 3 | **Pendiente de C** (URL de la demo) |

## Checklist del 24 nov (maquetar)
1. Rebase de `hi-coord` y `uv run python pitch/build_datasets_cm.py --refresh-portal`. Si cambia el total de datasets CM o algún grupo, actualizar la slide 2.
2. Cerrar todas las marcas «pendiente de A/B/C» de este fichero. Lo que no exista se quita de la slide; no se dibuja.
3. Hacer las capturas C1–C7 sobre la demo desplegada (consola sin errores) y generar los QR.
4. Maquetar con los tokens de arriba, exportar a PDF con hipervínculos activos y guardar también el PPTX.
5. Comprobar contraste AA y leer cada slide a 3 m (proyector). Mariano revisa el 24 (`docs/09_datamad/25_plan_competicion.md` §5).
