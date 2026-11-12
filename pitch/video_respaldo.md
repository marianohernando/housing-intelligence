# Vídeo de respaldo de 2 minutos — Vida Fácil (PITCH-003)

## Para qué sirve
Es el plan B de la final del 26 nov: si cae la wifi o la demo, se pone este vídeo en lugar de los bloques 2 y 3 del guion (`pitch/guion.md`, «Antes de empezar», punto 4). Cuenta el mismo recorrido que la demo en directo y se entiende solo, también sin sonido, gracias a los rótulos.

- **Cuándo se graba:** el 23 nov (freeze), sobre la demo desplegada y verificada (https://vidafacil-madrid.vercel.app). Así coincide con lo que verá el jurado. Antes no: hasta el freeze la web todavía puede cambiar.
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
| 3 | 0:20–0:38 | 18 s | 32 (≤ 39) | 15 s |
| 4 | 0:38–0:55 | 17 s | 28 (≤ 37) | 13 s |
| 5 | 0:55–1:07 | 12 s | 24 (≤ 26) | 11 s |
| 6 | 1:07–1:22 | 15 s | 21 (≤ 32) | 10 s |
| 7 | 1:22–1:44 | 22 s | 35 (≤ 47) | 16 s |
| 8 | 1:44–1:58 | 14 s | 24 (≤ 30) | 11 s |
| **Total** | | **118 s** | **202** | **93 s de voz + pausas para mirar** |

**Lo que va entre corchetes** (`[pct]`, `[N]`, `[zona]`…) se lee en la pantalla el día de la grabación y se escribe igual en el rótulo. Nunca se pone una cifra de memoria.

**El buscador está encendido en producción desde el 11 nov** (`evidence/gate-06/2026-11-11-deploy/deploy-12-buscador.md`, PR #11), así que los planos 2, 3 y 4 se graban.

**Reserva: si el 23 nov la demo vuelve a enseñar «Muy pronto»** (C ha vuelto a una versión sin buscador), esos tres planos no se graban: nunca se graba una pantalla simulada. Sus 47 s se reparten así:
- **Plano 6 entra desde el mapa:** clic en un distrito de la región (propuesta: Chamartín) y vuelo a 3D. Se alarga hasta 30 s y suma la tarjeta «Qué falta aquí» con «A pie: N min».
- **Locución añadida:** «Y cuánto se tarda andando, por las calles de verdad: [N] minutos hasta el centro de salud más cercano».
- **Plano 5:** pasa detrás del 6. Desde la zona, «Ver todo lo que falta» y la fuente de una fila.
- **El resto:** pausas más largas en los planos 7 y 8.

Se vuelve a contar con el comando de arriba.

---

## Planos

### Plano 1 · 0:00–0:08 · Portada
- **Pantalla:** portada de la demo con «Encuentra tu sitio en Madrid» y «Así funciona». Sin cursor en movimiento.
- **Rótulo:** «Vida Fácil · Encuentra tu sitio en Madrid».

<!-- voz:p1:inicio -->
Vida Fácil te ayuda a encontrar tu sitio en Madrid con datos abiertos oficiales.
<!-- voz:p1:fin -->

### Plano 2 · 0:08–0:20 · El caso de ejemplo
- **Acción:** clic en «Ver un ejemplo: pareja con 2 hijos que trabaja en la Castellana» (`textos_web.md`, `portada.ejemplo.boton`). Rellena la búsqueda y la lanza.
- **Se ve:** la tarjeta «Tu búsqueda» rellena con el caso. Se recorre con el cursor: «En pareja», «Con hijos» (2), «Colegios», «Transporte» y «Salud», «Colegio a 10 min andando», «Trabajo en» y el alquiler de hasta 1.500 € al mes.
- **Rótulo:** «Pareja con 2 hijos · alquiler hasta 1.500 €/mes · trabajo en la Castellana».
- **Fuente:** `data/fixtures/contracts/scenario_state.familia_castellana.fixture.json`. Si A cambia el caso precargado, se cambian la locución y el rótulo.

<!-- voz:p2:inicio -->
Una pareja con dos hijos busca alquiler. Trabajan en la Castellana, pueden pagar hasta mil quinientos euros al mes y quieren un colegio cerca.
<!-- voz:p2:fin -->

### Plano 3 · 0:20–0:38 · Zonas que encajan
- **Acción:** señalar el mapa ya coloreado y la lista «Zonas que encajan». Clic en la 1.ª y señalar su tarjeta con el cursor, despacio.
- **Se ve:** el mapa con la escala de violetas y la leyenda «Encaje con tu búsqueda», y la tarjeta de la zona con «[pct] % de encaje», «La 1.ª que más encaja» y 5 hechos con su fiabilidad.
- **Rótulo:** «[zona] · [pct] % de encaje».
- **Estado:** hecho en producción. Desde el 13 nov (`fit-0.6`, con el alquiler de contratos nuevos de D-228) encajan 27 zonas y la 1.ª es Latina, con un 98 % y «39 min en transporte público hasta Paseo de la Castellana (Azca), llegando a las 9:00» (`POST /api/v1/search` con el fixture). Se graba el 23 nov con lo que salga en pantalla.

<!-- voz:p3:inicio -->
La búsqueda sale sola. El mapa se colorea según cuánto encaja cada zona con esta familia. La primera encaja en un [pct] por ciento, y debajo vemos por qué, dato a dato.
<!-- voz:p3:fin -->

### Plano 4 · 0:38–0:55 · ¿Y si cambias algo?
- **Acción:** cerrar la tarjeta (×) y bajar hasta «¿Y si cambias algo?», que sale plegado a la opción que más zonas suma. Pulsar «Ver todas las opciones», señalarlas y pulsar «Probar así» en la primera. El mapa se recalcula y sale «Ahora ves las zonas con: [opción]».
- **Se ve:** «Con tu búsqueda tal cual salen [N] zonas» y las opciones con sus cifras de la API.
- **Rótulo:** «Con tu búsqueda: [N] zonas · [opción]: [N] zonas».
- **Estado:** hecho en producción. El 13 nov (`fit-0.6`): «Con tu búsqueda tal cual salen 27 zonas» y dos opciones, «+5 min a pie hasta colegio con primaria: saldrían 44 zonas, 17 más» y «+150 €/mes: saldrían 30 zonas, 3 más» (`POST /api/v1/search` con el fixture).

<!-- voz:p4:inicio -->
¿Y si quieren más opciones? Con su búsqueda tal cual salen [N] zonas. Si cambian una sola cosa, por ejemplo [opción], salen [N]. Un toque y se aplica.
<!-- voz:p4:fin -->

### Plano 5 · 0:55–1:07 · De dónde sale cada dato
- **Acción:** «Volver a mi búsqueda», abrir otra vez la tarjeta de la 1.ª zona y pulsar «Ver todo lo que falta». En una fila, «De dónde sale: [N] conjuntos de datos» y clic en uno. Se abre la ficha del portal de datos de la Comunidad en una pestaña nueva; se ve 2 s y se vuelve. En el montaje se corta entre clics: en 12 s no cabe el recorrido entero.
- **Se ve:** los nombres de los conjuntos de datos de la fila, cada uno enlazado, y luego la ficha del portal CM con su licencia.
- **Rótulo:** «Cada dato enlaza a su fuente oficial».
- **Estado:** hecho en producción: la lista de «Qué falta» enlaza cada conjunto a su ficha (`evidence/map-004/2026-11-11/prod_c4_madrid_que_falta_desktop.png`, de Madrid capital y anterior a gap-0.3; el enlace a la ficha no cambia). La tarjeta del buscador no tiene enlace a la fuente: por eso se pasa por «Qué falta».

<!-- voz:p5:inicio -->
Cada dato dice de dónde sale. Aquí, la ficha oficial en el Portal de Datos Abiertos de la Comunidad de Madrid, con su licencia.
<!-- voz:p5:fin -->

### Plano 6 · 1:07–1:22 · La zona en 3D
- **Acción:** en la misma lista de «Qué falta», clic en «Ver la zona». Dejar que la cámara vuele y se incline; no tocar nada durante el vuelo.
- **Se ve:** la zona en 3D con contorno violeta y etiquetas de colegios, centros de salud y estaciones, y las migas «Madrid › [distrito]» o «Comunidad de Madrid › [municipio]».
- **Rótulo:** «[zona] en 3D».
- **Estado:** hecho en producción (`evidence/map-004/2026-11-11/prod_c5_chamartin_3d_desktop.png`, Chamartín). Si el 3D no carga el 23, se graba la vista 2D y se quita «en tres dimensiones».

<!-- voz:p6:inicio -->
Entramos en la zona en tres dimensiones: sus colegios, sus centros de salud y sus estaciones, sacados de los datos oficiales.
<!-- voz:p6:fin -->

### Plano 7 · 1:22–1:44 · Qué falta
- **Acción:** pestaña «Qué falta» y elegir «Puente de Vallecas» en la lista de zonas, o abrir `/que-falta?zona=distrito/2807913`. Recorrer las filas con el cursor de arriba abajo, despacio.
- **Se ve:** las 6 filas FALTA / JUSTO / CUBIERTO / SIN DATOS, cada una con su valor, la referencia de los municipios de su tipo, la fiabilidad, los minutos a pie y de dónde sale.
- **Rótulo:** «Lo que tienes a 15 min andando, comparado con los municipios de su tipo».
- **Zona:** la misma que en el bloque 3 del guion: Puente de Vallecas (`/que-falta?zona=distrito/2807913`). Con `gap-0.3` (D-217), escuelas infantiles sale FALTA (2,8 frente a 4,9) y farmacias CUBIERTO (4,5 frente a 3,1). Comprobado en producción el 12 nov con `GET /api/v1/gaps/distrito/2807913`. Madrid capital ya no vale: con gap-0.3 no tiene ninguna fila de servicios en FALTA.
  - Tiene que tener al menos una fila FALTA y otra CUBIERTO.

<!-- voz:p7:inicio -->
Y lo que le falta. Medimos lo que la gente tiene a quince minutos andando y lo comparamos con municipios parecidos. [Fila]: falta. [Fila]: cubierto. Y cuando no tenemos un dato, lo decimos: sin datos.
<!-- voz:p7:fin -->

### Plano 8 · 1:44–1:58 · Cierre
- **Pantalla:** pie de la web con el contador de conjuntos de datos y, encima, el rótulo final a pantalla completa sobre fondo `--bg`.
- **Rótulo final (4 s):**
  - Vida Fácil · Encuentra tu sitio en Madrid
  - vidafacil-madrid.vercel.app
  - github.com/marianohernando/housing-intelligence · Código abierto (Apache-2.0)
  - [N] conjuntos de datos del Portal de Datos Abiertos de la Comunidad de Madrid
- **Fuente de [N]:** el contador del pie (`GET /api/v1/datasets`, `cm_open_data_count`; 27 en producción desde el 13 nov, igual que `pitch/datasets_cm.md`).

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
