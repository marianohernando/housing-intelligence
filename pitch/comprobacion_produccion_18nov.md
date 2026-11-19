# Comprobación en producción, 18 nov 2026 (línea D)

Respaldo de las cifras y textos que el pitch cita como «producción, 18 nov»: guion (bloques 2, 3 y 4), vídeo de respaldo (planos 2 a 5), slides y preguntas 48 y 60. Las filas y la tarjeta se leyeron a 1440 × 900; a 390 × 844 solo se hizo la captura C6. Las medidas del móvil de la pregunta 43 no salen de aquí: son las de `evidence/gate-06/2026-11-15-ux-1/ux-movil-1.md` y `evidence/gate-06/2026-11-16-ux-2/ux-movil-2.md`.

## Cómo se comprobó
- **Web:** https://vidafacil-madrid.vercel.app, con el despliegue de `55651c2` (`evidence/gate-06/2026-11-15-deploy/deploy-35-55651c2-ux3.md`). Entre `55651c2` y `origin/claude/sprint-1-public` no hay cambios en `apps/web` (`git log 55651c2..origin/claude/sprint-1-public -- apps/web`, vacío el 18 nov).
- **Navegador:** Playwright, a 1440 × 900 y 390 × 844, por la tarde del 18 nov.
- **Caso:** el ejemplo de la portada, «Ejemplo: pareja con 2 hijos que trabaja en la Castellana» (`data/fixtures/contracts/scenario_state.familia_castellana.fixture.json`).
- **Qué se leyó:** el texto que pinta la web, que sale de la API de producción (`POST /api/v1/search` y `GET /api/v1/gaps/…`). Para la lista, la tarjeta y «Qué falta» no se llamó a la API directamente; para el suelo público y el número de conjuntos, sí (al final).
- **Capturas:** las de `pitch/capturas/` (C1, C2, C3 y C6), hechas en la misma sesión.

## Lo que se vio
**Lista** (C2 y C6):
- título «Zonas que os convienen» y, debajo, «Hemos encontrado 42 zonas para vosotros.»;
- leyenda del mapa: cumplen todo 42 zonas, no cumplen todo 157 y sin datos 0;
- filas, en escritorio:

  | Zona | Banda | Precio |
  |---|---|---|
  | Puente de Vallecas | Muy buena opción · 94 % | Unos 1.129 € al mes |
  | Latina | Muy buena opción · 94 % | Unos 1.101 € al mes |
  | Usera | Muy buena opción · 93 % | Unos 1.019 € al mes |
  | Moratalaz | Muy buena opción · 93 % | Unos 1.083 € al mes |
  | Tetuán | Muy buena opción · 92 % | Unos 1.488 € al mes |

- bajo la lista: «Precios orientativos: hoy pueden ser algo más caros.» y «Hemos mirado las 199 zonas de la Comunidad de Madrid.».

**Tarjeta de Puente de Vallecas** (`?zona=distrito/2807913`; C1):
- lo esencial:
  - «Volver a la lista»;
  - «Distrito de Madrid · Muy buena opción»;
  - «Unos 1.129 € al mes», con «Precio orientativo»;
  - «Colegio con primaria a unos 4 min andando»;
  - «Parada de autobús a unos 2 min andando · Metro o Cercanías a unos 10 min»;
  - «Centro de salud a unos 8 min andando»;
  - «41 min en transporte público hasta Paseo de la Castellana (Azca), llegando a las 9:00»;
  - «No le falta nada de lo que buscáis.».
- en «Ver más sobre Puente de Vallecas»:
  - «Muy buena opción · 94 %», «La 1.ª que más os conviene» e «Igual de buena que Latina (94 %).»;
  - «Lo que tenéis aquí»: «Dato fiable» en el colegio, la parada, el centro de salud y «Alquiler unos 1.129 € al mes por 77 m² (14,7 €/m², contratos firmados en 2024)»; «Dato aproximado» en los 41 min;
  - «Lo que le falta a esta zona»: «Tiene lo que pedís. Aun así, comparado con municipios parecidos, aquí faltan escuelas infantiles.»;
  - colegios, centros de salud y farmacias CUBIERTO, a pie 4, 8 y 3 min;
  - «Ver todo lo que falta», que lleva a `/que-falta?zona=distrito/2807913`, y «Ver la zona».

**«Casi valen (5)»**, con «Les falta una sola cosa de lo que pedís.»:

| Zona | Lo que le falta | Precio |
|---|---|---|
| Chamartín | Se pasa unos 90 € al mes de vuestro presupuesto | Unos 1.590 € al mes |
| Arganzuela | Se pasa unos 20 € al mes | Unos 1.518 € al mes |
| Centro | Se pasa unos 190 € al mes | Unos 1.692 € al mes |
| Chamberí | Se pasa unos 230 € al mes | Unos 1.733 € al mes |
| Retiro | Se pasa unos 30 € al mes | Unos 1.525 € al mes |

**«¿Queréis ver más zonas?»** (C3):
- «Hemos encontrado 42 zonas para vosotros. Mirad cuántas salen si cambiáis una sola cosa:»;
- «+5 min a pie hasta colegio con primaria · saldrían 49 más: 91 zonas en total», con «Ver esas zonas»;
- «+150 €/mes · saldrían 3 más: 45 zonas en total»;
- «Lo que más limita vuestra búsqueda es: Colegio con primaria a 10 min andando como mucho».

**«Qué falta en Puente de Vallecas»** (`/que-falta?zona=distrito/2807913`):
- «Aquí falta: escuelas infantiles. Sin datos: viviendas grandes para familias.»;
- escuelas infantiles, FALTA:
  - «Aquí hay 57 por cada 100 que hay en municipios parecidos.»;
  - «Afecta a 9.433 niños de 0 a 4 años.»;
  - a pie hasta la escuela infantil más cercana, 6 min, «Dato fiable»;
  - «De dónde sale: 5 conjuntos de datos».

## El Portal del Suelo 4.0 (D-246)
**CSV del portal** ([ficha](https://datos.comunidad.madrid/dataset/parcelas_portal_suelo)), descargado el 18 nov por la tarde, antes de que la capa estuviera en la web, y contado por `uso_principal_codigo`:
- 525 parcelas, 291 de uso residencial (`R`);
- 29 municipios con alguna parcela residencial;
- 394.298 m² edificables (`superficie_edificable`) entre las residenciales;
- más parcelas residenciales: Majadahonda 101, Pozuelo de Alarcón 44 y Madrid 38.

**En producción desde el 18 nov:** despliegue de `747cb65` y sync, verificado por C antes y después del sync (`evidence/gate-06/2026-11-18-deploy/deploy-36-747cb65-suelo.md`, PR #90). D lo leyó en la API esa noche, ya con el sync hecho:
- `GET /api/v1/features/suelo_publico_vivienda_m2/values?level=municipio`: 179 municipios, 29 con parcelas; 291 parcelas (los `items`) y 394.298 m² edificables (la suma de `value`). Morata de Tajuña tiene 1 parcela sin superficie publicada: su valor sale vacío, no 0, y no suma;
- más parcelas: Majadahonda 101 (29.312 m²), Pozuelo de Alarcón 44 y Madrid 38 (137.580 m²). Las mismas cifras que el CSV;
- `?level=distrito`: 7 de los 21 distritos de Madrid, con 38 parcelas; Vicálvaro 16 (67.808 m²), Hortaleza 9, Fuencarral-El Pardo 7 y San Blas-Canillejas 3;
- `GET /api/v1/datasets?cm_only=true`: `cm_open_data_count: 36`; sin el filtro, 53 en total.

En la web, la línea sale en la pantalla de un municipio o de un distrito, en «Más datos de la zona» → «Vivienda nueva y lo que viene». En Vicálvaro: «Suelo público para vivienda: 16 parcelas, 67.808 m² edificables.» (lo vio C en producción; D no hizo capturas de la capa). La búsqueda y «Qué falta» del caso de ejemplo no cambian: la capa no puntúa (D-246 §8 y §9; golden 10/10 en la misma evidencia).
