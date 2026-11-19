# investor_sample — fixtures de los datos para inversores (D-247)

- `ayto_censo_locales_actividades.csv`: 33 filas reales (25 locales) del fichero de actividades
  del «Censo de locales, sus actividades y terrazas de hostelería y restauración» del
  Ayuntamiento de Madrid (datos.madrid.es, CC BY 4.0, carga del 17 nov 2026), de los barrios de
  Palacio y Castillejos y una de Embajadores: farmacias, fruterías, autoservicios, bares,
  locales cerrados, en uso de vivienda y de baja, interiores, agrupados, «puerta de calle
  asociado», un local con varios epígrafes y uno con el epígrafe «SIN ASIGNAR». Solo las
  columnas que lee el pipeline: sin rótulo, direcciones ni coordenadas.
- `ayto_edificabilidad_remanente_ambitos.xlsx`: las 7 filas reales de Tetuán de «PGOUM 97.
  Edificabilidad remanente en ámbitos» (Ayuntamiento de Madrid, datos.madrid.es, CC BY 4.0,
  julio de 2026). El original es .xls; aquí va en .xlsx, que el mismo lector abre.
- `veda_remanente_puntos.yaml`: los puntos de esos 7 ámbitos, puestos en secciones de Tetuán de la
  muestra, no donde están de verdad (uno con el 70 % de su superficie en su barrio, para la nota).
- `inversores_barrios_m40.yaml`: un anillo de muestra con los centroides de esas secciones, no la M-40:
  Castillejos dentro y Almenara en el borde, con su nota; los otros 4 barrios de la muestra, fuera.

La tabla CM de unidades urbanas por uso está en `stat_sample/cm_catastro_unidades_urbanas_uso.csv`
(`scripts/build_stat_fixtures.py`).
