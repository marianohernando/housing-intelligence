# Gate 01 — limitaciones conocidas (2026-10-20)

- Alcance: solo `cm_secciones_censales` ha pasado Bronze → Silver → PostGIS. Los otros 16 P0 están registrados con licencia CLEAR pero sin pipeline.
- Geometría del seccionado de 2019 (la versión publicada en el portal de la Comunidad). El INE publica `seccionado_2025`; incorporarlo como actualización declarada es la card DATA-008.
- 3 barrios de Madrid (28079183, 28079193, 28079194) no tienen nombre en `cm_barrios_madrid` (128 barrios frente a 131 en el seccionado). Se publican sin nombre; no se inventa.
- Los distritos fuera de Madrid capital son distritos censales del INE, no distritos administrativos; su nombre es descriptivo.
- Gate 2 (Silver canónico / geo) queda cubierto en la parte geométrica (CRS, validez, bounds, contención, H3, golden points). Falta entity resolution y address resolution, que llegan con POIs y Catastro.
