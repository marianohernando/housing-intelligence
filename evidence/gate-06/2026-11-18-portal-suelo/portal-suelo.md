# Suelo público para vivienda (18 nov, D-246)

Rama `claude/f8-portal-suelo`. Idea de producto de Mariano: además de «dónde vivir», «dónde construir». Las parcelas residenciales del Portal del Suelo 4.0 (portal de datos abiertos de la Comunidad de Madrid) en «Vivienda nueva y lo que viene» de la pantalla de zona, dentro de «Más datos de la zona». Contexto: no puntúa. Decisión: D-246. Textos: `pitch/textos_web.md` (`zona.vivienda_nueva.suelo*`).

**Cómo se ha medido.** Un `npm ci` y un `npm run build` (el primer intento lo cortó el aviso de seguridad de Next; el segundo terminó con la caché del primero), con `next start` en el 3092 contra la API de la rama en el 8092 sobre `housing_suelo`, una copia completa de `housing` con el dataset cargado y la feature calculada (versión `2026-11-18-b96deb8ff739`).

## Qué se ve

- **Majadahonda** (municipio, `01-majadahonda-*.png`): «Suelo público para vivienda: 101 parcelas, 29.312 m² edificables.», la nota, la fuente con su fecha y «Ver las 101 parcelas» plegado; abierto (`01-majadahonda-lista-*.png`), cada parcela con su localización y parcela, sus m², «En venta» y «Ayuntamiento de Majadahonda», y «Ver en el visor de la Comunidad».
- **Vicálvaro** (distrito, `02-vicalvaro-*.png`): «16 parcelas, 67.808 m² edificables», debajo de los ámbitos del Plan General en obras; en la lista, las de Los Berrocales en concesión y las de la Agencia de Vivienda Social sin régimen (su código, D, no lo explica la Comunidad).
- **Puente de Vallecas** (distrito sin parcelas, `03-puente-de-vallecas-sin-parcelas-*.png`): la tarjeta como antes, sin la línea ni «0 parcelas».
- A 1440 px, la tarjeta; a 390 px, lo que enseña la hoja abierta con la línea arriba.

## Comprobaciones

- `capture-portal-suelo.mjs` (`capturas-portal-suelo.json`): **52/52** a 1440 y 390 px. La línea dice el número de parcelas y los m² de la respuesta de la API para esa zona; fuente y fecha; la lista empieza plegada; un enlace al visor por parcela, en una pestaña nueva; régimen solo para V y C; ningún texto de menos de 16 px ni objetivo de menos de 44 px en la tarjeta con la lista abierta; ningún color de alarma; nada en la tarjeta esencial; **axe 0** con la lista abierta; nada en la zona sin parcelas.
- `apps/web/scripts/check-ux-mobile.mjs --widths 390 --counts ""` (`tamanos-portal-suelo.json`): **0 textos de menos de 16 px y 0 objetivos de menos de 44 px** en todas las pantallas del recorrido; los 3 controles del mapa, aparte, como siempre. **axe: 0 incidencias** a 390 y 1440 px.
- `infra/deploy/e2e/e2e_prod.mjs --base http://localhost:3092`: **escritorio 1440 px 116/116, móvil 390 px 92/92** (`e2e/e2e-report.json`), sin cambios en el e2e ni en `shown_text.mjs`: los textos nuevos son de la web, no de la API.

## Invariante

- `scripts/golden_search.py` contra `housing_suelo`: **10 de 10**, con `ranked_order` y `near_miss_order` del ejemplo.
- Las 9 búsquedas del golden y la de barrios en los 21 distritos, byte a byte, con y sin las 331 filas de `suelo_publico_vivienda_m2` (borradas en una transacción que se deshace): **30 de 30 iguales**.

## Tests

`make lint typecheck test-unit` (Python 1052, vitest 570) y `make test-db` (157) limpios, con ruff, pyright, eslint y tsc.
