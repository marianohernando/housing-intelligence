# zone_context_sample — fixtures de «Vivienda nueva y lo que viene» (D-241)

Recortes reales de las fuentes, coherentes con `admin_sample` (La Acebeda, Ajalvir y Madrid; en
Madrid, los distritos de Centro, Chamartín y Tetuán):

- `cm_transacciones_nueva_usada.csv`: «Transacciones inmobiliarias de vivienda nueva y de segunda
  mano, por municipio» del portal de datos abiertos de la Comunidad de Madrid (CC BY 4.0), años
  2025 y 2026, todos los indicadores (el pipeline se queda con la serie).
- `ayto_pgoum_desarrollo_ambitos.xlsx`: «PGOUM 97. Estado de desarrollo de los ámbitos» del
  Ayuntamiento de Madrid (datos.madrid.es, CC BY 4.0), versión de julio de 2026, filas de los
  distritos 1, 5 y 6 (el original es .xls; aquí va en .xlsx, que el mismo lector abre).
- `plan_vive.yaml`: la entrada de Madrid de `data/catalog/manual/plan_vive.yaml`, sin sus distritos.

La tabla del valor tasado por antigüedad está en `stat_sample/cm_valor_tasado_vivienda_antiguedad.csv`
(Madrid, La Acebeda y Ajalvir, 2024 y 2025).

Suelo público para vivienda (D-246):

- `cm_parcelas_portal_suelo.csv`: cinco filas reales de «Parcelas publicadas en el Portal del
  Suelo 4.0» (portal de datos abiertos de la CM, CC BY 4.0, 18 nov 2026): tres residenciales de
  Madrid (venta, concesión y el régimen «D», que la Comunidad no explica), una terciaria de Madrid
  (fuera de alcance) y una residencial de Morata de Tajuña sin superficie edificable, pasada a
  Ajalvir para que caiga en la geografía de muestra. La columna `contacto_direccion` va vacía: trae
  nombres, teléfonos y correos de personas, y el pipeline no la lee.
- `portal_suelo_madrid_puntos.yaml`: los puntos de las tres de Madrid, puestos en secciones de la
  muestra (Almenara y Castillejos, en Tetuán), no donde están de verdad.
