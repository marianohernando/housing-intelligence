# «Entorno» de la zona (D-237) — evidencia del 14 nov, con la revisión del PR #65

Web construida con `npm run build` (API local contra la copia de trabajo `housing_ruido`), capturada con Playwright a 1440 px y a 390 px (×2), con «Aparcamientos» pulsado en «Todos los centros».

| Fichero | Qué enseña |
|---|---|
| `distrito-usera-*.png` | Distrito de Madrid: ruido (14 % de las calles de día, 32 % de noche), aire de la estación de fondo más cercana de su zona (Méndez Álvaro, 21,2 µg/m³, a 2,7 km), aparcamiento público a unos 13 min y 2 disuasorios gratuitos con 351 plazas |
| `municipio-getafe-*.png` | Municipio: ruido «sin dato publicado», aire de su estación de tráfico (25,6 µg/m³), aparcamiento público a unos 23 min y 6 disuasorios del CRTM con 2.446 plazas, todos gratuitos |
| `*-entorno-*.png` | El bloque «Entorno» solo (en el móvil, con la hoja abierta) |
| `*-aparcamientos-*.png` | «Todos los centros» con el tipo «Aparcamientos» y su lista: nombre, plazas y si es gratuito |
| `ruido-contraste.md` | El ruido antes y después de la revisión (Lden en los cruces → Ld cada 10 m), frente a la tabla 7 de la memoria del MER 2021 |
| `golden-search.txt` | `scripts/golden_search.py` contra `housing_ruido`: 10 de 10, con `ranked_order` y `near_miss_order` del ejemplo |
| `make-lint-typecheck-test-unit.txt` | `make lint typecheck test-unit` en verde (932 de Python, 485 de vitest) |
| `make-test-db.txt` | `make test-db` contra una base de tests vacía con las migraciones: 151 en verde |

Gate 1 de los nueve datasets: `evidence/gate-01/2026-11-14/`.
