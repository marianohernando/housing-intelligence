# D-239 — Desempate por servicios a pie y hospitales públicos o privados (14 nov)

Evidencia del PR #56. La API de esta rama corrió en local, contra la base del contenedor y en solo lectura (`default_transaction_read_only=on`). Cada caso se comparó con la respuesta de producción (`/api/v1/search` y `/api/v1/search/barrios`) del mismo día.

## Invariante del pitch: el caso del ejemplo

Pareja con 2 hijos de 4 y 8 años, trabajo en la Castellana, alquiler hasta 1.500 €/mes, colegio a 10 min y prioridades colegios, transporte y salud.

| | Producción | Esta rama |
|---|---|---|
| Zonas que encajan / sin dato | 27 / 15 | 27 / 15 |
| Top 10 | Latina 98, Moratalaz 98, Ciudad Lineal 98, Puente de Vallecas 98, Fuencarral-El Pardo 97, Usera 97, Carabanchel 97, Hortaleza 97, San Blas-Canillejas 97, Villaverde 97 | idéntico |
| Casi encajan (93 %) | Chamartín, Salamanca, Centro, Chamberí, Retiro | idéntico |
| Respuesta entera (`data`) | — | igual byte a byte |
| `/search/barrios`, 21 distritos | — | iguales los 21: resultados, «Casi encajan», mapa y Reality Check |

La primera versión del PR aplicaba el desempate también a «Casi encajan». Las cinco del ejemplo empatan exactamente: todas fallan solo el presupuesto, y con ese desempate salía Chamberí primera. En los barrios, el orden cambiaba en 5 distritos. Por eso el desempate solo ordena «Zonas que encajan» (D-239 A.2).

## Casos del feedback: pareja, alquiler hasta 10.000 €/mes

| Caso | Producción (antes) | Esta rama (después) |
|---|---|---|
| Sin prioridades: 57 zonas, las 57 al 100 % | Alcalá de Henares, Alcobendas, Alcorcón, Algete, Aranjuez, Arganda del Rey, Arroyomolinos, Boadilla del Monte, Ciempozuelos, Colmenar Viejo | Chamberí, Tetuán, Puente de Vallecas, Salamanca, Centro, Usera, Arganzuela, Ciudad Lineal, Carabanchel, Retiro |
| Transporte y salud: 57 zonas, 24 al 100 % | Móstoles, Parla, Torrejón de Ardoz, Alcalá de Henares, Alcorcón, Leganés, Coslada, Fuenlabrada, Arganzuela, Salamanca | el mismo top 10 que sin prioridades |

Con 5.000 €/mes, el máximo del deslizador de la web, sale lo mismo: 57 zonas empatadas y el mismo top 10.

## Hospitales en `/places` (todos los centros sanitarios)

- 85 hospitales: 35 públicos (30 los gestiona el SERMAS y 5 una empresa) y 50 privados.
- Con gestión privada: Fundación Jiménez Díaz (651 camas), Torrejón (250), el de la calle Gladiolo de Móstoles (Rey Juan Carlos, 362 camas; sin nombre hasta la próxima carga del registro), Villalba (217) e Infanta Elena (186).
- Fuentes:
  - [Hospitales de la red del Servicio Madrileño de Salud](https://www.comunidad.madrid/salud/hospitales-red-servicio-madrileno-salud), actualizada el 26 may 2026;
  - [Control y seguimiento de centros y servicios de gestión indirecta](https://www.comunidad.madrid/salud/control-seguimiento-centros-servicios-gestion-indirecta), actualizada el 27 oct 2026.

  Las dos se consultaron el 14 nov.

## Capturas (build de producción de la web contra esa API, 1440 y 390 px)

| Fichero | Qué muestra |
|---|---|
| `empate-1440.png`, `empate-390.png` | En pareja, 5.000 €/mes y nada marcado: «Encajan 57 zonas igual de bien…» sobre la lista, con Chamberí, Tetuán, Puente de Vallecas… |
| `hospitales-moncloa-aravaca-1440.png`, `-390.png` | «6 hospitales en Moncloa-Aravaca: 2 públicos y 4 privados» y la nota de `centros.hospital.dependencia` |
| `hospitales-moncloa-aravaca-lista-1440.png`, `-390.png` | La lista: «Hospital público · gestión privada · Hospital Universitario Fundación Jiménez Díaz · 651 camas instaladas» |
| `hospitales-mostoles-1440.png`, `-390.png` | «3 hospitales en Móstoles: 2 públicos y 1 privado» |
| `hospitales-mostoles-lista-1440.png`, `-390.png` | El Rey Juan Carlos, aún sin nombre: «Hospital público · gestión privada · 362 camas instaladas» |

Sin errores en la consola del navegador.
