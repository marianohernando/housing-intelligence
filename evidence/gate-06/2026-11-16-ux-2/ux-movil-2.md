# Claridad en el móvil, segunda entrega (16 nov)

Rama `claude/s1-ux-mobile-2`, desde `e0417ae` (entrega 1, #79, D-244). Decisiones de Mariano para la opción 2 de la auditoría (`prompts/UX_AUDITORIA_MOVIL.md` §7): la fila y la tarjeta esenciales, «Volver a la lista» y el botón atrás, la pantalla de zona plegada y la deuda de la entrega 1. Decisión: D-245. Textos: `pitch/textos_web.md` («UX móvil 2»).

**Cómo se ha medido.** Web compilada (`npm run build` + `next start`, puerto 3071) contra la API de la rama en el puerto 8071, sobre la base local `housing` en solo lectura. El «antes» es el código de `e0417ae` en `next dev`. Script: `apps/web/scripts/check-ux-mobile.mjs`.

```
node apps/web/scripts/check-ux-mobile.mjs --base http://localhost:3071 --out evidence/gate-06/2026-11-16-ux-2 --label despues --widths 390,360 --counts 390,360,1440 --shots
```

## Cuánto se ve (antes y después)

Una «cosa» es un elemento visible con texto propio (un nombre, una banda, una cifra, una etiqueta) o un control sin texto (la X de antes). No cuenta lo que es solo para el lector de pantalla ni lo plegado. Fila: las 5 primeras de la lista. Tarjeta: la de la 1.ª zona, al abrirla («primera pantalla»: lo que se ve sin bajar, dentro de la hoja en el móvil).

| | Ejemplo | 390 px antes | 390 px después | 360 px antes | 360 px después | 1440 px antes | 1440 px después |
|---|---|---|---|---|---|---|---|
| Cosas por fila | Familia | 7-8 | **4** | 7-8 | **4** | 7-8 | **5** (con el %) |
| Cosas por fila | Pareja jubilada | 8-9 | **4** | 8-9 | **4** | 8-9 | **5** |
| Tarjeta, primera pantalla | Familia | 17 | **12** | 15 | **12** | 24 | **12** |
| Tarjeta, primera pantalla | Pareja jubilada | 16 | **12** | 16 | **11** | 22 | **13** |
| Tarjeta entera, plegada | Familia | 40 | **12** | 40 | **12** | 40 | **12** |
| Tarjeta entera, plegada | Pareja jubilada | 43 | **13** | 43 | **13** | 43 | **13** |
| Tarjeta con «Ver más» abierto | Familia | — | 48 | — | 48 | — | 48 |
| Tarjeta con «Ver más» abierto | Pareja jubilada | — | 54 | — | 54 | — | 54 |

- **Fila, antes:** cabecera de empate («Empatan al 94 %»), puesto, nombre, «Distrito de Madrid», banda, %, «≈ 1.129 €/mes», «por 77 m²» y, a veces, «Dato poco seguro». **Después:** puesto, nombre, banda y «Unos 1.129 € al mes» (en el escritorio, además, el % pequeño tras la banda).
- **Tarjeta, después:** «Volver a la lista», nombre, «Madrid · Muy buena opción», «Unos 1.129 € al mes» y «Precio orientativo», lo que pidió con sus minutos (3-4 líneas), lo que le falta o «No le falta nada de lo que buscáis», y «Ver más sobre…». Con «Ver más» abierto está todo lo de antes (el %, el puesto, el empate, los hechos con su fiabilidad, el precio con los m², el rango y el aviso de 2024, «Lo que le falta a esta zona» y «Ver la zona»): no se pierde ningún dato.
- El contador del «antes» se volvió a pasar con la misma regla (lo plegado no cuenta): `antes/tamanos-antes.json`, campo `counts`.

## Letra y botones (texto < 16 px · objetivos < 44 px)

**0 · 0 en todas las pantallas, a 390 y a 360 px** (`tamanos-despues.json`): portada, formulario (cerrado, abierto y con el ejemplo), lista, tarjeta, tarjeta con «Ver más», distrito con sus barrios, la pantalla de zona entera, «No comparable» en «Qué falta» y «Somos mayores» con un lugar. Son nuevas en la medida la tarjeta con «Ver más», la pantalla de zona entera (el enlace de las migas, «Madrid», medía 21 px y ahora 44) y «No comparable». No se cuentan, antes ni después, los 3 controles del mapa (MapLibre, obligatorios por licencia).

## axe (WCAG 2.2 AA)

0 incidencias, a 390 y a 360 px, en todos los estados de arriba (también la pantalla de zona con «Más datos de la zona» abierto, medida igual: 0 · 0), y a 1440 px en la lista, la tarjeta con «Ver más» y la pantalla de zona abierta.

## e2e contra la web compilada

`infra/deploy/e2e/e2e_prod.mjs --base http://localhost:3071`: **escritorio 1440 px 114/114, móvil 390 px 90/90** tras la revisión independiente (antes de ella, 105/105 y 81/81) (`e2e/e2e-report.json`). Antes: 86/86 y 62/62. Se han adaptado sin quitar ninguna comprobación (el aviso de 2024, bajo la lista; el % y los hechos de la tarjeta, tras «Ver más»; «para vosotros») y se han añadido:
- **Fila esencial:** cada fila a la vista dice el nombre, la banda y «Unos … € al mes» de la API; en el móvil sin %, en el escritorio con él; nunca «Distrito de», m² ni «Empatan».
- **Tarjeta:** lo esencial sin %, con la banda y «Precio orientativo»; la zona en la dirección (`?zona=`); «Ver más» despliega el % y los hechos de la API y el aviso de 2024; «Volver a la lista» vuelve a la lista y quita `?zona=`.
- **J5, pareja jubilada:** la tarjeta del 1.er barrio dice lo que le falta de lo suyo según el `/gaps` que pidió, o «No le falta nada de lo que buscáis»; nunca colegios ni escuelas infantiles; el botón atrás vuelve a la lista. Y el arreglo que pidió C: al desmarcar «Somos mayores» sin volver a buscar, «¿Quieres ver más zonas?» ya no ofrece las propuestas anteriores; al buscar otra vez, ninguna vuelve a marcarlo.
- **J6, la zona en la dirección:** una fila añade `?zona=`; `history.back()` vuelve a la lista y el foco a la fila; «Volver a la lista» también; la pantalla de zona tiene el contexto plegado en «Más datos de la zona» y su «Volver a la lista» lleva a la lista; `/?zona=…` abre la zona, y abierta así «Volver» la cierra sin salir.

## Golden, tests y build

- `scripts/golden_search.py` contra `housing` en solo lectura: **10 de 10**. La API no cambia.
- `make lint typecheck test-unit`: Python 1031, vitest 562 (antes 1030 y 542), eslint, tsc y pyright limpios. `make test-db` no se ha pasado en local (crea y migra `housing_test`, y la regla de esta sesión es no escribir en ninguna base): lo pasa la CI (job «integration»).
- Builds: uno tras otro, sin borrar `.next` (el último, con los arreglos de la revisión, es el medido).

## Capturas (390, 360 y 1440 px)

| Pantalla | Después | Antes (390 y 1440 px) |
|---|---|---|
| Lista, ejemplo «Pareja jubilada» | `01-lista-pareja-jubilada-*.png` | `antes/04-ejemplo-pareja-jubilada-*.png` |
| Tarjeta esencial de su 1.er barrio | `02-tarjeta-pareja-jubilada-*.png` | `antes/04b-tarjeta-pareja-jubilada-*.png` |
| Lista, ejemplo «Familia» | `03-lista-familia-*.png` | `antes/05-lista-*.png` |
| Tarjeta esencial, cerrada | `04-tarjeta-familia-*.png` | `antes/06-tarjeta-*.png` |
| Tarjeta con «Ver más» abierto | `05-tarjeta-ver-mas-*.png` | (antes todo estaba a la vista: `antes/06-tarjeta-*.png`) |
| Pantalla de zona, arriba | `06-pantalla-zona-*.png` | `antes/08-distrito-barrios-*.png` |
| Pantalla de zona, «Más datos de la zona» plegado | `06b-pantalla-zona-plegada-*.png` | (antes, 6 bloques más a la vista) |
| Barrios de un distrito | `07-distrito-barrios-*.png` | `antes/08-distrito-barrios-*.png` |
| Portada, formulario, «Somos mayores» (con y sin lugar) y «Cómo lo calculamos» | `09-portada-*.png`, `10-formulario-*.png`, `11-somos-mayores-*.png`, `11b-somos-mayores-lugar-*.png`, `12-como-lo-calculamos-*.png` | (de la entrega 1, en `2026-11-15-ux-1/`) |
| «No comparable» (Barajas, centros de salud) | `08-no-comparable-*.png` | antes: «Aquí vive tan poca gente…» y, de la API, «aquí viven muy pocas personas (50.375)» |

## Retoques tras abrir el PR

- **La cabecera concuerda con el hogar:** «Zonas que os convienen» con dos o más personas, «Zonas que te convienen» con una, como la línea de debajo (`resultsTitle`, con test; el e2e lo comprueba con el ejemplo de la familia).
- **«No comparable» en la API, en su origen** (`not_comparable_text`, `hi_domain/gap_impact.py`): Barajas, centros de salud, decía «No comparable: aquí viven muy pocas personas (50.375) para saber si falta.» y dice «No comparable: para la gente que vive aquí le corresponden menos de 4 centros de salud y, con números tan pequeños, no se puede saber si faltan.». En la fila de vivienda (denominador de hogares) sigue «aquí viven muy pocos hogares de 4 o más personas (1)» (La Acebeda), que ahí es el motivo. Comprobado con la API local sobre `housing` en solo lectura. Ni el contrato ni la fórmula cambian.
- **«No sabemos si le faltan…» se queda** (decisión de Mariano, D-245 §4).
- **El trayecto a la familia o a «donde vivimos ahora»** ya no dice «, llegando a las 9:00» (`commute_text`, `hi_domain/fit.py`): la tarjeta de la pareja jubilada dice «27 min en transporte público hasta Ciudad Lineal (metro)» (`02-tarjeta-pareja-jubilada-*.png`). El del trabajo y los estudios sigue igual, y el cálculo no cambia. Golden 10 de 10, sin tocarlo: sus escenarios con lugar son de trabajo.

## Revisión independiente del #81 (R-01 a R-13)

- **R-01:** «No le falta nada…» (con el visto verde) solo cuando ninguna fila pertinente es «No comparable» ni SIN DATOS; si alguna lo es, «De lo que podemos comparar, no le falta nada.» sin visto y debajo «No sabemos si…». En un barrio, con el distrito: captura `02-tarjeta-pareja-jubilada-*.png` («En Barajas, de lo que podemos comparar, no falta nada.»).
- **R-02:** las filas pertinentes son las del hogar y las de lo que se marca (`marked_rows`); test de la pareja sin hijos que marca «Colegios».
- **R-03:** «tú» o «vosotros» en una sola función (`voice`), con tests.
- **R-04:** los topes del % se quedan en lo esencial sin la coletilla; sin «a las 9:00» para la familia y la casa también cuando no hay trayecto (en la API).
- **R-05:** el panel del barrio recupera la banda con el %, el empate, los m² y la fiabilidad.
- **R-06:** el historial marca el paso en `history.state`; `?zona=` inválido vuelve a `/`; «Volver a la lista» de la pantalla de zona vuelve dos pasos sin apilar (e2e J6, con el botón adelante).
- **R-07:** «No comparable» por fila y en su unidad; la vivienda conserva la frase de la API.
- **R-08:** el e2e espera a «Qué falta» antes de leer la tarjeta; e2e de «No sabemos…», de `?zona=` inválido y de otro nivel, del botón adelante y del paso de barrio a distrito (J7); axe a 1440; «Más datos de la zona» medido abierto.
- **R-09:** el foco vuelve a la fila si se ve (`checkVisibility`) y, si no, al título.
- **R-10:** el precio una vez en lo esencial y su desglose en «Ver más» sin repetir la cifra; la tarjeta dice si es distrito, barrio o municipio; «Precios orientativos…» también al comprar.
- **R-12:** entran los dos cambios de texto de la API; API y web se despliegan juntas; golden 10/10.
- **R-13:** `rankingRows` borrado; capturas de la portada, el formulario, «Somos mayores» y «Cómo lo calculamos» de nuevo (`09` a `12`).

## Lo que queda abierto

- Volver con el botón atrás desde la pantalla de zona a su tarjeta enseña la lista un instante antes de la tarjeta; volver a la lista por un enlace ya no enseña la tarjeta.
- Scripts de QA antiguos (`check-qa.mjs`, `check-search.mjs`, `count-requests.mjs`): sin adaptar ni ejecutar, como en la entrega 1. No los usa la CI.
