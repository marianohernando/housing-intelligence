# Fórmula `fit-0.9` en la web (línea B, F6, 15 nov)

Decisiones de Mariano en F5 (`FORMULA_DECISION`, opción A con el tope de 1 h), en la parte de la web. No depende de los números de la línea A: la web funciona con la API de hoy (`fit-0.8`, sin `match_band`) y con la de `fit-0.9`.

Cómo se comprobó:
- API de esta rama sobre la base local `housing` (datos del lote 4), en solo lectura (`default_transaction_read_only=on`). Responde `fit-0.8`.
- Web con `next build` y `next start`, con el buscador activo y esa API.
- Playwright con Chromium, a 1440 y a 390 px, y axe (WCAG 2.2 AA): `report.json`.
- e2e del repo (`infra/deploy/e2e/e2e_prod.mjs`) contra esta web: `e2e-local.txt`.
- Vitest (521 tests), ESLint y `tsc`, en verde.

Todas las capturas salen de respuestas reales de la API local, salvo las `10_SIMULADO_*`: son la respuesta real al caso de ejemplo con `match_band` añadido y los tres hechos nuevos que la línea A pondrá en la tarjeta. Sirven para ver que la web los enseña; las cifras de `fit-0.9` no están en ninguna captura.

## Capturas

| Fichero | Qué se ve |
|---|---|
| `01_ranking_bandas_empates_casi_*.png`, `01b_casi_presupuesto_390.png` | El caso de ejemplo. Cada fila lleva la banda encima del número («Encaja muy bien» / «98 %»). Latina, Moratalaz, Ciudad Lineal y Puente de Vallecas van bajo «Empatan al 98 %», unidas por una barra; las seis siguientes, bajo «Empatan al 97 %». Arriba, una sola vez, «Precio de contratos firmados en 2024. Los anuncios de hoy suelen pedir más.». En «Casi encajan» no hay %: «Se pasa ≈ 90 €/mes de tu presupuesto» (Chamartín, 1.590 € frente a 1.500) |
| `02_tarjeta_latina_banda_empate_aviso2024_*.png` | La tarjeta de Latina: «Encaja muy bien» / «98 %», el aviso de 2024 bajo el alquiler, «La 1.ª que más encaja» y «Empata al 98 % con Puente de Vallecas, Moratalaz y Ciudad Lineal.». El hecho del alquiler ya no repite «un anuncio de hoy puede pedir más» |
| `03_tarjeta_casi_chamartin_*.png` | La tarjeta de una zona de «Casi encajan»: sin %, con «Se pasa ≈ 90 €/mes de tu presupuesto» |
| `04_compra_casi_se_pasa_*.png` | Comprar con 400.000 €, pareja y nada más (CN-compra del banco): «Se pasa ≈ 6.000 €» (Arganzuela), «≈ 11.000 €» (Tetuán), «≈ 28.000 €» (Centro)… «de tu presupuesto». Al comprar no sale el aviso de 2024 |
| `05_trayecto_casi_tarda_*.png` | El ejemplo con «Tardar como mucho 30 min»: «Tarda ≈ 9 min más de lo que pides» (Latina, 38,5 min), «≈ 3 min» (Ciudad Lineal, 32,5)… |
| `06_casarrubuelos_nombre_*.png`, `06b_casarrubuelos_tarjeta_*.png` | Alquiler de 800 €, nada más: Casarrubuelos sale 1.º. En la tarjeta, a 1440 y a 390 px, el nombre corta con guion por su sílaba («Casarru-buelos», `lang="es"` y `hyphens: auto`) y no se solapa con la pastilla |
| `07_sin_lugar_aviso_*.png` | Sin lugar de trabajo ni de familia y con «Toda la Comunidad» (1.200 €, «Sin escaleras» y «Transporte»): «¿Trabajas fuera de casa? Dinos dónde o elige «Madrid capital» en «¿Dónde?» y afinamos el orden.» |
| `08_sin_lugar_foco_trabajo_*.png` | Tras pulsar «Dinos dónde»: el foco en el campo de «Trabajo en», a la vista |
| `09_como_lo_calculamos_encaje_*.png` | «Cómo sale el % de encaje» con el método nuevo. El «Ejemplo real» tiene la estructura nueva y todavía las cifras de `fit-0.8` (marcadas con un TODO solo en el código) |
| `10_SIMULADO_hechos_fit09_*.png` | **Simulada.** Los hechos «Faltan escuelas infantiles: como mucho 89 %», «Más de 1 h de trayecto: como mucho 74 %» y uno con un `topic` que la web no conoce («Tardas más de 1 h 30…»): salen todos, el último con el icono de «otro» |

## Comprobaciones (`report.json`)

- **Bandas:** salen de `match_band` si la API lo envía, y si no, del % con los umbrales 90, 75 y 60 (`lib/match.ts`, tests). Sin % no hay banda.
- **Empates:** las filas seguidas con el mismo % llevan «Empatan al {pct} %» encima. Cada una lo dice al lector de pantalla: el nombre accesible de Latina es «1 Latina Distrito de Madrid Encaja muy bien · 98 % de encaje, empata con Puente de Vallecas, Moratalaz y Ciudad Lineal…».
- **«Casi encajan»:** la cifra sale de `value − threshold` de la condición que falla. Sin esas cifras, «No cumple: {condición}», como antes. Nunca se inventa (tests).
- **Aviso de 2024:** una vez en la cabecera de la lista al alquilar y bajo el alquiler de la tarjeta; ninguna vez al comprar (`aviso_2024: 0`).
- **«Dinos dónde» y «¿Dónde?»:** llevan el foco al campo de «Trabajo en» y a la opción marcada de «¿Dónde?» (`foco_tras_*`).
- **Casarrubuelos:** el nombre en dos líneas, con `hyphens: auto` y `lang="es"`, y su borde derecho a la izquierda de la pastilla (`solapa: false`).
- **axe:** 0 incidencias en todas las pantallas, a 1440 y a 390 px. Ningún desborde horizontal ni error en la consola.
- **e2e:** 70 de 70 a 1440 y 44 de 44 a 390. El check de los hechos de la tarjeta acepta el hecho del alquiler sin «; un anuncio de hoy puede pedir más», que ahora dice el aviso; pasa también contra la web de producción de hoy.
