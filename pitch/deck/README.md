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
| `../capturas/C1.png`… | Capturas reales (C1–C7 de `pitch/slides.md`). Si no hay una aquí, el build usa la de la evidencia (`EVIDENCE_CAPTURES` en `build.py`), recortada en `deck.css`. C5–C7 son de B en producción (`evidence/map-004/2026-11-11/prod_*`). C1–C4 son de B con datos reales (`evidence/map-004/2026-11-12/deck/`): C3 y C4 tras gap-0.3 (PR #17) y C1 y C2 con `fit-0.2` (PR #19). Si no hay ninguna, el hueco sale con borde discontinuo |

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
| Contraste de los 12 pares de color, con el cristal mezclado sobre el punto más oscuro del fondo | 4,5:1 texto; 3:1 texto grande (cifra de datasets, números en círculo) | Todos en verde: el peor es 4,87:1 (violeta de la cifra grande sobre cristal) y el texto pequeño más bajo, 4,94:1 (fuentes sobre el fondo) |
| Tamaño mínimo de letra | 22 px (≈ 11 pt en una slide estándar de 13,33 in, solo para fuentes y pies). La lectura va a 28 px o más y los títulos a 56 px o más | Mínimo 22 px |
| PDF | 4 páginas de 1440 × 810 pt (1920 × 1080 px), con Inter y Plus Jakarta Sans incrustadas | OK |
| `--final` | Ninguna marca «pendiente» y las 7 capturas presentes | 12 nov, con las C3 y C4 de B (PR #17, fusionado): genera sin fallos con `DECK_INTEGRANTES`; sin él, solo falta el nombre |

**Nota:** Chrome incrusta las fuentes variables como Type 3. Se ven bien en Acrobat, Vista Previa y Chrome; aun así, se revisa el PDF en el portátil de la final.

## Marcas pendientes hoy
| Dónde | Qué falta | De quién |
|---|---|---|
| Slide 1 | El nombre completo, que se pasa con `DECK_INTEGRANTES` | Mariano, el 24 nov |

Cerradas el 11 nov:
- el buscador está encendido en producción (`deploy-12-buscador.md`, PR #11);
- C1–C3 son capturas de producción de C (PR #11, fusionado el 12 nov) y C4–C7, de B.

Cerradas el 12 nov: C3 y C4 rehechas por B tras gap-0.3 (PR #17), con recortes nuevos en `deck.css`; C1 y C2 rehechas con `fit-0.2` (PR #19), con el número 3 de la slide 4 bajado 15 px para que quede junto a «Qué falta aquí».

Cambiadas el 12 nov, con gap-0.3 (D-217) en producción:
- el ejemplo de la slide 3 pasa de Madrid capital (que ya sale JUSTO en centros de salud) a **Puente de Vallecas, escuelas infantiles**: 2,781 frente a 4,87, ratio 0,571 (`GET /api/v1/gaps/distrito/2807913`, comprobado en producción el 12 nov);
- la slide 2 cuenta 26 datasets CM (los dos de camas y las tres topologías del CRTM con la accesibilidad de las estaciones son del 12 nov) y nombra al Ministerio de Sanidad entre las fuentes de apoyo (D-218).

Las de B se hicieron antes de desplegar el PR #9, así que en algunos textos todavía se ve el método anterior. Los recortes de `deck.css` los dejan fuera (`pitch/slides.md`, «Capturas necesarias», con la lista de lo que se rehace tras gap-0.3).


Para cerrar una marca, se quita `class="pending"` y su `data-pending` en `deck.html`. Si lo marcado no llega, se borra el elemento entero: nunca se deja un hueco ni un «próximamente».

## Checklist del 24 nov
1. Rebase y `uv run python pitch/build_datasets_cm.py --refresh-portal`; el build toma de ahí el número y los enlaces de la slide 2.
2. Hacer las capturas C1–C7 sobre la demo desplegada (`pitch/slides.md`, «Capturas necesarias») y guardarlas como `pitch/capturas/C1.png`… Escritorio a 1440 × 900 y móvil a 390 × 844, a 2×. Una captura en `pitch/capturas/` sustituye a la de B; si cambia el encuadre, se ajusta su recorte en `deck.css` (`object-view-box`).
3. Si cambia la captura C1, revisar las posiciones de los números 1–3 de la slide 4 (`.s4 .m1`… en `deck.css`). Hoy están puestas sobre la de producción.
4. Cerrar las marcas pendientes y construir con `--final` y `DECK_INTEGRANTES`.
5. Revisar `build/preview-*.png` y el PDF a pantalla completa, leyéndolo a 3 m. Mariano lo revisa.
6. Copiar el PDF al portátil y a un USB. Se sube a la plataforma el 26 antes de las 13:30.
