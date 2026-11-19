# serpavi_sample — fixture del SERPAVI (D-242)

Recorte real de la base de datos del Sistema Estatal de Referencia del Precio del Alquiler de
Vivienda (Ministerio de Vivienda y Agenda Urbana, base 2011-2024 publicada el 9 de marzo de 2026;
reutilización citando la fuente y la fecha de actualización): las secciones de `admin_sample`
(Sol, Palacio, Chamartín y Tetuán en Madrid; La Acebeda y Ajalvir), sus distritos y municipios, y
el primer territorio de otra provincia en cada hoja. Solo las columnas de 2023 y 2024, para que los
tests vean un año que `period_min` deja fuera.

Regenerar con `uv run python scripts/build_serpavi_fixture.py [libro.xlsx]` (sin argumento, lee
el libro de Bronze).
