# Informe de incoherencias enviado a la Comunidad de Madrid · 24 nov 2026

- **Canal:** «Formulario de valoración de Datos Abiertos» del portal (<https://www.comunidad.madrid/info/form/valora-datos-abiertos>), enlazado desde «Participa en Datos abiertos».
- **Quién:** Mariano, el 24 nov. Está dado de alta como reutilizador de datos abiertos de la Comunidad desde el 23 nov.
- **Qué:** 17 incoherencias en los 39 conjuntos que usa Vida Fácil y cuatro propuestas. El texto enviado va abajo, tal cual.

## Cómo se comprobó antes de enviarlo (24 nov)

Cada punto se volvió a mirar en el portal ese mismo día. Lo que no se pudo comprobar con limpieza se quitó.

| Punto | Fuente de la comprobación | Resultado |
|---|---|---|
| Frecuencia: 0 de 39 en el campo estándar; 19 en el campo libre (11 con «OTROS»); las 20 del Instituto de Estadística sin ella | API CKAN `package_show` de las 39 fichas | Se mantiene |
| Exportación DCAT sin licencia, contacto, tema ni cobertura; formato como literal | `/dataset/<id>.jsonld` de 4 fichas | Se mantiene |
| Contacto | API CKAN | **Corregido**: 27 de 29 fichas sin correo. Las 2 de calidad del aire lo dan en el campo libre «Correo» |
| Errata «Vicenconsejería de Sanidad» | Extra «Viceconsejería» de 2 fichas | Se mantiene |
| El registro sanitario no publica nombres; 4 centros de salud «S/N» sin coordenadas; 2 pares de coordenadas repetidas | CSV del registro, actualizado el 24 nov | Se mantiene |
| Consultorio CS12766 (Buitrago) con coordenadas en otro municipio | El fallo salía de nuestro geocodificado | **Quitado** |
| Centros educativos: 40 sin localizar y 22 con un distrito distinto | El fichero no cambia desde el 5 may; ver `../../gate-01/2026-11-12/audit-places.md` | Se mantiene |
| Farmacias: 4 sin coordenadas; la n.º 763 con coordenadas en Valdemoro | CSV del 23 nov; `../../../pitch/revision_10_zonas.md` D3 | Se mantiene |
| Atención social | CSV del 15 nov | **Corregido**: 85 de 2.633 registros sin coordenadas (el 34 del borrador era nuestra cuarentena) |
| Barrios: 128, con Villa de Vallecas y Vicálvaro con 2 cada uno | CSV de «Barrios del Municipio de Madrid» | Se mantiene |
| Seccionado de 2019 | Recurso sin cambios desde jun 2024; `../../gate-01/2026-10-20/known-limitations.md` | Se mantiene |
| GTFS de metro del 27-05-2025, con calendario hasta el 20260527 y `feed_info` sin fechas | Zip enlazado por la ficha (ítem de ArcGIS modificado el 30-05-2025) | Se mantiene |
| `wheelchair_boarding` y `GRADOACCESIBILIDAD` | `../../gate-01/2026-11-12/estaciones-accesibles.md`; las fichas del CRTM no cambian desde sep 2025 | Se mantiene |

## Texto enviado

```text
Incidencias al reutilizar 39 conjuntos del Portal de Datos Abiertos (Vida Fácil, DATAMAD 2026)

Hola:

Soy Mariano, reutilizador registrado del portal. En Vida Fácil (DATAMAD 2026) usamos 39 conjuntos de datos.comunidad.madrid: 29 de la Comunidad y 10 del Consorcio Regional de Transportes. Al cargarlos y cruzarlos con otras fuentes oficiales hemos encontrado lo siguiente. Lo hemos vuelto a comprobar en el portal el 24 de noviembre de 2026. El detalle, registro a registro, está en github.com/marianohernando/housing-intelligence (carpeta evidence).

1. METADATOS
- Frecuencia: ninguna de las 39 fichas la declara en el campo estándar (frequency en CKAN, dct:accrualPeriodicity en DCAT). 19 la ponen como texto en el campo libre «Frecuencia de actualización de datos» (11 de ellas con «OTROS», entre ellas las 10 del Consorcio). Las 20 del Instituto de Estadística no la indican. El Monitorizador MELODA (spain.meloda.org) da a las 39 un 1 sobre 5 en actualización.
- Exportación DCAT: en datos.comunidad.madrid/dataset/<id>.jsonld no aparece la licencia, aunque la API CKAN sí la da (cc-by). Tampoco aparecen el punto de contacto, el tema ni la cobertura geográfica. El formato va como texto («CSV») y no como URI del vocabulario europeo de tipos de fichero. Lo hemos comprobado en oficinas_farmacia, centros_educativos, centros_servicios_establecimientos_sanitarios y 1934259.
- Contacto: 27 de las 29 fichas de la Comunidad no tienen correo de contacto. Las 2 de la Red de Calidad del Aire lo ponen en un campo libre («Correo»), no en el campo estándar. Las 10 del Consorcio sí lo tienen.
- Errata: el campo Viceconsejería dice «Vicenconsejería de Sanidad» en las fichas «Oficinas de farmacia» y «Centros, servicios y establecimientos sanitarios».

2. CENTROS, SERVICIOS Y ESTABLECIMIENTOS SANITARIOS
- El registro no publica el nombre del centro. Para los centros de salud y los hospitales hay que cruzarlo por dirección con los catálogos del Ministerio de Sanidad. En nuestro cruce quedaron sin nombre 17 centros de salud, 7 consultorios y 6 hospitales generales.
- Cuatro centros de salud tienen la dirección «S/N» y no tienen coordenadas:
  - CS1184 (calle de Arenas del Rey, Madrid);
  - CS6158 (calle de Mirueña, Madrid);
  - CS10286 (calle Ramón María del Valle Inclán, Alcalá de Henares);
  - CS7529 (calle Juan de Borgoña, Alcalá de Henares).
  El catálogo de atención primaria del Ministerio da su número de portal.
- Coordenadas repetidas en direcciones distintas:
  - los consultorios CS12726 (Carretera s/n) y CS13403 (Plaza de la Sierra 1), de Piñuécar-Gandullas;
  - CH0017 y CH0018 (Juan Bravo 49 y Juan Bravo 39, Madrid).

3. CENTROS EDUCATIVOS (fichero del 5 de mayo de 2026)
- 40 centros no tienen coordenadas o tienen una dirección que no hemos podido localizar con CartoCiudad (IGN). Por ejemplo, el CEIP de Navalafuente figura en «Eras de Arriba 56», y CartoCiudad solo llega al número 16.
- 22 centros de Madrid figuran en un distrito distinto del que dan sus coordenadas, casi todos junto a un límite de distrito. Por ejemplo, el CEIP Nuria Espert figura en Hortaleza, pero sus coordenadas y la sección censal del INE lo sitúan en Barajas.

4. OFICINAS DE FARMACIA Y ATENCIÓN SOCIAL
- 4 farmacias no tienen coordenadas: n.º 178, 1899, 2683 y 2976.
- La farmacia n.º 763 está en la calle de Afueras a Valverde 36, en Madrid, pero sus coordenadas caen en Valdemoro, a unos 25 km.
- En el «Registro de centros de atención social», 85 de los 2.633 registros no tienen coordenadas.

5. GEOGRAFÍA
- «Barrios del Municipio de Madrid» tiene 128 barrios: Villa de Vallecas y Vicálvaro aparecen con 2 cada uno. La división actual del Ayuntamiento tiene 131 barrios, y en el fichero faltan el 183, el 193 y el 194.
- «Secciones censales» publica el seccionado de 2019. El INE ya publica el de 2025.

6. FICHAS DEL CONSORCIO
- El GTFS que enlaza «Oferta planificada de la Red de Metro» es del 27-05-2025. Su calendar.txt vence el 27-05-2026, feed_info.txt no trae fechas de validez, y sigue siendo el que está publicado.
- En el estándar GTFS, wheelchair_boarding = 2 significa «no accesible». En estos GTFS aparece en estaciones accesibles y en todo el Metro Ligero.
- El campo GRADOACCESIBILIDAD (T/P/N) de las topologías no tiene diccionario publicado.

PROPUESTAS
1. Pasar la frecuencia al campo estándar, con el vocabulario europeo de frecuencias.
2. Incluir en la exportación DCAT-AP la licencia, el contacto, el tema y la cobertura, y dar el formato como URI.
3. Añadir el nombre del centro al registro sanitario.
4. Revisar los registros citados.

Gracias por publicar estos datos: sin ellos, Vida Fácil no existiría.

Mariano · Vida Fácil · https://vidafacil-madrid.vercel.app
```
