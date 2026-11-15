# air_sample — fixtures de calidad del aire (D-237)

`cm_calidad_aire_zonas.csv`: las tres filas reales de la ficha «Red de Calidad del Aire. Municipios
por zonas» de la Comunidad de Madrid (CC BY 4.0) de los municipios de `admin_sample` (Madrid,
Ajalvir y La Acebeda, que la ficha escribe sin artículo). Los datos horarios de los tests de
integración son sintéticos: `tests/integration/conftest.py` (`air_hourly_extract`) escribe un año
entero con el formato de cada red.
