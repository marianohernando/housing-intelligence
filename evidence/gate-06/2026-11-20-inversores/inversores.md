# Para inversores y promotores (20 nov, D-248)

Rama `claude/f9-investor-app`. La sección `/inversores` lista los barrios piloto (Madrid capital dentro de la M-40, D-247) y `/inversores/{barrio}` da la ficha de un barrio con la calculadora de viabilidad v0. Lleva la etiqueta «Plan Inversor (acceso libre durante el concurso)», sin cobro ni login. Decisión: D-248. Textos: `pitch/textos_web.md` §11.

**Cómo se ha medido.** Con `next build` (`NEXT_PUBLIC_FEATURE_SEARCH=true`, como en producción) y `next start` en el 3094, contra la API de la rama en el 8094. La base es `housing_inv_b`, una copia completa de `housing` a la que se han añadido dos cosas:
- el dataset de los visados (`cm_visados_presupuesto_obra`, versión `2026-11-19-37e839d23fbf`) y la feature `pem_visado_vivienda_bloque_m2`;
- la lista de los 108 barrios piloto, sacada del YAML de la línea A sin commitear.

Las features de la línea A (comercio, remanente y suelo vacante) aún no están: la API las devuelve `null`, con su motivo y un aviso, y la web dice «Sin dato».

## Capturas (1440 y 390 px)

- `*-lista.png`: los 108 barrios por distrito. Cada uno con lo que falta en el distrito (el distrito se nombra: «Falta en el distrito de Carabanchel: escuelas infantiles…»), sus parcelas públicas y su precio estimado. A 390 px, la primera pantalla.
- `*-ficha.png`: **Pinar del Rey** (Hortaleza), con 4 parcelas del Portal del Suelo. Las secciones van en orden: quién vive aquí, precios, qué falta (cada fila con «Dato del distrito de Hortaleza»), suelo, calculadora y fuentes.
  - Cada cifra lleva su marca («Dato», «Supuesto», «Lo pones tú») y su fuente.
  - A 1440 px, la página entera; a 390 px, la primera pantalla.
- `*-ficha-suelo.png`: las 4 parcelas con sus m² edificables, su gestor y «Ver en el visor de la Comunidad».
- `1440-calculadora.png`: la calculadora entera.
  - Arriba, el suelo: la parcela R25-L, de 12.192 m², elegida por defecto.
  - Los supuestos, con su fuente y su desglose.
  - Junto al PEM, «Mínimo oficial (PEM visado); el coste de mercado suele ser mayor: ajusta el coeficiente».
- `*-escenarios-sin-suelo.png`: sin precio del suelo **no hay veredicto**. El titular de cada escenario es lo máximo que se puede pagar por el suelo: 35,83 millones de € (2.939 €/m² edificable) en el base, 3.364 en el optimista y 2.513 en el pesimista. Debajo, la comprobación de demanda: con la renta media del barrio (41.018 €), la hipoteca sería el 42 % y el alquiler el 37 %, los dos por encima del 30 %.
- `*-escenarios-con-suelo.png`: con el suelo a 3.200 €/m² edificable, el semáforo (icono, palabra y color): base 15,1 % «Ajustar», optimista 22,8 % «Sale» y pesimista 5,6 % «No sale».
- `*-impresion.png` y `ficha-inversores.pdf`: la vista de «Guardar como PDF».
  - Sin la cabecera ni los botones.
  - Con la fecha de generación, la de los datos, las fuentes con su dirección y los avisos.
  - Con los desgloses abiertos.

## Comprobaciones

- `apps/web/scripts/check-inversores.mjs` (`check-inversores.json`) mide la lista, la ficha, la calculadora con suelo y la impresión, a 390 y 1440 px:
  - **0 textos de menos de 16 px** y **0 objetivos de menos de 44 px** en el contenido de la sección; el pie común lo mide `check-ux-mobile.mjs`.
  - Sin desborde horizontal y **axe 0** (WCAG 2.2 AA).
  - Sin errores de consola.
  - También comprueba que sin precio del suelo no sale ningún «Sale», «Ajustar» ni «No sale».
- `infra/deploy/e2e/e2e_prod.mjs --base http://localhost:3094` (`e2e-report.json`): **escritorio 1440 px 116/116 y móvil 390 px 92/92**, sin cambiar el e2e.

## Invariante

`scripts/golden_search.py` contra `housing_inv_b` (con el dataset y la feature nuevos): **10 de 10**. Ni `/search` ni `/gaps` leen nada de D-248.

## Tests

- `make lint typecheck test-unit`: limpios.
- Tests del dominio con casos a mano: uno que sale, uno de «ajustar», uno que no sale y el valor residual sin suelo.
- Vitest de `lib/investors.ts`.
- `make test-db` sobre una base de tests vacía con las migraciones (`housing_inv_b_test`): **162 tests**, entre ellos los 5 de `tests/integration/test_api_investors.py`, incluida la carga del dataset de los visados y su paso por `/datasets`.
- Números: Python 1084 (unitarios y de datos) y vitest 591.
