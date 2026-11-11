# Deck de la final — Vida Fácil (bases §8)

Las 4 slides de la entrega del 26 nov:
1. título, integrantes y descripción;
2. problema y datasets con enlaces;
3. resultados;
4. pantallazo.

Están maquetadas en HTML a 16:9 (1920 × 1080) con el estilo del brief (D-201): modo claro, navy + violeta + cristal, Plus Jakarta Sans e Inter, con los tokens que B validó en la web. El contenido sale de `pitch/slides.md`; aquí va su versión corta, para leerla proyectada.

## Ficheros
| Fichero | Qué es |
|---|---|
| `deck.html` | Plantilla de las 4 slides, con huecos `{{…}}` que rellena el build |
| `deck.css` | Tokens y maquetación. Tamaños pensados para proyector |
| `build.py` | Rellena la plantilla, comprueba contraste y tamaños, imprime el PDF con Chrome y revisa el PDF |
| `build/` | Salida (no se versiona): `index.html`, `VidaFacil_DATAMAD2026.pdf` y `preview-N.png` |
| `../capturas/C1.png`… | Capturas reales (C1–C7 de `pitch/slides.md`). Si no hay una aquí, el build usa la de producción del 11 nov (`EVIDENCE_CAPTURES` en `build.py`), recortada en `deck.css`. C4–C7 son de B (`evidence/map-004/2026-11-11/prod_*`). C1–C3 son de C (`evidence/gate-06/2026-11-11-deploy/prod-buscador-*`) y llegan con el PR #11. Si no hay ninguna, el hueco sale con borde discontinuo |

## Cómo se genera
Desde la raíz del repo. Necesita Chrome (o `CHROME=/ruta`), poppler para revisar el PDF y red para las fuentes de Google:
```bash
uv run --with segno==1.6.6 python pitch/deck/build.py            # borrador: se permiten marcas pendientes
DECK_INTEGRANTES="…" uv run --with segno==1.6.6 python pitch/deck/build.py --final   # 24 nov
```

Lo que rellena el build:
- **Slide 2:** las filas de datasets y el número de la cabecera salen del catálogo y de la instantánea del portal, igual que `pitch/datasets_cm.md`. Solo los nombres cortos están escritos a mano, en `SHORT_NAMES`.
- **QR:** los de la demo y el repo los genera `segno` (versión fijada; se usa con `--with`, sin tocar `uv.lock`).
- **Equipo (slide 1):** el nombre completo sale de `DECK_INTEGRANTES` al construir. Decisión de Mariano (11 nov): en el repo público solo «Mariano»; el nombre completo va solo en el PDF del deck y en el formulario. Sin la variable sale «Mariano» marcado como pendiente, y `--final` no deja pasar.

## Qué comprueba
| Comprobación | Umbral | Resultado del 11 nov |
|---|---|---|
| Contraste de los 12 pares de color, con el cristal mezclado sobre el punto más oscuro del fondo | 4,5:1 texto; 3:1 texto grande (cifra «21», números en círculo) | Todos en verde: el peor es 4,87:1 (violeta de la cifra grande sobre cristal) y el texto pequeño más bajo, 4,94:1 (fuentes sobre el fondo) |
| Tamaño mínimo de letra | 22 px (≈ 11 pt en una slide estándar de 13,33 in, solo para fuentes y pies). La lectura va a 28 px o más y los títulos a 56 px o más | Mínimo 22 px |
| PDF | 4 páginas de 1440 × 810 pt (1920 × 1080 px), con Inter y Plus Jakarta Sans incrustadas | OK |
| `--final` | Ninguna marca «pendiente» y las 7 capturas presentes | Hoy falla solo por C1–C3, hasta que se fusione el PR #11. Con ellas en su sitio, el 11 nov pasó todo menos el nombre, que se pasa con `DECK_INTEGRANTES` |

**Nota:** Chrome incrusta las fuentes variables como Type 3. Se ven bien en Acrobat, Vista Previa y Chrome; aun así, se revisa el PDF en el portátil de la final.

## Marcas pendientes hoy
| Dónde | Qué falta | De quién |
|---|---|---|
| Slide 1 | El nombre completo, que se pasa con `DECK_INTEGRANTES` | Mariano, el 24 nov |
| Slides 3 y 4 | Capturas C1, C2 y C3: ya están hechas en producción, en la rama `claude/s1-deploy` (PR #11). El build las encuentra en cuanto se fusiona | A, al fusionar el PR #11 |

Cerradas el 11 nov:
- el buscador está encendido en producción (`deploy-12-buscador.md`, PR #11);
- las cifras de Madrid capital se comprobaron en producción con `gap-0.2` (0,371 frente a 0,5553);
- C4, C5, C6 y C7 son capturas de producción de B.

Esas capturas se hicieron antes de desplegar el PR #9, así que en algunos textos todavía se ve el método anterior. Los recortes de `deck.css` los dejan fuera (`pitch/slides.md`, «Capturas necesarias»).

Para comprobar el encuadre de C1–C3 antes de la fusión, se copian de esa rama a `pitch/capturas/` y se borran después: no se versionan dos veces.

Para cerrar una marca, se quita `class="pending"` y su `data-pending` en `deck.html`. Si lo marcado no llega, se borra el elemento entero: nunca se deja un hueco ni un «próximamente».

## Checklist del 24 nov
1. Rebase y `uv run python pitch/build_datasets_cm.py --refresh-portal`; el build toma de ahí el número y los enlaces de la slide 2.
2. Hacer las capturas C1–C7 sobre la demo desplegada (`pitch/slides.md`, «Capturas necesarias») y guardarlas como `pitch/capturas/C1.png`… Escritorio a 1440 × 900 y móvil a 390 × 844, a 2×. Una captura en `pitch/capturas/` sustituye a la de B; si cambia el encuadre, se ajusta su recorte en `deck.css` (`object-view-box`).
3. Si cambia la captura C1, revisar las posiciones de los números 1–3 de la slide 4 (`.s4 .m1`… en `deck.css`). Hoy están puestas sobre la de producción.
4. Cerrar las marcas pendientes y construir con `--final` y `DECK_INTEGRANTES`.
5. Revisar `build/preview-*.png` y el PDF a pantalla completa, leyéndolo a 3 m. Mariano lo revisa.
6. Copiar el PDF al portátil y a un USB. Se sube a la plataforma el 26 antes de las 13:30.
