# Banco de preguntas del jurado — Vida Fácil

**Cómo usarlo:**
- 5 minutos de preguntas (bases §9).
- Cada respuesta tiene 3 frases como máximo: primero la respuesta, después el dato y por último el límite, si lo hay.
- La evidencia es para Mariano; no se lee en voz alta.
- Si algo no se sabe: «No lo sé con certeza; lo compruebo y os lo envío». Nunca se inventa una cifra.

**Perfiles:** salen de `docs/09_datamad/25_plan_competicion.md` §4. Lo que valora cada miembro del jurado es una inferencia a partir de su trayectoria pública.

> Las decisiones del 11 y el 12 nov están registradas como D-199 a D-224 (`docs/00_index/01_decisions_log.md`). El brief de diseño (`DISENO_VIDA_FACIL.md`, adoptado por D-201) sigue fuera del repo: se cita como documento interno, no como evidencia pública.

**Marcas:** «pendiente de A/B/C» = todavía no existe. Se revisa el 23 nov (freeze) y el 25 nov (ensayos).

**Las más probables** están al final y hay que prepararlas primero: de la 41 a la 45 (jurado simulado del 12 nov), la 46 y la 47 (cifras de impacto, 12 nov), la 48 (barrios, 13 nov), la 49 y la 50 (prueba con usuarios, 14 nov), de la 51 a la 53 (lo que cambió tras la prueba, 14 nov), de la 54 a la 59 (contexto de la zona, alquiler de los anuncios, coche y validación de la fórmula, 15 nov), la 60 (el siguiente paso: desde el 19 nov ya se puede buscar una parcela exacta de Madrid capital y calcular si una promoción sale; decir qué vivienda hace falta construir en ella, todavía no) y la 61 (¿por qué no van a una consultora?, de la prueba con un inversor del 19 nov).

---

## Alberto Abella · Gaia-X España (APIs, interoperabilidad, espacios de datos)

**1. ¿Cómo se integra esto con otros sistemas?**
Con una API pública versionada (`/api/v1`) cuyos contratos están publicados como JSON Schema y que se explica en una página pública, `/desarrolladores`, con un ejemplo que se puede copiar para cada ruta. Las zonas se identifican con el código INE del municipio, así que se cruzan con cualquier otra fuente oficial.
- Evidencia: `docs/04_technical_architecture/31_public_api_routes.md` · `data/schemas/api/*.schema.json` (16 esquemas el 19 nov, 6 de ellos de la versión para inversores) · `GET /api/v1/gaps/municipio/28092` · `/desarrolladores`, en producción desde el 19 nov (D-249; despliegue de `20b46d9` verificado por C: `evidence/gate-06/2026-11-19-deploy/deploy-38-20b46d9-desarrolladores.md`, PR #99): las 15 rutas de datos, cada una con un `curl` probado contra producción (D-249 §1; las 2 de la búsqueda por parcela, en el despliegue de `79020a1`: `evidence/gate-06/2026-11-19-deploy/deploy-39-79020a1-parcela.md`, PR #102).
- Si preguntan cuánto cuesta integrarla: nada. La API y el MCP son abiertos y gratuitos para todos, también para empresas y ayuntamientos, igual que los datos (decisión de Mariano del 19 nov, `pitch/modelo_negocio.md`). La API está en producción, sin claves, con 15 rutas de datos (5 de ellas, de la versión para inversores: 3 de D-248 y las 2 de la búsqueda por parcela, D-250) y su descripción OpenAPI en `/api/v1/openapi.json` (leída por D el 19 nov, tras el despliegue de `79020a1`).
- Límite, si preguntan por integrarla en su web: en producción, el navegador solo deja llamar a la API desde nuestro dominio (CORS, `cors_origins` en `apps/api/src/hi_api/settings.py`). Se integra desde un servidor o un agente, no desde el JavaScript de la web de un tercero. Comprobado por D el 19 nov: con otro origen, la respuesta no trae `Access-Control-Allow-Origin`.

**2. ¿Tenéis MCP para agentes de IA?**
Sí: un servidor MCP con siete herramientas de solo lectura (buscar zonas, qué falta, explicar una zona, encontrar una zona por su nombre, las fuentes de datos y, desde el 19 nov, dos de la versión para inversores). Llaman a los mismos servicios que la API, nunca a SQL libre, así que un agente no puede inventar ni cambiar datos, y los tests comprueban que cada herramienta responde lo mismo que su ruta de la API. Hoy funciona en local (`make mcp`), y cómo conectarlo está en `/desarrolladores`; servirlo en remoto está planteado.
- Evidencia: D-225 · D-249 §1 y §2 (`ficha_inversor` y `viabilidad`; la página, en producción desde el 19 nov, lo marca «Funciona en local», y el MCP en remoto, «Aún no disponible») · `services/mcp/` · `docs/04_technical_architecture/32_mcp_server.md` · `make mcp` · `CLAUDE.md` §3 (Arquitectura).
- Si preguntan si se cobra: no. El MCP y la API son abiertos y gratuitos para todos (decisión de Mariano del 19 nov, `pitch/modelo_negocio.md`). Hoy el MCP se arranca en local con el código abierto (Apache-2.0) y una base Postgres propia con los datos cargados (`32_mcp_server.md`, «Arrancarlo en local»).
- Si quieren verlo: un clip de 20 s con un agente preguntando «¿qué le falta a Parla?» (**pendiente de A**).

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
Pagarán los inversores y los promotores privados, con un plan de precios, y su versión ya está en la web: empieza, como las herramientas de pago, por la parcela exacta, en toda Madrid capital, calcula si una promoción sale y le pone al lado el contexto de demanda de su zona: quién vive, qué le falta y a qué precios. Para las personas y los ayuntamientos es gratis: un ayuntamiento ve qué le falta a su municipio frente a otros parecidos y a cuánta gente afecta, para decidir dónde invertir primero, sin contrato ni licitación. La API y el MCP también son gratis para todos, como los datos, y se explican en una página pública, `/desarrolladores`: de pago solo quedarán el plan para inversores y el estudio a medida.
- Evidencia: `pitch/modelo_negocio.md` (decisión de Mariano del 19 nov, que sustituye a la del 12 nov) · `CLAUDE.md` §16 (cliente inicial: promotoras e inmobiliarias medianas) · «Qué falta» en producción en 179 municipios y 21 distritos (`GET /api/v1/gaps?level=municipio` y `?level=distrito`, 19 nov) · la versión para inversores, «Para inversores y promotores», en producción desde el 19 nov: D-247 y D-248, despliegue de `396d8f6` y sync verificados por C (`evidence/gate-06/2026-11-19-deploy/deploy-37-396d8f6-inversores.md`, PR #96) · la búsqueda por parcela, «Busca tu parcela», en producción desde el 19 nov: D-250, despliegue de `79020a1` verificado por C (`evidence/gate-06/2026-11-19-deploy/deploy-39-79020a1-parcela.md`, PR #102) · «como las herramientas de pago»: Nestra también entra por referencia catastral, dirección o punto en el mapa (pregunta 60) · `/desarrolladores`, en producción desde el 19 nov (D-249; despliegue de `20b46d9`, PR #99): API y MCP «gratis para todos, también para empresas y ayuntamientos, igual que los datos».
- Si preguntan qué enseña la ficha de una parcela (D-250 §6 y D-252; leída por D en la API de producción el 19 nov y, tras el despliegue de D-252, el 20 nov):
  - los datos de la parcela, que elabora Vida Fácil a partir de los del Catastro: superficie, lo construido, su uso y «¿Está sin edificar?», según su uso en el Catastro. No dice «solar»: es una condición legal, con servicios (Ley 9/2001, art. 14.1.a), que ningún dato abierto da por parcela (D-252 §4);
  - el planeamiento del Ayuntamiento, con el enlace a su ficha oficial y el aviso «Información urbanística sin valor jurídico». Si la parcela está en un ámbito del Plan General, también su estado: las cuatro fases que publica el Ayuntamiento (planeamiento, gestión, proyecto de urbanización y obras de urbanización; conjunto 203200, D-252 §3);
  - la edificabilidad de partida, siempre editable y marcada «Dato» (VEDA del Ayuntamiento o el Portal del Suelo de la Comunidad), «Supuesto» (la norma zonal aplicada a la superficie) o «Sin dato». Desde D-252, también por uso: una línea por fuente con su uso, y lo que el plan publica por uso (residencial, terciario, dotacional…) para su parcela urbanística, sin repartir nunca una cifra. Una cifra oficial en un ámbito sin terminar, o de un uso que no es vivienda, queda como referencia, y la calculadora empieza en «Sin dato» (D-252 §1, §2 y §4);
  - el contexto de su barrio: quién vive, precios, qué falta y suelo;
  - la calculadora de viabilidad ya rellena (`viability-0.2`, D-252 §6). Solo con el precio del suelo da el semáforo, marcado como supuesto: «Sale» desde el margen objetivo (20 % de partida), «Ajustar» entre el 15 % y el objetivo, y «No sale» por debajo; la ficha cita la Orden ECO/805/2003, que fija un margen mínimo del 18 % para tasar vivienda de primera residencia. Sin precio del suelo, da lo máximo que se podría pagar por él. Tres escenarios: base, optimista (+10 % de precio y −5 % de coste) y pesimista (−10 % de precio y +15 % de coste). Con «Sin dato», la persona pone los m²;
  - el coste, el dato que más cambia la cuenta (D-252 §5 y §7): un PEM de partida de 968 €/m², marcado «Supuesto» (el punto medio del bloque abierto en Madrid, de 871 a 1.064 €/m², en los Costes de Referencia General de la Comunidad de Madrid, actualizados a 2022), y a la vista, como referencia baja, el de los visados de obra nueva de la Comunidad, 644 €/m² en 2025, marcado «Dato». «De dónde sale el coste y cuánto varía» da las tres referencias con lo que es cada una, y «Qué incluye el coste y qué no», lo que la cuenta deja fuera: la financiación, los impuestos de compra del suelo, la urbanización y el derribo;
  - «Guardar como PDF».
  - Se dice «datos de la parcela», nunca «información catastral»: la licencia del Catastro solo deja usar la información transformada (D-250 §1).
- Si preguntan dónde funciona: la búsqueda, en toda Madrid capital; un punto de fuera da «Ese punto está fuera de Madrid capital». El contexto completo del barrio y «Explorar barrios» son el piloto: los 108 barrios de Madrid capital dentro de la M-40, en 17 distritos (D-247 §1; `GET /api/v1/investors/zones`, 19 nov). Fuera del piloto, la ficha da las cifras del distrito o de la ciudad y lo avisa (D-250 §5). El resto de la región, todavía no.
- Si piden un ejemplo: las 4 parcelas de demostración, rehechas con las reglas de D-252 (§9). D-252 está en producción desde el 19 nov (despliegue de `f806850`, verificado por C: `evidence/gate-06/2026-11-19-deploy/deploy-41-f806850-coste.md`, PR #112), y D leyó estas fichas en la API de producción el 20 nov. Sin precio del suelo y con los supuestos de partida (margen del 20 %), la calculadora da lo máximo que se puede pagar por el suelo, redondeado a tres cifras:
  - Méndez Álvaro 47, en el barrio de Atocha: sin edificar, con 13.121 m² edificables oficiales de vivienda (VEDA), en el ámbito APR.02.06, ya terminado (sus cuatro fases, «Finalizado»), con el enlace a la ficha de su expediente. Por uso, el plan da a su parcela urbanística, la Manzana B, 60.231 m² residenciales y 21.300 m² terciarios: el total que permite, no lo que queda. Unos 61,2 millones de € en el escenario base (69,9 en el optimista y 50,8 en el pesimista; también en deploy-41);
  - Almería 1, en Fuente del Berro: suelo público en venta, que ofrece Metro de Madrid, sin urbanizar, en el ámbito APR.04.09, «Cocheras Metro Pte. de Ventas». Hoy tiene 6.573 m² construidos, de uso industrial: no está sin edificar. El ámbito no está terminado: sus cuatro fases salen «Sin iniciar» y, en VEDA, «pendiente de planeamiento de desarrollo» (Ayuntamiento, a 1 de julio de 2026; conjuntos 203200 y 203182). Por eso la edificabilidad de partida es «Sin dato» y los 32.697 m² de vivienda del Portal del Suelo 4.0 salen solo como referencia: la calculadora no da escenarios hasta que la persona pone los m². La ficha avisa además de que, si es suelo urbano no consolidado o urbanizable, la ley pide ceder gratis el suelo para el 10 % de la edificabilidad del ámbito y costear la urbanización (Ley 9/2001, arts. 18.2.c, 18.2.d y 21.1). No damos una cifra donde el planeamiento no está desarrollado. Hasta D-252 salían como «Dato», con una cifra para el suelo; lo corregimos tras la prueba con P7 (inversor) y una auditoría. Comprobada por C en producción tras el despliegue de `c4eaab1` (D-252b);
  - Mayor 61, en Palacio: un edificio en división horizontal, con 224 m² «supuestos» por la norma zonal 1 (68 m² × 5 × 0,66), que la persona puede cambiar. **Su cifra con D-252, pendiente de C** (D-252c): hasta entonces, no se da;
  - Luis Misson 2, en Berruguete: sin edificar y «Sin dato», porque la norma zonal 4 no tiene coeficiente; la persona pone los m².
  - La primera búsqueda de una parcela tarda unos 11 s, porque pregunta al Catastro y al Ayuntamiento; las siguientes, unos 0,3 s (deploy-39, punto 13). En la demo, mejor una de estas 4.
- Si preguntan en qué se diferencia de Nestra: pregunta 60.
- Si preguntan por qué no van a una consultora, o si las consultoras son la competencia: pregunta 61. Las consultoras y las inmobiliarias que les hacen el estudio a los promotores también son clientes: con la ficha hacen sus estudios más rápido, y para ellas es el plan Equipo (`pitch/modelo_negocio.md`, añadido el 19 nov tras la prueba con P7 (inversor)).
- Si piden precios (hipótesis por validar, `pitch/modelo_negocio.md`):
  - plan Inversor, unos 99–199 €/mes; Equipo, para una promotora, un fondo, una consultora o una inmobiliaria con varias personas, unos 399 €/mes;
  - estudio a medida, de 490 a 1.500 €;
  - de referencia, Nestra, que analiza la normativa de parcelas en España, cobra 175, 437,50 y 1.050 €/mes, sin IVA y con pago anual ([precios](https://www.nestra.es/precios), consultados el 19 nov);
  - antes de fijarlos, entrevistas de disposición a pagar (`docs/08_validation/09_pricing_validation.md`).
- Si insiste en que aún no cobráis: es verdad, y es a propósito. Durante el concurso, la versión para inversores es de acceso libre, sin cobro, sin cuentas y sin datos de nadie, y la web lo dice: «Plan Inversor (acceso libre durante el concurso)» (D-248 §1; leído por D en `/inversores` el 19 nov). El plan de precios es una hipótesis. Antes de cobrar faltan las cuentas y el cobro, un plan comercial de Vercel y las entrevistas de disposición a pagar (`pitch/modelo_negocio.md`, «Qué falta para cobrar»).
- Si preguntan qué pagarían, si ya está abierto: lo que solo usa quien invierte y aún no existe. Qué entra en cada plan es una hipótesis sin validar (`pitch/modelo_negocio.md`, «Planes y precios»).

**7. Si los datos son abiertos, ¿por qué pagaría alguien?**
Por el trabajo que hay encima: cruzar 39 conjuntos de la Comunidad, y 59 con los de apoyo, con formatos distintos, controlar su calidad, comparar cada zona con otras parecidas y explicarlo con su fuente. Hacer eso a mano para cada estudio cuesta semanas; aquí está hecho, se recarga con un comando y detecta qué fuente ha cambiado.
- Evidencia: `pitch/datasets_cm.md` · `evidence/gate-01/2026-11-10/summary.md` · `evidence/gate-01/2026-11-10/idempotent-rerun.txt`.

**8. ¿La licencia de los datos permite un uso comercial?**
Sí. Los datos del portal CM son CC BY y la licencia del CRTM permite reutilizarlos citando la fuente. En ambos casos cumplimos la atribución y no vendemos el dato en bruto, sino el análisis.
- Evidencia: licencias por dataset en `pitch/datasets_cm.md` · `data/catalog/sources/comunidad_madrid_ckan.yaml` y `crtm_open_data.yaml` (`commercial_use: true`, `attribution_text`).
- Si preguntan por las fuentes de la búsqueda por parcela (D-250 §1): el Ayuntamiento (planeamiento y VEDA), el Portal del Suelo de la Comunidad y CartoCiudad son CC BY 4.0. El Catastro deja usar, también con fines comerciales, solo la información transformada: la ficha da los datos de la parcela que elabora Vida Fácil a partir de los suyos, con la cita y la fecha de la consulta, y nunca los presenta como «información catastral» (`data/catalog/sources/catastro_ovc.yaml`).

**9. ¿En qué os diferenciáis de los portales inmobiliarios o de las consultoras?**
Los portales enseñan la oferta de pisos; nosotros enseñamos la necesidad y el encaje de cada zona. Frente a un estudio de consultora, aquí todo es abierto, reproducible y cita cada dato.
- Evidencia: `docs/09_datamad/25_plan_competicion.md` §8.
- Si preguntan por qué un promotor no iría directamente a una consultora: no es lo uno o lo otro. La ficha de la parcela es el primer filtro, antes de pagar un estudio completo, y las consultoras y las inmobiliarias también son clientes (pregunta 61).

**10. ¿Cuánto cuesta mantenerlo?**
Hoy, 0 € al mes: la web y la API van en el plan gratuito de Vercel y la base en el de Supabase, y los datos se recargan copiando tablas ya validadas. Para un uso comercial habría que pasar a planes de pago, porque el gratuito de Vercel no lo admite.
- Evidencia: `evidence/gate-06/2026-11-11/supabase-sync-demo.txt` (base de la demo: 100 MB de los 500 del plan gratuito) · D-188.
- Alojamiento: `infra/deploy/README.md` y `evidence/gate-06/2026-11-11-deploy/deploy-1-production.md` (plan Hobby: «solo personal y no comercial»).
- Si preguntan cuánto para cobrar: unos 45 $/mes como mínimo, con Vercel Pro (20 $) y Supabase Pro (desde 25 $). La base ocupa 100 MB de los 8 GB incluidos, así que lo que crece con el uso es el cómputo de la API (`pitch/modelo_negocio.md`, precios del 12 nov).

---

## Loren Escot · UCM, Estudios Estadísticos (rigor de los indicadores)

**11. ¿Cómo decidís que algo «falta»?**
Medimos lo que la gente de la zona tiene a 15 minutos andando, repartido entre todos los que lo comparten, y lo comparamos con los demás municipios de su tipo, rurales o urbanos. FALTA exige dos cosas: menos del 80 % de esa referencia (la regla de los cuatro quintos) y que la diferencia no se explique por el azar del tamaño de la zona; CUBIERTO es llegar al 100 %, y lo demás es JUSTO. Es una señal para priorizar, no un veredicto, y el método está declarado y versionado (`gap-0.3`).
- Evidencia: D-213 (puntos 1 y 2: 29 CFR 1607.4(D); intervalo exacto de Poisson de Garwood al 95 %, como en Fingertips y en los gráficos en embudo de Spiegelhalter, 2005) · D-217 (2SFCA: mismos cortes y misma prueba) · `packages/domain/src/hi_domain/gaps.py` · `apps/api/src/hi_api/services/gap_reference.py` · `evidence/gate-04/2026-11-12/gap-status-gap03.md`.
- Estado: hecho en la API y en producción (GAP-001 F5; DATA-AUDIT T2, `b88c4fb`). `GET /api/v1/gaps/distrito/2807913` da `gap-0.3` (comprobado el 12 nov).

**12. ¿Qué es eso de «al alcance a pie»? ¿Por qué no contáis centros sin más?**
Porque contar centros por habitante trata igual una clínica pequeña que un centro grande y no ve lo que hay al otro lado del límite de un distrito. Usamos el método 2SFCA (Luo y Wang, 2003): lo que ofrece cada centro se reparte entre todos los que viven a 15 minutos andando de él, cada calle suma lo que le toca de cada centro, y la zona es la media de sus calles según cuánta gente vive en cada una. Los 15 minutos a 4 km/h son los del estudio «El Madrid de los 15 minutos» del Ayuntamiento, y con 10 o 20 minutos el orden de los municipios casi no cambia (Spearman de 0,995 a 0,997).
- Evidencia: D-217 §1–2 · `packages/domain/src/hi_domain/access/fca.py` · `services/features/src/hi_features/fca.py` (`two_step_fca`) · test de propiedades de capacidad conservada · `evidence/gate-03/2026-11-12/fca-sensitivity.md`.
- Límite, si insiste: la captación es binaria, dentro o fuera, sin decaimiento con la distancia (E2SFCA, Luo y Qi 2009, es la mejora declarada), y la gente se coloca en las calles según su longitud, no por portal (D-217 §9).
- Estado: hecho y en producción desde el 12 nov (`gap-0.3`).

**13. ¿Por qué comparáis con municipios del mismo tipo y no con toda la región?**
Porque la oferta depende del tipo de territorio: a pie y por niño, los municipios rurales tienen más del doble de escuelas infantiles que los urbanos (unas 12 por cada 1.000 niños, frente a menos de 5). Con la media de la región a cualquier ciudad le faltaría de todo, y con el método anterior la diferencia entre rural y urbano ya era significativa en las 6 filas (χ², p < 0,05). Usamos la definición legal de medio rural de la Ley 45/2007 (menos de 30.000 habitantes y menos de 100 por km²), y ninguna zona se compara consigo misma: Madrid es la mitad de la población urbana.
- Evidencia: referencias de `gap-0.3` en `GET /api/v1/gaps?level=municipio&row=escuela_infantil`. Cada zona deja fuera su municipio, así que la rural va de 12,13 a 12,86 y la urbana de 4,531 a 4,87 (`evidence/map-004/2026-11-12/cifras/cifras_api.json`, PR #18): «más del doble» vale para todas · D-213 (punto 1 y tabla χ²: de p = 0,039 en farmacias a p < 10⁻³⁰⁰ en vivienda; 84 municipios rurales y 95 urbanos) · `evidence/gate-04/2026-11-11/phase-gap001-f5-review.txt`.
- Límite, si insiste: el tipo se asigna por municipio, la superficie es la de la geometría de 2019 y el modelo de Poisson no trata la sobredispersión (D-213, punto 5).
- Estado: hecho (GAP-001 F5; D-217 mantiene la referencia).

**14. ¿Qué pasa con los municipios pequeños, donde una ratio se dispara?**
Si en un municipio se esperan menos de 3,69 casos, el límite superior al 95 % de un recuento de cero, lo comparamos junto con sus vecinos más cercanos del mismo tipo, a 15 km o menos, hasta que el grupo llega a ese mínimo; la fila lo dice y nombra a los vecinos. Si ni así se llega, sale «zona pequeña para comparar» y nunca FALTA: La Acebeda, con 70 habitantes y sin farmacia a pie, sale JUSTO con esa marca. Con los vecinos, los municipios que no se podían comparar en colegios bajan de 140 a 65, y por debajo de un umbral de población el dato se publica con confianza 0,5.
- Evidencia: D-213 (punto 3, `reliable: false`) · D-217 §6–7 (filtros espaciales adaptativos, Talbot et al., 2000; radio de 15 km, del orden de las zonas básicas de salud rurales) · `comparison_group` en la API · `small_population_threshold` en los YAML de las filas · `null_policy`.
- Estado: hecho en la API y en producción (12 nov): La Acebeda, farmacia, JUSTO con `reliable: false` y sin grupo; Redueña, farmacia, CUBIERTO junto con 6 vecinos (ratio del grupo 1,51) (`GET /api/v1/gaps?level=municipio&row=farmacia`). En la web: «Junto con sus vecinos» y «Comparado con municipios parecidos de la zona» (PR #13 de B).

**15. Puente de Vallecas y Centro tienen cifras parecidas en escuelas infantiles. ¿Por qué uno sale FALTA y el otro no?**
Porque FALTA pide además que la diferencia no pueda ser casualidad. Puente de Vallecas tiene 0,57 de la referencia y tantos niños que la diferencia es clara; Centro tiene 0,66, pero con menos niños podría ser azar, así que sale JUSTO. Preferimos no marcar una falta que no podemos sostener.
- Evidencia: `GET /api/v1/gaps?level=distrito&row=escuela_infantil` (producción, 12 nov: Puente de Vallecas 2,781 frente a 4,87, FALTA; Centro 3,218, ratio 0,6608, JUSTO; los dos con `reliable: true`) · D-213 punto 2.
- Si preguntan por otros: Villaverde (0,61) y Carabanchel (0,68) también salen FALTA; Vicálvaro (0,65), JUSTO.

**16. ¿Contáis centros o plazas?**
La capacidad que se publica: aulas de primaria en colegios y plazas autorizadas en hogares, clubes y centros de día de mayores. Las aulas se publican por municipio, no por colegio, así que las repartimos a partes iguales y el dato baja a «aproximado»; de escuelas infantiles, centros de salud y farmacias nadie publica plazas ni médicos, y cada uno cuenta como uno. Cada fila lo declara, y nunca estimamos una capacidad centro a centro.
- Evidencia: D-217 §3–4 (tabla de capacidad; población asignada por centro de salud y cupos médicos no existen en abierto) · `proxy_note` en `data/catalog/features/*.yaml` y en cada fila de la API · `confidence: 0.8` en `aulas_primaria_a_pie_por_1000_ninos.yaml`.

**17. Madrid capital tiene 3 millones de habitantes. ¿No esconde la media todo?**
Sí, por eso Madrid se divide en sus 21 distritos, y lo que se tiene a pie se calcula calle a calle, mucho más fino que el municipio. Así sale, por ejemplo, que en Puente de Vallecas faltan escuelas infantiles aunque Madrid entera no sale FALTA en ninguna fila de servicios. Y lo que hay al otro lado del límite de un distrito también cuenta, porque se mide andando.
- Evidencia: D-200 · D-209 · D-210 · D-217 §2 y §7 · `evidence/gate-04/2026-11-12/gap-status-gap03.md` (Madrid, escuela infantil, JUSTO, 0,87) · `GET /api/v1/gaps/distrito/2807913` (producción, 12 nov).
- Si preguntan por la frase de antes («Madrid tiene un tercio menos de centros de atención primaria»): era con el método de contar centros por habitante. Midiendo lo que se alcanza a pie, Madrid sale JUSTO en centros de salud (0,95), cerca de los demás municipios urbanos (D-217 §7).
- Y si buscas solo en Madrid capital, el buscador compara sus 131 barrios (D-238; pregunta 52).
- Estado: hecho. Distritos con el padrón municipal (D-209); distancia a pie a 4 km/h (CORE-005, D-211); 2SFCA en la API y en la web desde el 12 nov; barrios en el buscador desde el 14 nov.

**18. ¿Cómo calculáis el % de encaje?**
Primero, las condiciones: cada una sale cumple, no cumple o «sin dato», y «sin dato» nunca cuenta como cumple; solo encajan las zonas que lo cumplen todo. Después, cada cosa que la persona marca puntúa de 0 a 1 y pesa más lo que marca primero (con 5, 33, 27, 20, 13 y 7 %): cada minuto a pie cuenta, un servicio combina lo cerca que está (60 %) y si hay plazas para tanta gente (40 %, la misma cifra de «Qué falta»), y el presupuesto vale 1 hasta el 75 % y 0,6 en el límite. Tres topes evitan que el % contradiga a la tarjeta (89 % si falta lo marcado, 74 % con más de 1 h de trayecto y la mitad si no se llega), el % va con su banda en palabras, en cuatro niveles y el método va versionado (`fit-0.9` en producción).
- Evidencia: D-215 (puntos 2 a 6) · D-243 (la fórmula «cerca y plazas») · `packages/domain/src/hi_domain/fit.py` · `CLAUDE.md` §14 · `pitch/metodologia.md` §1.3 · `pitch/banco_formula.md` (cómo se eligió).
- Límite, si insiste: no hay todavía diversificación ni soluciones Pareto (D-215, punto 10). El orden es el del % que se ve; a igual %, va primero la que tiene más cerca los servicios del día a día (D-243; pregunta 51).
- Estado: en producción desde el 15 nov (`fit-0.9`, despliegue de `025a4a2`). Con el caso de la Castellana, `POST /api/v1/search` da 42 de 199 zonas, con Puente de Vallecas y Latina empatadas arriba al 94 % (comprobado por D el 15 nov). Con `fit-0.6` (12 nov) eran 27, con Latina 1.ª al 98 %.

**19. El alquiler solo está publicado para municipios grandes. ¿Qué hacéis en el resto?**
Así es: la Comunidad publica el alquiler de 37 municipios, los de más de 20.000 habitantes con contratos suficientes, y el de los códigos postales de Madrid capital. En el resto usamos la referencia de precios de alquiler del Ministerio de Vivienda, la mediana de cada municipio llevada al nivel de la cifra de la Comunidad y a los contratos firmados en 2024: la marcamos como dato aproximado, o poco seguro si detrás hay menos de 30 contratos, damos el rango en el que está la mitad de los contratos y, en los 16 pueblos donde casi no se alquila, decimos que no hay dato y nunca lo damos por bueno. En los distritos de Madrid hacemos la media de sus códigos postales, ponderada por dónde están los colegios, centros de salud y centros sociales, y lo declaramos como aproximación: sale 14,5 €/m², y la Comunidad publica 15,1 para todo Madrid.
- Evidencia: D-214 (puntos 3 y 4) · D-242 (SERPAVI, base de datos 2011-2024 del Ministerio de Vivienda; 126 municipios y Sol rellenos) · `data/catalog/features/alquiler_m2_mensual.yaml` v2 · `evidence/gate-04/2026-11-11/phase-core006-f1.txt` (14,46 frente a 15,10) · `CLAUDE.md` §14 (UNKNOWN nunca equivale a PASS) · producción, 15 nov: con «Pueblos», 122 de 138 cumplen y 16 salen sin dato; Casarrubuelos, «Alquiler ≈ 571 €/mes» y «La mitad de los contratos, entre 500 y 790 €/mes» (`evidence/gate-06/2026-11-15-deploy/deploy-31-59187f8-lote4.md`).
- Si insiste en la licencia del Ministerio: su aviso legal autoriza la reutilización «para usos comerciales y no comerciales» si no se desnaturaliza la información, se cita la fuente y la fecha de la última actualización y no se sugiere que el Ministerio respalda el uso. La web cumple las tres cosas: la cita lleva su fecha, y el pie dice que Vida Fácil no es un servicio del Ministerio de Vivienda. Leído en https://www.mivau.gob.es/ministerio/aviso-legal el 15 nov.
- Estado: en producción desde el 15 nov.

**20. Vuestro alquiler estimado parece bajo. ¿Es real?**
Es una estimación y lo decimos en cada resultado: el precio por metro de la Comunidad, corregido con lo que cuestan de más los contratos firmados en 2024 según la Agencia Tributaria, por los metros del hogar. Sigue sin ser el precio de un anuncio, y los m² son construidos, del Catastro, así que el piso real es algo menor que el que suponemos (77 m² para 4 personas, la vivienda mediana de ese hogar en el Censo 2021). Por eso la tarjeta dice «un anuncio de hoy puede pedir más».
- Evidencia: D-214 (puntos 2 y 3) · D-228 (contratos nuevos) · pregunta 41 · ficha del portal CM (https://datos.comunidad.madrid/dataset/1934259, campo «Fuente»: «Estadística de Viviendas Declaradas en el Impuesto sobre la Renta de las Personas Físicas. Agencia Estatal de Administración Tributaria») · INE, tabla 59524 (https://www.ine.es/jaxi/Tabla.htm?tpx=59524&L=0) · `limitations` de `alquiler_m2_mensual.yaml`.
- Si preguntan por qué no usamos anuncios: no hay una fuente oficial y abierta de precios de oferta, y no hacemos scraping (pregunta 35).

**21. ¿Tenéis en cuenta lo que se tarda en llegar al trabajo?**
Sí: los minutos de puerta a puerta en transporte público para llegar a las 9:00, con los horarios publicados de las seis redes del Consorcio, desde cada sección censal hasta las 379 estaciones y el centro de cada zona. En el caso de ejemplo, Fuencarral-El Pardo queda a 29 minutos de la Castellana y Ciudad Lineal a 33. Son horarios programados de un día laborable, no tiempos reales, y donde el horario publicado tiene huecos lo decimos.
- Evidencia: D-220 · `packages/domain/src/hi_domain/access/transit.py` · `services/features/src/hi_features/commute.py` · `evidence/gate-03/2026-11-12/commute-matrix.md` · `evidence/gate-04/2026-11-12/golden-search-commute.txt`.
- Desde el 14 nov se puede poner un límite: «Tardar como mucho N min en transporte público» (30, 45, 60 o 90 min). Entonces es una condición: la zona cumple, no cumple o no lo sabemos. Con el caso de ejemplo y 45 min salen 10 zonas. La ayuda dice qué transporte cuenta: metro, autobús (EMT e interurbanos), Cercanías y Metro Ligero. Lo pidieron en la prueba con usuarios («me salían sitios muy lejos»). Evidencia: PR #53 · `trabajo.max_min` y `trabajo.ayuda` en `pitch/textos_web.md` · `evidence/gate-06/2026-11-14-deploy/deploy-27-ad4a8f2-d233.md` (e2e: «45 min» llega a `/search` y da 10 zonas, igual que la API).
- Límite, si insiste: el GTFS interurbano no trae expediciones de las líneas 720 a 726, y desde 45–50 zonas (Sierra Norte, sureste) no se llega al centro a las 9:00; ahí no hay dato, nunca 0. El paseo hasta la parada va en línea recta con un 30 % de rodeo (D-220 §3 y §6).
- Estado: hecho y en producción desde el 12 nov (despliegue de `28a0f2f`, `evidence/gate-06/2026-11-12-deploy/deploy-17-pub001.md`): el caso de ejemplo da «29 min en transporte público hasta Paseo de la Castellana (Azca), llegando a las 9:00» en Fuencarral-El Pardo.

**22. ¿Cómo medís «a 10 minutos andando»? ¿A qué velocidad?**
Por las calles de verdad, no en línea recta, a 4 km/h: el mismo paso que el estudio «El Madrid de los 15 minutos» del Ayuntamiento. En cada fila damos lo que tarda la mitad de la zona; si una zona no tiene calles en el mapa, sale «sin datos», nunca cero. Lo comprobamos con 15 casos de lugares conocidos: por ejemplo, La Acebeda no tiene farmacia y la más cercana queda a más de hora y media andando.
- Evidencia: D-210 · D-211 · `data/catalog/features/min_a_pie_*.yaml` y `pct_calle_*.yaml` · `scripts/check_walk_golden.py` y `evidence/gate-03/2026-11-11/phase-core005-f5.txt` (La Acebeda: farmacia a 109,7 min, D-211) · estudio del Ayuntamiento: https://geoportal.madrid.es/fsdescargas/IDEAM_WBGEOPORTAL/GEOPORTAL/Jornada/2022/SALA5_1130_PROXIMIDAD_POR_CALCULODEREDES.pdf («Velocidad de desplazamiento estimada en 4 Km/h»).
- Estado: hecho a 4 km/h, decisión de Mariano del 11 nov (CORE-005 Fase 5, `ad2129a`, D-211, Gate 3 PASS). En la API, con GAP-001 F1 (`2d05d78`), y en producción. Por ejemplo, Puente de Vallecas: la escuela infantil más cercana, a 6 min desde la mitad de sus calles (`min_a_pie_escuela_infantil` = 6,258, `GET /api/v1/gaps/distrito/2807913`, 12 nov). El % de calle a 10 minutos también está calculado (`pct_calle_*.yaml`), pero no se enseña.

---

## Ricardo Curto · Universidad de Oviedo (calidad, licencias y cita de fuentes)

**23. ¿Qué datasets del portal usáis exactamente y con qué licencia?**
39 datasets con ficha en el Portal de Datos Abiertos de la Comunidad de Madrid, cada uno con su enlace, licencia, qué alimenta y su informe de calidad, y 20 más de apoyo que no contamos como datos de la Comunidad. La lista se genera desde el catálogo, no se escribe a mano.
- Evidencia: `pitch/datasets_cm.md` (regenerado el 19 nov) · `pitch/build_datasets_cm.py` · `GET /api/v1/datasets?cm_only=true` en producción: 39, y 59 en total (comprobado por D el 19 nov, tras el despliegue de `396d8f6`). Eran 27 la noche del 12 nov, cuando se envió el formulario con 26; 29 con D-235, 35 con D-237 y D-241, 36 con D-246 (el Portal del Suelo 4.0, 18 nov) y 39 con D-247 y D-248 (el Catastro por uso, por municipio y por distrito, y los visados de obra, 19 nov).
- Si insiste en cuáles se ven: todos se ven en la web. 10 son contexto de la zona y no puntúan: las infracciones penales, la antigüedad de las viviendas, la renta, las 3 fichas del aire, los aparcamientos de disuasión, las compraventas de vivienda nueva, el valor tasado por antigüedad y el suelo público para vivienda (D-235, D-237, D-241 y D-246). 3 son de la versión para inversores, también sin puntuar: los 2 del Catastro por uso (D-247) y los visados de obra (D-248). La búsqueda por parcela (D-250, 19 nov) no suma ninguno: pregunta en vivo al Catastro, al Ayuntamiento y a CartoCiudad (las 2 capas de urbanismo del Ayuntamiento están en el catálogo, sin cargar: `pitch/datasets_cm.md`, sección 4) y toma la edificabilidad de VEDA y del Portal del Suelo, que ya está entre los 39. Los 2 de camas dan el total de la región bajo la nota del hospital (D-231). El resto alimenta el buscador o «Qué falta», o da la geografía y la población de base; entre ellos, los 3 de accesibilidad de las estaciones, que se usan con «Sin escaleras» (D-223).

**24. Los GTFS son del Consorcio. ¿Por qué los contáis como datos de la Comunidad?**
Porque el propio portal de la Comunidad los publica con su ficha y su licencia. Aun así, los separamos en la lista y damos también la descarga original del CRTM, para que se vea claro.
- Evidencia: D-196 · `pitch/datasets_cm.md` §2 (6 fichas con licencia «CRTM Licencia de datos abiertos (LDA)» en el portal CM).

**25. ¿Por qué usáis datos del Ministerio de Sanidad si el concurso es de datos de la Comunidad?**
Porque el portal de la Comunidad solo publica las camas de toda la región (85 hospitales y 20.776 camas instaladas en 2023), no las de cada hospital. El Catálogo Nacional de Hospitales sí las da y permite reutilizarlas citando la fuente y la fecha; lo usamos solo para poner nombre y camas a los hospitales del registro de la Comunidad, que sigue siendo la fuente de cada lugar, su tipo y su ubicación. Cruzamos 80 de los 85, 79 por su dirección postal y el Ramón y Cajal a mano con la web oficial del hospital, sin ningún desacuerdo entre público y privado.
- Evidencia: D-217 §4 · D-218 §1–4 · `evidence/gate-01/2026-11-12/hospitales-cnh.md` · `pitch/datasets_cm.md` §3 (licencia: aviso legal del Ministerio, Ley 37/2007).
- Límite, si preguntan por un hospital sin nombre: 5 de los 85 no se cruzan y salen como «Hospital general (Municipio)», sin camas. El Ramón y Cajal era uno: el catálogo lo pone en la calle de Ayala y no en la carretera de Colmenar. Lo emparejamos a mano con la web oficial del hospital, y el fichero de correcciones guarda la fuente de cada cambio. Hoy sale con sus 886 camas (D-218 §10; `data/catalog/corrections/places.yaml`; en producción, 12 nov).

**26. ¿Las camas cuentan para decir qué falta?**
No. A un hospital no se va andando a elegir, y medir las camas alcanzables exigiría el viaje en coche o en transporte público, que aún no calculamos. Lo que sí damos es el nombre y las camas de cada hospital, por ejemplo La Paz, con 966 camas instaladas, en Fuencarral-El Pardo, y en la fila de centros de salud los minutos a pie hasta el hospital general más cercano, como pista de dónde quedan las urgencias.
- Evidencia: D-217 §5 (`min_a_pie_hospital`; ninguna fuente abierta marca las urgencias 24 h) · D-218 §6–7 · producción, 12 nov: `GET /api/v1/places?category=health&admin_unit_id=ES.28.DIS.2807908&subcategory=Hospital general` («Hospital Universitario La Paz», `capacity` 966 «camas instaladas», `dependency: publica`; en el mismo distrito, «Hospital Universitario Ramon y Cajal», 886, y «Clínica Cemtro», 100).
- Estado: hecho en la API y en la web («Todos los centros» de cada zona; comprobado a mano por C en producción, PR #15). Las camas son las instaladas a 31 de diciembre de 2024, no las que funcionan un día concreto. Desde el 14 nov, cada hospital dice también si es público o privado (pregunta 53).

**27. ¿Qué control de calidad pasa un dataset antes de entrar?**
Claves únicas, que cada municipio exista en la geografía oficial, errores de lectura, ratio de registros en cuarentena y faltantes marcados como faltantes, no como cero. Los registros dudosos van a cuarentena, no se borran, y cada versión guarda la huella del fichero original.
- Evidencia: `evidence/gate-01/*/<dataset>/quality_report.json` · `lineage.json` (sha256 y URL) · `row_counts.json` (`quarantined`).

**28. ¿Encontrasteis errores en los datos del portal?**
Sí, y los tratamos sin ocultarlos. Comparamos 10 zonas a mano con la fuente oficial y encontramos centros sin coordenadas o en el municipio equivocado: 40 se han colocado con el geocodificador oficial del IGN, solo si la dirección cuadra, y los que no van a cuarentena, nunca al sitio equivocado. También sacamos del mapa 1.001 «centros polivalentes», casi todos clínicas privadas, que no son atención primaria ni servicios para mayores.
- Evidencia: `pitch/revision_10_zonas.md` (D1–D7) · D-216 §1 y §3 · D-218 §10 · `evidence/gate-01/2026-11-12/audit-places.md` · `evidence/gate-01/2026-11-12/correcciones.md` · `evidence/gate-01/2026-11-12/cm_centros_educativos/row_counts.json` (40 en cuarentena) · `notes` de `data/catalog/datasets/cm_secciones_censales.yaml` (geometría inválida reparada).
- Límite: los 4 centros de salud «S/N» de Madrid y Alcalá ya están colocados con el número de portal del catálogo del Ministerio (D-218 §10). Quedan sin poder colocar 3, porque ninguna fuente oficial da su ubicación: el consultorio de Villar del Olmo, el de Buitrago y el colegio de Navalafuente. Hoy cuentan como si no estuvieran, y A propone enseñar SIN DATOS.

**29. ¿Los datos están al día?**
Cada fuente se recarga según su propia frecuencia de publicación, y en los GTFS el control de calidad avisa si el horario está caducado. Por ejemplo, el GTFS de metro venció el 27 de mayo de 2026 y sigue siendo el último publicado: lo usamos y el control de calidad lo marca.
- Evidencia: control `feed_current` en `evidence/gate-01/2026-11-10/crtm_gtfs_metro/quality_report.json` · D-196.

**30. ¿Cómo citáis las fuentes en la propia aplicación?**
Cada fila de la lista y cada resultado llevan los datasets de los que salen, con el enlace a su ficha, la versión y la licencia. Además, la web muestra la atribución que pide cada licencia, incluido «Powered by CRTM».
- Evidencia: campo `datasets` de la API (`data/fixtures/contracts/zone_gap_list.mostoles.fixture.json`) · `attribution_text` en `data/catalog/sources/*.yaml`.
- Estado: hecho en producción: pie con Comunidad de Madrid, Ayuntamiento, «Powered by CRTM» y OpenStreetMap (`evidence/map-004/2026-11-11/prod_c4_madrid_que_falta_desktop.png`).

---

## Generales (cualquier miembro)

**31. ¿Qué hicisteis durante la competición y qué ya existía?**
El trabajo previo está identificado con el tag `pre-datamad` (22 oct): la geografía, los 10 primeros datasets y el mapa base. Desde el 7 nov hemos añadido el transporte del CRTM, 7 datasets más de la Comunidad, la lista de lo que falta con sus 6 filas, la red peatonal, la capacidad a pie, la web, el buscador y el despliegue.
- Evidencia: `README.md` («Trabajo previo a DATAMAD») · tag `pre-datamad` = `cf39459` · D-174 · `board/BOARD.md` (07 — DONE).
- Estado: hecho. La lista, la web y el buscador están en producción; el buscador, desde el 11 nov (`evidence/gate-06/2026-11-11-deploy/deploy-12-buscador.md`, PR #11).

**32. ¿Habéis usado IA?**
Sí, como asistente de programación, que las bases permiten (§7), y nosotros respondemos de todo el código y los resultados. El producto no usa IA para calcular nada: todas las cifras salen de reglas deterministas, versionadas y con tests.
- Evidencia: `docs/09_datamad/24_bases_oficiales_2026.md` §7 · `CLAUDE.md` §3 (IA).

**33. ¿Qué pasa con la privacidad?**
Nunca tratamos datos de personas: solo agregados por zona. Además, no mostramos equipamientos que expondrían a personas vulnerables, quitamos teléfonos, emails y NIF que publicaba la fuente, y la base de la demo no se puede leer desde fuera de la API.
- Evidencia: D-186 · D-198 · D-197 · control `no_contact_or_tax_ids` en los `quality_report.json` de puntos.

**34. ¿De dónde sale «lo que falta» si no tenéis usuarios?**
Hoy, de datos oficiales: población, hogares y equipamientos, comparados con los demás municipios del mismo tipo. El siguiente paso es sumar lo que la gente declare que necesita, anónimo y agregado por zona, y no lo simulamos en la demo.
- Evidencia: D-194 · `docs/09_datamad/25_plan_competicion.md` §8.

**35. ¿Por qué no usáis datos de los portales inmobiliarios?**
Porque no hacemos scraping: sus condiciones no lo permiten y las bases exigen respetar licencias. Además, enseñan la oferta, y lo que nosotros medimos es la necesidad.
- Evidencia: `CLAUDE.md` §15 · D-175 y D-185 (Google Maps y Gosom descartados) · bases §6.

**36. ¿Incluís seguridad? Es delicado.**
No la puntuamos, y es una decisión. El dato oficial que evaluamos, los hechos conocidos de infracciones penales por cada 1.000 habitantes, cuenta dónde se denuncia o dónde actúa la policía, no dónde se vive: en 2024, Humanes de Madrid daba 116,2 y Madrid 58,6, frente a 47,9 de referencia, y ordenar zonas así señalaría municipios por la actividad que reciben. Además, solo cubre 36 de las 199 zonas y ninguno de los distritos de Madrid.
- Evidencia: D-224 · D-226 · `evidence/gate-01/2026-11-12/seguridad-evaluacion.md` y `seguridad-fuentes.md` · D-204 y D-205 (nunca nacionalidad ni etiquetas como «peligroso»).
- Si insiste: en los 21 distritos de Madrid sí damos contexto, que no puntúa ni ordena. Es cómo valoran los vecinos la seguridad de su barrio, de 0 a 10, según la Encuesta de calidad de vida de 2025 del Ayuntamiento, con unas 400 personas por distrito; la media de Madrid es 6,4 de noche y 7,8 de día (D-226 §1). En la web se ve en dos barras: por ejemplo, Villaverde da 4,9 de noche y 6,8 de día. Las actuaciones de la Policía Municipal miden la actividad policial, no el riesgo de vivir allí. Los atropellos, sin saber cuánta gente camina por cada calle, señalan los barrios con más vida. Ninguno de los dos puntúa (D-226 §2–3). Y desde la noche del 14 nov la vista de cada zona enseña, solo como contexto, las infracciones penales conocidas por 1.000 habitantes, sin los delitos por internet y con el aviso «sube donde hay mucha gente de paso»; en los distritos, la cifra de toda la ciudad (D-235; pregunta 54).
- Estado: decidido (D-224, D-226 y D-235). La prioridad «Seguridad» no puntúa. La percepción vecinal está en la vista de zona de los distritos de Madrid, y las infracciones penales, como contexto en todas las zonas (en producción).

**37. ¿Sirve para alguien que no puede subir escaleras?**
Sí, si lo marca: «Sin escaleras» puntúa los minutos andando hasta la estación de metro, Metro Ligero o Cercanías que el Consorcio da como totalmente accesible, y nunca se deduce ni se etiqueta a nadie. Es una aproximación declarada: no mide autobuses, aceras, portales ni ascensores, y la tarjeta lo dice cuando no hay ninguna estación así a un paseo. En Madrid capital va de 6,8 minutos en Chamberí a 25,5 en Usera.
- Evidencia: D-223 · `evidence/gate-01/2026-11-12/estaciones-accesibles.md` · las 3 topologías del CRTM en el portal CM (`pitch/datasets_cm.md`, 24 a 26) · `evidence/gate-04/2026-11-12/golden-search-sin-escaleras.txt`.
- Si insiste en el grado: el CRTM no publica qué significa cada grado. Leemos T como accesibilidad total porque las 57 estaciones de Metro Ligero son T y la Comunidad dice que toda esa red es accesible; P y N no cuentan (D-223 §3). El `wheelchair_boarding` del GTFS no se usa porque no sigue el estándar (D-223 §4).
- Estado: hecho y en producción desde el 12 nov (`fit-0.4`, despliegue de `2761696`: `evidence/gate-06/2026-11-12-deploy/deploy-18-pub002.md`).

**38. ¿Funciona fuera de la Comunidad de Madrid?**
La arquitectura sí: añadir un dataset es añadir un YAML de pipeline, y la geografía se basa en códigos INE. Lo que haría falta en otra región es su portal de datos con equivalentes.
- Evidencia: `data/catalog/pipelines/` · `README.md` (Quickstart).

**39. ¿Es accesible para personas mayores?**
Está pensada para ellas: español llano, texto base de 17 px, botones de 44 px y contraste AA verificado también sobre el cristal. El estado de cada fila nunca depende solo del color: siempre va con texto e icono.
- Evidencia: `DISENO_VIDA_FACIL.md` · `apps/web/src/lib/__tests__/tokens.test.ts` · axe WCAG 2.2 AA en producción sin fallos (`prod-buscador-check.json`, PR #11).
- Estado: hecho. axe AA da 0 fallos en producción (11 nov): en escritorio, en la portada, los resultados, la tarjeta de zona y la compra; en el móvil, en los resultados y la tarjeta.

**40. ¿Por qué «Vida Fácil»?**
Porque es corto, en español y fácil de recordar para cualquiera, también para personas mayores. Comprobamos que no choca con ninguna marca del sector de la vivienda.
- Evidencia: D-199 · consulta de TMview (OEPM + EUIPO) del 11 nov en el PR #3.

---

## Las cinco preguntas difíciles (jurado simulado del 12 nov)

**41. Sale 1.107 € al mes por 77 m² en Fuencarral-El Pardo, y Salamanca entra con 1.500 €. ¿Eso es real?**
Era la media de todos los contratos declarados a Hacienda, también los antiguos, y se quedaba corta. Ahora multiplicamos el precio por metro de la Comunidad por cuánto más cuestan, en cada zona, los contratos firmados en 2024 según la Agencia Tributaria. Fuencarral-El Pardo pasa a unos 1.276 € y Salamanca a unos 1.797 €, así que con 1.500 € ya no entra, y el caso de ejemplo bajó de 33 a 27 zonas (desde el 15 nov son 42, porque los pueblos tienen el alquiler del Ministerio, pregunta 19).
- Evidencia: D-214 (puntos 2 y 3) · D-228, opción A, que eligió Mariano el 12 nov · producción, 12 nov (`fit-0.6`): Fuencarral-El Pardo «Alquiler ≈ 1.276 €/mes por 77 m² (16,6 €/m², contratos firmados en 2024; un anuncio de hoy puede pedir más)» y Salamanca ≈ 1.797 €/mes (23,3 €/m²), que no cumple el presupuesto · Agencia Tributaria, «Estadística de viviendas declaradas en IRPF», ejercicio 2024, «contratos de arrendamiento formalizados en el ejercicio» · `evidence/gate-01/2026-11-12/alquiler-contratos-nuevos/`. Factor por zona: entre 1,05 y 1,26 (Madrid, 1,20).
- Si preguntan por comprar: en los municipios, el precio es el valor tasado medio de la vivienda libre que publica la Comunidad (D-227); en los distritos y barrios de Madrid, una estimación: el valor tasado de toda la ciudad repartido según el valor catastral de cada zona (D-234). No es el de un anuncio. Con el caso de ejemplo y 300.000 € para comprar, encajan 20 de 199 zonas y 15 salen sin dato: la 1.ª es Puente de Vallecas, al 94 % y con «Comprar ≈ 229.000 € por 77 m²», un precio estimado (producción, 15 nov, `fit-0.9`, comprobado por D).
- Si preguntan por el índice de la Comunidad (1934428): solo dice cuánto varían los precios, no cuánto más cuesta un contrato nuevo, y es un único valor para toda la región (D-228 §2).
- Estado: en producción desde el 12 nov (`fit-0.6`). Con 150 € más al mes, el caso de ejemplo gana 3 zonas («¿Queréis ver más zonas?»), así que el presupuesto ya cuenta.

**42. Latina sale al 94 % de encaje, pero en «Qué falta» va justa en escuelas infantiles y centros de salud. ¿Cómo puede ser?**
Porque desde el 15 nov el % usa la misma cifra que «Qué falta», pero solo para lo que la persona marca. Esta familia marca colegios, transporte y salud: el centro de salud de Latina va justo de plazas (99 de cada 100 que hay en zonas parecidas) y le quita menos de un punto, y la escuela infantil no la marca, así que no cuenta. Si una zona tiene FALTA en algo marcado, no pasa del 89 %: Puente de Vallecas, con FALTA en escuelas infantiles, se queda en el 89 % si la familia marca la escuela infantil.
- Evidencia: D-243 §2 y §9 (desglose de Latina: −3 por el trayecto, −1,1 por el colegio, −1,1 por la parada y −0,9 por el centro de salud) · producción, 15 nov, comprobado por D: `POST /api/v1/search` con el caso de ejemplo (Latina 94 %) y con la escuela infantil marcada a 10 min (Puente de Vallecas 89 %, «Faltan escuelas infantiles: como mucho 89 %») · `GET /api/v1/gaps/distrito/2807910` (12 nov: Latina, escuela infantil 0,95 y centro de salud 0,99, JUSTO).
- Si insiste en por qué antes salía al 98 % con JUSTO: con `fit-0.6` el % solo miraba los minutos, y por eso se cambió la fórmula (D-243 §1).

**43. ¿Quién lo ha usado?**
Siete personas, del 13 al 15 nov: seis de 26 a 55 años y una persona mayor, y lo que más pidieron ya está en la web: buscar solo en una parte de la región, con Madrid capital por barrios (lo pidieron 4 de las 6), un límite de tiempo hasta el trabajo, las paradas de autobús aparte y saber si un hospital es público. A la persona mayor le costó usarla en el móvil (letra y botones pequeños, palabras técnicas y demasiado a la vez), y desde el 15 nov la web es otra: letra de 16 px o más y botones de 44 px o más en todo el móvil, medidos; lenguaje llano; una portada que dice para qué sirve; «Somos mayores»; una lista con 4 cosas por fila en vez de 7 a 9, y una tarjeta con lo esencial y lo demás en «Ver más». Todavía no la ha vuelto a probar: la segunda ronda va ahora, y no adelantamos su resultado.
- Si preguntan qué se cambió para la persona mayor, en detalle (D-244 y D-245, en producción desde el 15 nov):
  - medido a 390 y a 360 px en todas las pantallas: 0 textos por debajo de 16 px, 0 botones por debajo de 44 px y axe sin incidencias. Antes, a 390 px, había 8 textos por debajo en la portada, 24 en el formulario, 36 en la lista y 25 en la tarjeta;
  - la portada empieza por «Te decimos en qué zonas de la Comunidad de Madrid puedes vivir con tu presupuesto y con lo que necesitas cerca.»;
  - «Somos mayores» pregunta «¿Cerca de dónde queréis vivir?» («Donde vivimos ahora» o «Cerca de nuestra familia») y marca de entrada el centro de salud, el metro o tren sin escaleras y el transporte. No suma personas ni cambia el %;
  - en el móvil, cada fila dice 4 cosas (el puesto, la zona, su banda y «Unos … € al mes») en vez de 7 a 9, y la primera pantalla de la tarjeta, 12 en vez de 17. Lo demás sigue en «Ver más»: no se ha quitado ningún dato;
  - «‹ Volver a la lista», y el botón atrás del móvil también vuelve a la lista;
  - si falta el dato de lo que buscas, la tarjeta lo dice: «No sabemos si le faltan…».
- Si preguntan si ahora sí la sabe usar: todavía no lo sabemos. Mariano repite la prueba ahora, con tres tareas (buscar, elegir una zona con su precio y volver a la lista) y sin ayudarla; hasta tener el resultado no se dice nada de cómo le ha ido.
- Si preguntan por las 10 zonas: además, comprobamos a mano 10 zonas contra las fuentes oficiales, y eso destapó errores del propio registro que ya están corregidos, como cuatro centros de salud sin número de portal y un hospital sin nombre.
- Si piden una frase: «Se valora mucho la cercanía al puesto de trabajo» y «Muy chula la web, funciona bien» (slide 3, sin nombre, como se prometió a los usuarios).
- Evidencia:
  - quién y qué pidieron: las notas de Mariano, que no se versionan porque llevan frases de las personas (`pitch/pruebas_usuarios/plantilla_resultados.md`);
  - lo que cambió: D-238 («cuatro personas pidieron buscar solo en una parte de la región»), el PR #53 (límite de tiempo y ayuda del transporte; `trabajo.max_min` y `trabajo.ayuda` en `pitch/textos_web.md`), D-233 (paradas por modo) y D-239 (desempate y hospitales);
  - las 10 zonas: `pitch/revision_10_zonas.md` · D-216 y D-218 §10;
  - lo que se cambió para la persona mayor: D-244 y D-245 (`docs/00_index/01_decisions_log.md`) · medidas antes y después en `evidence/gate-06/2026-11-15-ux-1/ux-movil-1.md` y `evidence/gate-06/2026-11-16-ux-2/ux-movil-2.md` · despliegues en `evidence/gate-06/2026-11-15-deploy/deploy-33-e0417ae-ux1.md`, `deploy-34-c0e9d11-ux2.md` y `deploy-35-55651c2-ux3.md`.
- Lo que pidieron y no entra antes del freeze: preguntas 49 y 50. «¿Por qué salían siempre pueblos?»: pregunta 51.
- Estado: lo que pidieron, en producción desde el 14 nov (despliegues de `ad4a8f2` y `f1b6f5a`: `evidence/gate-06/2026-11-14-deploy/deploy-27-ad4a8f2-d233.md` y `deploy-28-f1b6f5a.md`). Lo de la persona mayor, en producción desde el 15 nov (despliegues de `e0417ae`, `c0e9d11` y `55651c2`; comprobado otra vez por D el 18 nov). **No hay segunda prueba con personas todavía:** Mariano la manda ahora. Si llegan resultados o más personas antes del 26 nov, se cambia la respuesta; nunca se dice un resultado ni un número de memoria.

**44. ¿Qué es original? El Ayuntamiento ya hizo «El Madrid de los 15 minutos», y el 2SFCA es de 2003.**
El método de repartir la capacidad entre quienes la comparten no es nuestro, y lo citamos: lo nuevo es lo que hacemos con él. El estudio del Ayuntamiento de 2022 da a cada portal de Madrid capital un índice según haya o no cada servicio a 15 minutos. Nosotros cubrimos los 179 municipios, contamos cuánta gente comparte cada servicio, comparamos cada zona con las de su tipo con una prueba estadística y sumamos el tiempo en transporte público con los horarios del Consorcio, que ese estudio dejaba para el futuro; y lo juntamos con un buscador para personas, abierto y con la fuente de cada cifra.
- Evidencia: el estudio, Jornadas de Geodatos 2022 (https://geoportal.madrid.es/fsdescargas/IDEAM_WBGEOPORTAL/GEOPORTAL/Jornada/2022/SALA5_1130_PROXIMIDAD_POR_CALCULODEREDES.pdf):
  - «Objetivo del proyecto»: «desde cada portal»;
  - «Creación de un índice normalizado»: «Existencia o no del equipamiento/servicio»;
  - «Mejora del modelo y posibilidades futuras»: «Población por portal» e «Incorporar los datos General Transit Feed Specification».
- Más evidencia: D-217 (Luo y Wang, 2003; Talbot et al., 2000) · D-213 (comparación por tipo y prueba de Poisson) · D-220 (transporte).
- Si insiste: del estudio tomamos la velocidad de 4 km/h, para que los minutos se puedan comparar (D-211).

**45. ¿Quién lo mantiene cuando acabe el concurso?**
Mariano, y está pensado para que baste una persona. Los datos se recargan con un comando, cada conjunto pasa un control de calidad antes de entrar y una prueba revisa la web pública cada mañana. Al año son unos 2–3 días para la estadística anual y medio día por trimestre para los horarios del transporte; el código es abierto y cada decisión está escrita, así que otra persona puede retomarlo.
- Evidencia: `pitch/modelo_negocio.md` («Mantenimiento con una sola persona», estimación de D) · `.github/workflows/smoke-demo.yml` · `evidence/gate-01/` · `docs/00_index/01_decisions_log.md` · `LICENSE` (Apache-2.0).

## Dos más, con las cifras de impacto (12 nov)

**46. ¿Cómo sabéis que en una zona «falta» y no es casualidad?**
Porque FALTA exige dos cosas: tener menos del 80 % de lo que tienen los municipios parecidos, y que esa diferencia no se explique por azar con una prueba exacta de Poisson. En Puente de Vallecas, con 9.433 niños de 0 a 4 años, una diferencia así saldría por azar menos de 1 vez de cada 100. Por eso Centro, con una proporción parecida pero menos niños, sale JUSTO y no FALTA (pregunta 15).
- Evidencia: D-213 (punto 2: regla de los cuatro quintos e intervalo exacto de Poisson de Garwood, bilateral al 95 %, que equivale a unilateral al 2,5 %) · D-217 · D-229 §3 (`p_value` de cada zona en `GET /api/v1/gaps/impact`) · `evidence/gate-04/2026-11-12/impact-cifras.txt`: p = 0,001 en Puente de Vallecas, 0,016 en Carabanchel y 0,011 en Villaverde.
- Si insiste en los pueblos pequeños: un pueblo con muy pocos casos esperados se compara junto con sus vecinos parecidos (D-217 §6). Si ni así llega, sale «zona pequeña para comparar», nunca FALTA (pregunta 14).
- Si insiste en las comparaciones múltiples: no corregimos por ellas. Con 199 zonas por fila, alguna FALTA podría salir por azar, así que damos la probabilidad de cada una para que se pueda juzgar. Todas las de la lista de impacto están por debajo de 0,02.

**47. ¿A cuánta gente afecta lo que falta?**
En toda la región:
- escuelas infantiles: 25.551 niños de 0 a 4 años, el 9,8 %;
- farmacias: 667.172 personas, el 9,4 %;
- centros de mayores: 54.581 personas de 65 años o más, el 4,1 %;
- vivienda grande: 99.483 hogares de 4 o más personas, el 14,8 %.

En colegios y centros de salud no hay ninguna zona con una falta clara. Las zonas salen ordenadas por la gente afectada, y esa es la lista de dónde invertir primero.
- Evidencia: D-229 (`impact-0.1`) · `GET /api/v1/gaps/impact` · `evidence/gate-04/2026-11-12/impact-cifras.txt` (datos del 12 nov). La gente afectada es la población que ya usa cada fila: el censo de la Comunidad y, en los distritos, el padrón. No se estima nada.
- Detalle, si lo piden:
  - escuelas infantiles: Puente de Vallecas (9.433 niños; 57 escuelas por cada 100 de los municipios parecidos), Carabanchel (9.150; 68) y Villaverde (6.968; 61);
  - farmacias: Getafe, Torrejón de Ardoz, Parla, Rivas-Vaciamadrid y Valdemoro;
  - mayores: 6 municipios, con Torrejón de Ardoz y Pozuelo de Alarcón a la cabeza;
  - vivienda: 25 municipios, con Fuenlabrada, Leganés y Alcorcón a la cabeza.
- Estado: en producción desde el 12 nov (`GET /api/v1/gaps/impact`, comprobado: 25.551 de 260.310 niños de 0 a 4 años, en 3 zonas). La web lo enseña en «Dónde invertir primero», en «Qué falta» sin zona (producción, 12 nov).

**48. Las primeras zonas salen muy parecidas: 94, 93, 92 %. ¿No diferencia poco?**
Entre distritos se parecen porque esta familia pide cosas que Madrid cumple casi en todas partes, y aun así el % ya separa: desde el 15 nov cada minuto cuenta y las plazas también, así que de las 42 zonas que cumplen todo, 12 salen «Muy buena opción», 5 «Buena opción», 13 «Opción regular» y 12 «Poco recomendable». Arriba, Puente de Vallecas y Latina están las dos al 94 %, y la tarjeta lo dice («Igual de buena que Latina»); va primera la que tiene más cerca los servicios del día a día. Y dentro de un distrito Vida Fácil baja a los barrios: en San Blas-Canillejas cumplen todo 7 de sus 8, con Arcos, Canillejas, Amposta, Simancas y Rosas al 89 %, y Rejas se queda fuera por el colegio.
- Evidencia:
  - el caso de ejemplo: D-243 §9 · producción, 15 nov, comprobado por D (`POST /api/v1/search` con el fixture, `fit-0.9`: 42 zonas, bandas 12 / 5 / 13 / 12; Puente de Vallecas y Latina al 94 %, Usera y Moratalaz 93) · las palabras de las bandas y «Igual de buena que Latina (94 %).», en producción desde el 15 nov (D-245, despliegue de `55651c2`), comprobadas por D el 18 nov;
  - los barrios: D-232 · producción, 15 nov (`POST /api/v1/search/barrios` con el caso de ejemplo y el distrito 2807920: 7 de 8; Rejas, «casi», por el colegio);
  - el alquiler por barrio: D-232 §4 (San Blas-Canillejas, de 14,9 a 16,0 €/m²).
- Límite, si insiste: dentro de un distrito el alquiler cambia poco, porque se publica por código postal y un código cubre varios barrios. Y con ruido en los datos, la 1.ª cambia a menudo, casi siempre por otra zona con el mismo %: por eso la web dice con quién empata cada zona, en la tarjeta («Igual de buena que…», D-243 §13 y D-245).
- Y con «¿Dónde?» en «Madrid capital», el buscador compara los 131 barrios: con el caso de ejemplo cumplen todo 78, con Puerta del Ángel, Vinateros y Lucero al 95 % (pregunta 52).
- Estado: en producción. La vista de un distrito enseña «Los barrios que más te convienen» («os» con más de una persona) tras buscar (PR #37; el título, desde D-244), «¿Dónde?» desde el 14 nov (D-238) y la fórmula `fit-0.9` desde el 15 nov (D-243, despliegue de `025a4a2`).

## Dos más, de la prueba con usuarios (14 nov)
Se responden con lo que ya enseña la web desde el 15 nov y con la hoja de ruta.

**49. ¿Y los proyectos futuros de Madrid, como el metro nuevo o los nuevos desarrollos?**
Hoy medimos lo que ya existe, y enseñamos lo que viene como contexto: las promociones del Plan Vive de la Comunidad y, en Madrid capital, los desarrollos residenciales del Plan General que están en obras o en trámite, como Los Berrocales o Los Ahijones en Vicálvaro, y el suelo público que la Comunidad y los ayuntamientos ofrecen para construir vivienda (pregunta 60). Una línea o una estación nueva entra en cuanto el Consorcio la publica en sus horarios, que recargamos cada trimestre; lo que aún está en proyecto iría como un escenario aparte, nunca mezclado con el dato de hoy. Nada de eso puntúa: dice dónde se prepara suelo, no cuántas viviendas habrá ni cuándo.
- Evidencia:
  - lo que viene: D-241 (Plan Vive, transcrito de la web de la Comunidad con su fecha de extracción; «PGOUM 97. Estado de desarrollo de los ámbitos», datos.madrid.es, CC BY 4.0) · producción, 15 nov: Getafe, Plan Vive con 864 viviendas, y los distritos de Madrid con sus ámbitos (`evidence/gate-06/2026-11-15-deploy/deploy-31-59187f8-lote4.md`); el suelo público, D-246, en producción desde el 18 nov (pregunta 60);
  - por qué no puntúa: D-241 §4 y §10 (puntuar «dónde habrá más vivienda» sería una predicción sin dato de cuándo ni cuántas);
  - horarios: los 6 GTFS del CRTM (D-196) y los minutos al trabajo calculados con ellos (D-220); recarga trimestral en `pitch/modelo_negocio.md` («Mantenimiento con una sola persona»);
  - escenario frente a dato: `docs/03_intelligence/21_temporal_and_forecasting_strategy.md` («Forecast» y «Scenario») y `CLAUDE.md` §11 (observado, estimado, forecast y escenario, siempre separados).
- Si insiste en los pueblos: fuera de Madrid no hay un registro abierto del planeamiento como el del Ayuntamiento (en el portal CM no sale ningún conjunto al buscar «planeamiento», 14 nov). Lo que sí hay es la parte de compraventas de vivienda nueva de cada municipio (pregunta 50).
- Estado: «Vivienda nueva y lo que viene», en producción desde el 15 nov (D-241); las líneas de metro en proyecto, hoja de ruta.

**50. ¿Puedo filtrar por vivienda nueva o por metros?**
Hoy no filtramos pisos concretos, porque no usamos anuncios: Vida Fácil elige zonas. Lo que sí damos es contexto de la zona: los metros del alquiler medio (77 m² en Latina), cuántas viviendas de más de 90 m² hay por cada 100 hogares de 4 o más personas, qué parte de las viviendas se construyó desde 2001 (en los distritos de Madrid, su año medio de construcción) y qué parte de las compraventas del último año fue de obra nueva. Filtrar pisos por metros o por obra nueva queda en la hoja de ruta, con datos que se puedan reutilizar legalmente.
- Evidencia:
  - sin anuncios: pregunta 35 · `CLAUDE.md` §15;
  - metros: el hecho del alquiler («Alquiler ≈ 1.101 €/mes por 77 m²», Latina, `evidence/gate-06/2026-11-12-deploy/caso-demo-fit06.md`) y la fila de vivienda (`data/catalog/features/viviendas_grandes_por_100_hogares_grandes.yaml`; en los distritos de Madrid, SIN DATOS);
  - antigüedad: D-235 §3. En los municipios, el censo anual de la Comunidad de 2023 (`censo_anual_vivienda_por_antiguedad`; Madrid, 16,5 % desde 2001). En los distritos y barrios de Madrid, el año medio de construcción del Catastro, del panel del Ayuntamiento (de 1926 en Centro a 1999 en Vicálvaro);
  - obra nueva: D-241 §5 («Compraventas de vivienda nueva y de segunda mano, por municipio», portal CM; en los 4 últimos trimestres, Getafe 28 % y Madrid 3,8 %);
  - hoja de ruta: D-069 (superficie, antigüedad y obra nueva o usada «cuando exista información fiable y legalmente reutilizable»).
- Si insiste en la obra nueva: la parte de compraventas nuevas dice dónde se construye, no qué piso queda libre ni a qué precio.
- Estado: los metros, la antigüedad y la obra nueva, en producción (15 nov); el filtro por vivienda, hoja de ruta.

## Tres más, de lo que cambió tras la prueba con usuarios (14 nov)

**51. ¿Por qué con mucho presupuesto salían siempre pueblos, y en orden alfabético?**
Porque era un empate real: con mucho presupuesto y nada marcado, todas las zonas que encajan llegan al 100 %, y entre ellas decidía la fiabilidad del alquiler, más alta en los municipios que en los distritos, y después el código INE, que va por orden alfabético: «Alcalá de Henares, Alcobendas, Alcorcón…». Nos lo dijeron en la prueba con usuarios y lo cambiamos: a igual %, va primero la zona que tiene más cerca los servicios del día a día, y la lista avisa de que encajan muchas igual de bien para que marques qué te importa. Hoy, con alquiler hasta 10.000 € y nada marcado, encajan 183 zonas, todas al 100 %, y arriba salen Chamberí, Tetuán, Salamanca, Puente de Vallecas y Centro.
- Evidencia: D-239 A §1–6 · D-243 §2 y §9 (con `fit-0.9` el desempate mira lo cerca que están los servicios, porque cada minuto cuenta) · producción, 15 nov, comprobado por D: `POST /api/v1/search` con una pareja, alquiler hasta 10.000 €/mes y nada marcado (`fit-0.9`): 183 zonas, todas al 100 % (eran 57 antes de que el alquiler del Ministerio rellenara los pueblos, D-242) · capturas del aviso en `evidence/gate-06/2026-11-14-tiebreak-hospitals/`.
- Si insiste en por qué no ordenar por precio o por población: sería una preferencia que nadie ha pedido («más barato» o «más grande» no es «mejor»), y un orden al azar daría listas distintas con la misma búsqueda (D-239 A §3).
- Estado: en producción desde el 14 nov (despliegue de `f1b6f5a`), y con `fit-0.9` desde el 15 nov.

**52. ¿Puedo buscar por barrio?**
Sí, en Madrid capital: en «¿Dónde?» eliges «Madrid capital» y Vida Fácil compara sus 131 barrios en lugar de los 21 distritos. Con el caso de ejemplo encajan 78, y arriba salen Puerta del Ángel, Vinateros y Lucero al 95 %. Lo pidieron 4 de las 6 personas de la prueba; también puedes buscar solo en los alrededores de Madrid o solo en los pueblos, según las zonas del Instituto de Estadística de la Comunidad.
- Evidencia: D-238 (§1, la zonificación; §4 y §5, la búsqueda; §8, las pruebas) · producción, 15 nov, comprobado por D con `fit-0.9` (`scope: madrid`: 78 de 131; Puerta del Ángel, Vinateros y Lucero al 95 %, y 8 barrios al 94 %, entre ellos Almendrales, Palomeras Bajas y Campamento). Con `fit-0.7` (14 nov) eran Lucero y Campamento al 99 % (`evidence/gate-06/2026-11-14-deploy/deploy-28-f1b6f5a.md`) · Nomenclátor de la Comunidad de Madrid 2025, §3.4.
- Límites, si insiste:
  - «Qué falta» sigue siendo del distrito, y la tarjeta del barrio lo dice;
  - el alquiler de un barrio es el de sus códigos postales, así que cambia poco dentro de un distrito (D-232 §4), y Sol sale sin datos porque no tiene alquiler publicado (D-238 §8);
  - con «Toda la Comunidad», Madrid sigue por distritos, para no comparar un barrio con un municipio entero (D-238 §5).
- Si pregunta por «Pueblos»: la Comunidad solo publica el alquiler de los municipios de más de 20.000 habitantes, así que con alquiler casi todos los pueblos salen «sin datos». La web lo explica en vez de dar una lista vacía (D-238 §10).
- Estado: en producción desde el 14 nov (despliegue de `f1b6f5a`). El caso del pitch, sin «¿Dónde?», da lo mismo que antes.

**53. ¿Cómo sabéis si un hospital es público?**
Del registro de centros sanitarios de la Comunidad de Madrid, que publica de quién depende cada centro. Llamamos público a lo que es de la red del Servicio Madrileño de Salud, la que te asigna la tarjeta sanitaria, y privado a todo lo demás; cinco hospitales de la red los gestiona una empresa y salen «Hospital público · gestión privada»: la Fundación Jiménez Díaz, el Rey Juan Carlos, el Infanta Elena, el de Villalba y el de Torrejón. De los 85 hospitales, 35 son públicos y 50 privados.
- Evidencia: D-239 B · `cm_centros_sanitarios` (dependencia funcional) · dos páginas de la Comunidad de Madrid, consultadas el 14 nov: «Hospitales de la red del Servicio Madrileño de Salud» y «Control y seguimiento de centros y servicios de gestión indirecta» · producción, 14 nov: `evidence/gate-06/2026-11-14-deploy/deploy-28-f1b6f5a.md` (`/places`: 35 públicos, 5 de ellos de gestión privada, y 50 privados).
- Si insiste en la Fundación Jiménez Díaz: el registro la da como privada, pero está en la red por un concierto singular, así que sale pública (D-239 B §2).
- Si pregunta por los hospitales de los contratos de obra (Henares, Infanta Cristina, Infanta Leonor…): son públicos de gestión pública. La empresa construyó el edificio y lleva los servicios no sanitarios, pero la asistencia es del Servicio Madrileño de Salud.
- Si pregunta por un hospital con convenio, como la Fundación Instituto San José: sale privado. Puede recibir pacientes derivados, pero no es el hospital de referencia de la tarjeta sanitaria.
- Estado: en producción desde el 14 nov (despliegue de `f1b6f5a`). El Rey Juan Carlos sale aún sin nombre, como «Hospital público · gestión privada», hasta la próxima carga del registro (D-239).

## Seis más: contexto de la zona y preguntas difíciles de la fórmula (15 nov)

**54. Enseñáis delitos y renta por zona. ¿No estigmatiza eso a algunos barrios?**
Por eso no puntúan, no ordenan ni filtran: son datos informativos con su fuente, su año y su aviso, sin colores ni palabras como «peligroso» o «rica». Los delitos van sin los de internet y con el aviso de que suben donde hay mucha gente de paso, porque se cuentan donde se conocen, no donde vive quien los sufre; en Madrid damos la cifra de toda la ciudad, porque no se publica por distrito y repartirla sería inventar. La renta la pidieron los usuarios, pero ordenar por ella empujaría a las familias según el dinero de sus vecinos.
- Evidencia: D-235 §1–5 (`context_only`, sin `fit` ni `gap_row`, y el test `test_zone_context_never_scores_filters_or_enters_the_gaps`) · D-224 · D-226 · `zona.contexto.*` en `pitch/textos_web.md`.
- Si insiste: los propios vecinos no ven tanta diferencia. En la Encuesta de Calidad de Vida y Satisfacción con los Servicios Públicos 2025 del Ayuntamiento de Madrid, la percepción general de seguridad va de 7,5 en Chamberí a 6,4 en Villaverde: 1,1 puntos sobre 10.
- Estado: en producción (D-235).

**55. ¿Por qué el ruido solo en Madrid?**
Porque el dato es el Mapa Estratégico de Ruido 2021 del Ayuntamiento de Madrid, que se publica en abierto (Geoportal, CC BY 4.0) con detalle de calle. Contamos qué parte de las calles residenciales pasa de 65 decibelios de día o de 55 de noche, los objetivos de calidad acústica de las zonas residenciales: en Usera, el 14 % de las calles de día y el 32 % de noche. Es el ruido del tráfico calculado en la calle, no medido en la ventana; fuera de Madrid sale «sin dato publicado», nunca 0, y en ningún sitio puntúa.
- Evidencia: D-237 §1, §2 y §4–5 · Real Decreto 1367/2007, anexo II, tabla A · producción, 15 nov: Usera, «14 % de las calles de día, 32 % de noche»; Getafe, «sin dato publicado» (`evidence/gate-06/2026-11-15-deploy/deploy-31-59187f8-lote4.md`).
- Si insiste en los demás municipios: la ley obliga a las aglomeraciones de más de 100.000 habitantes a hacer su propio mapa estratégico de ruido (Directiva 2002/49/CE). No hemos cargado ninguno más: buscarlos en abierto es el siguiente paso.
- Si pregunta por qué importa: el 27,7 % de los hogares de la Comunidad dice sufrir ruidos de los vecinos o de la calle, frente al 22,1 % en España (INE, Encuesta de Condiciones de Vida, 2020).
- Si pregunta por el aire: sí está en toda la región. Es la media de dióxido de nitrógeno de 2025 en la estación de la zona o en la más cercana de su misma zona de calidad del aire, con el límite europeo al lado; en Getafe, 25,6 µg/m³ en su estación de tráfico (D-237 §2–3). Tampoco puntúa.

**56. El ocio sale de OpenStreetMap. ¿Por qué no de datos de la Comunidad?**
Porque el portal de la Comunidad no publica un censo con coordenadas de bares, restaurantes, gimnasios, cines ni museos de toda la región; sí publica las bibliotecas y los museos por municipio, y los usamos para comprobar OpenStreetMap. En las ciudades está bastante completo, pero en los pueblos falta algún local: de los 97 municipios con biblioteca pública según la Comunidad, 77 la tienen en el mapa. Por eso el ocio solo cuenta si lo marcas y no deja fuera ninguna zona salvo que marques «Imprescindible».
- Evidencia: D-236 §1, §3 y §5 · `evidence/gate-01/2026-11-14/ocio.md` · licencia ODbL («© OpenStreetMap contributors»), que no cuenta como dato CM.
- Estado: en producción (D-236, `fit-0.8`).

**57. Vuestros alquileres son de 2024. Los anuncios de hoy están entre un 16 % y un 33 % más altos.**
Es cierto, y lo decimos en cada resultado: nuestra cifra es lo que se pagó en los contratos firmados en 2024 según Hacienda, no lo que se pide hoy en un anuncio. Parte de la diferencia es la subida desde entonces (en Madrid, un 9,7 % en 2025 y un 4,5 % interanual en octubre de 2026, según idealista), y otra parte, que un anuncio es un precio pedido, no un contrato firmado. Donde usamos la referencia del Ministerio damos también el rango de la mitad de los contratos, y la distancia con los anuncios fue uno de los casos que se miraron al elegir la fórmula.
- Evidencia: D-228 (contratos firmados en 2024, Agencia Tributaria) · D-242 (rango) · el aviso de cada resultado: «un anuncio de hoy puede pedir más» · contraste hecho para el banco de la fórmula (15 nov, `pitch/banco_formula.md`, filas D01–D04 y D09–D10), con los precios de anuncio de idealista (septiembre y octubre de 2026, en parte a través de Housfy) y de Fotocasa (Madrid capital, 23,11 €/m² en octubre de 2026). Son fuentes de anuncios, con fiabilidad media.
- Si insiste: la distancia no es igual en todas partes. En varias zonas baratas el anuncio sale entre 1,28 y 1,33 veces nuestra cifra (Puente de Vallecas, Leganés y Colmenar Viejo, este último con la cifra de El Diario de Madrid, fila D04); en las caras, entre 1,16 y 1,19 (Chamberí y Centro). No pasa en todas: Collado Villalba, también barata, sale a 1,17. En el conjunto, de 1,16 a 1,33. Así que una zona que entra justa en el presupuesto puede no entrar con los precios de hoy.
- Cuánto cambiaría: si todos los alquileres fueran un 20 % más caros, el ejemplo del pitch pasaría de 42 a 39 zonas, y una persona sola con 900 € que trabaja en Sol, de 9 a 1. Ninguna fórmula lo arregla: es un dato, y por eso la web lo avisa en la lista y en la tarjeta («Precio de contratos firmados en 2024. Los anuncios de hoy suelen pedir más.») (`pitch/banco_formula.md`, «Lo que no arregla ninguna fórmula»).
- Estado: la fórmula elegida por Mariano el 15 nov («cerca y plazas», `fit-0.9`) está en producción desde ese día. No cambia el alquiler, que sigue siendo el de los contratos firmados.

**58. ¿Y si voy en coche?**
Hoy no lo medimos: el trayecto es en transporte público, porque es lo que se puede calcular con datos abiertos de la Comunidad, los horarios del Consorcio, y lo decimos. Sabemos que pesa: según la Encuesta Domiciliaria de Movilidad de 2018 del Consorcio, el 52,7 % de los viajes al trabajo en la región se hace en vehículo privado, y desde la corona metropolitana el viaje medio en transporte público dura 47 minutos y en coche, entre 22 y 27 (el viaje al trabajo, en cualquier medio, dura 33 o 34 de media), así que para quien conduce los municipios salen peor de lo que son. El tiempo en coche está en la hoja de ruta; mientras, enseñamos el aparcamiento de disuasión o público más cercano.
- Evidencia: Consorcio Regional de Transportes de Madrid, Encuesta Domiciliaria de Movilidad 2018 (síntesis, pp. 24–25, y documento III, tablas 102 y 103; 13.009 hogares; filas B02, B03 y B05 de `pitch/banco_formula.md`) · D-220 (trayecto en transporte público) · D-237 (aparcamientos) · `pitch/metodologia.md` §1.8 («Medimos lo que tienes andando…») · `CLAUDE.md` §11 (movilidad multimodal).
- Si insiste: el límite «Tardar como mucho N min» también es en transporte público. La encuesta es de antes de la pandemia y del teletrabajo.
- Estado: hoja de ruta.

**59. ¿Cómo validasteis la fórmula del encaje?**
Con un banco de pruebas en cuatro capas: perfiles sacados de la prueba con usuarios y casos de control, cada uno con lo que esperaba ver; una rejilla de 1.000 búsquedas sintéticas (hogar, presupuesto, trabajo, días de oficina, prioridades, ámbito y metros); pruebas de coherencia, como que más presupuesto nunca quite zonas o que menos minutos de trayecto nunca bajen el %; y la robustez frente al error de los datos, moviendo cada valor dentro de su fiabilidad. Además comparamos los resultados con fuentes externas, que no ajustan la fórmula y solo sirven para comprobarla: las encuestas de Fotocasa y del CIS sobre qué se valora al elegir casa y la Encuesta Domiciliaria de Movilidad del Consorcio sobre cuánto se tarda al trabajo. Con todo eso, Mariano eligió el 15 nov la variante «cerca y plazas»: en las 1.000 búsquedas, las zonas al 90 % o más con FALTA en algo marcado bajaron de 578 a 0, y las búsquedas con más de 10 zonas empatadas arriba, del 29 % al 8 %.
- Evidencia: `pitch/banco_formula.md`: qué comprueba el banco (17 personas con 79 expectativas, la rejilla de 1.000 búsquedas, 5 pruebas de coherencia y la robustez) y su evidencia externa, entre otras el CIS, Barómetro de la Vivienda y el Alquiler (estudio 3212, 2018); Fotocasa Research, «Experiencia en compraventa en 2024»; y el Consorcio Regional de Transportes, Encuesta Domiciliaria de Movilidad 2018. Cada fuente lleva su fecha, su muestra y su sesgo declarado: por ejemplo, Fotocasa son usuarios de un portal, y el CIS es de 2018 y de toda España.
- Si insiste en un caso: con mucho presupuesto, las zonas empataban al 100 % y salían pueblos por orden alfabético; lo vio la prueba con usuarios y lo arregló el desempate (pregunta 51).
- Si insiste en los resultados: con las personas de la prueba se cumplen 37 de 42 expectativas (antes, 20) y el control no empeora (17 de 20, antes 16); la evidencia externa, que no se usó para ajustar, pasa de 19 a 20 de 24. La web desplegada da exactamente los mismos % y órdenes que el banco (D-243 §7–8).
- Si insiste en que los parámetros no están validados con usuarios: es verdad. El 89 %, el 74 %, el 0,6 del presupuesto o la mitad salen de las bandas y de umbrales que ya había. Habrá una segunda ronda con las mismas personas, que compare zonas de dos en dos («¿mejor esta o esta?»); el banco ya está preparado para cargarla.
- Si insiste en lo que la fórmula no arregla: son datos. P6, que buscaba con su bebé y no veía su zona, ve todos los distritos si busca 60 m² en vez de los 71 que se suponen para un hogar de 3 personas. A P1, con 400.000 € para comprar, Tetuán le sale 5.º si se corrige el precio estimado de ese distrito, que hoy sale caro frente al resto de la ciudad (D-234); está en la hoja de ruta.
- Estado: en producción desde el 15 nov (`fit-0.9`, D-243, despliegue de `025a4a2`). El banco y su evidencia, en `pitch/banco_formula.md`.

## Una más: el siguiente paso, de dónde vivir a dónde construir (18 nov)
Aprobado por Mariano el 18 nov. En las slides va sin nombres de empresas; aquí sí, porque son la validación de mercado.

**60. ¿Cuál es el siguiente paso? ¿No hay ya empresas que analizan parcelas?**
Buscar una parcela exacta y calcular si una promoción sale ya se puede; decir qué vivienda hace falta construir en ella, y para quién, todavía no. El «¿se puede construir?» ya se vende a promotores, y eso nos dice que hay mercado: Nestra, en España, lee la normativa urbanística de una parcela y calcula lo que admite, y Sitescope, en Polonia, hace lo mismo con el planeamiento polaco. Empezamos como ellas, por la parcela, y le ponemos al lado el contexto de demanda de su zona, del que ninguna habla en su web; cruzarlo con la vivienda que le falta a esa zona, para decir qué hace falta construir ahí (el Housing Gap), es el siguiente paso.
- Si preguntan qué hay hoy: «Busca tu parcela», **en producción desde el 19 nov** (D-250, despliegue de `79020a1` verificado por C: `evidence/gate-06/2026-11-19-deploy/deploy-39-79020a1-parcela.md`, PR #102), de acceso libre durante el concurso. Se entra por referencia catastral, por dirección (la web enseña los portales que coinciden y nunca elige por la persona) o con un clic en el mapa, en toda Madrid capital. La ficha trae los datos de la parcela, su planeamiento con el enlace oficial, la edificabilidad de partida, el contexto del barrio y la calculadora ya rellena; ejemplos, en la pregunta 6. El contexto completo del barrio es el del piloto, los 108 barrios de Madrid capital dentro de la M-40; fuera, con las cifras del distrito o de la ciudad. La lista de barrios de D-247 y D-248 sigue detrás, como «Explorar barrios». Y, **desde el 18 nov** (D-246), el suelo público en la vista de cada zona. En la pantalla de un municipio o de un distrito de Madrid, en «Más datos de la zona» → «Vivienda nueva y lo que viene», el suelo público para vivienda del Portal del Suelo 4.0 de la Comunidad: las parcelas de uso residencial que la Comunidad y los ayuntamientos ofrecen en venta o en concesión, con sus m² edificables y, plegada, la lista de parcelas, cada una con su gestor y su enlace al visor de la Comunidad. En toda la región, 291 parcelas en 29 municipios, con 394.298 m² edificables; en Madrid capital, 38 en 7 distritos (Vicálvaro, 16 parcelas y 67.808 m²); Majadahonda, 101. Es contexto: no puntúa ni ordena zonas, y no dice cuántas viviendas caben.
- Límite, si insiste:
  - no decimos qué se puede construir en una parcela. Damos su planeamiento con el enlace a la ficha oficial, unos m² de partida, oficiales o «supuestos» por la norma zonal, que la persona puede cambiar, y, desde D-252, lo que el plan publica por uso para su parcela urbanística, que es el total que permite, no lo que queda; la normativa de la parcela manda, y la ficha lo dice («Información urbanística sin valor jurídico»). En normativa, Nestra y Sitescope van muy por delante: no competimos ahí, sino en la demanda;
  - tampoco cruzamos todavía la parcela con la vivienda que le falta a su zona: en los 21 distritos de Madrid, la fila «vivienda» de «Qué falta» sale hoy SIN DATOS (`GET /api/v1/gaps?level=distrito&row=vivienda`, leído por D el 19 nov), así que la ficha de una parcela no la tiene.
- Si preguntan quién lo pagaría: los inversores y los promotores de la slide 3, con el plan de precios (pregunta 6). Para las personas y los ayuntamientos sigue siendo gratis.
- Evidencia:
  - Nestra: [nestra.es](https://www.nestra.es), consultada el 18 nov: entrada por referencia catastral, dirección o punto en el mapa; normativa con el artículo de cada cifra, edificabilidad, usos permitidos y número de viviendas; para promotores, arquitectos, inversores, propietarios de suelo, ayuntamientos y bancos. No habla de la demanda de los hogares;
  - Sitescope: [sitescope.ai](https://sitescope.ai/), consultada el 18 nov: informes de parcela, un espacio de trabajo con IA sobre planeamiento y normativa local, y una API en desarrollo; usa la fuente oficial polaca (GUGiK). Tampoco habla de la demanda de los hogares;
  - el Portal del Suelo 4.0: [ficha del portal](https://datos.comunidad.madrid/dataset/parcelas_portal_suelo) y `data/catalog/datasets/cm_parcelas_portal_suelo.yaml` (CC BY 4.0); 525 parcelas en el CSV del 18 nov, 291 de uso residencial. Cargado el 18 nov con Gate 1 en PASS (`evidence/gate-01/2026-11-18/cm_parcelas_portal_suelo/`) y en producción ese día (despliegue de `747cb65` y sync: `evidence/gate-06/2026-11-18-deploy/deploy-36-747cb65-suelo.md`, PR #90). Las cifras de producción las leyó D en `GET /api/v1/features/suelo_publico_vivienda_m2/values` el 18 nov (`pitch/comprobacion_produccion_18nov.md`);
  - la demanda, lo que ya tenemos: «Qué falta» por zona y a cuánta gente afecta (preguntas 46 y 47) y el diseño del recomendador de vivienda, `docs/03_intelligence/16_housing_gap_product_recommender.md` y `51_housing_gap_math_spec.md`;
  - la versión para inversores: D-247 (los datos) y D-248 (la viabilidad, la API y la web), en producción desde el 19 nov (despliegue de `396d8f6` y sync, verificado por C antes y después del sync: `evidence/gate-06/2026-11-19-deploy/deploy-37-396d8f6-inversores.md`, PR #96);
  - la búsqueda por parcela: D-250, en producción desde el 19 nov (despliegue de `79020a1`, verificado por C: `evidence/gate-06/2026-11-19-deploy/deploy-39-79020a1-parcela.md`, PR #102). Capturas de producción en `evidence/gate-06/2026-11-19-deploy/deploy-39/`: la búsqueda en el móvil (`390-buscar.jpg`), la ficha de Méndez Álvaro 47 (`390-ficha-mendez-alvaro.jpg`) y la de Almería 1 entera (`1440-ficha-almeria.jpg`). Son de antes de D-251 y D-252: la de Almería 1 ya no vale, porque hoy sale «Sin dato» (pregunta 6);
  - el análisis por parcela está en la visión desde D-040 («Parcel Intelligence ampliado», `docs/01_product/05_pro_layer.md`); quedó fuera del concurso con D-192, y Mariano lo trajo el 19 nov con D-250, sin el Housing Gap.
- Estado: la búsqueda por parcela, en producción desde el 19 nov (D-250), con la versión por barrios detrás (D-247 y D-248); decir qué vivienda hace falta construir en cada parcela, un plan. El suelo público, en producción desde el 18 nov (D-246).

## Una más: ¿por qué no una consultora? (prueba con un inversor, 19 nov)
Sale de la prueba de la versión para inversores que hizo el 19 nov un inversor con experiencia en promoción, P7 (inversor): «la gente que va a hacer eso se va a una inmobiliaria o una consultora a que les hagan el estudio completo».

**61. Para invertir, un promotor va a una consultora o a una inmobiliaria a que le hagan el estudio completo. ¿Para qué iba a usar esto?**
Porque antes de pagar un estudio completo hay que saber qué parcela merece uno, y la ficha es ese primer filtro: en unos minutos da la parcela, su planeamiento, una edificabilidad de partida, cuánto se podría pagar por el suelo o, con su precio, si una promoción sale, y el contexto de demanda de su zona. Las consultoras y las inmobiliarias no son la competencia, sino clientes: con la ficha hacen sus estudios más rápido, con cada dato citado, y para ellas es el plan Equipo. No sustituye al estudio completo, y lo decimos nosotros mismos en cada ficha: «No es una tasación ni un informe vinculante ni una garantía de rentabilidad.»
- Si preguntan qué tiene el estudio completo que la ficha no tiene: la visita, la normativa completa de la parcela (pregunta 60) y una tasación. P7 (inversor) señaló tres cosas más; dos ya están en la ficha (D-252) y la tercera está en curso (D-253):
  - la edificabilidad por uso, separando residencial, terciario y dotacional: ya está. Una línea por fuente con su uso, y lo que el plan publica por uso para la parcela urbanística, sin repartir nunca una cifra (D-252 §1–2; pregunta 6);
  - el coste de obra, que según él «baila mucho»: ya está explicado. Un PEM de partida de 968 €/m² (supuesto, Costes de Referencia General de la Comunidad de Madrid, 2022), el de los visados como referencia baja (644 €/m², 2025), las tres referencias con lo que es cada una, qué incluye el coste y qué no, y un escenario pesimista con un 15 % más de coste (D-252 §5–6; pregunta 6);
  - si la parcela tiene servicios, como la acometida de agua o el suministro de luz: la ficha todavía no lo dice. Ya no la llama «solar», que es una condición legal con servicios, sino «¿Está sin edificar?» (D-252 §4); los servicios, en curso (D-253).
- Si preguntan si ya lo usa alguna consultora: no. Que paguen es una hipótesis, como los precios, y se valida en las entrevistas de disposición a pagar (`docs/08_validation/09_pricing_validation.md`). Durante el concurso, la versión para inversores es de acceso libre, sin cuentas ni cobro (D-248 §1).
- Evidencia:
  - el aviso, en producción: en la ficha de cada parcela (`notices` de `GET /api/v1/investors/parcels`, leído por D el 19 nov con Almería 1) y en la sección de inversores de «Cómo lo calculamos» (D-251, leída por D el 19 nov). El texto está en `packages/domain/src/hi_domain/viability.py`;
  - el coste, en la misma respuesta, tras el despliegue de D-252: `defaults.pem_m2`, 968 €/m² («supuesto», `data/catalog/manual/costes_referencia_construccion.yaml`); `defaults.pem_permits_m2`, 644 €/m² (visados de obra nueva de viviendas en bloque de 2025, de toda la Comunidad, `cm_visados_presupuesto_obra`, «dato»); y `defaults.cost_coefficient`, 1,3575, marcado «supuesto» y desglosado;
  - el cliente: `CLAUDE.md` §16 (cliente inicial, «promotoras/inmobiliarias medianas»; «vender informes/estudios antes del SaaS completo») · las consultoras y las inmobiliarias, entre los clientes de la capa PRO (`docs/01_product/05_pro_layer.md`) y del go-to-market (`docs/06_business/06_go_to_market.md`) · el plan Equipo, en `pitch/modelo_negocio.md`.
- Estado: el posicionamiento, en el pitch desde el 19 nov (preguntas 6, 9 y 61 y `modelo_negocio.md`); la voz y las slides no cambian. La edificabilidad por uso y el coste, en producción desde el 19 nov (D-252). Los servicios, el «primer filtro» y la frase para consultoras en la web, en curso (D-253): **esta respuesta se cierra cuando D-253 esté en producción**.
