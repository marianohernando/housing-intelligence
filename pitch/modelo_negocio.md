# Modelo de negocio

**Decisión de Mariano (23 nov), que sustituye a la del 19 nov.** Tras el jurado simulado del 21 nov («no está claro quién paga ni por qué, si la API da gratis lo de inversores»):

- **Gratis siempre, para todos: los datos, las zonas, «Qué falta», cada ficha de parcela y la API.**
  - **Personas:** para quien busca dónde vivir, Vida Fácil es gratis y completa. La versión gratuita no se recorta para empujar a pagar (`CLAUDE.md` §3 y §16).
  - **Ayuntamientos:** cada ayuntamiento ve qué le falta a su municipio frente a municipios parecidos, dónde y a cuánta gente afecta, con la fuente de cada dato. Es «Qué falta», en producción en los 179 municipios y en los 21 distritos de Madrid (`GET /api/v1/gaps?level=municipio` y `?level=distrito`, 179 y 21 zonas, 19 nov). Les sirve para saber qué pedir primero y dónde reservar suelo, sin contrato ni licitación: las farmacias, la salud y los colegios los decide la Comunidad, y el ayuntamiento pone el suelo (pregunta 64).
  - **Inversores y promotores:** la ficha de cada parcela es gratis. «Busca tu parcela», por referencia catastral, dirección o clic en el mapa, en toda Madrid capital (D-250; despliegue de `79020a1` verificado por C: `evidence/gate-06/2026-11-19-deploy/deploy-39-79020a1-parcela.md`, PR #102). La ficha da los datos de la parcela (elaborados a partir de los del Catastro), su planeamiento con el enlace oficial, la edificabilidad de partida, sus servicios, el cálculo de si una promoción sale y, al lado, el contexto de demanda de su zona (D-247, D-248, D-252 y D-253). El contexto completo del barrio es el del piloto, los 108 barrios de Madrid capital dentro de la M-40; fuera, con las cifras del distrito o de la ciudad.
  - **La API pública:** abierta y gratuita, sin claves, igual que los datos (abajo).
- **De pago: lo que solo necesita quien trabaja con suelo a escala.**
  - **El plan empresarial:** carteras de parcelas, avisos de suelo nuevo, la API y el MCP a gran volumen con clave.
  - **Los informes personalizados:** estudios de suelo a medida, revisados a mano antes de entregarlos.
- **Hoy no se cobra nada, y lo de pago no existe todavía.** Durante el concurso la web dice «Plan Inversor (acceso libre durante el concurso)» (D-248 §1), que es el modelo del 19 nov: se cambia en la web cuando se decida (pendiente de B: `inversores.modelo`, `inversores.desarrolladores` y `pie.desarrolladores` en `pitch/textos_web.md`).

**Del lado de pago, las consultoras y las inmobiliarias** que les hacen el estudio a los promotores y a los inversores. Se añadió el 19 nov, tras la prueba de la versión para inversores con P7 (inversor), con experiencia en promoción: «la gente que va a hacer eso se va a una inmobiliaria o una consultora a que les hagan el estudio completo».
- **No son la competencia, sino clientes.** La ficha de la parcela es el primer filtro, en minutos, antes de pagar un estudio completo; quien hace esos estudios la usa para hacerlos más rápido, con cada dato citado, y para seguir muchas parcelas a la vez es el plan empresarial. Desde el 20 nov la web lo dice así (D-253 §8): arriba de la ficha, «Esto es un primer filtro de minutos, gratis y con fuentes. No sustituye al estudio de viabilidad que hace una consultora o un arquitecto.»; la sección «Lo que añade un estudio completo»; y «Llévate esta ficha (PDF) a tu consultora: ahorra parte de la recopilación de datos públicos.».
- **Es el cliente inicial del repo:** «promotoras/inmobiliarias medianas», con la idea de «vender informes/estudios antes del SaaS completo» (`CLAUDE.md` §16). Las consultoras y las inmobiliarias ya estaban entre los clientes de la capa PRO (`docs/01_product/05_pro_layer.md`) y del go-to-market (`docs/06_business/06_go_to_market.md`).
- **No sustituye al estudio completo, y lo decimos nosotros:** «No es una tasación ni un informe vinculante ni una garantía de rentabilidad.», en la ficha de cada parcela y en la sección de inversores de «Cómo lo calculamos» (D-251; leído por D en producción el 19 nov).
- **Es una hipótesis, como los precios:** se valida en las mismas entrevistas de disposición a pagar. Las respuestas, en las preguntas 6, 7 y 61 de `pitch/preguntas.md`.

**La API pública y el MCP: abiertos y gratuitos, sin clave.** También para empresas y ayuntamientos, que pueden meter «Qué falta» y el encaje de cada zona en sus propias herramientas o en un agente de IA. Lo explica una página pública, **`/desarrolladores`** («API y MCP para desarrolladores»), en producción desde el 19 nov (D-249; despliegue de `20b46d9` verificado por C: `evidence/gate-06/2026-11-19-deploy/deploy-38-20b46d9-desarrolladores.md`, PR #99): qué funciona hoy, cómo conectarlo y qué está solo planteado, marcado «Aún no disponible». Lo que hay hoy:
- **La API pública** (`/api/v1`) está en producción y no pide claves. Tiene 15 rutas de datos y 2 de salud, con su descripción OpenAPI en `/api/v1/openapi.json` (leída por D en producción el 19 nov, tras el despliegue de `79020a1`). 5 de las rutas de datos son de la versión para inversores, también gratis: 3 de D-248 y las 2 de la búsqueda por parcela (D-250). Las rutas y sus contratos están en `docs/04_technical_architecture/31_public_api_routes.md`, y en `/desarrolladores` cada una lleva un `curl` que se probó contra producción (D-249 §1; las 2 de la parcela, en el despliegue de `79020a1`, PR #102). La clave sería solo para el gran volumen, en el plan empresarial; el uso normal sigue sin clave.
- **El MCP** tiene siete herramientas de solo lectura: buscar zonas, qué falta, explicar una zona, encontrar una zona por su nombre y las fuentes de datos (D-225, `docs/04_technical_architecture/32_mcp_server.md`), y desde el 19 nov, dos de la versión para inversores, `ficha_inversor` y `viabilidad` (D-249 §2). Desde el 23 nov funciona también en remoto, gratis y sin clave, en `https://vidafacil-madrid.vercel.app/api/v1/mcp` (D-255, #123): solo lectura, Streamable HTTP y sin estado. `/desarrolladores` lo marca «Funciona hoy» y explica cómo conectarlo. El código es abierto (Apache-2.0) y también se puede arrancar en local con una base propia («Arrancarlo en local» en `32_mcp_server.md`). Solo el gran volumen con clave iría en el plan empresarial.

**Lo que no cambia:** nunca se venden datos de personas; solo zonas, y siempre agregadas.

---

## Planes y precios (hipótesis para validar)

| Plan | Para quién | Precio | Qué incluye |
|---|---|---|---|
| Gratis | todos: personas, ayuntamientos, inversores y empresas | 0 € | los datos, las zonas, «Qué falta», el suelo público para vivienda (D-246), la ficha de cada parcela de Madrid capital y la API pública sin clave. Todo está en producción. El MCP, de código abierto, también en remoto y sin clave (desde el 23 nov) |
| Plan empresarial | una promotora, un fondo, una consultora o una inmobiliaria | de 249 a 399 €/mes | carteras de parcelas, avisos de suelo nuevo, la API y el MCP a gran volumen con clave. **Nada de esto existe todavía** |
| Informes personalizados | quien quiere el trabajo hecho | de 490 a 1.500 € | un estudio de suelo a medida, revisado a mano antes de entregarlo |

**Lo de pago no recorta lo gratis.** Personas, ayuntamientos e inversores tienen la web entera, sin límites, y cada ficha de parcela; los planes de pago añaden lo que se usa a escala.

**De dónde salen los precios:**
- **Los del repo** (`docs/06_business/03_pricing.md`):
  - PRO Business, 249–399 €/mes: el plan empresarial toma esta horquilla;
  - informes de 490, 990 y 1.500 €: los informes personalizados.

  El plan Inversor del 19 nov (99–199 €/mes) desaparece: lo que incluía, la ficha de la parcela, pasa a ser gratis.
- **Referencia de mercado:** Nestra, que analiza en España la normativa urbanística de una parcela, cobra 175, 437,50 y 1.050 €/mes en sus planes Starter, Professional y Business. Son precios sin IVA y con pago anual; tiene además un plan gratuito y uno a medida ([precios de Nestra](https://www.nestra.es/precios), consultados el 19 nov).
- El análisis de mercado completo es un documento interno del 19 nov, fuera del repo, como el brief de diseño.

**Punto de equilibrio, con lo que sabemos:** la infraestructura mínima para poder cobrar cuesta unos 45 $/mes (ver «Coste a escala»), así que un solo plan empresarial la cubre. El tiempo de quien lo mantiene, no: media hora a la semana, medio día por trimestre y 2–3 días al año según «Mantenimiento con una sola persona» (estimación de D), más lo que pida cada informe. No hay todavía ningún cliente ni ninguna entrevista hecha.

**Regla del repo:** no se fija ningún precio sin entrevistas de disposición a pagar (`docs/08_validation/09_pricing_validation.md`).

## Qué falta para cobrar
- Construir lo de pago: las carteras, los avisos y la clave de la API y del MCP para gran volumen.
- Cuentas y cobro: la demo no tiene cuentas ni proyectos guardados.
- Pasar a un plan comercial: el gratuito de Vercel no admite cobrar (ver «Coste a escala»).
- Las entrevistas de disposición a pagar con inversores y promotores, y también con consultoras e inmobiliarias.

## Qué se dice en el pitch
- **Slide 3, columna «Viabilidad»:** «Gratis siempre: datos, zonas, «Qué falta», cada ficha de parcela y la API.», «Pagarán las empresas: plan empresarial e informes a medida.», «API y MCP abiertos y gratuitos, sin clave.» y, al pie, «Ninguna cifra la genera una IA: salen de cálculos deterministas sobre datos oficiales, cada una con su fuente.».
- **Slide 3, columna «Utilidad»:** «Inversores: busca tu parcela en Madrid capital y calcula si sale, con la demanda de su zona.».
- **Guion, bloque 5:** «¿Quién paga? Gratis siempre: los datos, las zonas, qué falta, cada ficha de parcela y la API. Pagarán las empresas un plan con carteras de parcelas y avisos de suelo nuevo, e informes a medida.».
- **«Pagarán», no «pagan»:** hoy no se cobra nada.
- **«API y MCP abiertos y gratuitos, sin clave»** desde el 23 nov por la tarde: el MCP ya funciona en remoto (D-255). Por la mañana decía «API abierta y gratuita; MCP de código abierto», porque el MCP solo funcionaba en local.
- **No se dice «de dónde vivir a dónde construir»** como algo hecho (revisión del #98): hoy ninguna parcela se cruza con la vivienda que le falta a su zona. Es el paso siguiente (pregunta 60).
- **Cobertura, sin exagerar:** la búsqueda por parcela, toda Madrid capital; el contexto completo del barrio y «Explorar barrios», el piloto de la M-40 (108 barrios). Nunca «toda la región».
- **El Catastro:** «datos de la parcela, elaborados a partir de los del Catastro», nunca «información catastral» (D-250 §1).
- **Las consultoras y las inmobiliarias** no van en la voz ni en la slide: se dice «las empresas». Si preguntan, están en las preguntas 6, 9 y 61 de `pitch/preguntas.md`.
- **Los precios** no se dicen en voz alta ni van en la slide. Si preguntan, están en la pregunta 6 de `pitch/preguntas.md`.

## Lo que decía el 19 nov (sustituido el 23 nov)
- Personas y ayuntamientos, gratis; pagarían los inversores y los promotores por su versión, con un plan Inversor (unos 99–199 €/mes), un plan Equipo (unos 399 €/mes) y el estudio a medida (490–1.500 €).
- La API y el MCP, gratis para todos. En la slide 3, «Gratis para personas y ayuntamientos. Pagarán inversores y promotores.» y «Código abierto, y API y MCP gratis.».
- Por qué cambia: el jurado simulado vio que lo que se quería cobrar ya era gratis en la API, y que «API y MCP gratis» prometía un MCP que solo funciona en local.

## Lo que decía el 12 nov (sustituido)
- En el pitch, los ayuntamientos pagaban un informe de «Qué falta» de 990–1.500 €, por contrato menor.
- Los primeros ingresos serían estudios de 490 a 1.500 € para promotoras y consultoras.
- La API y el MCP serían gratis sin uso comercial. Desde el 19 nov son gratis para todos.

El texto completo, con las tres opciones que se compararon, está en el historial de git de este fichero.

---

## Coste a escala

**Hoy cuesta 0 €/mes, pero no vale para cobrar.**
- La demo está en el plan gratuito de Vercel (Hobby), que es solo para uso personal y no comercial.
- La [guía de uso justo de Vercel](https://vercel.com/docs/limits/fair-use-guidelines) cuenta como comercial cualquier despliegue del que alguien saque dinero, incluido cobrar por el servicio o anunciarlo.
- La base está en el plan gratuito de Supabase: ocupa 100 MB de 500 (`evidence/gate-06/2026-11-11/supabase-sync-demo.txt`), y los proyectos gratuitos se pausan tras una semana sin uso.

**Mínimo para cobrar: unos 45 $/mes** ([precios de Vercel](https://vercel.com/pricing) y [de Supabase](https://supabase.com/pricing), consultados el 12 nov):

| Servicio | Plan | Precio | Qué incluye |
|---|---|---|---|
| Vercel | Pro, 1 desarrollador | 20 $/mes | 20 $ de crédito de uso al mes |
| Supabase | Pro | desde 25 $/mes | 8 GB de base, 250 GB de transferencia y 10 $ de cómputo (una instancia Micro) |

**Con más uso:**
- La base de datos no es el problema: 100 MB frente a 8 GB.
- Lo que crece es el cómputo de la API en Vercel:
  - 0,60 $ por millón de llamadas;
  - CPU activa desde 0,128 $ por hora;
  - memoria desde 0,0106 $ por GB y hora.
- Con unos miles de búsquedas al día debería caber en el crédito incluido, pero no está medido: hay que vigilar el panel de uso el primer mes.
- Con la API gratis para todos, ese cómputo es lo primero que se vigila. Hoy no pide claves; si el uso crece, se añade un límite por IP (`docs/04_technical_architecture/29_api_mcp_security_rate_limits.md`), y el gran volumen pasa a la clave del plan empresarial.
- La recarga de datos se hace en local (`make ingest`, `make supabase-sync`), así que no cuesta nada en la nube.

## Mantenimiento con una sola persona

**Lo que ya está automatizado:**
- **Cada mañana:** una prueba de humo contra la web pública, a las 7:30 (`.github/workflows/smoke-demo.yml`).
- **En cada cambio:** cinco comprobaciones de CI: Python, web, integración con PostGIS, auditoría de dependencias y secretos.
- **Con datos nuevos:** cada conjunto pasa un control de calidad antes de entrar. Si falla, no entra y lo dice (`evidence/gate-01/`).
- **Para todo lo demás:** una sola entrada, `make`. El despliegue y la vuelta atrás están documentados en `infra/deploy/README.md`.

**Calendario propuesto** (estimación de D, a medir):

| Cada | Qué | Tiempo estimado |
|---|---|---|
| Semana | Revisar la prueba de humo y los errores | 30 min |
| Trimestre | Recargar los horarios del Consorcio. Caducan: el del metro venció en mayo de 2026 | medio día |
| Año | Recargar la estadística anual (padrón, censo, alquiler, centros) y los catálogos del Ministerio de Sanidad. Volver a calcular «Qué falta» | 2–3 días |
| Estudio vendido | Revisar a mano el estudio del cliente antes de enviarlo | 2–4 h |

**Riesgo de depender de una persona y cómo se reduce:**
- el código es abierto (Apache-2.0);
- cada decisión está en `docs/00_index/01_decisions_log.md`;
- cada conjunto de datos se declara en un YAML del catálogo, y para añadir uno basta con escribir su YAML.
