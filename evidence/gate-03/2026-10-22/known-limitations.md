# Gate 03 — limitaciones conocidas (2026-10-22)

- Gate 3 está iniciado, no cerrado: hay 12 features de las 75–125 objetivo del Sprint P1.
- Todas son municipales. Faltan features por sección censal y H3, y las de accesibilidad a pie (isócronas por red) que pide la documentación (card CORE-005).
- Los equipamientos se miden como cobertura por población (centros o plazas por habitante), no como acceso real. Un centro grande y uno pequeño cuentan igual.
- En municipios pequeños las ratios son inestables. Por debajo del umbral declarado en cada YAML se publican con confidence 0,5, sin ocultarlas.
- `tamano_medio_hogar` cuenta el tramo "5 o más" como 5 (confidence 0,9).
- El alquiler solo existe en los 37 municipios donde la fuente lo publica. El resto queda como desconocido, nunca como 0.
- Nacionalidad y sexo no pueden ser features (test que lo impide). Se descartó el porcentaje de población extranjera (D-189).
- No hay todavía tests de deriva ni de redundancia entre features (docs/02_data/35).
