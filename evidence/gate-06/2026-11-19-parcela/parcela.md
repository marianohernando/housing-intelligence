# Busca tu parcela (19 nov, D-250)

Rama `claude/f11-investor-parcel`. `/inversores` abre con «Busca tu parcela» (la referencia catastral, la dirección con los portales para que la persona elija el suyo, o un clic en el mapa) y la lista de barrios pasa detrás, como «Explorar barrios». `/inversores/parcela/{referencia}` es la ficha de una parcela de Madrid capital: datos de la parcela (elaborados a partir de los del Catastro), planeamiento del Ayuntamiento con su enlace oficial y el aviso de que no tiene valor jurídico, edificabilidad de partida (oficial, supuesta o sin dato), el barrio, la calculadora y las fuentes. Decisión: D-250. Textos: `pitch/textos_web.md` §11.

## Cómo se ha medido

- **Solo las 4 parcelas de demostración**, sin llamar a ninguna fuente: la API de la rama en el 8096 con `PARCEL_UPSTREAMS=false`, que sirve sus fichas guardadas (`fallback: "demo_snapshot"`, por eso cada ficha lleva el aviso «te enseñamos los datos guardados el 19 de noviembre de 2026»), y la base `housing` en **solo lectura** para el barrio.
- Web: `next dev` en el 3096 (sin `next build` local, por el disco), con `NEXT_PUBLIC_FEATURE_SEARCH=true` como en producción. El botón «N · 1 Insight» de las capturas es la barra de desarrollo de Next: no está en producción.
- Los dos ejemplos nuevos de `/desarrolladores` (`?rc=2122202VK4722A` y `/parcels/candidates?q=mendez alvaro 47`) se probaron aparte, una vez, con la API de la rama **en proceso y con las fuentes oficiales en vivo** (unas 5 peticiones): ficha completa, barrio de Atocha (piloto), sin `fallback` y con `Cache-Control` público; y un portal, el de esa referencia. Todo lo demás de esta carpeta es con `PARCEL_UPSTREAMS=false`.
- Las 4 parcelas: Méndez Álvaro 47–49 (2122202VK4722A, solar, edificabilidad oficial de VEDA: 13.121 m²), Almería 1 (3959601VK4735H, Portal del Suelo: 32.697 m²), Luis Misson 2 (0390314VK4709A, solar en NZ 4: sin coeficiente, «Sin dato») y Mayor 61 (9943003VK3794D, división horizontal de 6 inmuebles, NZ 1 grado 2º: 68 × 5 × 0,66 = 224 m², «Supuesto»). Sus fichas las escribió `scripts/parcel_demo_snapshot.py` el 19 nov con unas 20 peticiones en serie; en todo el desarrollo, unas 27 a los servicios oficiales.

## Capturas

- `1440-buscar.png`, `390-buscar.png`, `360-buscar.png`: la primera pantalla. En un móvil de 390 px se ve el campo de la referencia catastral.
- `1440-buscar-mapa.png`: el mapa pequeño, con el estilo de la app y su cita de OpenStreetMap a 16 px.
- `*-buscar-estados.png`: una referencia mal escrita («Una referencia catastral tiene 14, 18 o 20 letras y números.», sin llamar a la API) y la caja de direcciones sin red («El buscador de direcciones no responde ahora. Usa la referencia catastral o el mapa.»).
- `*-ficha-*.png|jpg`: las 4 fichas (las de 1440 px, enteras y reducidas a 900 px de ancho). En cada una, la cita del Catastro con su fecha, la del Ayuntamiento y el aviso urbanístico. La edificabilidad lleva su etiqueta («Dato», «Supuesto» o «Sin dato») y la calculadora empieza con esos m². Las 4 están en barrios del piloto (Atocha, Fuente del Berro, Berruguete y Palacio): la ficha del barrio de D-248 va debajo.
- `ficha-parcela-mayor.pdf`: «Guardar como PDF» de Mayor 61, con las fuentes, su dirección y los avisos.

## Comprobaciones

- `check-parcela.json` (`apps/web/scripts/check-parcela.mjs`): a 360, 390 y 1440 px, en la búsqueda, sus estados, las 4 fichas y la impresión, **0 textos de menos de 16 px, 0 objetivos de menos de 44 px, sin desborde horizontal y axe 0** (WCAG 2.2 AA), sin errores de consola.
- `check-inversores.mjs` (D-248) sigue verde con «Explorar barrios»: la lista, la ficha de Pinar del Rey, la calculadora con suelo y la impresión, a 390 y 1440 px.
- e2e (`infra/deploy/e2e/e2e_prod.mjs` contra `next dev`): **145/145 a 1440 px y 121/121 a 390 px** (antes 123 y 99; J9 suma 22 en cada uno y J8 pasa a 15 rutas).
- Golden (`scripts/golden_search.py`, `housing` en solo lectura): 10 de 10, con una salida idéntica byte a byte a la del código de la base (20b46d9).
- Python: `make lint`, `make typecheck`, las pruebas unitarias (60 de reglas puras, 51 de la API con respuestas sintéticas y 6 de la caché y el límite) y `make test-db` (173, con 3 nuevas del barrio).
