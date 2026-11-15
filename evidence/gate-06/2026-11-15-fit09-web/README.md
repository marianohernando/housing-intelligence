# Fórmula `fit-0.9` en la web (línea B, F6, 15 nov)

Decisiones de Mariano en F5 (`FORMULA_DECISION`, opción A con el tope de 1 h), en la parte de la web. La web funciona con la API de `fit-0.9` (PR #76, `match_band`) y con la anterior (`fit-0.8`, sin el campo: la banda sale del %).

Cómo se comprobó, tras integrar la API de `fit-0.9` (PR #76) en esta rama:
- API de esta rama sobre la base local `housing_fit09` (datos del lote 4 y el factor 1,155 de D-243 §11), en solo lectura (`default_transaction_read_only=on`). Responde `fit-0.9`.
- Web con un solo `next build` y `next start`, con el buscador activo y esa API.
- Playwright con Chromium, a 1440 y a 390 px, y axe (WCAG 2.2 AA): `report.json`.
- e2e del repo (`infra/deploy/e2e/e2e_prod.mjs`) contra esta web: `e2e-local.txt`.
- Vitest (525 tests), ESLint y `tsc`, en verde.

**Con la API de `fit-0.9` se rehicieron las capturas donde cambian las cifras o lo que se ve.** No se rehicieron `03_*`, `04_*`, `06_casarrubuelos_nombre_1440.png` ni `09_como_lo_calculamos_encaje_390.png`: con la API nueva salen con el mismo texto y las mismas cifras (solo cambia el color del mapa que se trasluce detrás de la tarjeta). Las `10_SIMULADO_*` se sustituyen por `10_hechos_limite_fit09_*`, con un hecho real de la API. Todas las capturas salen de respuestas reales de la API local.

## El caso de ejemplo con `fit-0.9`

La respuesta de la API coincide con el golden (`golden_family`) y con D-243 §9:
- encajan 42 de las 199 zonas, 157 no cumplen y ninguna sale sin datos; de las 42, 12 «muy bien», 5 «bien», 13 «regular» y 12 «poco»;
- top 10: Puente de Vallecas 94, Latina 94, Usera 93, Moratalaz 93, Tetuán 92, Ciudad Lineal 92, Villaverde 92, Carabanchel 90, Coslada 90 y Leganés 90;
- «Casi encajan», todas por el presupuesto y sin banda: Chamartín, Arganzuela, Centro, Chamberí y Retiro;
- «¿Y si cambias algo?»: +5 min a pie hasta el colegio, 49 zonas más; +150 €/mes, 3.

## Capturas

| Fichero | Qué se ve |
|---|---|
| `01c_ranking_plegado_empate_una_fila_*.png` | La lista plegada (5 filas): Puente de Vallecas y Latina bajo «Empatan al 94 %», Usera y Moratalaz bajo «Empatan al 93 %», y Tetuán, la única a la vista de su empate, con «Empatan al 92 % (3 zonas)» (R-04) |
| `01_ranking_bandas_empates_casi_*.png`, `01b_casi_presupuesto_390.png` | El caso de ejemplo con las 10 primeras. Cada fila lleva la banda de `match_band` encima del número («Encaja muy bien» / «94 %»), y los empates van unidos por una barra: «Empatan al 94 %», «al 93 %», «al 92 %» y «al 90 % (5 zonas)». Arriba, una sola vez, el aviso de 2024. En «Casi encajan» no hay %: «Se pasa ≈ 90 €/mes» (Chamartín), «≈ 20 €» (Arganzuela), «≈ 190 €» (Centro), «≈ 230 €» (Chamberí) y «≈ 30 €» (Retiro) «de tu presupuesto» |
| `02_tarjeta_latina_banda_empate_aviso2024_*.png` | La tarjeta de Latina: «Encaja muy bien» / «94 %», el aviso de 2024 bajo el alquiler, «La 2.ª que más encaja» y «Empata al 94 % con Puente de Vallecas.» El hecho del alquiler no repite «un anuncio de hoy puede pedir más» |
| `03_tarjeta_casi_chamartin_*.png` | La tarjeta de una zona de «Casi encajan»: sin %, con «Se pasa ≈ 90 €/mes de tu presupuesto». Sin cambios con `fit-0.9` |
| `04_compra_casi_se_pasa_*.png` | Comprar con 400.000 €, pareja y nada más (CN-compra del banco): «Se pasa ≈ 6.000 €» (Arganzuela), «≈ 11.000 €» (Tetuán), «≈ 28.000 €» (Centro)… «de tu presupuesto». Al comprar no sale el aviso de 2024. Sin cambios con `fit-0.9` |
| `05_trayecto_casi_tarda_*.png` | El ejemplo con «Tardar como mucho 30 min»: «Tarda ≈ 11 min más de lo que pides» (Puente de Vallecas), «≈ 9 min» (Latina), «≈ 10 min» (Moratalaz), «≈ 14 min» (Usera) y, por el presupuesto, Chamartín |
| `06_casarrubuelos_nombre_*.png`, `06b_casarrubuelos_tarjeta_*.png` | Alquiler de 800 €, nada más: Casarrubuelos sale 1.º, al 100 % y empatado con 107 zonas más. Con el factor 1,155 su alquiler pasa a ≈ 490 €/mes (entre 420 y 670 €). El nombre va entero en una línea y la pastilla del % baja bajo él (`flex-wrap`, sin `hyphens`; R-02) |
| `06c_barrios_empates_plegado_*.png`, `06d_barrios_empates_*.png` | «Los barrios que mejor encajan» de Latina tras el ejemplo (con `fit-0.9`, San Blas-Canillejas ya no está entre las 10 primeras): Puerta del Ángel y Lucero bajo «Empatan al 95 %», Los Cármenes y Campamento bajo «al 94 %» (plegado, «al 94 % (2 barrios)»), Aluche y Águilas bajo «al 93 %», y Cuatro Vientos, «Encaja bien» al 88 %, con la misma marca que la lista (R-05) |
| `07_sin_lugar_aviso_*.png` | Sin lugar de trabajo ni de familia y con «Toda la Comunidad» (1.200 €, «Sin escaleras» y «Transporte»): «¿Trabajas fuera de casa? Dinos dónde o elige «Madrid capital» en «¿Dónde?» y afinamos el orden.» Arriba, Parla al 94 % |
| `08_sin_lugar_foco_trabajo_*.png` | Tras pulsar «Dinos dónde»: el foco en el campo de «Trabajo en», a la vista |
| `09_como_lo_calculamos_encaje_*.png`, `09b_ejemplo_real_390.png` | «Cómo sale el % de encaje» con el método nuevo: los topes del trayecto sobre la ventana (R-01) y la tabla de bandas de `lib/match.ts` (R-06). El «Ejemplo real» lleva las cifras de `fit-0.9`: 42 zonas y sus bandas, el empate de arriba, por qué va primera Puente de Vallecas, los puntos que pierde Latina (unos 6: 3 por el trayecto, 1,1 por el colegio, 1,1 por la parada y 0,9 por el centro de salud) y «Casi encajan». A 390 px, `09b` enseña el ejemplo; `09` (la cabecera del apartado) no cambia |
| `10_hechos_limite_fit09_*.png` | Un hecho de tope real de la API (D-243 §3): una persona con 500 €, «Transporte» y trabajo en Vicálvaro (Cercanías), 5 días. Zarzalejo, «Encaja poco» / «32 %», con «No llegas a Vicálvaro (Cercanías) a las 9:00 en transporte público: el encaje se queda en la mitad» primero, con el icono del trayecto |

## Comprobaciones (`report.json`)

- **Bandas:** salen de `match_band` de la API, el tipo del contrato generado. Si llega `null` o falta, del % con los umbrales 90, 75 y 60, y solo en zonas que cumplen todo: una con `passes_all: false` no lleva banda (`lib/match.ts`, tests). Sin % no hay banda.
- **Empates:** las filas seguidas con el mismo % llevan «Empatan al {pct} %» encima, también en los barrios de un distrito. Cada una lo dice al lector de pantalla: el nombre accesible de la 1.ª es «1 Puente de Vallecas Distrito de Madrid Encaja muy bien 94 % · 94 % de encaje, empata con Latina…».
- **«Casi encajan»:** la cifra sale de `value − threshold` de la condición que falla. Sin esas cifras, «No cumple: {condición}», como antes. Nunca se inventa (tests).
- **Aviso de 2024:** una vez en la cabecera de la lista al alquilar y bajo el alquiler de la tarjeta; ninguna vez al comprar (`aviso_2024: 0`).
- **«Dinos dónde» y «¿Dónde?»:** llevan el foco al campo de «Trabajo en» y a la opción marcada de «¿Dónde?» (`foco_tras_*`).
- **Casarrubuelos:** el nombre en una línea y la pastilla debajo (`pastilla_bajo_el_nombre: true`), sin solaparse con el texto del nombre (`solapa: false`).
- **«Cómo lo calculamos»:** sin «TODO» en la página (`todo_visible: false`).
- **axe:** 0 incidencias en todas las pantallas, a 1440 y a 390 px. Ningún desborde horizontal ni error en la consola.
- **e2e:** 74 de 74 a 1440 y 48 de 48 a 390, contra esta web y la API de `fit-0.9`. Los cuatro checks del aviso de 2024 fallarán contra producción hasta que se despliegue este PR.
- **`check-search`** (`on`), con los puertos de esta prueba: sin fallos. La tarjeta de Puente de Vallecas dice «Empata al 94 % con Latina.».
