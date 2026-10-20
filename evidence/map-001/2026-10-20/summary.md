# MAP-001 — Map shell sobre la geografía canónica (2026-10-20)

Primer resultado visible pedido por `START_HERE_ON_COMPUTER.md` §8: Madrid en mapa + datos reales + una microzona seleccionable + lineage visible.

- API: `GET /api/v1/geo/admin-units?level=municipio|distrito|barrio|seccion_censal&simplify_m=…` (FastAPI, SQL parametrizado, envelope con `data_version`).
- Web: `/map` (Next.js 16 + MapLibre GL 5.24, sin teselas de terceros). El frontend solo habla con la API.
- Verificado con Playwright: 179 municipios a escala regional (`01_region.png`); zoom a Madrid, clic en Sol → barrio 28079016, 0,45 km², procedencia "Comunidad de Madrid — CC BY 4.0 · versión 2026-10-20-37703ffcdfd0" (`02_madrid_selected.png`).
- Consola: solo un 404 de `favicon.ico`.
- Tests: unitarios de validación de la API, integración de la API contra la geografía publicada, unitarios de helpers web.

Limitaciones: la zona seleccionada no se resalta en el mapa; sin modo teclado ni lista alternativa (WCAG pendiente para Gate 6); payload de municipios ~330 KB sin vector tiles.
