# Claridad en el móvil, remate de la entrega 2 (16 nov)

Rama `claude/s1-ux-mobile-3`, desde `c0e9d11` (#81 fusionado, D-245). Tres puntos menores de la revisión de #81 y uno de diseño: M-01 (concordancia «tú»/«vosotros» incompleta), M-02 y M-03 (textos de D-245 que no decían lo que hace el código) e I-03 (el panel del barrio repetía la banda y el precio de su fila). Decisión: D-245 §11. Textos: `pitch/textos_web.md` («Remate»). Solo la web y los textos: ni el contrato, ni la fórmula, ni la API cambian.

**Cómo se ha medido.** Un solo `npm run build` (sin borrar `.next`) con `next start` en el puerto 3081, contra la API de la rama en el 8081 sobre la base local `housing` en solo lectura (`default_transaction_read_only=on`).

## Qué cambia en pantalla

- **M-01, «tú» o «vosotros» según el hogar** también en «Casi valen» y en lo que una zona no cumple en su tarjeta («Se pasa unos 90 € al mes de vuestro presupuesto»; `01-casi-valen-*.png`, `03-tarjeta-casi-valen-*.png`), en «¿Queréis ver más zonas?» («Mirad cuántas salen si cambiáis una sola cosa:», «Lo que más limita vuestra búsqueda es:», «No os decimos que gastéis más…»; `02-quereis-ver-mas-zonas-*.png`), en la leyenda tras buscar («Zonas que os convienen», «Os conviene menos/más»; `01-casi-valen-1440.png`) y en «Lo que tenéis aquí», «Fuera de vuestra búsqueda», «Tiene lo que pedís…», «Ningún … cumple todo lo que pedís. Mirad abajo…», «… vuestro presupuesto» de los pueblos, la etiqueta del mapa y «¿Trabajáis fuera de casa? Decidnos dónde…». El criterio y lo que sigue en «tú», en D-245 §11.
- **I-03, el panel del barrio** dice solo lo que su fila deja fuera: el % (en el móvil, donde la fila no lo enseña), con quién empata, «Para un piso de unos 77 m² · Dato aproximado» y sus hechos (`04-barrio-panel-*.png`; en el escritorio, sin el %, que ya está en la fila).
- **Barrios sin contorno en el mapa** (contornos bloqueados en la prueba): salen plegados como los demás y cada fila es un botón que abre su panel (`aria-expanded`), sin tocar el mapa (`05-barrios-sin-contorno-plegados-*.png`, `05b-barrio-sin-contorno-abierto-*.png`). Antes salían todos abiertos.
- **Revisión de #82 (R-01 a R-05):** el selector de la leyenda dice «¿Qué queréis ver?» tras buscar con dos o más personas (R-01); el aviso de empate de «Somos mayores» con una persona sola dice «… elige cerca de dónde quieres vivir…» (R-02, con test). Sin build nuevo, a petición del orquestador: las capturas son de antes de R-01 (`01-casi-valen-1440.png` aún dice «¿Qué quieres ver?») y R-02 no sale en ellas. El guion comprueba el % del panel en el móvil con `^\d+\s*%` (R-03); los textos del panel guardados en `capturas-ux3.json` también lo cumplen. El e2e de la leyenda mira solo su título y su rampa, no las opciones del selector (R-05).
- **«No comparable» para el lector de pantalla (visto en producción por C):** la etiqueta dice el motivo de su fila (`notComparableHelp`, con test), no la frase común de «centros u hogares»; en «Qué falta» no lo repite, porque la frase de la API va a la vista en la misma fila. Tampoco está en el build medido: lo cubren el test, tsc y el build de la CI.
- **M-02 y M-03:** solo textos (D-245 §7 y §9, `fila.zona_pequena.ayuda` y el comentario de `GapRowItem.tsx`).

## Letra, botones y axe

- `apps/web/scripts/check-ux-mobile.mjs --widths 390 --counts ""` (`tamanos-despues.json`): **0 textos de menos de 16 px y 0 objetivos de menos de 44 px** en todas las pantallas a 390 px (portada, formulario, lista, tarjeta, tarjeta con «Ver más», distrito, pantalla de zona, «No comparable», «Somos mayores»); los 3 controles del mapa, como siempre, aparte. **axe: 0 incidencias** a 390 px y a 1440 px.
- Lo que cambia, con su propio guion (`capture-ux3.mjs`, `capturas-ux3.json`, 39/39 a 390 y 1440 px): la tarjeta de una zona de «Casi valen» con «Ver más» y el distrito con un panel de barrio abierto, con y sin contorno: axe 0, ningún texto de menos de 16 px ni botón de menos de 44 px, y ninguna frase en «tú» sobre la búsqueda de la familia.

## e2e contra la web compilada

`infra/deploy/e2e/e2e_prod.mjs --base http://localhost:3081`: **escritorio 1440 px 116/116, móvil 390 px 92/92**, también tras R-05 (contra el mismo build) (`e2e/e2e-report.json`; antes 114/114 y 90/90). Se han adaptado sin debilitar ninguna comprobación: «¿Queréis ver más zonas?» y «Lo que tenéis aquí» se buscan con las palabras del hogar del ejemplo (una pareja), y J5 comprueba que no sale ni «¿Trabajas…?» ni «¿Trabajáis…?». Nuevas: el título de la leyenda es «Zonas que os convienen» y su rampa dice «Os conviene menos» y «Os conviene más» (sin mirar el selector), y cada fila de «Casi valen» dice lo que le falta con «vuestro presupuesto» o «pedís» (`nearMissLine` de `shown_text.mjs`, que ya no acepta las dos formas a la vez).

## Golden y tests

- `scripts/golden_search.py` contra `housing` en solo lectura: **10 de 10**.
- `make lint typecheck test-unit`: Python 1031, vitest 566 (antes 562: una pareja y una persona sola en «Casi valen» y en la tarjeta, la voz nueva, `noneText`, `fitsButShortText`, el alquiler de los pueblos, el aviso de empate de una persona mayor que vive sola y la ayuda de «No comparable» de cada fila), eslint, tsc, ruff y pyright limpios.

## Lo que queda abierto

- Los hechos de la API siguen en «tú» («No llegas a … en transporte público»): son de la API, no de la web.
- `ZonePrice.long` y `ZonePrice.area` ya no los usa ningún componente (los usaba el panel del barrio); no se borran sin confirmación.
