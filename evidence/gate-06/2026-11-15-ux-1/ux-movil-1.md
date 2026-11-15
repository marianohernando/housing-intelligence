# Claridad en el móvil, primera entrega (15 nov)

Rama `claude/s1-ux-mobile`, desde `0c6ce28` (producción con `fit-0.9`). Origen: la prueba en persona del 15 nov con una persona mayor («difícil de entender, muchos datos juntos») y la auditoría `prompts/UX_AUDITORIA_MOVIL.md` (opción 1, con «Somos mayores», D-244).

**Cómo se ha medido.** Web compilada (`npm run build` + `next start`, puerto 3061) contra la API de la rama en el puerto 8061, sobre la base local `housing` en solo lectura. El «antes» es el código de `0c6ce28` en `next dev` (las capturas de `antes/` llevan el indicador «N» de Next en la esquina). Script: `apps/web/scripts/check-ux-mobile.mjs`.

```
node apps/web/scripts/check-ux-mobile.mjs --base http://localhost:3061 --out evidence/gate-06/2026-11-15-ux-1 --label despues --widths 390,360 --shots
```

Para cada pantalla lista cada texto por debajo de 16 px y cada objetivo táctil por debajo de 44 px (alto o ancho), sin contar lo que solo es para el lector de pantalla. Una casilla o una opción cuenta por su etiqueta, que es lo que se toca. «Formulario abierto» es el formulario con todas sus ayudas y «Más opciones» desplegadas; «formulario con el ejemplo», el que deja el ejemplo de la familia (lugar de trabajo, días, límite, servicio a un paseo y contador).

## Antes y después (texto < 16 px · objetivos < 44 px)

| Pantalla | 390 px, antes | 390 px, después | 360 px, antes | 360 px, después |
|---|---|---|---|---|
| Portada | 8 · 1 | **0 · 0** | 8 · 1 | **0 · 0** |
| Formulario | 24 · 2 | **0 · 0** | 24 · 2 | **0 · 0** |
| Formulario abierto | 26 · 2 | **0 · 0** | 26 · 2 | **0 · 0** |
| Formulario con el ejemplo | 32 · 2 | **0 · 0** | 32 · 2 | **0 · 0** |
| Lista | 36 · 0 | **0 · 0** | 36 · 0 | **0 · 0** |
| Tarjeta | 25 · 1 | **0 · 0** | 25 · 1 | **0 · 0** |

- **Antes:** textos de 12,2 a 15,3 px: la banda («Encaja muy bien», 12,2), «por 77 m²» (12,8), «· Dato fiable» y FALTA/JUSTO/CUBIERTO (13,3), «Distrito de Madrid», «Empatan al 94 %» y «Probar así» (13,6), y las opciones, chips, ayudas y avisos (14,9). Objetivos: «Alquilar» y «Comprar» (38 px), «Ver las zonas en una lista» (39 px) y «Ver todo lo que falta» (24 px).
- **Después:** el texto más pequeño mide 16 px en el escritorio y 16,9 px en el móvil (`--text-xs`); el cuerpo, 17 y 18 px. Todos los objetivos miden 44 px o más.
- **No se cuentan,** antes ni después, los 3 controles del mapa (el (i) de las fuentes y los dos enlaces de licencia «© OpenStreetMap · Powered by CRTM», que son de MapLibre y obligatorios por licencia).
- Detalle de cada elemento: `tamanos-antes.json` y `tamanos-despues.json`.

## axe (WCAG 2.2 AA)

0 incidencias después, a 390 y a 360 px, en la portada, el formulario abierto, la lista y la tarjeta (`tamanos-despues.json`, campo `axe`). Antes: 0 en la primera pasada y 1 `target-size` intermitente en la segunda (la línea «Para unos 77 m² (cámbialo)», que ya no existe).

## e2e contra la web compilada

`infra/deploy/e2e/e2e_prod.mjs --base http://localhost:3061`: escritorio 1440 px **74/74**, móvil 390 px **50/50** (`e2e/e2e-report.json`). Los textos que comprueba se han adaptado sin quitar ninguna comprobación: el resumen («Hemos encontrado 42 zonas para ti.»), «Hemos mirado las 199 zonas…», el aviso del alquiler, «¿Quieres ver más zonas?» con las dos cifras de la API («saldrían 49 más: 91 zonas en total»), «Buscar zonas para mí» y el ejemplo de la familia por su nombre. En el móvil, el recorrido del mapa por filas toca antes «Ver el mapa», porque la portada abre ahora con la búsqueda.

## Golden y contrato

`scripts/golden_search.py` contra `housing` en solo lectura: **10 de 10**. `golden_senior` no usa `seniors`. Tests nuevos: el dominio destaca centros de mayores con «Somos mayores» y la búsqueda da las mismas zonas, % y recuentos con y sin el campo; el contrato es aditivo (`seniors: false` por defecto, sin sumar personas).

## Capturas (390, 360 y 1440 px)

| | 390 | 360 | 1440 |
|---|---|---|---|
| Portada | `01-portada-390.png` | `01-portada-360.png` | `01-portada-1440.png` |
| Formulario | `02-formulario-390.png` | `02-formulario-360.png` | `02-formulario-1440.png` |
| «Somos mayores» elegido (con «En pareja») | `03-somos-mayores-390.png` | `03-somos-mayores-360.png` | `03-somos-mayores-1440.png` |
| Ejemplo «Pareja jubilada» | `04-ejemplo-pareja-jubilada-390.png` | `04-ejemplo-pareja-jubilada-360.png` | `04-ejemplo-pareja-jubilada-1440.png` |
| Lista (ejemplo de la familia) | `05-lista-390.png` | `05-lista-360.png` | `05-lista-1440.png` |
| Tarjeta (la 1.ª de la lista) | `06-tarjeta-390.png` | `06-tarjeta-360.png` | `06-tarjeta-1440.png` |
| «Cómo lo calculamos» (desempate y ejemplo real) | `07-como-lo-calculamos-390.png` | `07-como-lo-calculamos-360.png` | `07-como-lo-calculamos-1440.png` |

Antes, a 390 y 1440 px: `antes/01-portada-*.png`, `antes/02-formulario-*.png`, `antes/05-lista-*.png`, `antes/06-tarjeta-*.png` y `antes/07-como-lo-calculamos-*.png`.

## Lo que se ve en las capturas y queda abierto

- **Portada del móvil:** la hoja abre desplegada; «Tu búsqueda» y «¿Dónde?» se ven sin deslizar nada a 390 y a 360 px. A 360 px las pestañas «Qué falta» y «Cómo lo calculamos» se parten en dos líneas dentro de su botón: no se salen de la pantalla.
- **Fila de la lista:** con letra de 16 px o más, la banda, el % y el precio van en la línea de debajo del nombre (antes, «Distrito / de / Madrid» palabra a palabra). La entrega 2 rehace la fila (nombre, banda y precio).
- **Ejemplo «Pareja jubilada» (`fit-0.9`):** 155 zonas, y arriba salen pueblos pequeños bien dotados al 98 % (Anchuelo, Morata de Tajuña). Es el efecto conocido de D-243 §13 sin lugar de trabajo. Con «Somos mayores» ya no sale `resultados.sin_lugar`, que además de pedir el trabajo proponía «Madrid capital». Queda para decidir: una línea solo con «¿Dónde?» para quien no trabaja, o el ejemplo en «Alrededores» o «Madrid capital».
- **Scripts de QA antiguos** (`apps/web/scripts/check-qa.mjs`, `check-search.mjs`, `count-requests.mjs`): buscan los textos de antes y la hoja plegada; no se han adaptado ni ejecutado. No los usa la CI.
