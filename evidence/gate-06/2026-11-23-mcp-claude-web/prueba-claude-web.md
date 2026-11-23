# MCP remoto (D-255) desde Claude web · 23 nov 2026

**Qué se probó:** el MCP remoto de producción, `https://vidafacil-madrid.vercel.app/api/v1/mcp` (deploy-46, código `542283b8`).
- **Cliente:** Claude web.
- **Cómo se conectó:** como conector personalizado, sin autenticación («No sign in»).
- **Quién:** Mariano, el 23 nov por la tarde.

Abajo están las dos preguntas y las respuestas de Claude, tal como las copió Mariano. El texto lo redacta el modelo; las cifras salen de las herramientas del MCP.

Las cifras se comparan con la API pública justo después de la prueba: `GET /api/v1/gaps/distrito/2807905` y `GET /api/v1/datasets?cm_only=true`, en el mismo despliegue.

## Comprobación contra la API pública

| Fila (Chamartín, `gap-0.4`) | Lo que dijo Claude por el MCP | La API | ¿Cuadra? |
|---|---|---|---|
| Mayores | JUSTO; 2,6 frente a 4,4 («un 41 % menos»), unos 35.000 mayores | JUSTO; 2,618 frente a 4,447; 34.896 personas | Sí |
| Escuelas infantiles | JUSTO; 4,8 frente a 4,9 | JUSTO; 4,831 frente a 4,87 | Sí |
| Colegios | CUBIERTO; 25,4 frente a 22,7 | CUBIERTO; 25,4 frente a 22,72 | Sí |
| Centros de salud | CUBIERTO; 0,44 frente a 0,39 | CUBIERTO; 0,4425 frente a 0,3858 | Sí |
| Farmacias | CUBIERTO; 7,3 frente a 3,1 | CUBIERTO; 7,334 frente a 3,054 | Sí |
| Vivienda | «no hay datos»; «solo sirve de contexto» | SIN_DATOS; fila de contexto (D-254) | Sí |
| Datasets de la Comunidad | 39 | `cm_open_data_count` 39 | Sí |

Claude también ofreció mirar Chamartín por secciones censales. Es una oferta real: `GET /api/v1/gaps/seccion_censal/2807905001` responde 200 con `gap-0.4`.

## Pregunta 1 · «¿Qué le falta a Chamartín?»

> A Chamartín no le falta nada en sentido estricto. Comparado con los otros municipios urbanos de la Comunidad, ningún servicio sale en «FALTA». El punto flojo son los centros de mayores.
>
> Centros de mayores: JUSTO, pero es lo más débil. Hay 2,6 plazas al alcance a pie por cada 100 personas de 65 años o más, frente a 4,4 en los otros municipios urbanos. Es un 41 % menos, para unos 35.000 mayores. Cuenta hogares, clubes y centros de día. El más cercano queda a unos 10 min andando. Este dato puede quedarse corto, porque el registro de la Comunidad no incluye los centros municipales de mayores del Ayuntamiento de Madrid.
>
> Escuelas infantiles: JUSTO, en la media. Hay 4,8 escuelas por cada 1.000 niños de 0 a 4 años, frente a 4,9 en los otros municipios urbanos. La más cercana está a unos 5 min. Se cuentan escuelas y no plazas, porque las plazas no se publican.
>
> Cubierto: colegios, 25,4 aulas de primaria por cada 1.000 niños, frente a 22,7; centros de salud, 0,44 por cada 10.000 habitantes, frente a 0,39 (el más cercano, a unos 9,5 min); farmacias, 7,3 por cada 10.000 habitantes, frente a 3,1 (más del doble).
>
> Vivienda grande: no hay datos (falta la fuente). En esta herramienta la vivienda solo sirve de contexto, no se valora.
>
> Los datos son del 19/11/2026.

Al final de la respuesta, Claude citó estas fuentes:
- Comunidad de Madrid, Portal de Datos Abiertos, CC BY 4.0;
- Instituto Geográfico Nacional (CartoCiudad), CC BY 4.0;
- Ayuntamiento de Madrid, CC BY 4.0;
- OpenStreetMap contributors, ODbL.

## Pregunta 2 · «¿Qué datasets de la Comunidad usa Vida Fácil?»

> Vida Fácil usa 39 datasets del portal de datos abiertos de la Comunidad de Madrid. Por temas: población y hogares (5); servicios (8); vivienda y suelo (12); entorno (4); transporte, del CRTM (10).
>
> Casi todos tienen licencia CC BY 4.0. La excepción son los 10 del CRTM, que van con la licencia de datos abiertos del CRTM y piden la atribución «Powered by CRTM».
>
> Además de estos, usa fuentes de fuera de la Comunidad, como el padrón del Ayuntamiento de Madrid y la red peatonal de OpenStreetMap. Las ubicaciones de colegios, centros de salud, farmacias y centros de mayores se sitúan en el mapa con CartoCiudad (IGN).

La lista completa por temas que dio Claude coincide con `pitch/datasets_cm.md`: 5 + 8 + 12 + 4 + 10 = 39.
