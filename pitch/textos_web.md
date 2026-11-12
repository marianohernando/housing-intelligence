# Textos de la web — Vida Fácil

Para la línea B: estos son los textos de la web, listos para usar tal cual. Si un texto no cabe o no encaja en el diseño, cámbialo en la web y avisa en el PR #2 para que lo actualice aquí.

**Fase de mejora (13 nov): textos para un jurado no técnico.** El jurado simulado se perdió en cinco sitios. Todo es **pendiente de B**, y lo que sale de la API, también **pendiente de A**:
- **«100 %» con JUSTO debajo:** una línea bajo el %, `encaje.aviso_*` (sección 4). Mariano decidió explicarlo, no cambiar el nombre del %.
- **«Qué falta» sin resumen:** una línea arriba, `falta.resumen.*` (sección 5), por ejemplo «Aquí falta: escuelas infantiles.».
- **«0,46 centros de salud por 10.000 hab.»:** la frase principal de cada fila pasa a ser «Aquí hay {n} por cada 100 que hay en municipios parecidos» (`falta.fila.comparacion`). La cifra técnica se queda, más pequeña, tras «Ver la cifra».
- **Un distrito «frente a otros municipios urbanos»:** `falta.fila.referencia.distrito` dice con quién se compara («sin contar Madrid, como Getafe o Alcalá de Henares») y por qué.
- **«desde la mitad de sus calles»:** sale del texto de los hechos (A) y la idea se explica una vez, en `falta.leyenda.a_pie`.
- **«A pie hasta el hospital: 51 min»:** a más de 30 min se da la distancia, «a unos 3,4 km» (`hospital.distancia`).

**Revisión del PR #26 de B (12 nov, noche): chip «Sin escaleras» (D-223) y seguridad (D-224).**
- `importa.sin_escaleras`: queda **definitiva tal cual** la ayuda de B, «Estación de metro o tren accesible (sin escaleras) según el CRTM, cerca de casa.». Usa las mismas palabras que el hecho de la API y nombra la fuente.
- **Icono:** propongo `TrainFront` (lucide) en vez de `Accessibility`.
  - El símbolo de la silla de ruedas convierte una preferencia en una etiqueta de discapacidad (D-204 y la regla de arriba).
  - Además, deja fuera a quien también busca una estación sin escaleras, como quien va con carrito, una persona mayor o alguien con maletas.
  - El tren dice lo que se mide: la estación. El texto del chip ya dice «sin escaleras».
- `importa.pronto_lista`: hoy dice «Muy pronto: zonas verdes y seguridad.». Va **«Muy pronto: zonas verdes.»**, porque la seguridad no va a puntuar (D-224) y no se promete. Cuando la web enseñe el chip de zonas verdes, la línea se quita.
- **Texto del CRTM de A** (`555c2b4`): bien. Añade «hasta las estaciones accesibles» y «grados de accesibilidad», que son las 3 topologías del CRTM (D-223). Sigue diciendo qué va en bruto (los nombres de las estaciones) y qué va explotado (los minutos), como pide la licencia. En la web, `ATTRIBUTIONS_FALLBACK` y el fixture ya lo tienen igual.

**Revisión del PR #22 de B (12 nov, noche): atribución plegada en móvil.** En la portada y en la vista de zona no hay pie, y en móvil las citas quedan detrás de un botón (i).
- `mapa.fuentes`, el nombre del (i): B propone «Fuentes y licencias del mapa». Va «Fuentes y licencias de los datos», porque lo que se abre cita las fuentes de toda la pantalla, también las de la hoja, y no solo las del mapa.
- **El (i) basta para 4 de las 6 fuentes:**
  - Comunidad de Madrid, Ayuntamiento e IGN (CartoCiudad) usan CC BY 4.0. Esta licencia deja citar de cualquier forma razonable según el medio, también con un enlace a donde está la cita (sección 3(a)(2)).
  - El Ministerio de Sanidad pide citar la fuente y la fecha de actualización, pero no dice dónde.
- **Para OpenStreetMap y el CRTM no basta:**
  - La guía de atribución de la OSMF dice que la cita no debe obligar a tocar el mapa para verla. Se puede plegar después de cerrarla, al mover el mapa o a los 5 segundos, pero no desde el primer momento.
  - La licencia del CRTM (§2.2) dice: «Debe quedar claramente la indicación "Powered by CRTM" incluyendo enlace a la página oficial del CRTM».
- **Va `mapa.atribucion.movil`:** «© OpenStreetMap · Powered by CRTM», siempre a la vista junto al (i) y cada uno con su enlace. El (i) sigue abriendo la lista completa.
- **No hace falta un enlace «Fuentes» aparte:** el (i) cubre las demás licencias, y la pestaña «Cómo lo calculamos», que se ve siempre, lleva al pie con todas las citas.
- `pie.crtm`: el catálogo dice «Datos en bruto / explotados según el caso», pero la licencia pide decir cuál de los dos es. Pendiente de A: cambiar `attribution_text` en `data/catalog/sources/crtm_open_data.yaml` (texto en la sección 10).

**CORE-009 (12 nov, noche): el trabajo cuenta en minutos de transporte público** (D-220, `fit-0.2`). Llega a producción con el próximo despliegue de C:
- el hecho de la tarjeta lo escribe la API: «33 min en transporte público hasta Paseo de la Castellana (Azca), llegando a las 9:00»;
- cambia `trabajo.ayuda` («Miramos cuánto tardarías en transporte público para llegar a las 9:00.»), se quita `trabajo.transporte_pronto` y `trabajo.max_min` queda listo por si B activa el límite.

**PR #18 de B (12 nov, noche).** Aplicados los 4 cambios de la revisión del #17. Además:
- **CartoCiudad** se cita «© Instituto Geográfico Nacional (CartoCiudad), CC BY 4.0 scne.es», como pide el IGN. Cambia en `pie.cartociudad` y en `mapa.atribucion`.
- **Hospitales**, definitivos tal cual: «los hospitales que hemos podido identificar en el Catálogo Nacional de Hospitales del Ministerio de Sanidad; de unos pocos solo sabemos el tipo y el municipio», en «El hospital» y en el límite de las camas (`metodologia.md` §1.4 y §1.8).
- **Rurales y urbanos**, definitivo tal cual: «más del doble de escuelas infantiles que los urbanos (unas 12 por cada 1.000 niños, frente a menos de 5)». La cifra única «12,3 frente a 4,9» no valía, porque cada zona tiene su referencia: la rural va de 12,13 a 12,86 y la urbana de 4,531 a 4,87.

**Revisión del PR #17 de B (12 nov, tarde).** B aplicó las diferencias de abajo y dejó tres textos provisionales y una duda de maquetación:
- `centros.camas`: hoy dice «Camas: Ministerio de Sanidad, Catálogo Nacional de Hospitales 2025». Va «Camas instaladas a 31 de diciembre de 2024, según el Catálogo Nacional de Hospitales 2025 del Ministerio de Sanidad.», con el enlace en el nombre del catálogo. Es una frase, no una etiqueta. Además, dice la fecha que pide el aviso legal donde se ven las camas, y la vista de zona no tiene pie. Sin `/datasets`, el mismo texto fijo.
- `centros.sin_nombre_algunos`: hoy dice «La fuente oficial no publica el nombre de algunos de estos centros.». Va «Algunos centros salen sin nombre porque no hemos podido comprobarlo en las fuentes oficiales.». En hospitales y centros de salud el nombre sale del catálogo del Ministerio, y si falta es porque no se pudo cruzar (como el Ramón y Cajal hasta que A lo corrigió con la web oficial del hospital, D-218 §10), no porque nadie lo publique.
- `mapa.atribucion`: hoy dice «Comunidad de Madrid · Powered by CRTM · Ministerio de Sanidad · CartoCiudad (IGN), CC BY 4.0 scne.es». Va «Comunidad de Madrid · Ayuntamiento de Madrid · Powered by CRTM · Ministerio de Sanidad (catálogos a 31/12/2024 y 31/12/2025) · © Instituto Geográfico Nacional (CartoCiudad), CC BY 4.0 scne.es». Las pantallas con mapa no tienen pie: ahí tiene que estar la fecha del Ministerio, y también el Ayuntamiento, cuyo padrón da la población de los distritos que se ven.
- **«Qué cuenta en cada servicio»** (`metodologia.md` §1.4) va como lista y no como tabla: en el móvil, con tres columnas, quedaban dos o tres palabras por línea. Cada punto es «**{servicio},** para {quién, en minúscula}: {qué cuenta}.».

**Novedades del 12 nov, con gap-0.3 (D-217) y los hospitales (D-218) en producción.** Son para los textos que B dejó provisionales en el PR #13 («listed for line D» en `apps/web/src`). Las claves están en las secciones 3, 5, 5b y 10.
- **Definitivos tal cual** (B puede quitar la marca):
  - `grupo.etiqueta` («Junto con sus vecinos») y `grupo.ayuda`;
  - `fila.mide.*`: lo que mide cada fila, a 15 min andando y repartido entre todos los que lo tienen cerca (`ROW_MEASURE` en `gaps.ts`);
  - `falta.fila.a_pie.hospital` («el hospital general más cercano») y su etiqueta «El hospital:»;
  - leyenda, `/zonas` y aria del mapa con «los pueblos muy pequeños, junto con sus vecinos» (`leyenda.fila.frente`, `zonas.fila.intro`, `mapa.aria.fila`);
  - `mapa.sin_calles` («Mapa sin fondo de calles.»);
  - de «Todos los centros» (sección 5b): el título, «Ver en el mapa», «Ver la lista ({n})», `centros.elige`, `centros.cargando`, `centros.colegios_fila`, `centros.sin_nombre`, «ubicación aproximada», `mapa.aria.centros` y los recuentos de colegios, escuelas infantiles, hospitales, farmacias y mayores.
- **Cambian:**
  - `falta.intro`: la web sigue con el texto de D-213 y no dice «a pie». Va «Miramos lo que tiene la gente a 15 minutos andando, repartido entre todos los que lo comparten, y lo comparamos con los demás municipios de su tipo, urbanos o rurales.».
  - `grupo.frase` (`groupText` en `gaps.ts`): «Juntos tienen el {n} % de lo que tendrían con la media de los municipios de su tipo» pasa a «Juntos tienen el {n} % de lo que tienen de media los municipios de su tipo». Es más fácil de leer y dice lo mismo que `comparison_group.ratio_to_reference`.
  - `hospital.nota`: se añade al final «y no cuenta para el estado de la fila». Así nadie lee los minutos al hospital como parte de FALTA, JUSTO o CUBIERTO (D-217 §5).
  - **«Cómo lo calculamos»:** va `pitch/metodologia.md` §1.4–1.8, que sustituye al texto provisional de B. Las diferencias:
    - el párrafo «El hospital» de la web dice «Las camas de cada hospital tampoco las tenemos todavía»: **desde D-218 ya no es cierto**, porque «Todos los centros» enseña las camas de cada hospital;
    - «Qué datos usamos» no nombra al Ministerio de Sanidad ni a CartoCiudad (§1.7);
    - faltan dos límites: «Colocamos a la gente por calles» y «Las camas de hospital no cuentan en la lista» (§1.8);
    - los umbrales de «Qué significa la fiabilidad» son anteriores a gap-0.3 (500 menores de 15 años en colegios, 500 mayores en residencias). Ahora son 300 niños de 5 a 14 años y 300 mayores, y se añade el aviso de las aulas repartidas (§1.6);
    - la tabla «Qué cuenta en cada servicio» suma la columna «Para quién» y el ejemplo real de Puente de Vallecas (§1.4).
  - **Recuento de centros de salud en «Todos los centros»:** la lista incluye los consultorios, así que va «{n} centros de salud y consultorios en {zona}», «1 centro de salud o consultorio en {zona}» y «Ningún centro de salud ni consultorio en {zona}». Así cuadra con la fila, donde los consultorios no cuentan como capacidad.
  - **Pie (sección 10), por licencia:**
    - faltan dos atribuciones obligatorias: `pie.sanidad`, porque el aviso legal del Ministerio pide citar la fuente y la fecha de actualización, y `pie.cartociudad` (CC BY 4.0 scne.es);
    - `pie.independiente` suma al Ministerio;
    - `pie.contador` deja de sumar el CRTM aparte, porque sus 6 conjuntos ya cuentan en {n}.

**Novedades del 11 nov (última hora), con el buscador ya encendido en producción.** Son para los textos que B dejó provisionales en los PR #9 y #10, marcados con «pending line D» en `apps/web/src`:
- **Definitivos tal cual** (B puede quitar la marca):
  - de la lista del PR #10, todos menos los cambios de abajo: resultados, «¿Y si cambias algo?», leyenda, tarjeta, «Lo quiero a un paseo» y «Trabajo en»;
  - además, `movil.hoja.mapa`, `falta.fila.region`, `falta.fila.fuente` (con el número), la leyenda por fila, `zonas.ciudad_entera` y `carga.estado_zonas`.
- **Cambian:**
  - `cerca.item`: «a menos de {n} min andando» pasa a «a {n} min andando como mucho». Así coincide con la condición que devuelve la API («Colegio con primaria a 10 min andando como mucho») y con el caso de ejemplo. Además, «a menos de 10» dejaría fuera los 10 justos, y la API los cuenta.
  - `cerca.servicio.transporte`: «Parada de transporte» pasa a «Parada de transporte público», como el hecho de la API («Parada de transporte público a 2 min andando»).
  - `resultados.casi.ayuda`: «Fallan en una sola cosa.» pasa a «Cumplen todo menos una cosa.».
  - `rc.opcion.cuenta`, `rc.cambio` y `leyenda.zonas`: con 1 zona va en singular («saldría 1 zona, 1 más»; «Con este cambio sale 1 zona.»). Hoy la web escribiría «saldrían 1 zona».
  - `carga.fuentes`: la lista de «Cómo lo calculamos» dice «Cargando la lista de datos…»; vale «Cargando los conjuntos de datos…», que ya estaba aquí.
- **Aún comparan con toda la Comunidad (D-213).** Quedan tres textos de la web con el método anterior. En producción se ven los tres:
  - la primera de las «Tres reglas» de «Cómo lo calculamos» (`como-lo-calculamos/page.tsx`): va la de `pitch/metodologia.md` §1.1;
  - `zonas.fila.intro` (`zonas/page.tsx`);
  - `mapa.aria.fila` (`VidaMap.tsx`).
- **Sin usar, se quitan:**
  - `rc.opcion.aria`: un nombre accesible distinto del texto visible incumple WCAG 2.5.3;
  - `zona.coste.alquiler`: el hecho de coste de la API ya trae la cifra, los m² y el aviso de que es orientativo.

  `trabajo.dias` y `hogar.hijos.edades` se quedan como referencia: los rellena el caso de ejemplo, pero la web no deja cambiarlos.

**Novedades del 11 nov (noche), para los textos que B dejó provisionales en el PR #2:**
- **Barra de barrios:** `barrios.titulo` pasa a «Ir a un barrio», porque la barra solo mueve el mapa. Nuevos: `barrios.todo` («Todo {distrito}») y `barrios.ayuda`.
- **«Qué falta»:** «Cambiar de zona» pasa a `falta.otra_zona` («Elegir otra zona»), el mismo texto que ya sale cuando la zona no existe.
- **Definitivos:**
  - de la lista: `falta.leyenda.titulo` («Cómo leer esta lista»), `falta.leyenda.a_pie`, `falta.fila.a_pie` con sus destinos, `a_pie.min`, `zona.falta.a_pie` y `falta.fila.fuente`, con el número de conjuntos;
  - del buscador apagado: `busqueda.pronto`, `leyenda.pronto` y `zona.encaje.pronto`;
  - de navegación y carga: `movil.hoja.mapa`, `zonas.*`, `carga.zonas` y `carga.fuentes`.
- **Nombres de fila:** `fila.mayores` y `fila.vivienda` igualan las etiquetas del catálogo: «Centros de mayores» y «Vivienda para familias».
- **Método nuevo (D-213, `gap-0.2`):** cada zona se compara con los demás municipios de su tipo y no con toda la Comunidad. Cambian `estado.falta`, `estado.justo`, `estado.cubierto`, `falta.intro`, `falta.fila.referencia` y `portada.paso3`; hay `falta.fila.region` nuevo.
- **Buscador (D-214, D-215):** cambian `importa.colegios`, `trabajo.max_min` (la web envía el trabajo sin límite) y `presupuesto.compra.sin_datos`. La distancia al trabajo llega ya escrita en `facts` («A 3,2 km en línea recta de…»).
- **«Poco fiable» (`reliable: false`):** propongo `fila.zona_pequena`, «Zona pequeña para comparar», en lugar de «Pocos datos para saberlo con seguridad». El dato sí lo tenemos; lo que pasa es que en la zona vive muy poca gente. Además, «pocos datos» se confunde con SIN DATOS y con la fiabilidad del dato (sección 6), que es otra cosa.

## Reglas de escritura (D-199, D-202, D-204 y brief de diseño)
- **Español llano, de tú, en frases cortas.** Pensado para cualquier persona, también mayores.
  - Sin anglicismos ni jerga: nunca «dataset», «score», «ranking», «match» ni «Reality Check» en pantalla.
  - En pantalla se dice «conjunto de datos», «encaje» y «¿Y si cambias algo?».
- **Encaje siempre en %**, con hechos debajo. Nunca «92/100» ni barras (D-202).
- **Números a la española:** `1.500 €`, `0,47`, `10 min`. Se formatean igual que `hi_domain.gaps.es_number`.
- **Estados de «Qué falta»:** siempre con texto e icono, nunca solo color.
- **Sin login ni icono de usuario.**
- **Seguridad:** nunca «peligroso» ni «inseguro» (D-205). «Sin escaleras» es una preferencia, nunca una etiqueta de discapacidad (D-204).
- **Variables** van entre llaves: `{zona}`, `{n}`… Los textos que ya devuelve la API (hechos, explicaciones, avisos de cada fila) se muestran tal cual y aquí no se repiten.
- **Marcas:** «pendiente de A» = la API aún no lo da; «pendiente de B» = decisión de diseño.

---

## 1. Cabecera, pestañas y portada

| Clave | Texto | Notas |
|---|---|---|
| `meta.title` | Vida Fácil — Encuentra tu sitio en Madrid | `<title>` de la portada |
| `meta.title.plantilla` | {página} · Vida Fácil | Resto de páginas |
| `meta.description` | Encuentra la zona de la Comunidad de Madrid que mejor encaja con tu vida y mira qué le falta a cada una. Con datos abiertos oficiales. | |
| `cabecera.nombre` | Vida Fácil | Logo de texto |
| `cabecera.lema` | Encuentra tu sitio en Madrid | |
| `pestana.mapa` | Mapa | |
| `pestana.que_falta` | Qué falta | |
| `pestana.como` | Cómo lo calculamos | Nunca «Metodología» ni «Análisis» |
| `a11y.saltar` | Saltar al contenido | Enlace oculto hasta recibir el foco |
| `portada.titulo` | Encuentra tu sitio en Madrid | Ya está así en la web de B |
| `portada.subtitulo` | Te decimos qué zonas encajan con tu vida y qué le falta a cada una, con datos oficiales. | |
| `portada.como_funciona.titulo` | Así funciona | Ya está así en la web de B |
| `portada.paso1` | **Cuéntanos cómo es tu hogar** y lo que te importa: colegios, salud, transporte… | Ya está así en la web de B |
| `portada.paso2` | **Mira las zonas que encajan** y por qué, con hechos que puedes comprobar. | Ya está así en la web de B |
| `portada.paso3` | **Entra en una zona** y mira qué le falta frente a zonas parecidas. | Cambia el 11 nov por D-213: ya no se compara con toda la región |
| `portada.ejemplo.boton` | Ver un ejemplo: pareja con 2 hijos que trabaja en la Castellana | Abre el caso precargado con un toque |
| `portada.ejemplo.ayuda` | Rellenamos la búsqueda por ti para que veas cómo funciona. Luego puedes cambiar lo que quieras. | |
| `portada.empezar` | Empezar mi búsqueda | |

---

## 2. Tarjeta «Tu búsqueda»

| Clave | Texto | Notas |
|---|---|---|
| `busqueda.titulo` | Tu búsqueda | |
| `busqueda.plegar` | Ocultar mi búsqueda | Tarjeta plegable en la pantalla de zona |
| `busqueda.desplegar` | Ver mi búsqueda | |
| `busqueda.reiniciar` | Empezar de nuevo | |

### «Tu hogar»
| Clave | Texto | Notas |
|---|---|---|
| `hogar.titulo` | Tu hogar | |
| `hogar.ayuda` | ¿Quién va a vivir contigo? | |
| `hogar.solo` | Solo/a | Chip del brief |
| `hogar.pareja` | En pareja | |
| `hogar.hijos` | Con hijos | Al marcarlo aparece el contador |
| `hogar.hijos.cuantos` | ¿Cuántos hijos? | Contador de 1 a 8 (`Household.minors`, máximo 8) |
| `hogar.hijos.edades` | Edades (si quieres) | Opcional (`minor_ages`). Ayuda: «Nos sirve para saber si buscas escuela infantil o colegio.» Hoy no se muestra: las rellena el caso de ejemplo (4 y 8 años) y la web no deja cambiarlas |
| `hogar.mayores` | Con mayores a cargo | Al marcarlo aparece el contador |
| `hogar.mayores.cuantos` | ¿Cuántas personas mayores? | Contador de 1 a 4 (`seniors_in_care`, máximo 4) |
| `hogar.contador.menos` | Quitar uno | `aria-label` del botón «−» |
| `hogar.contador.mas` | Añadir uno | `aria-label` del botón «+» |
| `hogar.resumen` | {n} personas en casa | Resumen cuando la tarjeta está plegada |

### «Me importa» (D-204)
Se pueden marcar varios. El orden en que se marcan es el orden de importancia (`priorities`, la más importante primero).

| Clave | Chip | Ayuda (una línea, al pasar el ratón o al tocar «?») | Notas |
|---|---|---|---|
| `importa.titulo` | Me importa | Marca lo que más te importa. Lo primero que marques cuenta más. | |
| `importa.transporte` | Transporte | Paradas cerca de casa y con autobuses o trenes a menudo. | |
| `importa.salud` | Salud | Centro de salud cerca de casa. | |
| `importa.colegios` | Colegios | Colegios con primaria, públicos o concertados, cerca de casa. | Los mismos que cuenta la fila de colegios (GAP-001 F2) |
| `importa.zonas_verdes` | Zonas verdes | Parques de una hectárea o más, cerca de casa. | Cambia el 12 nov: los jardines pequeños no cuentan (D-222 §2). En la API desde `fit-0.3`, desplegado el 12 nov, con el hecho «Parque urbano a N min andando desde la mitad de sus calles». La web aún no enseña el chip: **pendiente de B** |
| `importa.seguridad` | — | — | **No hay chip** (D-224): la tasa oficial de hechos conocidos cuenta dónde se denuncia, no dónde se vive, y solo cubre 36 de las 199 zonas. No se promete en `importa.pronto_lista`. La explicación va en «Cómo lo calculamos» (`metodologia.md` §1.8). Si Mariano abre la opción de D-224 §3, iría como contexto en la vista de zona, nunca como chip. Hecho de la API para la prioridad (D-226 §5): «Seguridad: no la puntuamos (no hay un dato oficial que la mida para quien vive en cada zona)» |
| `zona.seguridad_vecinos` | Así valoran sus vecinos la seguridad de su barrio: {noche} de noche y {dia} de día, de 0 a 10 (en todo Madrid, {noche_madrid} y {dia_madrid}). Encuesta de calidad de vida del Ayuntamiento de Madrid, {año}, unas 400 personas por distrito. | Solo en los 21 distritos de Madrid, como contexto en la vista de zona (D-226 §1): sin colores de estado ni de alarma, y nunca «peligroso» ni «inseguro». No puntúa, no ordena y no entra en «Qué falta». Valores de `seguridad_percibida_noche` y `seguridad_percibida_dia` (`GET /features/{id}/values`); la referencia es la fila de la ciudad (28079). Con una coma decimal: «6,4». **Pendiente de B** |
| `importa.sin_escaleras` | Sin escaleras | Estación de metro o tren accesible (sin escaleras) según el CRTM, cerca de casa. | Opcional y sin marcar (D-204, D-223). Definitiva el 12 nov (PR #26 de B). Icono: `TrainFront`, no la silla de ruedas. Hechos de la API: «Estación de metro o tren accesible (sin escaleras) a N min andando desde la mitad de sus calles» y «Sin estación de metro o tren accesible a un paseo (no mide autobuses, aceras ni portales)». En producción desde el 12 nov (despliegue de `2761696`). El icono, **pendiente de B** |
| `importa.pronto` | Muy pronto | Etiqueta pequeña del chip desactivado. Ayuda: «Estamos añadiendo estos datos.» | |
| `importa.pronto_lista` | Muy pronto: zonas verdes. | Línea bajo los chips | La seguridad no entra (D-224). Se quita cuando la web enseñe el chip de zonas verdes. Revisión del PR #26 |
| `importa.orden` | Lo más importante para ti: {lista} | Resumen con la tarjeta plegada |

### «Trabajo en»
| Clave | Texto | Notas |
|---|---|---|
| `trabajo.titulo` | Trabajo en | |
| `trabajo.placeholder` | Escribe una estación, un distrito o un municipio | Sin calles: no hay búsqueda de calles sin un geocodificador externo. Los lugares son las estaciones del CRTM (`/places`) y las zonas del mapa |
| `trabajo.ayuda` | Miramos cuánto tardarías en transporte público para llegar a las 9:00. | Cambia con `fit-0.2` (CORE-009, D-220), cuando llegue a producción. Hasta entonces, «Así miramos lo lejos que te queda cada zona.» |
| `trabajo.dias` | ¿Cuántos días vas a la semana? | Opcional (`days_per_week`). Hoy no se muestra: lo rellena el caso de ejemplo (4 días) y la web no deja cambiarlo |
| `trabajo.max_min` | Tardar como mucho {n} min en transporte público | CORE-009 hecho en la API (D-220 §8): con límite, cada zona sale cumple, no cumple o sin dato. Hoy la web envía el trabajo sin límite (`max_minutes: null`) y no enseña este campo; si B lo activa tras el despliegue de `fit-0.2`, va este texto |
| `trabajo.transporte_pronto` | Tiempo en transporte: muy pronto | Etiqueta pequeña bajo el campo. **Se quita** cuando `fit-0.2` llegue a producción: el tiempo en transporte ya está calculado (D-220) |
| `trabajo.sin_resultados` | No encontramos ese lugar. Prueba con una estación o con el nombre del municipio. | |
| `trabajo.encontrados` | {n} lugares encontrados. Usa las flechas para elegir uno. | Región viva del combobox. Con 1: «1 lugar encontrado. Usa las flechas para elegirlo.» |
| `trabajo.lugar.estacion` | {estación} ({tipo}) | {tipo}: «metro», «Cercanías» o «Metro Ligero». Por ejemplo, «Nuevos Ministerios (metro)» |
| `trabajo.lugar.distrito` | {distrito} (Madrid) | Por ejemplo, «Chamartín (Madrid)». Los municipios van solo con su nombre |
| `trabajo.quitar` | Quitar este lugar | |

### «Lo quiero a un paseo»
`ScenarioState.nearby`: servicios a un paseo. El caso de ejemplo pide colegio a 10 min andando como mucho, imprescindible.

| Clave | Texto | Notas |
|---|---|---|
| `cerca.titulo` | Lo quiero a un paseo | |
| `cerca.item` | {servicio} a [{n}] min andando como mucho | Los minutos son un selector dentro de la frase. Antes, «a menos de {n} min andando»: ver las novedades de última hora, arriba |
| `cerca.minutos.aria` | Minutos andando hasta {servicio} | `aria-label` del selector, con {servicio} en minúscula |
| `cerca.servicio.escuela_infantil` | Escuela infantil | Nombres de `NeedKey` |
| `cerca.servicio.colegio` | Colegio | |
| `cerca.servicio.centro_salud` | Centro de salud | |
| `cerca.servicio.farmacia` | Farmacia | |
| `cerca.servicio.mayores` | Centro de mayores | |
| `cerca.servicio.transporte` | Parada de transporte público | |
| `cerca.anadir` | Añadir un servicio… | Primera opción del selector |
| `cerca.anadir.aria` | Añadir un servicio a un paseo | `aria-label` del selector |
| `cerca.quitar` | Quitar {servicio} | Con {servicio} en minúscula: «Quitar colegio» |
| `cerca.obligatorio` | Imprescindible | Interruptor (`required`). Ayuda: «Si lo marcas, solo verás zonas que lo cumplen.» |

### Presupuesto (D-203)
| Clave | Texto | Notas |
|---|---|---|
| `presupuesto.titulo` | Presupuesto | |
| `presupuesto.alquilar` | Alquilar | Selector de dos opciones |
| `presupuesto.comprar` | Comprar | |
| `presupuesto.alquiler.valor` | Hasta {importe} € al mes | Rango del slider: 100–20.000 € (`RENT_RANGE_EUR`) |
| `presupuesto.compra.valor` | Hasta {importe} € | Rango del slider: 10.000–5.000.000 € (`BUY_RANGE_EUR`) |
| `presupuesto.compra.etiqueta` | Orientativo | Etiqueta junto al importe de compra, siempre visible |
| `presupuesto.compra.ayuda` | No hay un precio oficial de compra por zona tan completo como el del alquiler. Lo usamos solo como orientación. | |
| `presupuesto.compra.sin_datos` | Aún no tenemos precios oficiales de compra por zona, así que no podemos comprobar si entra en tu presupuesto. | Hecho en la API: con compra, la condición sale UNKNOWN en todas las zonas (D-214, punto 5). Cambia si llega DATA-021 (19–22 nov) |
| `presupuesto.sin_limite` | Sin límite de presupuesto | Opción del slider (`budget: null`) |
| `presupuesto.slider.aria` | Presupuesto máximo | `aria-label` |
| `presupuesto.fuera_rango.alquiler` | El alquiler tiene que estar entre 100 y 20.000 € al mes. | |
| `presupuesto.fuera_rango.compra` | El precio de compra tiene que estar entre 10.000 y 5.000.000 €. | |

### Botón principal
| Clave | Texto |
|---|---|
| `busqueda.boton` | Ver zonas que encajan |
| `busqueda.boton.cargando` | Buscando zonas… |

### Si el buscador se apaga
Producción tiene el buscador encendido desde el 11 nov (`NEXT_PUBLIC_FEATURE_SEARCH=true`, `apps/web/src/lib/capabilities.ts`; `evidence/gate-06/2026-11-11-deploy/deploy-12-buscador.md`, PR #11). Estos textos solo salen en dos casos:
- si C vuelve a una versión sin buscador;
- en el paquete sin red (`make demo-offline`), que compila la web sin ninguna variable `NEXT_PUBLIC_*` salvo la URL de la API (`infra/deploy/offline/demo_offline.sh`).

| Clave | Texto | Notas |
|---|---|---|
| `busqueda.pronto` | Muy pronto podrás ver qué zonas encajan contigo. Mientras, toca una zona del mapa para ver qué le falta. | En la tarjeta «Tu búsqueda», en lugar del botón. Sustituye a «Estamos terminando el cálculo del encaje…» |
| `leyenda.pronto` | Muy pronto verás aquí qué zonas encajan contigo. | Leyenda del mapa |

---

## 3. Mapa

| Clave | Texto | Notas |
|---|---|---|
| `mapa.aria` | Mapa de la Comunidad de Madrid por municipios, con Madrid capital dividida en sus 21 distritos. | `aria-label` del lienzo (D-200) |
| `mapa.alternativa` | Ver las zonas en una lista | Enlace siempre visible para quien no use el mapa |
| `leyenda.titulo` | Encaje con tu búsqueda | Del brief |
| `leyenda.menos` | Encaja menos | Extremo claro |
| `leyenda.mas` | Encaja más | Extremo violeta |
| `leyenda.sin_datos` | Sin datos | Gris con borde discontinuo (`match_pct: null` nunca es 0) |
| `leyenda.antes_de_buscar` | Haz tu búsqueda para ver qué zonas encajan contigo. | Antes del primer resultado |
| `leyenda.cumple` | Cumple todo | Tras buscar: zonas con todas las condiciones en PASS |
| `leyenda.no_cumple` | No cumple todo | Falla alguna condición |
| `leyenda.zonas` | {n} zonas | Junto a cada clase. Con 1: «1 zona» |
| `leyenda.ver` | ¿Qué quieres ver? | Selector del mapa (decisión de datamad-10). Opciones: «Encaje con tu búsqueda» y los nombres de las 6 filas (sección 5) |
| `leyenda.fila.frente` | frente a los municipios de su tipo (urbanos o rurales); los pueblos muy pequeños, junto con sus vecinos. | Tras la definición de la fila elegida. Con los vecinos de gap-0.3 (D-217 §6): definitivo el 12 nov |
| `leyenda.sin_calcular` | {n} zonas sin calcular todavía. | Con 1: «1 zona sin calcular todavía.» |
| `leyenda.nivel_caido` | No hemos podido cargar {los municipios \| los distritos de Madrid}: salen sin calcular. | Con «Reintentar» |
| `leyenda.lista` | Ver estas zonas en una lista | Abre `/zonas?fila=…` |
| `mapa.aria.encaje` | Cada zona tiene el color de su encaje con tu búsqueda; la leyenda lo explica y la lista de zonas que encajan está junto al mapa. | `aria-label` del mapa tras buscar |
| `mapa.aria.fila` | Cada zona tiene el color de su estado en {fila} frente a los municipios de su tipo (los pueblos muy pequeños, junto con sus vecinos); la leyenda lo explica. | {fila} en minúscula. Definitivo el 12 nov, con los vecinos de gap-0.3 |
| `mapa.aria.centros` | En el mapa salen, agrupados, {recuento en minúscula}; su lista está en «Todos los centros». | `aria-label` del mapa con una capa de centros (sección 5b) |
| `mapa.atribucion` | Comunidad de Madrid · Ayuntamiento de Madrid · Powered by CRTM · Ministerio de Sanidad (catálogos a 31/12/2024 y 31/12/2025) · © Instituto Geográfico Nacional (CartoCiudad), CC BY 4.0 scne.es | Atribución del mapa (MapLibre añade la del mapa base). «Powered by CRTM», «Ministerio de Sanidad…» y «CartoCiudad…» enlazados como en `pie.*`. Las pantallas con mapa no tienen pie: aquí van la fecha del Ministerio (aviso legal) y el Ayuntamiento (padrón por distrito). Revisión del PR #17. En escritorio se ve entera. En móvil va plegada tras el (i) (PR #22), con `mapa.atribucion.movil` a la vista |
| `mapa.fuentes` | Fuentes y licencias de los datos | Nombre accesible del botón (i) de la atribución en móvil (`locale` de MapLibre, `AttributionControl.ToggleAttribution`). Revisión del PR #22: cambia «del mapa» por «de los datos» |
| `mapa.atribucion.movil` | © OpenStreetMap · Powered by CRTM | Solo en móvil, siempre a la vista junto al (i), con fondo como el (i) para el contraste AA. «© OpenStreetMap» enlaza a https://www.openstreetmap.org/copyright y «Powered by CRTM» a https://www.crtm.es. Son las dos licencias que piden la cita visible sin tocar nada: la guía de atribución de la OSMF y la licencia del CRTM (§2.2). Revisión del PR #22 |
| `mapa.sin_calles` | Mapa sin fondo de calles. | Aviso suave cuando solo falla el fondo de calles y las zonas sí se ven (paquete sin red) |
| `mapa.zona.tooltip` | {zona}: {pct} % de encaje | Al pasar por encima |
| `mapa.zona.tooltip.sin_datos` | {zona}: sin datos suficientes | |
| `migas.region` | Comunidad de Madrid | Primer nivel de las migas |
| `migas.madrid` | Madrid | Para los distritos: «Madrid › Chamartín» |
| `mapa.3d.etiqueta.estacion` | Estación | Etiquetas de cristal en 3D |
| `mapa.3d.etiqueta.parada` | Parada | |
| `mapa.3d.etiqueta.centro_salud` | Centro de salud | |
| `mapa.3d.etiqueta.colegio` | Colegio | |
| `mapa.3d.etiqueta.escuela_infantil` | Escuela infantil | |
| `mapa.3d.etiqueta.farmacia` | Farmacia | |
| `mapa.3d.etiqueta.mayores` | Residencia o centro de día | Servicios para mayores (D-186) |
| `mapa.3d.etiqueta.parque` | Parque | **Pendiente de A** (DATA-018) |
| `mapa.volver` | Volver al mapa de la región | |
| `mapa.sin_webgl` | Tu navegador no puede mostrar el mapa. Puedes ver las zonas en una lista. | Con enlace a `mapa.alternativa` |
| `movil.hoja.tirador` | Desliza hacia arriba para ver más | Hoja inferior en el móvil |
| `movil.hoja.mapa` | Ver el mapa | Botón que pliega la hoja y deja el mapa a la vista |
| `zonas.buscar` | Busca una zona | Lista de zonas (alternativa al mapa y elección de zona en «Qué falta») |
| `zonas.distritos` | Distritos de Madrid | Grupo de la lista |
| `zonas.municipios` | Municipios | Grupo de la lista |
| `zonas.ninguna` | No hay ninguna zona con ese nombre. | Búsqueda sin resultados |
| `zonas.ciudad_entera` | {ciudad} (toda la ciudad) | «Madrid (toda la ciudad)»: lleva a su lista de «Qué falta». En el mapa, Madrid capital son sus distritos |
| `zonas.titulo` | Todas las zonas | Página `/zonas` |
| `zonas.fila.intro` | Con su estado en {fila} frente a los municipios de su tipo: FALTA, JUSTO, CUBIERTO o SIN DATOS. Los pueblos muy pequeños se comparan junto con sus vecinos. | `/zonas?fila=…`, con {fila} en minúscula. Definitivo el 12 nov, con los vecinos de gap-0.3 |
| `carga.estado_zonas` | Cargando el estado de cada zona… | Lista de zonas con una fila elegida |

---

## 4. Zonas que encajan y tarjeta de zona

### Lista «Zonas que encajan»
Columna derecha tras buscar, mientras no hay una zona elegida. En el móvil va en la hoja inferior.

| Clave | Texto | Notas |
|---|---|---|
| `resultados.titulo` | Zonas que encajan | |
| `resultados.de` | De {n} zonas de la Comunidad de Madrid. | Bajo `rc.varias` («Con tu búsqueda tal cual salen 32 zonas.»). {n} = `zones_evaluated` (hoy 199) |
| `resultados.primeras` | Ver las {n} primeras | Se ven 5 y el botón abre hasta 10 |
| `resultados.menos` | Ver menos | |
| `resultados.resto` | Y {n} zonas más en el mapa. | Con 1: «Y 1 zona más en el mapa.» |
| `resultados.casi.ayuda` | Cumplen todo menos una cosa. | Bajo `zona.cerca_de_encajar.titulo` («Casi encajan»). Antes, «Fallan en una sola cosa.» |
| `resultados.cambiada` | Has cambiado tu búsqueda. Pulsa «Ver zonas que encajan» para ponerla al día. | Los resultados son de la búsqueda anterior |

### Tarjeta de zona

| Clave | Texto | Notas |
|---|---|---|
| `zona.encaje` | {pct} % de encaje | Chip grande. Nunca «/100» |
| `zona.encaje.aria` | Esta zona encaja en un {pct} % con tu búsqueda | |
| `zona.encaje.ayuda` | Cuánto se parece esta zona a lo que buscas. No es una nota de la zona. | Al tocar «?» |
| `encaje.aviso_justo` | Encaja con lo que pides. Aun así, frente a municipios parecidos, aquí van justos de {lista}. | Bajo el % de la tarjeta, si alguna fila de «Qué falta» sale JUSTO y ninguna FALTA. Ejemplo real, Fuencarral-El Pardo (100 %): «… aquí van justos de escuelas infantiles, colegios y centros de salud.» (`GET /api/v1/gaps/distrito/2807908`, 12 nov). Las filas, con `fila.lista.*`. No cuentan las filas de zona muy pequeña para comparar. Fase de mejora, **pendiente de B** |
| `encaje.aviso_falta` | Encaja con lo que pides. Aun así, frente a municipios parecidos, aquí faltan {lista}. | Si alguna fila sale FALTA y ninguna JUSTO. Ejemplo: Puente de Vallecas, «… aquí faltan escuelas infantiles.» |
| `encaje.aviso_falta_justo` | Encaja con lo que pides. Aun así, frente a municipios parecidos, aquí faltan {lista_falta} y van justos de {lista_justo}. | Si hay filas FALTA y JUSTO. Si todas salen CUBIERTO o SIN DATOS, no va ninguna línea |
| `fila.lista.escuela_infantil` | escuelas infantiles | Nombres de fila dentro de una frase, en minúscula. Se unen como «a», «a y b», «a, b y c» |
| `fila.lista.colegio` | colegios | |
| `fila.lista.centro_salud` | centros de salud | |
| `fila.lista.mayores` | centros de mayores | |
| `fila.lista.farmacia` | farmacias | |
| `fila.lista.vivienda` | viviendas grandes para familias | |
| `zona.puesto` | La {n}.ª que más encaja | Posición (`rank`) |
| `zona.hechos.titulo` | Lo que tienes aquí | Encima de los 3–5 hechos (`facts`) |
| `zona.hecho.confianza` | {nivel} | Junto a cada hecho, con los niveles de la sección 6 |
| `zona.coste.compra` | Precio estimado: unos {importe} € (orientativo) | Sin usar hoy: con compra no hay coste (D-214, punto 5). El alquiler llega como hecho de la API, con la cifra, los m² y el aviso («Alquiler medio ≈ 1.075 €/mes por 77 m² (14,0 €/m², media de los contratos vigentes; uno nuevo suele costar más)»), y no lleva clave aquí |
| `zona.coste.sin_datos` | Precio: sin datos en esta zona | Sin usar hoy, como `zona.coste.compra` |
| `zona.no_cumple` | No cumple todo lo que pides. | Si la API no nombra la condición que falla |
| `zona.no_sabemos` | No lo sabemos: nos falta el dato para comprobar lo que pides. No lo damos por bueno. | Zona con alguna condición `UNKNOWN` |
| `zona.encaje.antiguo` | Este encaje es de tu búsqueda anterior. | Tarjeta abierta tras cambiar la búsqueda (`resultados.cambiada`) |
| `zona.falta.titulo` | Qué falta aquí | Mini lista de 3 filas (`gap_highlights`) |
| `zona.falta.ver_todo` | Ver todo lo que falta | Abre la pestaña «Qué falta» con esta zona |
| `zona.boton` | Ver la zona | Del brief |
| `zona.fuente` | ¿De dónde sale? | Enlace que abre la procedencia (sección 9) |
| `zona.cerca_de_encajar.titulo` | Casi encajan | Zonas que fallan una condición (`near_misses`) |
| `zona.cerca_de_encajar.motivo` | No cumple: {condición} | {condición} = `label` de la condición que falla |
| `zona.condicion.cumple` | Cumple | `PASS` |
| `zona.condicion.no_cumple` | No cumple | `FAIL` |
| `zona.condicion.sin_dato` | No lo sabemos | `UNKNOWN`. Ayuda: «Nos falta el dato para comprobarlo. No lo damos por bueno.» |
| `zona.falta.a_pie` | A pie: {minutos} | Bajo el nombre de cada fila de la mini lista. {minutos} con `a_pie.min` (sección 5) |
| `zona.encaje.pronto` | Muy pronto verás cuánto encaja esta zona contigo. | En lugar de «Haz tu búsqueda…» mientras el buscador esté apagado (`busqueda.pronto`) |

### Barra de barrios (solo distritos de Madrid)
La barra **solo mueve el mapa**: la demo no tiene cifras por barrio y no las va a tener antes de la final. Por eso el título dice lo que hace y no promete datos del barrio.

| Clave | Texto | Notas |
|---|---|---|
| `barrios.titulo` | Ir a un barrio | Título de la barra inferior (MAP-004). Sustituye a «Barrios de la zona», que hacía esperar cifras de cada barrio |
| `barrios.todo` | Todo {distrito} | Primer chip: vuelve a encuadrar el distrito entero, por ejemplo «Todo Chamartín». Marcado al entrar en la zona |
| `barrios.ayuda` | Mueve el mapa a ese barrio. Las cifras de «Qué falta» son del distrito entero. | `aria-description` de la barra, o línea pequeña si cabe |

---

## 5. «Qué falta»: FALTA / JUSTO / CUBIERTO / SIN DATOS

Desde D-217 (`gap-0.3`, 12 nov) cada fila de servicios mide **lo que la gente tiene a 15 minutos andando, repartido entre todos los que lo comparten** (2SFCA), y no los centros por habitante. La comparación sigue siendo la de D-213: con **los demás municipios de su tipo**, urbanos o rurales (Ley 45/2007), y los pueblos demasiado pequeños para compararlos solos, junto con sus vecinos (`comparison_group`). La línea de explicación vale para cualquier fila, porque la API ya orienta la comparación: por encima de 1, la zona está mejor que su referencia (`ratio_to_reference`). El texto de cada fila (valor, referencia de su tipo y, entre paréntesis, la de toda la Comunidad) llega en `explanation` y se muestra debajo.

| Clave | Etiqueta | Línea de explicación | Icono (en producción, como se propuso) |
|---|---|---|---|
| `estado.falta` | FALTA | Tiene claramente menos que los municipios de su tipo, y no es por el tamaño de la zona. | Círculo con exclamación |
| `estado.justo` | JUSTO | Tiene menos que los municipios de su tipo, pero no tanto como para decir que falta. | Círculo con una raya |
| `estado.cubierto` | CUBIERTO | Tiene lo mismo o más que los municipios de su tipo. | Círculo con visto bueno |
| `estado.sin_datos` | SIN DATOS | No tenemos este dato para esta zona. No quiere decir que no haya. | Círculo con interrogación y borde discontinuo |

| Clave | Texto | Notas |
|---|---|---|
| `falta.titulo` | Qué falta en {zona} | |
| `falta.intro` | Miramos lo que tiene la gente a 15 minutos andando, repartido entre todos los que lo comparten, y lo comparamos con los demás municipios de su tipo, urbanos o rurales. | Cambia el 12 nov por D-217 (antes: «Comparamos cada servicio con los demás municipios de su tipo…») |
| `falta.resumen.falta` | Aquí falta: {lista}. | **Primera línea de «Qué falta»**, encima de las filas y en negrita. {lista} con `fila.lista.*`. Ejemplo: Puente de Vallecas, «Aquí falta: escuelas infantiles.». Fase de mejora, **pendiente de B** |
| `falta.resumen.nada_claro` | Aquí no falta nada claro. | Sin ninguna FALTA pero con alguna JUSTO. Va seguida de `falta.resumen.justo` |
| `falta.resumen.justo` | Van justos: {lista}. | Detrás de `falta.resumen.falta` o de `falta.resumen.nada_claro`. Ejemplo: Fuencarral-El Pardo, «Aquí no falta nada claro. Van justos: escuelas infantiles, colegios y centros de salud.» |
| `falta.resumen.cubierto` | Aquí no falta nada frente a municipios parecidos. | Todas las filas comparables, CUBIERTO |
| `falta.resumen.pequena` | Zona muy pequeña para comparar: {lista}. | Filas que no se pueden comparar ni siquiera con los vecinos (`reliable: false` y sin `comparison_group`). Esas filas no entran en «Van justos». Va con lo que haga A en «No comparable» (fase de mejora, punto 7) |
| `falta.resumen.sin_datos` | Sin datos: {lista}. | Al final, si alguna fila sale SIN DATOS. Ejemplo: en los distritos de Madrid, «Sin datos: viviendas grandes para familias.» |
| `falta.fila.comparacion` | Aquí hay {n} por cada 100 que hay en municipios parecidos. | **Frase principal de cada fila**, junto al estado. {n} = `ratio_to_reference` × 100, redondeado; puede pasar de 100 («Aquí hay 155 por cada 100…»). Ejemplo: Puente de Vallecas, escuelas infantiles, ratio 0,571: «Aquí hay 57 por cada 100 que hay en municipios parecidos.». Con `comparison_group`: «Junto con sus vecinos, hay {n} por cada 100…» (`grupo.frase`). Fase de mejora, **pendiente de B** |
| `falta.fila.ver_cifra` | Ver la cifra | Despliega la cifra técnica de `explanation` (por ejemplo, «2,8 escuelas infantiles al alcance a pie por cada 1.000 niños de 0 a 4 años; en los demás municipios urbanos…, 4,9»), en pequeño. No se pierde: el jurado técnico la busca |
| `falta.fila.referencia.distrito` | Municipios urbanos de la Comunidad, sin contar Madrid (como Getafe o Alcalá de Henares) | Sustituye a `reference_label` («Otros municipios urbanos de la Comunidad de Madrid») cuando la zona es un distrito. Es lo que hace la API: el municipio de la zona se deja fuera de su referencia, y en un distrito ese municipio es Madrid (`gap_reference.py`, `_others`) |
| `falta.referencia.ayuda.distrito` | Un distrito de Madrid se compara con las demás ciudades de la Comunidad, como Getafe o Alcalá de Henares. Madrid no puede compararse consigo misma. | Al tocar «?» junto a la referencia, en un distrito |
| `falta.referencia.ayuda.municipio` | Cada municipio se compara con los de su tipo: los rurales (pequeños y poco poblados) con los rurales, y los urbanos con los urbanos. | Al tocar «?» junto a la referencia, en un municipio. Criterio de la Ley 45/2007 (`metodologia.md` §1.4) |
| `falta.elige_zona` | Elige una zona en el mapa o escríbela aquí para ver qué le falta. | Sin zona elegida |
| `falta.buscador.placeholder` | Escribe un municipio o un distrito de Madrid | |
| `falta.fila.referencia` | {reference_label}: {referencia} | Si la web separa la referencia de `explanation`. `reference_label` llega de la API, por ejemplo «Otros municipios urbanos de la Comunidad de Madrid» |
| `falta.fila.region` | En toda la Comunidad de Madrid: {regional_reference} | Solo como contexto, en pequeño. `regional_reference` llega de la API |
| `fila.zona_pequena` | Zona pequeña para comparar | Etiqueta junto al estado cuando la API manda `reliable: false` (D-213, punto 3). La fila conserva su valor y nunca sale FALTA |
| `fila.zona_pequena.ayuda` | Aquí vive tan poca gente que no podemos saber con seguridad si falta. Por eso no la marcamos como FALTA. | Al tocar la etiqueta, y como línea en `falta.leyenda`. Con gap-0.3 sale solo si ni con los vecinos se puede comparar |
| `grupo.etiqueta` | Junto con sus vecinos | Etiqueta junto al estado cuando la API manda `comparison_group` (D-217 §6). El estado es el del grupo |
| `grupo.ayuda` | Comparado con municipios parecidos de la zona: es demasiado pequeño para compararlo solo, así que lo juntamos con sus vecinos más cercanos del mismo tipo. | Al tocar la etiqueta, y como línea en `falta.leyenda` |
| `grupo.frase` | Comparado con municipios parecidos de la zona. {zona} es demasiado pequeño para compararlo solo en este servicio, así que lo juntamos con {sus n vecinos más cercanos \| su vecino más cercano} del mismo tipo: {lista}. Juntos tienen el {n} % de lo que tienen de media los municipios de su tipo, y de ahí sale el estado. | En la fila, bajo las cifras de la zona: el estado es el del grupo y puede no cuadrar con la cifra propia. {lista} = `comparison_group.names` sin la propia zona, con «y» antes del último; {n} % = `comparison_group.ratio_to_reference` × 100, sin decimales |
| `falta.fila.ojo` | Ojo: {proxy_note} | Aviso de lo que el dato no mide. `proxy_note` llega de la API |
| `falta.otra_zona` | Elegir otra zona | Botón secundario junto a `zona.boton` («Ver la zona») y en el error `error.zona_no_existe`. Sustituye a «Cambiar de zona»: un solo texto para la misma acción |
| `falta.fila.fuente` | De dónde sale: {n} conjuntos de datos | Con 1: «De dónde sale: 1 conjunto de datos». Al abrirlo, los nombres de `datasets`, cada uno enlazado a su ficha |
| `falta.fila.a_pie` | A pie hasta {destino} | Con la cifra a la derecha (`a_pie.min`). Sale de `extra_indicators` (`min_a_pie_*`: mediana de las calles de la zona, a 4 km/h; D-210, D-211). La fila de vivienda no lleva |
| `falta.fila.a_pie.escuela_infantil` | la escuela infantil más cercana | {destino} |
| `falta.fila.a_pie.colegio` | el colegio más cercano | {destino} |
| `falta.fila.a_pie.centro_salud` | el centro de salud más cercano | {destino} |
| `falta.fila.a_pie.mayores` | el centro de mayores más cercano | {destino} |
| `falta.fila.a_pie.farmacia` | la farmacia más cercana | {destino} |
| `falta.fila.a_pie.hospital` | el hospital general más cercano | {destino}. Solo en la fila de centros de salud, aparte de sus minutos (`min_a_pie_hospital`, D-217 §5) |
| `hospital.titulo` | El hospital: | Delante de `hospital.nota` |
| `hospital.nota` | Es una pista de dónde pueden quedar las urgencias, no un dato de urgencias: ninguna fuente abierta dice qué hospitales las tienen abiertas las 24 horas. Andando, no en coche ni en ambulancia, y no cuenta para el estado de la fila. | Cambia el 12 nov: se añade «y no cuenta para el estado de la fila» |
| `a_pie.min` | {n} min | Redondeado al minuto. Menos de 1: «menos de 1 min». Más de 60: «más de 60 min». Sin valor: «Sin datos», con su motivo (`null_reason`), nunca 0 |
| `falta.leyenda.titulo` | Cómo leer esta lista | Tarjeta con los 4 estados y su línea de explicación (`estado.*`), más la línea de `fila.zona_pequena` |
| `falta.leyenda.a_pie` | Los minutos son andando por la calle, no en línea recta, a paso tranquilo (4 km/h). Es lo que tarda la mitad de la zona: unos vecinos lo tienen más cerca y otros más lejos. | Debajo de los estados. Mismo método que `pitch/metodologia.md` §1.5. Cambia el 13 nov: fuera «desde la mitad de las calles». La misma idea, como ayuda bajo «Lo que tienes aquí» en la tarjeta (`a_pie.mediana`) |
| `a_pie.mediana` | Los minutos andando son los de la mitad de la zona: unos vecinos lo tienen más cerca y otros más lejos. | Una vez, bajo los hechos de la tarjeta. A la vez, **pendiente de A**: quitar «desde la mitad de sus calles» del texto de los hechos de `/search` y dejar «Colegio con primaria a unos 9 min andando». El «unos» ya dice que es aproximado |
| `hospital.distancia` | Hospital más cercano: a {n} min andando | Sustituye a «A pie hasta el hospital: {n} min». Hasta 30 min, en minutos. **Más de 30 min: «Hospital más cercano: a unos {km} km»**, con {km} = minutos × 4 / 60, con un decimal (51 min → «a unos 3,4 km»). Andar 51 minutos hasta un hospital no es un dato útil, la distancia sí. Sigue con `hospital.nota`. **Pendiente de B** |
| `falta.filas_pendientes` | Estamos calculando el resto de servicios para esta zona. | Si la API avisa en `warnings` de filas aún no calculadas. Nunca se pintan como SIN DATOS |
| `falta.como` | ¿Cómo lo decidimos? | Enlace a «Cómo lo calculamos», sección «Qué falta» |

**Nombres de las 6 filas** (D-194). La API los manda en `label`; estos son los de respaldo, iguales que `gap_row.label` del catálogo (`data/catalog/features/`):

| Clave | Texto | `fila.mide.*`: qué mide (gap-0.3; la API manda su propia etiqueta en `indicator.label`) |
|---|---|---|
| `fila.escuela_infantil` | Escuelas infantiles | Escuelas infantiles a 15 min andando por cada 1.000 niños de 0 a 4 años, repartidas entre todos los que las tienen cerca |
| `fila.colegio` | Colegios | Aulas de primaria, públicas y concertadas, a 15 min andando por cada 1.000 niños de 5 a 14 años, repartidas entre todos los que las tienen cerca |
| `fila.centro_salud` | Centros de salud | Centros de salud del SERMAS a 15 min andando por cada 10.000 habitantes, repartidos entre todos los que los tienen cerca |
| `fila.mayores` | Centros de mayores | Plazas en hogares, clubes y centros de día a 15 min andando por cada 100 personas de 65 años o más, repartidas entre todos los que las tienen cerca |
| `fila.farmacia` | Farmacias | Farmacias a 15 min andando por cada 10.000 habitantes, repartidas entre todos los que las tienen cerca |
| `fila.vivienda` | Vivienda para familias | Viviendas de más de 90 m² por cada 100 hogares de 4 o más personas. En los distritos de Madrid, SIN DATOS (`SOURCE_MISSING`) |

Los textos de `fila.mide.*` son los de B (`ROW_MEASURE` en `gaps.ts`), definitivos el 12 nov. Las cifras de antes (centros por habitante) siguen como datos extra de cada fila (D-217 §3).

**Por qué falta un dato** (cuando `indicator.value` es `null`, la API manda `null_reason`):

| `null_reason` | Texto |
|---|---|
| `SOURCE_NO_COVERAGE` | La fuente oficial no publica este dato para esta zona. |
| `SOURCE_MISSING` | La fuente oficial no trae este dato. |
| `NOT_APPLICABLE` | Este dato no tiene sentido en esta zona. |
| `TEMPORARILY_UNAVAILABLE` | Este dato no está disponible ahora mismo. Vuelve a intentarlo más tarde. |
| `STALE` | El último dato publicado es demasiado antiguo para usarlo. |
| `PARSE_ERROR` | El dato publicado venía con errores y no lo usamos. |
| `ENTITY_NOT_RESOLVED` | No hemos podido situar este dato en el mapa. |
| `ESTIMATION_NOT_ALLOWED` | No hay dato oficial y preferimos no inventarlo. |
| `UNKNOWN` | No sabemos este dato. |

## 5b. «Todos los centros» de una zona (D-216, D-218)
Panel de la vista de zona con cada tipo de centro, su recuento, su capa en el mapa y su lista. Los nombres y las camas llegan de `/places` (`places-1`).

| Clave | Texto | Notas |
|---|---|---|
| `centros.titulo` | Todos los centros | |
| `centros.ver` | Ver en el mapa | Un tipo de centro a la vez |
| `centros.elige` | Toca un tipo de centro para verlo en el mapa. | Sin tipo elegido |
| `centros.cargando` | Buscando los centros de {zona}… | |
| `centros.lista` | Ver la lista ({n}) | |
| `centros.colegios_fila` | Públicos y concertados: los mismos que cuenta «Qué falta». | Bajo el recuento de colegios |
| `centros.sin_nombre` | La fuente oficial no publica el nombre de cada centro de este tipo. | Si no sale el nombre de ninguno |
| `centros.sin_nombre_algunos` | Algunos centros salen sin nombre porque no hemos podido comprobarlo en las fuentes oficiales. | Si falta el de algunos. Revisión del PR #17 |
| `centros.camas` | Camas instaladas a 31 de diciembre de 2024, según el [Catálogo Nacional de Hospitales 2025] del Ministerio de Sanidad. | Bajo el recuento de hospitales. Enlace al catálogo (`url` de `/datasets`), con «(se abre en una pestaña nueva)» oculto. La fecha sale del nombre del catálogo en `/datasets` («actualizado a 31 de diciembre de 2024»); sin `/datasets`, este texto fijo. Revisión del PR #17 |
| `centros.recuento.colegio` | {n} colegios con primaria en {zona} · 1 colegio con primaria en {zona} · Ningún colegio con primaria en {zona} | |
| `centros.recuento.escuela_infantil` | {n} escuelas infantiles en {zona} · 1 escuela infantil en {zona} · Ninguna escuela infantil en {zona} | |
| `centros.recuento.centro_salud` | {n} centros de salud y consultorios en {zona} · 1 centro de salud o consultorio en {zona} · Ningún centro de salud ni consultorio en {zona} | Cambia el 12 nov: la lista incluye los consultorios |
| `centros.recuento.hospital` | {n} hospitales en {zona} · 1 hospital en {zona} · Ningún hospital en {zona} | Generales, especializados, de media y larga estancia y de salud mental, cada uno con su etiqueta en la lista |
| `centros.recuento.farmacia` | {n} farmacias en {zona} · 1 farmacia en {zona} · Ninguna farmacia en {zona} | |
| `centros.recuento.mayores` | {n} centros de mayores en {zona} · 1 centro de mayores en {zona} · Ningún centro de mayores en {zona} | Hogares, clubes y centros de día; las residencias no salen (la fila es la misma) |
| `centro.detalle` | {nombre} · {capacidad} · ubicación aproximada | Cada parte solo si la API la manda. {capacidad} = `capacity.value` y `capacity.unit` («966 camas instaladas», «120 plazas autorizadas»). «ubicación aproximada» si `coordinates` es `geocoded` (D-216 §3) |

---

## 6. Confianza en palabras

**Cortes de D, confirmados por A el 11 nov.** El 0,5 cuenta como «Dato aproximado» porque es el tope que reciben las zonas con poca población (D-189). La API da la confianza de 0 a 1. En zonas con poca población la baja a 0,5 como máximo, y 0 significa desconocido (`docs/04_technical_architecture/31_public_api_routes.md`, «Reglas que la web puede dar por hechas»).

| Confianza | Clave | Texto | Ayuda (al tocar) |
|---|---|---|---|
| 0,8 o más | `confianza.alta` | Dato fiable | Sale de un registro oficial completo. |
| De 0,5 a menos de 0,8 | `confianza.media` | Dato aproximado | El dato es oficial, pero la zona tiene poca población o la fuente no está completa: tómalo como una aproximación. |
| Más de 0 y menos de 0,5 | `confianza.baja` | Dato poco seguro | Faltan bastantes datos en la fuente. Úsalo con cuidado. |
| 0 o sin valor | `confianza.ninguna` | Sin datos | No tenemos este dato. |

| Clave | Texto |
|---|---|
| `confianza.aria` | Fiabilidad del dato: {texto} |

---

## 7. «¿Y si cambias algo?» (Reality Check)

Siempre visible bajo «Zonas que encajan». Va plegado a la opción que más zonas añade y se despliega solo con 5 zonas o menos (decisión de datamad-10; `FEW_ZONES`, PR #10). No salen las opciones que añaden 0 zonas. Las cifras y las etiquetas de cada opción (`label`, por ejemplo «+150 €/mes») llegan de la API. Al tocar una opción, la web reenvía `relaxed_scenario`.

| Clave | Texto | Notas |
|---|---|---|
| `rc.titulo` | ¿Y si cambias algo? | |
| `rc.ninguna` | Con tu búsqueda tal cual no sale ninguna zona. | `zones_passing = 0` |
| `rc.una` | Con tu búsqueda tal cual sale 1 zona. | |
| `rc.varias` | Con tu búsqueda tal cual salen {n} zonas. | |
| `rc.cambio` | Con este cambio salen {n} zonas. | En lugar de `rc.varias` tras aplicar una opción. Con 1: «Con este cambio sale 1 zona.»; con 0: «Con este cambio no sale ninguna zona.» |
| `rc.intro` | Mira cuántas salen si cambias una sola cosa: | |
| `rc.opcion` | {label} | Primera línea de cada opción |
| `rc.opcion.cuenta` | saldrían {n} zonas, {añadidas} más | Segunda línea. {n} = `zones_if_relaxed`, {añadidas} = `added_zones`. Con 1 zona: «saldría 1 zona, 1 más». El nombre accesible de la opción es su texto visible (WCAG 2.5.3) |
| `rc.boton` | Probar así | En cada opción |
| `rc.mas` | Ver todas las opciones | Con el bloque plegado |
| `rc.menos` | Ver menos | |
| `rc.sin_opciones` | Cambiar una sola cosa no añade zonas. | Ninguna opción añade zonas |
| `rc.sin_dato` | En {n} zonas no podemos comprobarlo todo por falta de datos. No las contamos como buenas. | `zones_unknown` > 0 |
| `rc.limite` | Lo que más limita tu búsqueda es: {condición} | `binding_constraint` |
| `rc.nota` | No te decimos que gastes más: te enseñamos qué cuesta cada alternativa. | Frase del mensaje de la idea (sin cifras) |
| `rc.deshacer` | Volver a mi búsqueda | Tras aplicar una opción |
| `rc.aplicado` | Ahora ves las zonas con: {label} | Aviso tras aplicar una opción |

---

## 8. Estados de vacío, carga y error

| Clave | Texto | Cuándo |
|---|---|---|
| `carga.mapa` | Cargando el mapa… | |
| `carga.zonas` | Cargando las zonas… | Lista de zonas |
| `carga.fuentes` | Cargando los conjuntos de datos… | Lista de «Cómo lo calculamos» (`GET /api/v1/datasets`) |
| `carga.busqueda` | Buscando zonas que encajan… | |
| `carga.zona` | Preparando la zona… | Vuelo de cámara y 3D |
| `carga.falta` | Calculando qué falta en {zona}… | |
| `carga.lento` | Está tardando un poco más de lo normal. Gracias por esperar. | Más de 5 s |
| `vacio.sin_busqueda` | Cuéntanos cómo es tu hogar y pulsa «Ver zonas que encajan». | |
| `vacio.sin_resultados` | Ninguna zona cumple todo lo que pides. Mira abajo qué pasa si cambias algo. | Lleva al bloque de la sección 7 |
| `error.red` | No hemos podido conectar. Comprueba tu conexión a internet e inténtalo otra vez. | Fallo de red |
| `error.servidor` | Algo ha fallado por nuestra parte. Inténtalo de nuevo en unos minutos. | Error 5xx |
| `error.zona_no_existe` | No encontramos esa zona. Elige otra en el mapa. | 404 de `/gaps` |
| `error.busqueda_no_valida` | Hay algo en tu búsqueda que no podemos usar. Revisa los datos marcados. | 422 de `/search` |
| `error.fuera_cobertura` | Ese lugar está fuera de la Comunidad de Madrid. Vida Fácil solo cubre la Comunidad de Madrid. | `OUT_OF_COVERAGE` |
| `error.datos_insuficientes` | No hay datos suficientes para responder con seguridad en esta zona. | `INSUFFICIENT_DATA` |
| `error.fuente_caida` | Uno de los datos oficiales no está disponible ahora. Te enseñamos lo que tenemos y marcamos lo que falta. | `SOURCE_DEGRADED` |
| `error.demasiadas` | Hay mucha gente usando Vida Fácil ahora mismo. Espera unos segundos y vuelve a intentarlo. | `RATE_LIMITED` |
| `error.reintentar` | Reintentar | Botón |
| `error.sin_conexion_mapa` | No se ha podido cargar el mapa. Puedes seguir con la lista de zonas. | Fallo de las teselas |

---

## 9. Procedencia («¿De dónde sale?»)

| Clave | Texto | Notas |
|---|---|---|
| `fuente.titulo` | De dónde sale este dato | |
| `fuente.conjunto` | {nombre} — {publica} | Por cada `DatasetRef` |
| `fuente.cm` | Portal de Datos Abiertos de la Comunidad de Madrid | Etiqueta si `is_cm_open_data` |
| `fuente.version` | Versión de los datos: {version} | |
| `fuente.licencia` | Licencia: {licencia} | |
| `fuente.abrir` | Abrir en el portal | Enlace a `url`, en una pestaña nueva |
| `fuente.abrir.aria` | Abrir {nombre} en el portal de datos (se abre en una pestaña nueva) | |

---

## 10. Pie y atribuciones

Las atribuciones salen de `attribution_text` en `data/catalog/sources/`. Cada licencia pide citar la fuente; el CRTM pide además «Powered by CRTM» con enlace, indicar si los datos son en bruto o explotados y no sugerir que respalda el servicio (`data/catalog/sources/crtm_open_data.yaml`, `notes`).

| Clave | Texto | Enlace | Notas |
|---|---|---|---|
| `pie.contador` | Datos: {n} conjuntos de la Comunidad de Madrid (con los del CRTM) + Ayuntamiento de Madrid + Ministerio de Sanidad | Página «Cómo lo calculamos» | {n} = `cm_open_data_count` de `GET /api/v1/datasets`: 26 en producción el 12 nov (con las 3 topologías del CRTM, D-223). Cambia el 12 nov: los 6 del CRTM ya están dentro de {n}, y el Ministerio de Sanidad se usa desde D-218 |
| `pie.cm` | Fuente: Comunidad de Madrid — Portal de Datos Abiertos (datos.comunidad.madrid), CC BY 4.0. | https://datos.comunidad.madrid | |
| `pie.crtm` | Powered by CRTM — datos del Consorcio Regional de Transportes de Madrid (www.crtm.es). En bruto: los nombres de las estaciones. Explotados: los minutos hasta las paradas y en transporte público, que calcula Vida Fácil con sus paradas y horarios. | https://www.crtm.es | Obligatorio con enlace. La licencia (§2.2) pide decir si los datos son en bruto o explotados. El `attribution_text` del catálogo, que es lo que enseña la web, dice «Datos en bruto / explotados según el caso» y no dice cuál: **pendiente de A** cambiarlo por este texto en `data/catalog/sources/crtm_open_data.yaml`. Cambia el 12 nov (revisión del PR #22) por el trabajo en minutos de transporte público (D-220) |
| `pie.ayto` | Fuente: Ayuntamiento de Madrid — datos.madrid.es, CC BY 4.0. | https://datos.madrid.es | En uso desde DATA-012 (padrón y panel de distritos). Condiciones vigentes: CC BY 4.0, uso comercial y no comercial (https://datos.madrid.es/pages/condiciones-de-uso, leída el 11 nov); no fijan un texto de cita, así que se usa el `attribution_text` del catálogo con la licencia añadida |
| `pie.osm` | © OpenStreetMap contributors, ODbL. | https://www.openstreetmap.org/copyright | Red peatonal (`osm_red_peatonal`) |
| `pie.sanidad` | Fuente: Ministerio de Sanidad — Catálogo Nacional de Hospitales 2025 (actualizado a 31/12/2024) y Catálogo de Centros de Atención Primaria del SNS 2026 (actualizado a 31/12/2025). | https://www.sanidad.gob.es/estadEstudios/estadisticas/sisInfSanSNS/ofertaRecursos/hospitales/home.htm | **Nuevo, obligatorio:** el aviso legal pide citar la fuente y la fecha de actualización (`data/catalog/sources/ministerio_sanidad.yaml`, D-218 §1). Hoy la web no lo cita |
| `pie.cartociudad` | Geocodificación: © Instituto Geográfico Nacional (CartoCiudad), CC BY 4.0 scne.es. | https://www.cartociudad.es | **Nuevo, obligatorio.** Es la forma de cita que pide el IGN (PR #18, 12 nov). coloca los centros marcados «ubicación aproximada» (`data/catalog/sources/ign_cartociudad.yaml`, D-216 §3). Hoy la web no lo cita |
| `pie.mapa_base` | Mapa: OpenFreeMap © OpenMapTiles. Datos de © OpenStreetMap. | openfreemap.org · openmaptiles.org · openstreetmap.org/copyright | Texto del ejemplo de OpenFreeMap. Hecho: el mapa de producción ya pinta «OpenFreeMap © OpenMapTiles Data from OpenStreetMap» en su esquina, así que en el pie no se repite (capturas `prod_*` de `evidence/map-004/2026-11-11/`) |
| `pie.independiente` | Vida Fácil no es un servicio de la Comunidad de Madrid, del Ayuntamiento, del CRTM ni del Ministerio de Sanidad. | | Cumple el «no sugerir respaldo» del CRTM y evita parecer un servicio oficial. Cambia el 12 nov: suma el Ministerio |
| `pie.proyecto` | Vida Fácil · Proyecto para DATAMAD 2026 | | Cambia el 13 nov: un solo nombre visible, «Vida Fácil» (jurado simulado). «Housing Intelligence» solo queda en el nombre del repositorio, que se ve en el enlace del código. **Pendiente de B** (`SiteFooter.tsx`, `TEXT.project`) |
| `pie.codigo` | Código abierto (Apache-2.0) | https://github.com/marianohernando/housing-intelligence | D-191 |
| `pie.como` | Cómo lo calculamos | Pestaña | |
