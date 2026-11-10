# MAP-002 — Indicadores municipales y equipamientos en el mapa (2026-10-22)

- API: `GET /api/v1/features`, `GET /api/v1/features/{id}/values`, `GET /api/v1/places?category=…` (SQL parametrizado, envelope con `data_version` = versiones de dataset usadas).
- Web `/map`: selector de 12 indicadores públicos, coropleta por municipio (cuantiles sin cortes repetidos), leyenda textual, "sin dato publicado (no es cero)" en gris, capas activables de colegios, atención primaria y servicios para mayores, procedencia del indicador con versiones exactas.
- Verificado con Playwright:
  - `01_renta_per_capita.png`: renta per cápita 2023 de los 179 municipios.
  - `02_alquiler_unknowns.png`: alquiler €/m²; los municipios sin dato publicado salen en gris, nunca como 0.
  - `03_mayores_madrid.png`: plazas de residencia por 100 mayores + puntos de servicios para mayores; Madrid = 2,88 (2025).
- Consola del navegador: 0 errores y 0 avisos.

Limitaciones: payload de colegios ~1,2 MB en GeoJSON (vector tiles pendiente, MAP-003); sin navegación por teclado del mapa (la información está también en el panel); coropleta solo municipal.
