# Vídeo de respaldo de 2 minutos — Vida Fácil (PITCH-003)

## Para qué sirve
Es el plan B de la final del 26 nov: si cae la wifi o la demo, se pone este vídeo en lugar de los bloques 2, 3 y 4 del guion, los de la demo (`pitch/guion.md`, «Antes de empezar», punto 4). Cuenta el mismo recorrido que la demo en directo y en el mismo orden que el pitch desde el 23 nov: primero «Qué falta», para ayuntamientos; después, la ficha de una parcela, para inversores; y, como base, la búsqueda para personas. Se entiende solo, también sin sonido, gracias a los rótulos.

- **Cuándo se graba:** el 23 nov, sobre la demo desplegada y verificada (https://vidafacil-madrid.vercel.app; deploy-46, `542283b8`). Así coincide con lo que verá el jurado.
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
| 1 | 0:00–0:08 | 8 s | 16 (≤ 17) | 7 s |
| 2 | 0:08–0:26 | 18 s | 35 (≤ 39) | 16 s |
| 3 | 0:26–0:38 | 12 s | 24 (≤ 26) | 11 s |
| 4 | 0:38–0:58 | 20 s | 36 (≤ 44) | 17 s |
| 5 | 0:58–1:16 | 18 s | 30 (≤ 39) | 14 s |
| 6 | 1:16–1:30 | 14 s | 21 (≤ 30) | 10 s |
| 7 | 1:30–1:44 | 14 s | 20 (≤ 30) | 9 s |
| 8 | 1:44–1:58 | 14 s | 29 (≤ 30) | 13 s |
| **Total** | | **118 s** | **211** | **97 s de voz + pausas para mirar** |

**Recuento del 23 nov**, con el orden nuevo del pitch (comando de arriba). Hasta el 22 nov el vídeo seguía el recorrido del 19 nov: la búsqueda de la familia, la fuente de un dato, la zona en 3D y «Qué falta» (199 palabras). El texto de entonces está en el historial de git de este fichero.

**Lo que va entre corchetes** (`[N]`, `[opción]`, `[zona]`…) se lee en la pantalla el día de la grabación y se escribe igual en el rótulo. Nunca se pone una cifra de memoria.

**Reserva: si la demo vuelve a enseñar «Muy pronto»** en lugar de la búsqueda, los planos 5 y 6 no se graban: nunca se graba una pantalla simulada. Sus 32 s se reparten así:
- **Tras el plano 2, la zona en 3D (18 s):** desde Puente de Vallecas, «Ver la zona», y se deja volar la cámara. Locución: «Y la zona en tres dimensiones, con sus colegios, sus centros de salud y sus estaciones.».
- **El resto:** pausas más largas en los planos 4 y 8.

Se vuelve a contar con el comando de arriba.

---

## Planos

### Plano 1 · 0:00–0:08 · Portada
- **Pantalla:** portada de la demo con el lema, «La zona que te conviene, y lo que le falta», y la pestaña «Inversores» en la cabecera. Sin cursor en movimiento.
- **Rótulo:** «Vida Fácil · La zona que te conviene, y lo que le falta».

<!-- voz:p1:inicio -->
Vida Fácil: qué le falta a cada zona de la Comunidad de Madrid, con datos abiertos.
<!-- voz:p1:fin -->

### Plano 2 · 0:08–0:26 · Qué le falta a una zona (ayuntamientos)
- **Acción:** pestaña «Qué falta». Señalar «Dónde invertir primero» y la tarjeta de escuelas infantiles; después, clic en Puente de Vallecas (o abrir `/que-falta?zona=distrito/2807913`) y recorrer sus filas despacio, de arriba abajo.
- **Se ve:** en «Dónde invertir primero», la cifra de escuelas infantiles y «El 9,8 % de toda la Comunidad, en 3 zonas.»; en Puente de Vallecas, la fila de escuelas infantiles en FALTA con «Aquí hay 57 por cada 100 que hay en municipios parecidos.» y «Afecta a 9.433 niños de 0 a 4 años.», y alguna fila CUBIERTO (leído en producción el 23 nov, tras el deploy-46).
- **Rótulo:** «[N] niños de 0 a 4 años viven donde faltan escuelas infantiles».
- **Desde el 23 nov la vivienda no sale en «Dónde invertir primero»:** es contexto, no una falta (D-254, `gap-0.4`). En producción, el 23 nov, salen tres tarjetas: escuelas infantiles (9,8 %, en 3 zonas), farmacias (9,4 %, en 5) y centros de mayores (4,1 %, en 6).

<!-- voz:p2:inicio -->
Para un ayuntamiento: en toda la región, [N] niños de cero a cuatro años viven en [N] zonas donde faltan escuelas infantiles. En Puente de Vallecas hay [N] por cada cien que en municipios parecidos.
<!-- voz:p2:fin -->

### Plano 3 · 0:26–0:38 · De dónde sale cada dato
- **Acción:** en una fila de Puente de Vallecas, «De dónde sale: [N] conjuntos de datos» y clic en uno. Se abre la ficha del portal de datos de la Comunidad en una pestaña nueva; se ve 2 s y se vuelve. En el montaje se corta entre clics.
- **Se ve:** los nombres de los conjuntos de datos de la fila, cada uno enlazado, y luego la ficha del portal CM con su licencia.
- **Rótulo:** «Cada dato enlaza a su fuente oficial».

<!-- voz:p3:inicio -->
Cada dato dice de dónde sale. Aquí, la ficha oficial en el Portal de Datos Abiertos de la Comunidad de Madrid, con su licencia.
<!-- voz:p3:fin -->

### Plano 4 · 0:38–0:58 · La ficha de una parcela exacta (inversores)
- **Acción:** pestaña «Inversores», «Busca tu parcela» con la referencia catastral 2122202VK4722A (Méndez Álvaro 47, una de las 4 parcelas de demostración), o abrir `/inversores/parcela/2122202VK4722A`, cargada antes: la primera consulta de una parcela tarda unos 11 s. Bajar despacio por el planeamiento, la edificabilidad, los servicios y «Quién vive en el barrio». Al final, señalar «¿Sale la promoción?» sin detenerse en sus cifras.
- **Se ve:** el aviso del primer filtro, el planeamiento con el enlace a la ficha oficial, «13.121 m² edificables» de vivienda (VEDA del Ayuntamiento), la potencia eléctrica de partida para unas 164 viviendas (al menos 499,1 kW, marcada como supuesto) y el contexto de demanda de la zona (leído en producción el 23 nov, tras el deploy-46).
- **Rótulo:** «Méndez Álvaro 47 · la ficha de la parcela».
- **No se pone en el rótulo la cifra del suelo:** depende de supuestos que la ficha enseña uno a uno (pregunta 6 de `pitch/preguntas.md`). Se dice «datos de la parcela», nunca «información catastral».

<!-- voz:p4:inicio -->
Para un promotor: la ficha de una parcela exacta de Madrid capital. Su planeamiento con el enlace oficial, [N] metros edificables de vivienda, la potencia eléctrica que pediría y, al lado, la demanda de su zona.
<!-- voz:p4:fin -->

### Plano 5 · 0:58–1:16 · La base: la zona que te conviene (personas)
- **Acción:** pestaña «Mapa» y clic en «Ejemplo: pareja con 2 hijos que trabaja en la Castellana». Señalar el mapa coloreado y la leyenda; clic en la 1.ª de «Zonas que os convienen» y señalar su tarjeta.
- **Se ve:** «Hemos encontrado [N] zonas para vosotros.», la leyenda con las que cumplen todo, las que no y las que no tienen datos, y la tarjeta de la 1.ª con su banda, «Unos … € al mes» y la nota «Precio de los contratos de alquiler de 2024: un anuncio de hoy suele pedir más.», sus minutos a pie, el trayecto hasta la Castellana y «No le falta nada de lo que buscáis.».
- **Rótulo:** «Pareja con 2 hijos · hasta 1.500 €/mes · trabajo en la Castellana».
- **Estado, en producción el 23 nov** (deploy-46, leído al rehacer las capturas C1 y C3): 42 zonas cumplen todo, 157 no y 0 sin datos. La 1.ª es Puente de Vallecas: «Unos 1.129 € al mes», «Colegio con primaria a unos 4 min andando» y «41 min en transporte público hasta Paseo de la Castellana (Azca), llegando a las 9:00». Fuente del caso: `data/fixtures/contracts/scenario_state.familia_castellana.fixture.json`.

<!-- voz:p5:inicio -->
Y, para quien busca casa, la base: una pareja con dos hijos, mil quinientos euros y trabajo en la Castellana. Cumplen lo que piden [N] zonas de toda la Comunidad.
<!-- voz:p5:fin -->

### Plano 6 · 1:16–1:30 · ¿Queréis ver más zonas?
- **Acción:** «‹ Volver a la lista» y bajar hasta «¿Queréis ver más zonas?», que sale plegado a la opción que más zonas suma. Pulsar «Ver todas las opciones», señalarlas y pulsar «Ver esas zonas» en la primera. El mapa se recalcula.
- **Se ve:** «Hemos encontrado [N] zonas para vosotros. Mirad cuántas salen si cambiáis una sola cosa:» y las opciones con sus cifras de la API.
- **Rótulo:** «Con vuestra búsqueda: [N] zonas · [opción]: [N] zonas».
- **Estado, en producción el 23 nov** (deploy-46, captura C3): «+5 min a pie hasta colegio con primaria · saldrían 49 más: 91 zonas en total» y «+150 €/mes · saldrían 3 más: 45 zonas en total».

<!-- voz:p6:inicio -->
¿Y si quieren más zonas? Si cambian una sola cosa, por ejemplo [opción], salen [N] más. Un toque y se aplica.
<!-- voz:p6:fin -->

### Plano 7 · 1:30–1:44 · La API y el MCP
- **Acción:** abrir `/desarrolladores` (enlace del pie, «API y MCP para desarrolladores») y bajar despacio por las rutas, un ejemplo con `curl` y cómo añadir el MCP.
- **Se ve:** «sin clave · solo lectura», las rutas de la API con su ejemplo y el MCP, también en remoto, «sin instalar nada» (leído en producción el 23 nov, tras el deploy-46).
- **Rótulo:** «API y MCP abiertos y gratuitos, sin clave».

<!-- voz:p7:inicio -->
Y todo esto, también para programas y agentes de IA: una API y un MCP abiertos y gratuitos, sin clave.
<!-- voz:p7:fin -->

### Plano 8 · 1:44–1:58 · Cierre
- **Pantalla:** pie de la web con el contador de conjuntos de datos y, encima, el rótulo final a pantalla completa sobre fondo `--bg`.
- **Rótulo final (4 s):**
  - Vida Fácil · La zona que te conviene, y lo que le falta
  - vidafacil-madrid.vercel.app
  - github.com/marianohernando/housing-intelligence · Código abierto (Apache-2.0)
  - [N] conjuntos de datos del Portal de Datos Abiertos de la Comunidad de Madrid
- **Fuente de [N]:** el contador del pie (`GET /api/v1/datasets`, `cm_open_data_count`): «Datos: 39 conjuntos de la Comunidad de Madrid…» en producción el 23 nov, igual que `pitch/datasets_cm.md`.

<!-- voz:p8:inicio -->
[N] conjuntos de datos abiertos de la Comunidad de Madrid, descargados de sus portales y sin scraping. Vida Fácil: la zona que te conviene, y lo que le falta.
<!-- voz:p8:fin -->

---

## Antes de grabar (23 nov)
1. C confirma que el smoke de la demo está en verde y la consola del navegador no muestra errores.
2. Quitar del texto las marcas «pendiente» de este fichero o adaptar el plano:
   - si falta una pieza, se quita el plano y se reparten sus segundos;
   - nunca se graba un mockup ni una pantalla simulada.
3. Cargar la demo una vez para tener la caché caliente, también la ficha de Méndez Álvaro 47. Hacer el recorrido completo una vez sin grabar.
4. Grabar cada plano 2 veces y quedarse con la mejor toma.
5. Locución: leer con calma. Si un plano se pasa de su duración, recortar el texto y volver a contar con el comando de arriba.

## Después de montar
1. Ver el vídeo entero sin sonido: se entiende con los rótulos.
2. Comprobar que dura ≤ 2:00, que cada cifra del rótulo coincide con la pantalla y que no aparece ningún dato personal ni ninguna pestaña ajena.
3. Probarlo en el portátil de la final, a pantalla completa y sin conexión.
4. Copiarlo a los 3 sitios y apuntar en el PR la fecha, la duración y el tamaño.
