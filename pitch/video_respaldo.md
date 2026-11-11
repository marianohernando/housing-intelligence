# Vídeo de respaldo de 2 minutos — Vida Fácil (PITCH-003)

## Para qué sirve
Es el plan B de la final del 26 nov: si cae la wifi o la demo, se pone este vídeo en lugar de los bloques 2 y 3 del guion (`pitch/guion.md`, «Antes de empezar», punto 4). Cuenta el mismo recorrido que la demo en directo y se entiende solo, también sin sonido, gracias a los rótulos.

- **Cuándo se graba:** el 23 nov (freeze), sobre la demo desplegada y verificada (https://vida-facil-eight.vercel.app). Así coincide con lo que verá el jurado. Antes no: hasta el 16–17 nov faltan piezas de A, B y C.
- **Quién:** la voz es de Mariano; el montaje lo puede hacer la línea D con las tomas.
- **Dónde se guarda:** **no se sube al repo** (es binario y pesa). Se guardan 3 copias:
  - en el escritorio del portátil de la final;
  - en un USB;
  - en una carpeta privada en la nube.
  - El enlace a la carpeta lo apunta Mariano; no va en el repo.

## Ficha técnica
| Elemento | Valor |
|---|---|
| Duración | 2:00 como máximo (objetivo 1:55) |
| Formato | MP4 (H.264 + AAC), 1920 × 1080 a 30 fps, menos de 150 MB |
| Grabación | Captura de pantalla de macOS (Cmd + Shift + 5 → «Grabar pantalla completa»), un plano por toma |
| Navegador | Ventana limpia a pantalla completa, zoom del 110 % para que se lea en el proyector, sin extensiones visibles, notificaciones desactivadas y cursor visible |
| Voz | Grabada aparte, con el micrófono del portátil en una sala sin eco, y ajustada a cada plano en el montaje |
| Rótulos | Quemados en la imagen: Plus Jakarta Sans 600 en navy `#141B3D`, sobre una tarjeta de cristal blanca al 82 % (tokens de `pitch/slides.md`). Además, un `.srt` con la locución |
| Montaje | iMovie (gratis en macOS): cortes entre planos y rótulos. Sin música, para que se oiga bien en la sala |
| Nombres | `VidaFacil_demo_2min.mp4` y `VidaFacil_demo_2min.srt` |

## Recuento de la locución
A unas 130 palabras por minuto, unas 2,2 palabras por segundo. Cada plano tiene un máximo de palabras para que dé tiempo a ver la pantalla.
```bash
for p in 1 2 3 4 5 6 7 8; do printf "p$p "; awk -v p=$p '$0 ~ "^<!-- voz:p"p":fin"{f=0} f; $0 ~ "^<!-- voz:p"p":inicio"{f=1}' pitch/video_respaldo.md | wc -w; done
```

| Plano | Tiempo | Duración | Palabras (máximo) | Locución a 130 ppm |
|---|---|---|---|---|
| 1 | 0:00–0:08 | 8 s | 14 (≤ 15) | 6 s |
| 2 | 0:08–0:20 | 12 s | 24 (≤ 26) | 11 s |
| 3 | 0:20–0:38 | 18 s | 33 (≤ 39) | 15 s |
| 4 | 0:38–0:55 | 17 s | 27 (≤ 37) | 12 s |
| 5 | 0:55–1:07 | 12 s | 24 (≤ 26) | 11 s |
| 6 | 1:07–1:22 | 15 s | 21 (≤ 32) | 10 s |
| 7 | 1:22–1:44 | 22 s | 34 (≤ 47) | 16 s |
| 8 | 1:44–1:58 | 14 s | 24 (≤ 30) | 11 s |
| **Total** | | **118 s** | **201** | **93 s de voz + pausas para mirar** |

**Lo que va entre corchetes** (`[pct]`, `[N]`, `[zona]`…) se lee en la pantalla el día de la grabación y se escribe igual en el rótulo. Nunca se pone una cifra de memoria.

---

## Planos

### Plano 1 · 0:00–0:08 · Portada
- **Pantalla:** portada de la demo con «Encuentra tu sitio en Madrid» y «Así funciona». Sin cursor en movimiento.
- **Rótulo:** «Vida Fácil · Encuentra tu sitio en Madrid».

<!-- voz:p1:inicio -->
Vida Fácil te ayuda a encontrar tu sitio en Madrid con datos abiertos oficiales.
<!-- voz:p1:fin -->

### Plano 2 · 0:08–0:20 · El caso de ejemplo
- **Acción:** clic en «Ver un ejemplo: pareja con 2 hijos que trabaja en la Castellana» (`textos_web.md`, `portada.ejemplo.boton`; texto final **pendiente de B**).
- **Se ve:** la tarjeta «Tu búsqueda» rellena: «Con hijos (2)», «Colegios», «Trabajo en: Castellana», «Hasta 1.500 € al mes».
- **Rótulo:** «Pareja con 2 hijos · alquiler hasta 1.500 €/mes · trabajo en la Castellana».
- **Fuente:** `data/fixtures/contracts/scenario_state.familia_castellana.fixture.json`. Si A cambia el caso precargado, se cambian la locución y el rótulo.

<!-- voz:p2:inicio -->
Una pareja con dos hijos busca alquiler. Trabajan en la Castellana, pueden pagar hasta mil quinientos euros al mes y quieren un colegio cerca.
<!-- voz:p2:fin -->

### Plano 3 · 0:20–0:38 · Zonas que encajan
- **Acción:** clic en «Ver zonas que encajan». Esperar a que se coloree el mapa y señalar la tarjeta de zona con el cursor, despacio.
- **Se ve:** el mapa con la escala de violetas y la leyenda «Encaje con tu búsqueda», y la tarjeta de la zona con «[pct] % de encaje» y 3–5 hechos con su fiabilidad.
- **Rótulo:** «[zona] · [pct] % de encaje».
- **Estado:** **pendiente de A** (CORE-003 y CORE-005) y **pendiente de B** (pantalla).

<!-- voz:p3:inicio -->
Pulsamos «Ver zonas que encajan». El mapa se colorea según cuánto encaja cada zona con esta familia. La primera encaja en un [pct] por ciento, y debajo vemos por qué, dato a dato.
<!-- voz:p3:fin -->

### Plano 4 · 0:38–0:55 · ¿Y si cambias algo?
- **Acción:** bajar hasta el bloque «¿Y si cambias algo?», señalar las opciones y pulsar una. El mapa se recalcula.
  - Si el caso precargado no hace aparecer el bloque, antes se baja el presupuesto con el slider a [Y] €/mes (`pitch/guion.md`, nota del bloque 2).
- **Se ve:** «Con tu búsqueda tal cual salen [N] zonas» y las opciones con sus cifras de la API.
- **Rótulo:** «Con tu búsqueda: [N] zonas · [opción]: [N] zonas».
- **Estado:** **pendiente de A y B**.

<!-- voz:p4:inicio -->
¿Y si salen pocas? Con su búsqueda tal cual salen [N] zonas. Si cambian una sola cosa, por ejemplo [opción], salen [N]. Un toque y se aplica.
<!-- voz:p4:fin -->

### Plano 5 · 0:55–1:07 · De dónde sale cada dato
- **Acción:** en la tarjeta de zona, clic en «¿De dónde sale?» y después en «Abrir en el portal». Se abre la ficha del portal de datos de la Comunidad en una pestaña nueva; se ve 2 s y se vuelve.
- **Se ve:** el nombre del conjunto de datos, su versión y su licencia, y luego la ficha del portal CM.
- **Rótulo:** «Cada dato enlaza a su fuente oficial».
- **Estado:** **pendiente de B** (panel de procedencia).

<!-- voz:p5:inicio -->
Cada dato dice de dónde sale. Aquí, la ficha oficial en el Portal de Datos Abiertos de la Comunidad de Madrid, con su licencia.
<!-- voz:p5:fin -->

### Plano 6 · 1:07–1:22 · La zona en 3D
- **Acción:** clic en «Ver la zona». Dejar que la cámara vuele y se incline; no tocar nada durante el vuelo.
- **Se ve:** la zona en 3D con contorno violeta y etiquetas de colegios, centros de salud y estaciones, y las migas «Madrid › [distrito]» o «Comunidad de Madrid › [municipio]».
- **Rótulo:** «[zona] en 3D».
- **Estado:** **pendiente de B**. Si el 3D no está, se graba la vista 2D y se quita «en tres dimensiones».

<!-- voz:p6:inicio -->
Entramos en la zona en tres dimensiones: sus colegios, sus centros de salud y sus estaciones, sacados de los datos oficiales.
<!-- voz:p6:fin -->

### Plano 7 · 1:22–1:44 · Qué falta
- **Acción:** clic en la pestaña «Qué falta». Recorrer las filas con el cursor de arriba abajo, despacio.
- **Se ve:** las filas FALTA / JUSTO / CUBIERTO / SIN DATOS, cada una con su valor, la referencia de la región, la fiabilidad y de dónde sale.
- **Rótulo:** «Comparado con el conjunto de la Comunidad de Madrid».
- **Zona:** la misma que en el bloque 3 del guion (**pendiente de A**, GAP-001).
  - Tiene que tener al menos una fila FALTA y otra CUBIERTO.
  - No se usa la fila de colegios como ejemplo de CUBIERTO hasta que GAP-001 corrija su filtro.

<!-- voz:p7:inicio -->
Y lo que le falta. Cada servicio se compara con el conjunto de la Comunidad, según cuánta gente vive aquí. [Fila]: falta. [Fila]: cubierto. Y cuando no tenemos un dato, lo decimos: sin datos.
<!-- voz:p7:fin -->

### Plano 8 · 1:44–1:58 · Cierre
- **Pantalla:** pie de la web con el contador de conjuntos de datos y, encima, el rótulo final a pantalla completa sobre fondo `--bg`.
- **Rótulo final (4 s):**
  - Vida Fácil · Encuentra tu sitio en Madrid
  - vida-facil-eight.vercel.app
  - github.com/marianohernando/housing-intelligence · Código abierto (Apache-2.0)
  - [N] conjuntos de datos del Portal de Datos Abiertos de la Comunidad de Madrid
- **Fuente de [N]:** el contador del pie (`GET /api/v1/datasets`, `cm_open_data_count`; hoy 21, según `pitch/datasets_cm.md`).

<!-- voz:p8:inicio -->
[N] conjuntos de datos abiertos de la Comunidad de Madrid, con control de calidad y código abierto. Vida Fácil: encuentra tu sitio en Madrid.
<!-- voz:p8:fin -->

---

## Antes de grabar (23 nov)
1. C confirma que el smoke de la demo está en verde y la consola del navegador no muestra errores.
2. Quitar del texto las marcas «pendiente» de este fichero o adaptar el plano:
   - si falta una pieza, se quita el plano y se reparten sus segundos;
   - nunca se graba un mockup ni una pantalla simulada.
3. Cargar la demo una vez para tener la caché caliente. Hacer el recorrido completo una vez sin grabar.
4. Grabar cada plano 2 veces y quedarse con la mejor toma.
5. Locución: leer con calma. Si un plano se pasa de su duración, recortar el texto y volver a contar con el comando de arriba.

## Después de montar
1. Ver el vídeo entero sin sonido: se entiende con los rótulos.
2. Comprobar que dura ≤ 2:00, que cada cifra del rótulo coincide con la pantalla y que no aparece ningún dato personal ni ninguna pestaña ajena.
3. Probarlo en el portátil de la final, a pantalla completa y sin conexión.
4. Copiarlo a los 3 sitios y apuntar en el PR la fecha, la duración y el tamaño.
