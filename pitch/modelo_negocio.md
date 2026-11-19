# Modelo de negocio

**Decisión de Mariano (19 nov), que sustituye a la del 12 nov.** Tres patas:
- **Personas: gratis.** Para quien busca dónde vivir, Vida Fácil es gratis y completa. La versión gratuita no se recorta para empujar a pagar (`CLAUDE.md` §3 y §16).
- **Ayuntamientos: gratis.** Cada ayuntamiento ve qué le falta a su municipio frente a municipios parecidos, dónde y a cuánta gente afecta, con la fuente de cada dato. Es «Qué falta», que ya está en producción en los 179 municipios y en los 21 distritos de Madrid (`GET /api/v1/gaps?level=municipio` y `?level=distrito`, 179 y 21 zonas, 19 nov). Les sirve para decidir dónde invertir primero, sin contrato ni licitación. Por ejemplo, Parla sale FALTA en farmacias: 2,0 por cada 10.000 habitantes a pie, frente a 4,2 en los demás municipios urbanos (`GET /api/v1/gaps/municipio/28106`, `gap-0.3`, 19 nov).
- **Inversores y promotores privados: pagarán, con un plan de precios.** Su versión, «Para inversores y promotores», está en la web desde el 19 nov, con un piloto en Madrid: la viabilidad sobre una parcela, con el contexto de su barrio (D-247 y D-248; despliegue de `396d8f6` verificado por C: `evidence/gate-06/2026-11-19-deploy/deploy-37-396d8f6-inversores.md`, PR #96). Durante el concurso es de acceso libre: sin cobro, sin cuentas y sin datos de nadie, y la web lo dice: «Plan Inversor (acceso libre durante el concurso)» (D-248 §1). El plan de precios es una hipótesis (ver «Qué falta para cobrar»).

**La API pública y el MCP: gratis para todos, igual que los datos** (otra decisión de Mariano, del 19 nov). También para empresas y ayuntamientos, que pueden meter «Qué falta» y el encaje de cada zona en sus propias herramientas o en un agente de IA. Lo que hay hoy:
- **La API pública** (`/api/v1`) está en producción y no pide claves. Tiene 13 rutas de datos y 2 de salud, con su descripción OpenAPI en `/api/v1/openapi.json` (leída por D en producción el 19 nov). 3 de las rutas de datos son de la versión para inversores (D-248), también gratis. Las rutas y sus contratos están en `docs/04_technical_architecture/31_public_api_routes.md`.
- **El MCP** tiene cinco herramientas de solo lectura: buscar zonas, qué falta, explicar una zona, encontrar una zona por su nombre y las fuentes de datos (D-225, `docs/04_technical_architecture/32_mcp_server.md`). Hoy funciona en local (`make mcp`) y no está desplegado. Como el código es abierto (Apache-2.0), cualquiera puede arrancarlo, pero necesita su propia base Postgres con los datos cargados («Arrancarlo en local» en `32_mcp_server.md`). Servirlo en remoto está planteado.

**Lo único de pago:** los planes para inversores (Inversor y Equipo) y el estudio a medida.

**Lo que no cambia:** nunca se venden datos de personas; solo zonas, y siempre agregadas.

---

## Planes y precios (hipótesis para validar)

| Plan | Para quién | Precio | Qué incluye |
|---|---|---|---|
| Gratis | personas y ayuntamientos | 0 € | la búsqueda, la ficha de cada zona, «Qué falta» y el suelo público para vivienda (D-246). Todo está en producción |
| API y MCP | todos, también empresas | 0 € | la API pública, en producción, y el MCP, hoy en local (ver arriba) |
| Inversor | un inversor o un promotor | unos 99–199 €/mes | lo que solo necesita quien invierte: la viabilidad sobre una parcela, con el contexto de su barrio (hoy en la web, de acceso libre durante el concurso), exportación a PDF y Excel, y avisos de suelo nuevo |
| Equipo | una promotora o un fondo con varias personas | unos 399 €/mes | lo del plan Inversor, con usuarios ilimitados, informes con su marca y carteras de parcelas |
| Estudio a medida | quien quiere el trabajo hecho | 490–1.500 € | un estudio de zona, revisado a mano antes de entregarlo |

**Lo de pago no recorta lo gratis.** Personas y ayuntamientos tienen la web entera, sin límites; los planes de pago añaden lo que solo usa quien invierte.

**De los planes de pago, hoy solo existe la versión para inversores, de acceso libre durante el concurso** (D-248): la viabilidad sobre una parcela, con el contexto de su barrio, que se guarda en PDF con la impresión del navegador. No hay cuentas, ni cobro, ni Excel, ni avisos. Se apoya en lo que ya es gratis: las fichas de zona, «Qué falta» y el suelo público.

**La API y el MCP no se cobran** (decisión de Mariano del 19 nov). Por eso ya no vale la línea «Enterprise/API, personalizado» de `docs/06_business/03_pricing.md`.

**De dónde salen los precios:**
- **Los del repo** (`docs/06_business/03_pricing.md`):
  - suscripción individual, 79–99 €/mes;
  - para equipos, 249–399 €/mes;
  - informes de 490, 990 y 1.500 €.

  El plan Equipo toma el techo de la horquilla de equipos y el estudio a medida, la de los informes. El plan Inversor sube el techo hasta 199 €/mes, más cerca de la referencia de mercado.
- **Referencia de mercado:** Nestra, que analiza en España la normativa urbanística de una parcela, cobra 175, 437,50 y 1.050 €/mes en sus planes Starter, Professional y Business. Son precios sin IVA y con pago anual; tiene además un plan gratuito y uno a medida ([precios de Nestra](https://www.nestra.es/precios), consultados el 19 nov).
- El análisis de mercado completo es un documento interno del 19 nov, fuera del repo, como el brief de diseño.

**Regla del repo:** no se fija ningún precio sin entrevistas de disposición a pagar (`docs/08_validation/09_pricing_validation.md`).

## Qué falta para cobrar
- Decidir qué sigue libre y qué pasa a ser de pago al acabar el concurso: hoy la versión para inversores es de acceso libre (D-248 §1).
- Cuentas y cobro: la demo no tiene cuentas ni proyectos guardados.
- Pasar a un plan comercial: el gratuito de Vercel no admite cobrar (ver «Coste a escala»).
- Las entrevistas de disposición a pagar con inversores y promotores.

## Qué se dice en el pitch
- **Slide 3, columna «Viabilidad»:** «Gratis para personas y ayuntamientos. Pagarán inversores y promotores.», y al pie, «Ya está, para inversores (piloto en Madrid): viabilidad sobre una parcela, con el contexto de su barrio.».
- **Guion, bloque 4:** «Gratis para personas y ayuntamientos: cada ayuntamiento ve qué le falta a su municipio. Nunca vendemos datos personales: solo zonas, siempre sumadas. Pagarán inversores y promotores, y su versión ya está en la web, con un piloto en Madrid: de dónde vivir a dónde construir, con la viabilidad sobre una parcela y el contexto de su barrio.».
- **«Pagarán», no «pagan»:** hoy no se cobra nada. La versión para inversores se describe de forma genérica hasta que esté en producción la versión por parcela exacta (datamad-10, 19 nov).
- **Los precios** no se dicen en voz alta ni van en la slide. Si preguntan, están en la pregunta 6 de `pitch/preguntas.md`.
- **La API y el MCP gratis para todos** no van, por ahora, en la voz ni en la slide: solo en las preguntas 1, 2 y 6. Se decidirá cuando esté en producción la página de documentación de la API y del MCP.

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
- Con la API gratis para todos, ese cómputo es lo primero que se vigila. Hoy no pide claves; si el uso crece, se añade un límite por IP (`docs/04_technical_architecture/29_api_mcp_security_rate_limits.md`).
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
