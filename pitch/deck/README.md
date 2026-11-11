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
| `../capturas/C1.png`… | Capturas reales (C1–C6 de `pitch/slides.md`). Si falta alguna, su hueco sale con borde discontinuo |

## Cómo se genera
Desde la raíz del repo. Necesita Chrome (o `CHROME=/ruta`), poppler para revisar el PDF y red para las fuentes de Google:
```bash
uv run --with segno==1.6.6 python pitch/deck/build.py            # borrador: se permiten marcas pendientes
DECK_INTEGRANTES="…" uv run --with segno==1.6.6 python pitch/deck/build.py --final   # 24 nov
```

Lo que rellena el build:
- **Slide 2:** las filas de datasets y el número de la cabecera salen del catálogo y de la instantánea del portal, igual que `pitch/datasets_cm.md`. Solo los nombres cortos están escritos a mano, en `SHORT_NAMES`.
- **QR:** los de la demo y el repo los genera `segno` (versión fijada; se usa con `--with`, sin tocar `uv.lock`).
- **Equipo (slide 1):** el nombre sale de `DECK_INTEGRANTES`, para no guardarlo en el repo público hasta que Mariano lo confirme; sin la variable sale «Mariano» marcado como pendiente.

## Qué comprueba
| Comprobación | Umbral | Resultado del 11 nov |
|---|---|---|
| Contraste de los 12 pares de color, con el cristal mezclado sobre el punto más oscuro del fondo | 4,5:1 texto; 3:1 texto grande (cifra «21», números en círculo) | Todos en verde: el peor es 4,87:1 (violeta de la cifra grande sobre cristal) y el texto pequeño más bajo, 4,94:1 (fuentes sobre el fondo) |
| Tamaño mínimo de letra | 22 px (≈ 11 pt en una slide estándar de 13,33 in, solo para fuentes y pies). La lectura va a 28 px o más y los títulos a 56 px o más | Mínimo 22 px |
| PDF | 4 páginas de 1440 × 810 pt (1920 × 1080 px), con Inter y Plus Jakarta Sans incrustadas | OK |
| `--final` | Ninguna marca «pendiente» y las 6 capturas presentes | Hoy falla a propósito: faltan las capturas y 6 marcas |

**Nota:** Chrome incrusta las fuentes variables como Type 3. Se ven bien en Acrobat, Vista Previa y Chrome; aun así, se revisa el PDF en el portátil de la final.

## Marcas pendientes hoy
| Dónde | Qué falta | De quién |
|---|---|---|
| Slide 1 | Nombre completo del equipo (`DECK_INTEGRANTES`) | Mariano |
| Slide 2 | «+ Ayuntamiento de Madrid (distritos)», solo si llega DATA-012 | A |
| Slide 3 | Zona y cifras finales de «Qué falta» (hoy Móstoles, provisional) y «+ los 21 distritos de Madrid» | A (GAP-001, DATA-012) |
| Slides 3 y 4 | URL de la demo verificada | C (17 nov) |
| Todas | Capturas C1–C6 | B / D el 24 nov |

Para cerrar una marca, se quita `class="pending"` y su `data-pending` en `deck.html`. Si lo marcado no llega, se borra el elemento entero: nunca se deja un hueco ni un «próximamente».

## Checklist del 24 nov
1. Rebase y `uv run python pitch/build_datasets_cm.py --refresh-portal`; el build toma de ahí el número y los enlaces de la slide 2.
2. Hacer las capturas C1–C6 sobre la demo desplegada (`pitch/slides.md`, «Capturas necesarias») y guardarlas como `pitch/capturas/C1.png`… Escritorio a 1440 × 900 y móvil a 390 × 844, a 2×.
3. Ajustar sobre la captura C1 las posiciones de los números 1–3 de la slide 4 (`.s4 .m1`… en `deck.css`).
4. Cerrar las marcas pendientes y construir con `--final` y `DECK_INTEGRANTES`.
5. Revisar `build/preview-*.png` y el PDF a pantalla completa, leyéndolo a 3 m. Mariano lo revisa.
6. Copiar el PDF al portátil y a un USB. Se sube a la plataforma el 26 antes de las 13:30.
