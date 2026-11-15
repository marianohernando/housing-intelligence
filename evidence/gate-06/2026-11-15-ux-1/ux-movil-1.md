# Claridad en el móvil, primera entrega (15 nov)

Rama `claude/s1-ux-mobile`, desde `0c6ce28` (producción con `fit-0.9`). Origen: la prueba en persona del 15 nov con una persona mayor («difícil de entender, muchos datos juntos») y la auditoría `prompts/UX_AUDITORIA_MOVIL.md` (opción 1, con «Somos mayores», D-244). Segunda pasada, tras la revisión del PR #79: el flujo de «Somos mayores» que decidió Mariano (R-01 y R-02) y R-03 a R-13. Las cifras y capturas de este documento son las de esa segunda pasada.

**Cómo se ha medido.** Web compilada (`npm run build` + `next start`, puerto 3061) contra la API de la rama en el puerto 8061, sobre la base local `housing` en solo lectura. El «antes» es el código de `0c6ce28` en `next dev` (las capturas de `antes/` llevan el indicador «N» de Next en la esquina). Script: `apps/web/scripts/check-ux-mobile.mjs`.

```
node apps/web/scripts/check-ux-mobile.mjs --base http://localhost:3061 --out evidence/gate-06/2026-11-15-ux-1 --label despues --widths 390,360 --shots
```

Para cada pantalla lista cada texto por debajo de 16 px y cada objetivo táctil por debajo de 44 px (alto o ancho), sin contar lo que solo es para el lector de pantalla. Una casilla o una opción cuenta por su etiqueta, que es lo que se toca. «Formulario abierto» es el formulario con todas sus ayudas y «Más opciones» desplegadas; «formulario con el ejemplo», el que deja el ejemplo de la familia (lugar de trabajo, días, límite, servicio a un paseo y contador). «Distrito» es la pantalla del distrito de esa tarjeta, con «Los barrios que más te convienen» para la misma búsqueda (revisión R-04; no se midió antes). «Somos mayores» con un lugar elegido es el formulario con «En pareja», «Somos mayores» y la estación de Ciudad Lineal en «¿Dónde vivís ahora?», con el selector de minutos y «Quitar» (revisión H6).

## Antes y después (texto < 16 px · objetivos < 44 px)

| Pantalla | 390 px, antes | 390 px, después | 360 px, antes | 360 px, después |
|---|---|---|---|---|
| Portada | 8 · 1 | **0 · 0** | 8 · 1 | **0 · 0** |
| Formulario | 24 · 2 | **0 · 0** | 24 · 2 | **0 · 0** |
| Formulario abierto | 26 · 2 | **0 · 0** | 26 · 2 | **0 · 0** |
| Formulario con el ejemplo | 32 · 2 | **0 · 0** | 32 · 2 | **0 · 0** |
| Lista | 36 · 0 | **0 · 0** | 36 · 0 | **0 · 0** |
| Tarjeta | 25 · 1 | **0 · 0** | 25 · 1 | **0 · 0** |
| Distrito (barrios) | — | **0 · 0** | — | **0 · 0** |
| «Somos mayores» con un lugar elegido | — | **0 · 0** | — | **0 · 0** |

- **Antes:** textos de 12,2 a 15,3 px: la banda («Encaja muy bien», 12,2), «por 77 m²» (12,8), «· Dato fiable» y FALTA/JUSTO/CUBIERTO (13,3), «Distrito de Madrid», «Empatan al 94 %» y «Probar así» (13,6), y las opciones, chips, ayudas y avisos (14,9). Objetivos: «Alquilar» y «Comprar» (38 px), «Ver las zonas en una lista» (39 px) y «Ver todo lo que falta» (24 px).
- **Después:** el texto más pequeño mide 16 px en el escritorio y 16,9 px en el móvil (`--text-xs`); el cuerpo, 17 y 18 px. Todos los objetivos miden 44 px o más.
- **No se cuentan,** antes ni después, los 3 controles del mapa (el (i) de las fuentes y los dos enlaces de licencia «© OpenStreetMap · Powered by CRTM», que son de MapLibre y obligatorios por licencia).
- Detalle de cada elemento: `tamanos-antes.json` y `tamanos-despues.json`.

## axe (WCAG 2.2 AA)

0 incidencias después, a 390 y a 360 px, en la portada, el formulario abierto, la lista, la tarjeta, la pantalla del distrito y el formulario de «Somos mayores» con un lugar (`tamanos-despues.json`, campo `axe`). Antes: 0 en la primera pasada y 1 `target-size` intermitente en la segunda (la línea «Para unos 77 m² (cámbialo)», que ya no existe).

## e2e contra la web compilada

`infra/deploy/e2e/e2e_prod.mjs --base http://localhost:3061`: escritorio 1440 px **86/86**, móvil 390 px **62/62** (`e2e/e2e-report.json`). El recorrido nuevo J5 (revisión R-06) carga el ejemplo de los jubilados y comprueba que `/search` responde 200 con `household.seniors: true`, `salud`, `sin_escaleras` y `transporte`, `scope: madrid` y un lugar `family` de 30 min y 3 días; que el resumen da los barrios de la API y que no sale «¿Trabajas fuera de casa?»; que se ve «Somos mayores» marcado, «¿Cerca de dónde queréis vivir?» con «Ciudad Lineal (metro)» y «Trabajo en» plegado (revisión H4); y que el importe rápido de 900 € llega como `amount_eur: 900`. Los textos que comprueba se han adaptado sin quitar ninguna comprobación: el resumen («Hemos encontrado 42 zonas para ti.»), «Hemos mirado las 199 zonas…», el aviso del alquiler, «¿Quieres ver más zonas?» con las dos cifras de la API («saldrían 49 más: 91 zonas en total»), «Buscar zonas para mí» y el ejemplo de la familia por su nombre. En el móvil, el recorrido del mapa por filas toca antes «Ver el mapa», porque la portada abre ahora con la búsqueda.

## Golden y contrato

`scripts/golden_search.py` contra `housing` en solo lectura: **10 de 10**. `golden_senior` no usa `seniors`. Tests nuevos: el dominio destaca centros de mayores con «Somos mayores» y la búsqueda da las mismas zonas, % y recuentos con y sin el campo; el contrato es aditivo (`seniors: false` por defecto, sin sumar personas); en la web, lo que marca «Somos mayores», el lugar, el ámbito por defecto, el ejemplo y el orden de la tarjeta (`scenario.test.ts`, `gaps.test.ts`).

**Ejemplo «Pareja jubilada que quiere vivir cerca de su familia»** (API `fit-0.9`, `housing`): **22 de los 131 barrios**. Arriba, Alameda de Osuna y Casco Histórico de Barajas (92 %); después, Ventas, Pueblo Nuevo, Quintana y San Pascual (89 %), La Concepción (88 %), Arcos y Rosas (87 %). Lo que más limita es el trayecto de 30 min hasta la estación de Ciudad Lineal.

## Capturas (390, 360 y 1440 px)

| | 390 | 360 | 1440 |
|---|---|---|---|
| Portada | `01-portada-390.png` | `01-portada-360.png` | `01-portada-1440.png` |
| Formulario | `02-formulario-390.png` | `02-formulario-360.png` | `02-formulario-1440.png` |
| «Somos mayores» elegido (con «En pareja») | `03-somos-mayores-390.png` | `03-somos-mayores-360.png` | `03-somos-mayores-1440.png` |
| Ejemplo «Pareja jubilada» | `04-ejemplo-pareja-jubilada-390.png` | `04-ejemplo-pareja-jubilada-360.png` | `04-ejemplo-pareja-jubilada-1440.png` |
| Lista (ejemplo de la familia) | `05-lista-390.png` | `05-lista-360.png` | `05-lista-1440.png` |
| Tarjeta (la 1.ª de la lista) | `06-tarjeta-390.png` | `06-tarjeta-360.png` | `06-tarjeta-1440.png` |
| «Somos mayores»: «¿Cerca de dónde queréis vivir?», con un lugar elegido | `03b-somos-mayores-lugar-390.png` | `03b-somos-mayores-lugar-360.png` | `03b-somos-mayores-lugar-1440.png` |
| Tarjeta del ejemplo de los jubilados («Lo que le falta…») | `04b-tarjeta-pareja-jubilada-390.png` | `04b-tarjeta-pareja-jubilada-360.png` | `04b-tarjeta-pareja-jubilada-1440.png` |
| «Cómo lo calculamos» (desempate y ejemplo real) | `07-como-lo-calculamos-390.png` | `07-como-lo-calculamos-360.png` | `07-como-lo-calculamos-1440.png` |
| Distrito: «Los barrios que más te convienen» | `08-distrito-barrios-390.png` | `08-distrito-barrios-360.png` | `08-distrito-barrios-1440.png` |

Antes, a 390 y 1440 px: `antes/01-portada-*.png`, `antes/02-formulario-*.png`, `antes/05-lista-*.png`, `antes/06-tarjeta-*.png` y `antes/07-como-lo-calculamos-*.png`.

## Lo que se ve en las capturas y queda abierto

- **Portada del móvil:** la hoja abre desplegada; «Tu búsqueda» y «¿Dónde?» se ven sin deslizar nada a 390 y a 360 px. A 360 px las pestañas «Qué falta» y «Cómo lo calculamos» se parten en dos líneas dentro de su botón: no se salen de la pantalla.
- **Fila de la lista:** con letra de 16 px o más, la banda, el % y el precio van en la línea de debajo del nombre (antes, «Distrito / de / Madrid» palabra a palabra). La entrega 2 rehace la fila (nombre, banda y precio).
- **Ejemplo «Pareja jubilada», resuelto (R-02):** con la primera versión (900 €, sin sitio, toda la Comunidad) salían 155 zonas con pueblos pequeños al 98 % arriba (Anchuelo, Morata de Tajuña). Con el diseño de Mariano (cerca de la familia, 30 min, «Madrid capital») salen 22 barrios cercanos. Tarjeta de su 1.º barrio (Barajas, captura `04b`): centros de salud (No comparable), farmacias (CUBIERTO) y centros de mayores (No comparable), sin «Colegios · JUSTO» ni escuelas infantiles: la tarjeta pone primero lo que importa al hogar, en todos los hogares (R-01 y la regla de «lo que le falta que le afecte», adelantada de la entrega 2).
- **Filas con «Dato aproximado»:** la cifra baja bajo la banda y se queda a la derecha. La entrega 2 rehace la fila.
- **Deuda anotada (revisión del PR #79):** el encuadre del mapa en el móvil (`lib/map/camera.ts`, la cabecera de 130 px y la leyenda de 100 px fijas, medidas con la raíz de 17 px) y la etiqueta en mayúsculas de `ZoneGapsView`.
- **Scripts de QA antiguos** (`apps/web/scripts/check-qa.mjs`, `check-search.mjs`, `count-requests.mjs`): buscan los textos de antes y la hoja plegada; no se han adaptado ni ejecutado. No los usa la CI.
