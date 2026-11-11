# Banco de preguntas del jurado — Vida Fácil

**Cómo usarlo:**
- 5 minutos de preguntas (bases §9).
- Cada respuesta tiene 3 frases como máximo: primero la respuesta, después el dato y por último el límite, si lo hay.
- La evidencia es para Mariano; no se lee en voz alta.
- Si algo no se sabe: «No lo sé con certeza; lo compruebo y os lo envío». Nunca se inventa una cifra.

**Perfiles:** salen de `docs/09_datamad/25_plan_competicion.md` §4. Lo que valora cada miembro del jurado es una inferencia a partir de su trayectoria pública.

> Las decisiones del 11 nov están registradas como D-199 a D-207 (`docs/00_index/01_decisions_log.md`). El brief de diseño (`~/Desktop/DATAMAD/prompts/DISENO_VIDA_FACIL.md`, adoptado por D-201) sigue fuera del repo: se cita como documento interno, no como evidencia pública.

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
Por el trabajo que hay encima: cruzar 21 conjuntos con formatos distintos, controlar su calidad, compararlos con la región y explicarlos con su fuente. Hacer eso a mano para cada estudio cuesta semanas; aquí está hecho, se recarga con un comando y detecta qué fuente ha cambiado.
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
Comparamos el indicador de la zona con la referencia regional, que es el total de la Comunidad dividido por su población. Por debajo del 80 % de la referencia es FALTA, entre el 80 % y el 100 % es JUSTO, y desde el 100 % es CUBIERTO. Es una señal para priorizar, no un veredicto, y los cortes están declarados y versionados.
- Evidencia: `packages/domain/src/hi_domain/gaps.py` (`gap-0.1`: `falta_below=0.8`, `cubierto_from=1.0`).
- Estado: cortes provisionales hasta el ADR de GAP-001 (**pendiente de A**).

**12. ¿Qué pasa con los municipios pequeños, donde una ratio se dispara?**
Por debajo de un umbral de población (500 menores de 15 años para colegios y 2.000 habitantes para salud), el indicador se publica con confianza 0,5 y se ve. Si falta el dato, sale SIN DATOS: nunca un cero.
- Evidencia: `small_population_threshold` en `data/catalog/features/colegios_publicos_por_1000_menores.yaml` y `centros_salud_por_10000_hab.yaml` · `null_policy`.

**13. «Centros por habitante» no es lo mismo que «plazas». ¿No es engañoso?**
Lo es si no se dice, y por eso cada fila declara su aproximación. Por ejemplo: «Cuenta centros, no plazas ni etapas: un centro grande y uno pequeño pesan igual». Donde haya un dato de capacidad oficial, lo usaremos.
- Evidencia: campo `proxy_note` en `data/catalog/features/*.yaml` y en cada fila de la API.

**14. Madrid capital tiene 3 millones de habitantes. ¿No esconde la media todo?**
Sí, por eso Madrid se divide en sus 21 distritos. Además, la distancia a pie se calcula por sección censal, que es mucho más fina que el municipio.
- Evidencia: D-200 · board CORE-005 · `evidence/gate-01/2026-11-11/osm_red_peatonal/`.
- Estado: distritos **pendiente de A** (DATA-012) y distancia a pie **pendiente de A** (CORE-005, Fases 3 y 4).

**15. ¿Cómo calculáis el % de encaje?**
Primero se comprueban las condiciones de la persona, cada una con PASS, FAIL o «sin dato», y un «sin dato» nunca cuenta como PASS. Después se puntúan las prioridades con pesos declarados. El método y su versión se ven en «Cómo lo calculamos».
- Evidencia: `CLAUDE.md` §14 · contrato `packages/contracts/src/hi_contracts/public/search.py`.
- Estado: **pendiente de A** (CORE-003). Confirmar los pesos reales antes del 25 nov.

**16. El alquiler solo está publicado para municipios grandes. ¿Qué hacéis en el resto?**
Así es: el dataset del portal cubre los municipios de más de 20.000 habitantes. En los demás, la condición de presupuesto queda como «sin dato», se dice y nunca se da por buena.
- Evidencia: título del dataset en `pitch/datasets_cm.md` · `CLAUDE.md` §14 (UNKNOWN nunca equivale a PASS).

---

## Ricardo Curto · Universidad de Oviedo (calidad, licencias y cita de fuentes)

**17. ¿Qué datasets del portal usáis exactamente y con qué licencia?**
21 datasets con ficha en el Portal de Datos Abiertos de la Comunidad de Madrid, cada uno con su enlace, licencia, qué alimenta y su informe de calidad. La lista se genera desde el catálogo, no se escribe a mano.
- Evidencia: `pitch/datasets_cm.md` · `pitch/build_datasets_cm.py`.

**18. Los GTFS son del Consorcio. ¿Por qué los contáis como datos de la Comunidad?**
Porque el propio portal de la Comunidad los publica con su ficha y su licencia. Aun así, los separamos en la lista y damos también la descarga original del CRTM, para que se vea claro.
- Evidencia: D-196 · `pitch/datasets_cm.md` §2 (6 fichas con licencia «CRTM Licencia de datos abiertos (LDA)» en el portal CM).

**19. ¿Qué control de calidad pasa un dataset antes de entrar?**
Claves únicas, que cada municipio exista en la geografía oficial, errores de lectura, ratio de registros en cuarentena y faltantes marcados como faltantes, no como cero. Los registros dudosos van a cuarentena, no se borran, y cada versión guarda la huella del fichero original.
- Evidencia: `evidence/gate-01/*/<dataset>/quality_report.json` · `lineage.json` (sha256 y URL) · `row_counts.json` (`quarantined`).

**20. ¿Encontrasteis errores en los datos del portal?**
Sí, y los tratamos sin ocultarlos. Por ejemplo: una geometría inválida en las secciones censales, reparada y documentada, y centros sin coordenadas válidas que van a cuarentena (55 de centros educativos).
- Evidencia: `notes` de `data/catalog/datasets/cm_secciones_censales.yaml` · `evidence/gate-01/2026-10-22/cm_centros_educativos/row_counts.json`.

**21. ¿Los datos están al día?**
Cada fuente se recarga según su propia frecuencia de publicación, y en los GTFS el control de calidad avisa si el horario está caducado. Por ejemplo, el GTFS de metro venció el 27 de mayo de 2026 y sigue siendo el último publicado: lo usamos y el control de calidad lo marca.
- Evidencia: control `feed_current` en `evidence/gate-01/2026-11-10/crtm_gtfs_metro/quality_report.json` · D-196.

**22. ¿Cómo citáis las fuentes en la propia aplicación?**
Cada fila de la lista y cada resultado llevan los datasets de los que salen, con el enlace a su ficha, la versión y la licencia. Además, la web muestra la atribución que pide cada licencia, incluido «Powered by CRTM».
- Evidencia: campo `datasets` de la API (`data/fixtures/contracts/zone_gap_list.mostoles.fixture.json`) · `attribution_text` en `data/catalog/sources/*.yaml`.
- Estado: atribuciones en el pie de la web **pendiente de B**.

---

## Generales (cualquier miembro)

**23. ¿Qué hicisteis durante la competición y qué ya existía?**
El trabajo previo está identificado con el tag `pre-datamad` (22 oct): la geografía, los 10 primeros datasets y el mapa base. Desde el 7 nov hemos añadido el transporte del CRTM, 5 datasets más, la lista de lo que falta por la API, la red peatonal, el buscador y el despliegue.
- Evidencia: `README.md` («Trabajo previo a DATAMAD») · tag `pre-datamad` = `cf39459` · D-174 · `board/BOARD.md` (07 — DONE).
- Estado: buscador y despliegue **pendiente de A y C** hasta el 17 nov.

**24. ¿Habéis usado IA?**
Sí, como asistente de programación, que las bases permiten (§7), y nosotros respondemos de todo el código y los resultados. El producto no usa IA para calcular nada: todas las cifras salen de reglas deterministas, versionadas y con tests.
- Evidencia: `docs/09_datamad/24_bases_oficiales_2026.md` §7 · `CLAUDE.md` §3 (IA).

**25. ¿Qué pasa con la privacidad?**
Nunca tratamos datos de personas: solo agregados por zona. Además, no mostramos equipamientos que expondrían a personas vulnerables, quitamos teléfonos, emails y NIF que publicaba la fuente, y la base de la demo no se puede leer desde fuera de la API.
- Evidencia: D-186 · D-198 · D-197 · control `no_contact_or_tax_ids` en los `quality_report.json` de puntos.

**26. ¿De dónde sale «lo que falta» si no tenéis usuarios?**
Hoy, de datos oficiales: población, hogares y equipamientos, comparados con la referencia regional. El siguiente paso es sumar lo que la gente declare que necesita, anónimo y agregado por zona, y no lo simulamos en la demo.
- Evidencia: D-194 · `docs/09_datamad/25_plan_competicion.md` §8.

**27. ¿Por qué no usáis datos de los portales inmobiliarios?**
Porque no hacemos scraping: sus condiciones no lo permiten y las bases exigen respetar licencias. Además, enseñan la oferta, y lo que nosotros medimos es la necesidad.
- Evidencia: `CLAUDE.md` §15 · D-175 y D-185 (Google Maps y Gosom descartados) · bases §6.

**28. ¿Incluís seguridad? Es delicado.**
Solo si la persona la marca como prioridad y solo con datos oficiales agregados: actuaciones de la Policía Municipal por cada 1.000 habitantes y por distrito. Nunca nacionalidad ni etiquetas como «peligroso»; fuera de Madrid capital, SIN DATOS.
- Evidencia: D-204 y D-205.
- Estado: extra **pendiente de A** (DATA-020, 19–22 nov). Si no está, decir «no lo incluimos todavía, y así es como lo haríamos».

**29. ¿Funciona fuera de la Comunidad de Madrid?**
La arquitectura sí: añadir un dataset es añadir un YAML de pipeline, y la geografía se basa en códigos INE. Lo que haría falta en otra región es su portal de datos con equivalentes.
- Evidencia: `data/catalog/pipelines/` · `README.md` (Quickstart).

**30. ¿Es accesible para personas mayores?**
Está pensada para ellas: español llano, texto base de 17 px, botones de 44 px y contraste AA verificado también sobre el cristal. El estado de cada fila nunca depende solo del color: siempre va con texto e icono.
- Evidencia: `~/Desktop/DATAMAD/prompts/DISENO_VIDA_FACIL.md` · `apps/web/src/lib/__tests__/tokens.test.ts` (rama `claude/s1-web`, PR #2).
- Estado: verificación en navegador **pendiente de B**.

**31. ¿Por qué «Vida Fácil»?**
Porque es corto, en español y fácil de recordar para cualquiera, también para personas mayores. Comprobamos que no choca con ninguna marca del sector de la vivienda.
- Evidencia: D-199 · consulta de TMview (OEPM + EUIPO) del 11 nov en el PR #3.
