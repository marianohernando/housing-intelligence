# Modelo de negocio: 3 opciones para elegir

Fichero de trabajo para que Mariano eligiera.

**Decisión de Mariano (12 nov):**
- **En el pitch:** la opción A, ayuntamientos (informe «Qué falta» por municipio, 990–1.500 €, por contrato menor).
- **Primeros ingresos:** la opción B, promotoras y consultoras (estudios de 490 a 1.500 €).
- **Siempre gratis:** la ciudadanía. La API y el MCP (opción C) también, sin uso comercial.
- **Coste en la slide 3:** «0 € hoy; unos 45 $/mes para uso comercial».

**Lo que no cambia en ninguna opción:**
- Para las personas, Vida Fácil es gratis y completa. La versión gratuita no se recorta para empujar a pagar (`CLAUDE.md` §3 y §16).
- Nunca se venden datos de personas: solo zonas y siempre agregados.

**Los precios son hipótesis.** Los de informes y suscripción salen de `docs/06_business/03_pricing.md`. Los de la API son propuesta de la línea D, sin respaldo en el repo. La regla del repo es no fijar ningún precio sin entrevistas de disposición a pagar (`docs/08_validation/09_pricing_validation.md`).

---

## Opción A · Ayuntamientos: informe «Qué falta» de su municipio

- **Cliente tipo:** la concejalía de servicios sociales, educación o urbanismo de un municipio urbano de la Comunidad de Madrid. Tiene datos sueltos y ningún técnico que los cruce.
- **La pregunta por la que paga:** «¿Qué nos falta frente a municipios como el nuestro, dónde y a cuánta gente afecta?». Por ejemplo, Parla sale FALTA en farmacias: 2,0 por cada 10.000 habitantes a pie, frente a 4,2 en los municipios urbanos (`GET /api/v1/gaps/municipio/28106`, 12 nov).
- **Qué recibe:**
  - un informe de 10–15 páginas con las 6 filas de «Qué falta», sus fuentes y sus límites, y la comparación con municipios parecidos;
  - una sesión de una hora para explicarlo;
  - el enlace a la vista de su municipio en la web.
- **Precio orientativo:**
  - **990–1.500 € por informe**, la horquilla de `03_pricing.md`;
  - seguimiento anual con los datos nuevos: hipótesis de unos 1.500 € al año, sin validar.
- **Por qué se puede vender:** queda muy por debajo del límite del contrato menor de servicios, 15.000 € sin IVA ([Ley 9/2017, art. 118](https://www.boe.es/buscar/act.php?id=BOE-A-2017-12902)). Un ayuntamiento puede contratarlo sin licitación.
- **Ventaja para el concurso:** es el uso más directo de los datos de la Comunidad para decidir dónde invertir.
- **Riesgo:** los ayuntamientos compran despacio y con presupuesto anual, y el mercado de la región es de 179 municipios.

## Opción B · Promotoras y consultoras: estudios de zona y suscripción

- **Cliente tipo:** una promotora o inmobiliaria mediana, o una consultora que hace estudios de mercado. Es el cliente inicial que fija `CLAUDE.md` §16.
- **La pregunta por la que paga:** «¿En qué zonas hay hogares que no encuentran lo que necesitan, y qué producto encaja?». Por ejemplo:
  - familias de 4 o más con pocas viviendas grandes;
  - mayores con pocas plazas cerca.
- **Qué recibe:**
  - primero, estudios a medida: se vende inteligencia antes de tener el producto de pago terminado (`docs/06_business/08_pro_gtm_and_offer_ladder.md`);
  - después, una suscripción con el mapa, comparativas entre zonas y exportación de datos.
- **Precio orientativo** (`03_pricing.md`):
  - estudio rápido de una zona, **490 €**; estudio completo, **990–1.500 €**;
  - suscripción individual, **79–99 €/mes**; para equipos, **249–399 €/mes**.
- **Riesgo:** la suscripción no existe todavía (en la demo no hay cuentas ni proyectos guardados), así que al principio solo se venden estudios.

## Opción C · Datos para software: API y MCP

- **Cliente tipo:** una empresa de software que quiere el «qué falta» o el encaje de cada zona dentro de su producto. Por ejemplo, una app de mudanzas, una aseguradora, una herramienta para gestores de residencias o un asistente de IA.
- **La pregunta por la que paga:** «Para esta zona, ¿qué servicios tiene a pie y qué le falta, con su fuente?». La respuesta llega en JSON o desde un agente.
- **Qué recibe:**
  - la API pública, que ya existe (`docs/04_technical_architecture/31_public_api_routes.md`);
  - el servidor MCP con cinco herramientas de solo lectura (`make mcp`), que hoy funciona en local.
- **Precio orientativo** (propuesta de D, sin validar):
  - gratis para uso no comercial e investigación, con un límite de llamadas;
  - de pago desde unos **99 €/mes** según volumen y uso comercial;
  - a medida a partir de ahí, como dice `03_pricing.md` para «Enterprise/API».
- **Riesgo:** hace falta un sistema de claves y de cobro por uso que hoy no existe. Además, el MCP tendría que funcionar en remoto y no solo en local.

---

## Coste a escala (las tres opciones)

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
| Informe vendido | Revisar a mano el informe del cliente antes de enviarlo | 2–4 h |

**Riesgo de depender de una persona y cómo se reduce:**
- el código es abierto (Apache-2.0);
- cada decisión está en `docs/00_index/01_decisions_log.md`;
- cada conjunto de datos se declara en un YAML del catálogo, y para añadir uno basta con escribir su YAML.

---

## Recomendación de D

- **A para el pitch, B para los primeros ingresos.**
  - **A** es la historia que el jurado entiende y la que más usa los datos de la Comunidad: «a este municipio le falta esto, y afecta a tantas personas».
  - **B** es el cliente que el proyecto ya eligió y el que puede pagar antes, con estudios sueltos.
- **C, más adelante:** cuando haya claves de API y el MCP en remoto.
- **Para la slide**, una sola línea: «Gratis para las personas. Pagan ayuntamientos y empresas por informes de lo que falta en su zona.». Va con el coste mínimo para cobrar, unos 45 $/mes.
- **Decide Mariano:** qué opción u opciones, y si los precios se dicen en la final o solo si preguntan.
