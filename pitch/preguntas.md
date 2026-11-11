# Banco de preguntas del jurado — Vida Fácil

**Cómo usarlo:**
- 5 minutos de preguntas (bases §9).
- Cada respuesta tiene 3 frases como máximo: primero la respuesta, después el dato y por último el límite, si lo hay.
- La evidencia es para Mariano; no se lee en voz alta.
- Si algo no se sabe: «No lo sé con certeza; lo compruebo y os lo envío». Nunca se inventa una cifra.

**Perfiles:** salen de `docs/09_datamad/25_plan_competicion.md` §4. Lo que valora cada miembro del jurado es una inferencia a partir de su trayectoria pública.

> Las decisiones del 11 nov están registradas como D-199 a D-213 (`docs/00_index/01_decisions_log.md`). El brief de diseño (`~/Desktop/DATAMAD/prompts/DISENO_VIDA_FACIL.md`, adoptado por D-201) sigue fuera del repo: se cita como documento interno, no como evidencia pública.

**Marcas:** «pendiente de A/B/C» = todavía no existe. Se revisa el 23 nov (freeze) y el 25 nov (ensayos).

---

## Alberto Abella · Gaia-X España (APIs, interoperabilidad, espacios de datos)

**1. ¿Cómo se integra esto con otros sistemas?**
Con una API pública versionada (`/api/v1`) cuyos contratos están publicados como JSON Schema. Las zonas se identifican con el código INE del municipio, así que se cruzan con cualquier otra fuente oficial.
- Evidencia: `docs/04_technical_architecture/31_public_api_routes.md` · `data/schemas/api/*.schema.json` (4 esquemas) · `GET /api/v1/gaps/municipio/28092`.

**2. ¿Tenéis MCP para agentes de IA?**
Está diseñado como herramientas que llaman a los mismos servicios de la API, nunca a SQL libre, para que un agente no pueda inventar ni modificar datos.
- Evidencia: `CLAUDE.md` §3 (Arquitectura) · board MCP-001.
- Estado: **pendiente de A** (MCP-001, 19–22 nov). Si no llega, responder: «Hoy está la API; el MCP es el siguiente paso y va sobre esos mismos servicios».

**3. ¿Vuestro catálogo de datos es reutilizable?**
Sí. Cada fuente, dataset, métrica y feature está descrito en YAML legible por máquina, con licencia, propietario y enlace, y ese catálogo se publica en CC BY 4.0. De ahí sale, por ejemplo, la lista de datasets que habéis visto, generada con un script.
- Evidencia: `data/catalog/` · D-191 · `pitch/build_datasets_cm.py`.

**4. ¿Podría ser un producto de datos en un espacio de datos?**
Encaja, porque cada resultado sale ya con su fuente, versión, licencia y nivel de confianza. Exportarlo en DCAT-AP o con un conector de espacio de datos todavía no está hecho: sería el siguiente paso.
- Evidencia: el campo `datasets` con `version` y `license` de cada fila (`data/fixtures/contracts/zone_gap_list.mostoles.fixture.json`).

**5. ¿Y si cambia un dataset del portal?**
Cada ingesta compara la huella (sha256) del fichero. Si no cambia, se salta; si cambia, crea una versión nueva. Si la nueva versión falla los controles, se sigue sirviendo la última válida.
- Evidencia: `evidence/gate-01/2026-11-10/idempotent-rerun.txt` · `last-valid-versions.txt` · `lineage.json` de cada dataset.

---

## Olga Quirós · ASEDIE (sector infomediario, negocio)

**6. ¿Quién paga?**
Las empresas que necesitan saber qué falta en una zona (promotoras, cadenas, residencias, comercios) pagan por análisis agregados y por la API. Las personas lo usan gratis y los ayuntamientos lo usan para planificar.
- Evidencia: `docs/09_datamad/25_plan_competicion.md` §1 · `CLAUDE.md` §16 (cliente inicial: promotoras e inmobiliarias medianas).

**7. Si los datos son abiertos, ¿por qué pagaría alguien?**
Por el trabajo que hay encima: cruzar 21 conjuntos con formatos distintos, controlar su calidad, comparar cada zona con otras parecidas y explicarlo con su fuente. Hacer eso a mano para cada estudio cuesta semanas; aquí está hecho, se recarga con un comando y detecta qué fuente ha cambiado.
- Evidencia: `pitch/datasets_cm.md` · `evidence/gate-01/2026-11-10/summary.md` · `evidence/gate-01/2026-11-10/idempotent-rerun.txt`.

**8. ¿La licencia de los datos permite un uso comercial?**
Sí. Los datos del portal CM son CC BY y la licencia del CRTM permite reutilizarlos citando la fuente. En ambos casos cumplimos la atribución y no vendemos el dato en bruto, sino el análisis.
- Evidencia: licencias por dataset en `pitch/datasets_cm.md` · `data/catalog/sources/comunidad_madrid_ckan.yaml` y `crtm_open_data.yaml` (`commercial_use: true`, `attribution_text`).

**9. ¿En qué os diferenciáis de los portales inmobiliarios o de las consultoras?**
Los portales enseñan la oferta de pisos; nosotros enseñamos la necesidad y el encaje de cada zona. Frente a un estudio de consultora, aquí todo es abierto, reproducible y cita cada dato.
- Evidencia: `docs/09_datamad/25_plan_competicion.md` §8.

**10. ¿Cuánto cuesta mantenerlo?**
Hoy, 0 € al mes: la web y la API van en el plan gratuito de Vercel y la base en el de Supabase, y los datos se recargan copiando tablas ya validadas. Para un uso comercial habría que pasar a planes de pago, porque el gratuito de Vercel no lo admite.
- Evidencia: `evidence/gate-06/2026-11-11/supabase-sync-demo.txt` (base de la demo: 100 MB de los 500 del plan gratuito) · D-188.
- Alojamiento: `infra/deploy/README.md` y `evidence/gate-06/2026-11-11-deploy/deploy-1-production.md` (rama `claude/s1-deploy`, PR #4) (plan Hobby: «solo personal y no comercial»).

---

## Loren Escot · UCM, Estudios Estadísticos (rigor de los indicadores)

**11. ¿Cómo decidís que algo «falta»?**
Comparamos la tasa de la zona con la de los demás municipios de su tipo, rurales o urbanos. FALTA exige dos cosas: menos del 80 % de esa referencia (la regla de los cuatro quintos) y que la diferencia no se explique por el azar del tamaño de la zona; CUBIERTO es llegar al 100 %, y lo demás es JUSTO. Es una señal para priorizar, no un veredicto, y el método está declarado y versionado (`gap-0.2`).
- Evidencia: D-213 (puntos 1 y 2: 29 CFR 1607.4(D); intervalo exacto de Poisson de Garwood al 95 %, como en Fingertips y en los gráficos en embudo de Spiegelhalter, 2005) · `packages/domain/src/hi_domain/gaps.py` · `apps/api/src/hi_api/services/gap_reference.py` · `evidence/gate-04/2026-11-11/phase-gap001-f5-review.txt`.
- Estado: hecho en la API y en producción (GAP-001 F5, `d02574f`, `f626e1f`; `GET /api/v1/gaps/municipio/28079` da `gap-0.2`, comprobado el 11 nov).

**12. ¿Por qué comparáis con municipios del mismo tipo y no con toda la región?**
Porque la tasa depende del tipo de territorio: cada pueblo tiene su consultorio, y los municipios rurales tienen 14,8 veces más centros de atención primaria por habitante que los urbanos. Con la media de la región, ningún distrito de Madrid salía cubierto en centros de salud, y la diferencia entre rural y urbano es significativa en las 6 filas (χ², p < 0,05). Usamos la definición legal de medio rural de la Ley 45/2007 (menos de 30.000 habitantes y menos de 100 por km²), y ninguna zona se compara consigo misma: Madrid es la mitad de la población urbana.
- Evidencia: D-213 (punto 1 y tabla χ²: de p = 0,039 en farmacias a p < 10⁻³⁰⁰ en vivienda; 84 municipios rurales y 95 urbanos) · `evidence/gate-04/2026-11-11/phase-gap001-f5-review.txt`.
- Límite, si insiste: el tipo se asigna por municipio, la superficie es la de la geometría de 2019 y el modelo de Poisson no trata la sobredispersión (D-213, punto 5).
- Estado: hecho (GAP-001 F5).

**13. ¿Qué pasa con los municipios pequeños, donde una ratio se dispara?**
Si en la zona se esperan menos de 3,69 casos, que es el límite superior al 95 % de un recuento de cero, la zona es demasiado pequeña para comparar y nunca sale FALTA, aunque se ve su valor. Por ejemplo, La Acebeda, con 70 habitantes y sin farmacia, sale JUSTO y marcada como «zona pequeña para comparar». Además, por debajo de un umbral de población el dato se publica con confianza 0,5, y si falta sale SIN DATOS, nunca un cero.
- Evidencia: D-213 (punto 3, `reliable: false`) · `phase-gap001-f5-review.txt` (La Acebeda, farmacia) · `small_population_threshold` en los YAML de las 6 filas · `null_policy`.
- Estado: hecho en la API y en producción. La Acebeda, farmacia: JUSTO con `reliable: false` (`GET /api/v1/gaps/municipio/28001`, comprobado el 11 nov). La leyenda del mapa por fila lo enseña como «Zona pequeña para comparar» (en colegios, 140 zonas: `evidence/gate-06/2026-11-11-deploy/prod-buscador-check.json`, PR #11).

**14. «Centros por habitante» no es lo mismo que «plazas». ¿No es engañoso?**
Lo es si no se dice, y por eso cada fila declara su aproximación. Por ejemplo: «Cuenta colegios con primaria, públicos o concertados, no plazas: un colegio grande y uno pequeño pesan igual». Donde haya un dato de capacidad oficial, lo usaremos.
- Evidencia: campo `proxy_note` en `data/catalog/features/*.yaml` y en cada fila de la API.

**15. Madrid capital tiene 3 millones de habitantes. ¿No esconde la media todo?**
Sí, por eso Madrid se divide en sus 21 distritos, y la distancia a pie se calcula por sección censal, mucho más fina que el municipio. También pasa lo contrario: Madrid entera tiene un tercio menos de centros de atención primaria por habitante que los demás municipios urbanos (FALTA), y en cambio ningún distrito por sí solo basta para afirmarlo.
- Evidencia: D-200 · D-209 · D-210 · D-213 («Efecto»: Madrid, 0,37 frente a 0,56; los 21 distritos, JUSTO) · `evidence/gate-03/2026-11-11/walk-coverage.txt` (las 4.843 zonas: secciones, municipios, distritos y región).
- Estado: hecho. Distritos con el padrón municipal (D-209); distancia a pie a 4 km/h (CORE-005, D-211), en la API (GAP-001 F1) y en la web (`evidence/map-004/2026-11-11/`).

**16. ¿Cómo calculáis el % de encaje?**
Primero, las condiciones: cada una sale PASS, FAIL o «sin dato», y «sin dato» nunca cuenta como PASS; solo encajan las zonas que lo cumplen todo. Después, cada criterio puntúa de 0 a 1 con una curva declarada (un colegio vale 1 hasta 10 min y 0 desde 30), y lo que la persona marca primero pesa más: con 5 criterios, 33, 27, 20, 13 y 7 %. El % es la media ponderada; lo que no tiene datos no cuenta como 0, sino que baja la confianza, y el método va versionado (`fit-0.1`).
- Evidencia: D-215 (puntos 2 a 6) · `packages/domain/src/hi_domain/fit.py` · `CLAUDE.md` §14 · caso real: `evidence/gate-04/2026-11-11/phase-core003-f2.txt` (Ciudad Lineal, 99 %).
- Límite, si insiste: no hay todavía diversificación ni soluciones Pareto; el orden es solo por % de encaje (D-215, punto 10).
- Estado: hecho en la API (CORE-003) y en producción desde el 11 nov (buscador de B, PR #10, encendido por C en el PR #11). El caso de la Castellana da lo mismo que en local: Ciudad Lineal, 99 % (`evidence/gate-06/2026-11-11-deploy/prod-buscador-check.json`).

**17. El alquiler solo está publicado para municipios grandes. ¿Qué hacéis en el resto?**
Así es: la Comunidad publica el alquiler de 37 municipios, los de más de 20.000 habitantes con contratos suficientes, y el de los códigos postales de Madrid capital. En el resto, la condición de presupuesto sale «sin dato», se dice y nunca se da por buena. En los distritos de Madrid hacemos la media de sus códigos postales, ponderada por dónde están los colegios, centros de salud y centros sociales, y lo declaramos como aproximación: sale 14,5 €/m², y la Comunidad publica 15,1 para todo Madrid.
- Evidencia: D-214 (puntos 3 y 4) · `data/catalog/features/alquiler_m2_mensual.yaml` v2 · `evidence/gate-04/2026-11-11/phase-core006-f1.txt` (14,46 frente a 15,10) · `CLAUDE.md` §14 (UNKNOWN nunca equivale a PASS).

**18. Vuestro alquiler estimado parece bajo. ¿Es real?**
Es orientativo y tira a la baja, y lo decimos en cada resultado: la Comunidad publica la media de los contratos vigentes declarados en el IRPF, no la de los anuncios, y un contrato nuevo suele costar más. Además, esos m² son construidos, del Catastro, así que el precio corresponde a un piso algo menor que el que suponemos (77 m² para 4 personas, la vivienda mediana de ese hogar en el Censo 2021). Por eso, cuando decimos que una zona no entra en el presupuesto, es fiable; cuando decimos que sí, avisamos de que puede costar más.
- Evidencia: D-214 (puntos 2 y 3) · ficha del portal CM (https://datos.comunidad.madrid/dataset/1934259, campo «Fuente»: «Estadística de Viviendas Declaradas en el Impuesto sobre la Renta de las Personas Físicas. Agencia Estatal de Administración Tributaria») · INE, tabla 59524 (https://www.ine.es/jaxi/Tabla.htm?tpx=59524&L=0) · `limitations` de `alquiler_m2_mensual.yaml`.
- Si preguntan por qué no usamos anuncios: no hay una fuente oficial y abierta de precios de oferta, y no hacemos scraping (pregunta 31).

**19. ¿Tenéis en cuenta lo que se tarda en llegar al trabajo?**
Todavía no en tiempo: hoy cuenta la distancia en línea recta desde la zona al trabajo, como preferencia y con confianza 0,5, nunca como condición. Vale 1 hasta 2 km y 0 desde 20 km, y la explicación de cada zona da los kilómetros. El tiempo en transporte público, con los horarios del CRTM que ya tenemos, es el siguiente paso (CORE-009).
- Evidencia: D-215 (puntos 2 y 5) · `fit.py` (`NEAR_KM, FAR_KM = 2.0, 20.0`).
- Estado: **pendiente de A** (CORE-009, 19–22 nov). Si llega, cambiar esta respuesta.

**20. ¿Cómo medís «a 10 minutos andando»? ¿A qué velocidad?**
Por las calles de verdad, no en línea recta, a 4 km/h: el mismo paso que el estudio «El Madrid de los 15 minutos» del Ayuntamiento. En cada fila damos los minutos en los que llega la mitad de las calles de la zona; si una zona no tiene calles en el mapa, sale «sin datos», nunca cero. Lo comprobamos con 15 casos de lugares conocidos: por ejemplo, La Acebeda no tiene farmacia y la más cercana queda a más de hora y media andando.
- Evidencia: D-210 · D-211 · `data/catalog/features/min_a_pie_*.yaml` y `pct_calle_*.yaml` · `scripts/check_walk_golden.py` y `evidence/gate-03/2026-11-11/phase-core005-f5.txt` (La Acebeda: farmacia a 109,7 min, D-211) · estudio del Ayuntamiento: https://geoportal.madrid.es/fsdescargas/IDEAM_WBGEOPORTAL/GEOPORTAL/Jornada/2022/SALA5_1130_PROXIMIDAD_POR_CALCULODEREDES.pdf («Velocidad de desplazamiento estimada en 4 Km/h»).
- Estado: hecho a 4 km/h, decisión de Mariano del 11 nov (CORE-005 Fase 5, `ad2129a`, D-211, Gate 3 PASS). En la API, con GAP-001 F1 (`2d05d78`), y en producción. Por ejemplo, Madrid capital: «A pie hasta el centro de salud más cercano: 12 min» (`evidence/map-004/2026-11-11/prod_c4_madrid_que_falta_desktop.png`). El % de calle a 10 minutos también está calculado (`pct_calle_*.yaml`), pero no se enseña.

---

## Ricardo Curto · Universidad de Oviedo (calidad, licencias y cita de fuentes)

**21. ¿Qué datasets del portal usáis exactamente y con qué licencia?**
21 datasets con ficha en el Portal de Datos Abiertos de la Comunidad de Madrid, cada uno con su enlace, licencia, qué alimenta y su informe de calidad. La lista se genera desde el catálogo, no se escribe a mano.
- Evidencia: `pitch/datasets_cm.md` · `pitch/build_datasets_cm.py`.

**22. Los GTFS son del Consorcio. ¿Por qué los contáis como datos de la Comunidad?**
Porque el propio portal de la Comunidad los publica con su ficha y su licencia. Aun así, los separamos en la lista y damos también la descarga original del CRTM, para que se vea claro.
- Evidencia: D-196 · `pitch/datasets_cm.md` §2 (6 fichas con licencia «CRTM Licencia de datos abiertos (LDA)» en el portal CM).

**23. ¿Qué control de calidad pasa un dataset antes de entrar?**
Claves únicas, que cada municipio exista en la geografía oficial, errores de lectura, ratio de registros en cuarentena y faltantes marcados como faltantes, no como cero. Los registros dudosos van a cuarentena, no se borran, y cada versión guarda la huella del fichero original.
- Evidencia: `evidence/gate-01/*/<dataset>/quality_report.json` · `lineage.json` (sha256 y URL) · `row_counts.json` (`quarantined`).

**24. ¿Encontrasteis errores en los datos del portal?**
Sí, y los tratamos sin ocultarlos. Por ejemplo: una geometría inválida en las secciones censales, reparada y documentada, y centros sin coordenadas válidas que van a cuarentena (55 de centros educativos).
- Evidencia: `notes` de `data/catalog/datasets/cm_secciones_censales.yaml` · `evidence/gate-01/2026-10-22/cm_centros_educativos/row_counts.json`.

**25. ¿Los datos están al día?**
Cada fuente se recarga según su propia frecuencia de publicación, y en los GTFS el control de calidad avisa si el horario está caducado. Por ejemplo, el GTFS de metro venció el 27 de mayo de 2026 y sigue siendo el último publicado: lo usamos y el control de calidad lo marca.
- Evidencia: control `feed_current` en `evidence/gate-01/2026-11-10/crtm_gtfs_metro/quality_report.json` · D-196.

**26. ¿Cómo citáis las fuentes en la propia aplicación?**
Cada fila de la lista y cada resultado llevan los datasets de los que salen, con el enlace a su ficha, la versión y la licencia. Además, la web muestra la atribución que pide cada licencia, incluido «Powered by CRTM».
- Evidencia: campo `datasets` de la API (`data/fixtures/contracts/zone_gap_list.mostoles.fixture.json`) · `attribution_text` en `data/catalog/sources/*.yaml`.
- Estado: hecho en producción: pie con Comunidad de Madrid, Ayuntamiento, «Powered by CRTM» y OpenStreetMap (`evidence/map-004/2026-11-11/prod_c4_madrid_que_falta_desktop.png`).

---

## Generales (cualquier miembro)

**27. ¿Qué hicisteis durante la competición y qué ya existía?**
El trabajo previo está identificado con el tag `pre-datamad` (22 oct): la geografía, los 10 primeros datasets y el mapa base. Desde el 7 nov hemos añadido el transporte del CRTM, 5 datasets más, la lista de lo que falta con sus 6 filas, la red peatonal, la web, el buscador y el despliegue.
- Evidencia: `README.md` («Trabajo previo a DATAMAD») · tag `pre-datamad` = `cf39459` · D-174 · `board/BOARD.md` (07 — DONE).
- Estado: hecho. La lista, la web y el buscador están en producción; el buscador, desde el 11 nov (`evidence/gate-06/2026-11-11-deploy/deploy-12-buscador.md`, PR #11).

**28. ¿Habéis usado IA?**
Sí, como asistente de programación, que las bases permiten (§7), y nosotros respondemos de todo el código y los resultados. El producto no usa IA para calcular nada: todas las cifras salen de reglas deterministas, versionadas y con tests.
- Evidencia: `docs/09_datamad/24_bases_oficiales_2026.md` §7 · `CLAUDE.md` §3 (IA).

**29. ¿Qué pasa con la privacidad?**
Nunca tratamos datos de personas: solo agregados por zona. Además, no mostramos equipamientos que expondrían a personas vulnerables, quitamos teléfonos, emails y NIF que publicaba la fuente, y la base de la demo no se puede leer desde fuera de la API.
- Evidencia: D-186 · D-198 · D-197 · control `no_contact_or_tax_ids` en los `quality_report.json` de puntos.

**30. ¿De dónde sale «lo que falta» si no tenéis usuarios?**
Hoy, de datos oficiales: población, hogares y equipamientos, comparados con los demás municipios del mismo tipo. El siguiente paso es sumar lo que la gente declare que necesita, anónimo y agregado por zona, y no lo simulamos en la demo.
- Evidencia: D-194 · `docs/09_datamad/25_plan_competicion.md` §8.

**31. ¿Por qué no usáis datos de los portales inmobiliarios?**
Porque no hacemos scraping: sus condiciones no lo permiten y las bases exigen respetar licencias. Además, enseñan la oferta, y lo que nosotros medimos es la necesidad.
- Evidencia: `CLAUDE.md` §15 · D-175 y D-185 (Google Maps y Gosom descartados) · bases §6.

**32. ¿Incluís seguridad? Es delicado.**
Solo si la persona la marca como prioridad y solo con datos oficiales agregados: actuaciones de la Policía Municipal por cada 1.000 habitantes y por distrito. Nunca nacionalidad ni etiquetas como «peligroso»; fuera de Madrid capital, SIN DATOS.
- Evidencia: D-204 y D-205.
- Estado: extra **pendiente de A** (DATA-020, 19–22 nov). Si no está, decir «no lo incluimos todavía, y así es como lo haríamos».

**33. ¿Funciona fuera de la Comunidad de Madrid?**
La arquitectura sí: añadir un dataset es añadir un YAML de pipeline, y la geografía se basa en códigos INE. Lo que haría falta en otra región es su portal de datos con equivalentes.
- Evidencia: `data/catalog/pipelines/` · `README.md` (Quickstart).

**34. ¿Es accesible para personas mayores?**
Está pensada para ellas: español llano, texto base de 17 px, botones de 44 px y contraste AA verificado también sobre el cristal. El estado de cada fila nunca depende solo del color: siempre va con texto e icono.
- Evidencia: `~/Desktop/DATAMAD/prompts/DISENO_VIDA_FACIL.md` · `apps/web/src/lib/__tests__/tokens.test.ts` · axe WCAG 2.2 AA en producción sin fallos (`prod-buscador-check.json`, PR #11).
- Estado: hecho. axe AA da 0 fallos en producción (11 nov): en escritorio, en la portada, los resultados, la tarjeta de zona y la compra; en el móvil, en los resultados y la tarjeta.

**35. ¿Por qué «Vida Fácil»?**
Porque es corto, en español y fácil de recordar para cualquiera, también para personas mayores. Comprobamos que no choca con ninguna marca del sector de la vivienda.
- Evidencia: D-199 · consulta de TMview (OEPM + EUIPO) del 11 nov en el PR #3.
