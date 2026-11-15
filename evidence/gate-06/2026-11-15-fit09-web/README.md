# Fórmula `fit-0.9` en la web (línea B, F6, 15 nov)

Decisiones de Mariano en F5 (`FORMULA_DECISION`, opción A con el tope de 1 h), en la parte de la web. No depende de los números de la línea A: la web funciona con la API de hoy (`fit-0.8`, sin `match_band`) y con la de `fit-0.9`.

Cómo se comprobó:
- API de esta rama sobre la base local `housing` (datos del lote 4), en solo lectura (`default_transaction_read_only=on`). Responde `fit-0.8`.
- Web con `next build` y `next start`, con el buscador activo y esa API.
- Playwright con Chromium, a 1440 y a 390 px, y axe (WCAG 2.2 AA): `report.json`.
- e2e del repo (`infra/deploy/e2e/e2e_prod.mjs`) contra esta web: `e2e-local.txt`.
- Vitest (525 tests), ESLint y `tsc`, en verde.

**Revisión del PR #75 aplicada (R-01 a R-08, R-10 y R-12):** se rehicieron todas las capturas y el informe con el mismo build.

Todas las capturas salen de respuestas reales de la API local, salvo las `10_SIMULADO_*`: son la respuesta real al caso de ejemplo con `match_band` añadido y los tres hechos nuevos que la línea A pondrá en la tarjeta. Sirven para ver que la web los enseña; las cifras de `fit-0.9` no están en ninguna captura.

## Capturas

| Fichero | Qué se ve |
|---|---|
| `01c_ranking_plegado_empate_una_fila_*.png` | La lista plegada (5 filas): Fuencarral-El Pardo es la única a la vista de su empate y lleva «Empatan al 97 % (6 zonas)» (R-04) |
| `01_ranking_bandas_empates_casi_*.png`, `01b_casi_presupuesto_390.png` | El caso de ejemplo. Cada fila lleva la banda encima del número («Encaja muy bien» / «98 %»). Latina, Moratalaz, Ciudad Lineal y Puente de Vallecas van bajo «Empatan al 98 %», unidas por una barra; las seis siguientes, bajo «Empatan al 97 %». Arriba, una sola vez, «Precio de contratos firmados en 2024. Los anuncios de hoy suelen pedir más.». En «Casi encajan» no hay %: «Se pasa ≈ 90 €/mes de tu presupuesto» (Chamartín, 1.590 € frente a 1.500) |
| `02_tarjeta_latina_banda_empate_aviso2024_*.png` | La tarjeta de Latina: «Encaja muy bien» / «98 %», el aviso de 2024 bajo el alquiler, «La 1.ª que más encaja» y «Empata al 98 % con Moratalaz, Ciudad Lineal y Puente de Vallecas.», en el orden de la lista (R-10). El hecho del alquiler ya no repite «un anuncio de hoy puede pedir más» |
| `03_tarjeta_casi_chamartin_*.png` | La tarjeta de una zona de «Casi encajan»: sin %, con «Se pasa ≈ 90 €/mes de tu presupuesto» |
| `04_compra_casi_se_pasa_*.png` | Comprar con 400.000 €, pareja y nada más (CN-compra del banco): «Se pasa ≈ 6.000 €» (Arganzuela), «≈ 11.000 €» (Tetuán), «≈ 28.000 €» (Centro)… «de tu presupuesto». Al comprar no sale el aviso de 2024 |
| `05_trayecto_casi_tarda_*.png` | El ejemplo con «Tardar como mucho 30 min»: «Tarda ≈ 9 min más de lo que pides» (Latina, 38,5 min), «≈ 3 min» (Ciudad Lineal, 32,5)… |
| `06_casarrubuelos_nombre_*.png`, `06b_casarrubuelos_tarjeta_*.png` | Alquiler de 800 €, nada más: Casarrubuelos sale 1.º. En la tarjeta, a 1440 y a 390 px, el nombre va entero en una línea y la pastilla del % baja bajo él, porque no caben juntos (`flex-wrap`, sin `hyphens`; R-02) |
| `06c_barrios_empates_plegado_*.png`, `06d_barrios_empates_*.png` | «Los barrios que mejor encajan» de San Blas-Canillejas tras el ejemplo: Canillejas, Arcos y Simancas bajo «Empatan al 97 %», y Rosas y Amposta bajo «Empatan al 96 %», con la misma marca que la lista (R-05) |
| `07_sin_lugar_aviso_*.png` | Sin lugar de trabajo ni de familia y con «Toda la Comunidad» (1.200 €, «Sin escaleras» y «Transporte»): «¿Trabajas fuera de casa? Dinos dónde o elige «Madrid capital» en «¿Dónde?» y afinamos el orden.» |
| `08_sin_lugar_foco_trabajo_*.png` | Tras pulsar «Dinos dónde»: el foco en el campo de «Trabajo en», a la vista |
| `09_como_lo_calculamos_encaje_*.png` | «Cómo sale el % de encaje» con el método nuevo. Los topes del trayecto van sobre la ventana, como en la API: sin límite, más de 1 h y 1 h 30; con tu límite, el doble y el triple; los dos, solo con 3 días o más (R-01). La tabla de bandas sale de `lib/match.ts` (R-06). El «Ejemplo real» tiene la estructura nueva y todavía las cifras de `fit-0.8` (marcadas con un TODO solo en el código) |
| `10_SIMULADO_hechos_fit09_*.png` | **Simulada.** Los hechos «Faltan escuelas infantiles: como mucho 89 %», «Más de 1 h de trayecto: como mucho 74 %» y uno con un `topic` que la web no conoce («Tardas más de 1 h 30…»): salen todos, el último con el icono de «otro» |

## Comprobaciones (`report.json`)

- **Bandas:** salen de `match_band` si la API lo envía, y si no, del % con los umbrales 90, 75 y 60 (`lib/match.ts`, tests). Sin % no hay banda.
- **Empates:** las filas seguidas con el mismo % llevan «Empatan al {pct} %» encima, también en los barrios de un distrito. Cada una lo dice al lector de pantalla, con los nombres en el orden de la lista: el nombre accesible de Latina es «1 Latina Distrito de Madrid Encaja muy bien · 98 % de encaje, empata con Moratalaz, Ciudad Lineal y Puente de Vallecas…».
- **«Casi encajan»:** la cifra sale de `value − threshold` de la condición que falla. Sin esas cifras, «No cumple: {condición}», como antes. Nunca se inventa (tests).
- **Aviso de 2024:** una vez en la cabecera de la lista al alquilar y bajo el alquiler de la tarjeta; ninguna vez al comprar (`aviso_2024: 0`).
- **«Dinos dónde» y «¿Dónde?»:** llevan el foco al campo de «Trabajo en» y a la opción marcada de «¿Dónde?» (`foco_tras_*`).
- **Casarrubuelos:** el nombre en una línea y la pastilla debajo (`pastilla_bajo_el_nombre: true`), sin solaparse con el texto del nombre (`solapa: false`).
- **axe:** 0 incidencias en todas las pantallas, a 1440 y a 390 px. Ningún desborde horizontal ni error en la consola.
- **e2e:** 74 de 74 a 1440 y 48 de 48 a 390. El check de los hechos de la tarjeta acepta el hecho del alquiler sin «; un anuncio de hoy puede pedir más», que ahora dice el aviso (`factAsShown` de `infra/deploy/e2e/shown_text.mjs`, que usan también `check-search` y `check-qa`). Cuatro checks nuevos: el aviso de 2024 sale una vez en la lista y en la tarjeta al alquilar, «Comprar» llega a la API y al comprar el aviso no sale. Esos cuatro fallarán contra producción hasta que se despliegue este PR.
