# «Entorno» de la zona (D-237) — evidencia del 14 nov

Web construida con `npm run build` (API local contra la copia de trabajo `housing_ruido`), capturada con Playwright a 1440 px y a 390 px (×2), con «Aparcamientos» pulsado en «Todos los centros».

| Fichero | Qué enseña |
|---|---|
| `distrito-usera-*.png` | Distrito de Madrid: ruido (29 % de día, 36 % de noche), aire de la estación más cercana de su zona (Plaza Elíptica, 31,7 µg/m³, a 1,6 km), aparcamiento público a unos 13 min y 2 disuasorios gratuitos con 351 plazas |
| `municipio-getafe-*.png` | Municipio: ruido «sin dato publicado», aire de su estación (25,6 µg/m³), aparcamiento público a unos 23 min y 6 disuasorios del CRTM con 2.446 plazas, todos gratuitos |
| `*-entorno-*.png` | El bloque «Entorno» solo (en el móvil, con la hoja abierta) |
| `*-aparcamientos-*.png` | «Todos los centros» con el tipo «Aparcamientos» y su lista: nombre, plazas y si es gratuito |
| `golden-search.txt` | `scripts/golden_search.py` contra `housing_ruido`: 9 de 9, con `ranked_order` y `near_miss_order` del ejemplo |
| `make-lint-typecheck-test-unit.txt` | `make lint typecheck test-unit` en verde |
| `make-test-db.txt` | `make test-db` contra una base de tests vacía con las migraciones: 144 en verde |

Gate 1 de los nueve datasets: `evidence/gate-01/2026-11-14/`.
