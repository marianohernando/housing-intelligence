# Comprobación en producción, 18 nov 2026 (línea D)

Respaldo de las cifras y textos que el pitch cita como «producción, 18 nov»: guion (bloques 2 y 3), vídeo de respaldo (planos 2 a 5), slides y preguntas 43, 48 y 60.

## Cómo se comprobó
- **Web:** https://vidafacil-madrid.vercel.app, con el despliegue de `55651c2` (`evidence/gate-06/2026-11-15-deploy/deploy-35-55651c2-ux3.md`). Entre `55651c2` y `origin/claude/sprint-1-public` no hay cambios en `apps/web` (`git log 55651c2..origin/claude/sprint-1-public -- apps/web`, vacío el 18 nov).
- **Navegador:** Playwright, a 1440 × 900 y 390 × 844, por la tarde del 18 nov.
- **Caso:** el ejemplo de la portada, «Ejemplo: pareja con 2 hijos que trabaja en la Castellana» (`data/fixtures/contracts/scenario_state.familia_castellana.fixture.json`).
- **Qué se leyó:** el texto que pinta la web, que sale de la API de producción (`POST /api/v1/search` y `GET /api/v1/gaps/…`). Ese día no se llamó a la API directamente.
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

## Fuera de la web: el Portal del Suelo 4.0
CSV del portal ([ficha](https://datos.comunidad.madrid/dataset/parcelas_portal_suelo)), descargado el 18 nov y contado por `uso_principal_codigo`:
- 525 parcelas, 291 de uso residencial (`R`);
- 29 municipios con alguna parcela residencial;
- 394.298 m² edificables (`superficie_edificable`) entre las residenciales;
- más parcelas residenciales: Majadahonda 101, Pozuelo de Alarcón 44 y Madrid 38.

**Pendiente de confirmar en producción:** la capa la está metiendo otra línea en la web. Hasta que datamad-10 lo confirme, el pitch no la cita como hecha (pregunta 60 y frase de reserva del bloque 4 del guion).
