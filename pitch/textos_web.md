# Textos de la web — Vida Fácil

Para la línea B: estos son los textos de la web, listos para usar tal cual. Si un texto no cabe o no encaja en el diseño, cámbialo en la web y avisa en el PR #2 para que lo actualice aquí.

**Novedades del 11 nov (noche), para los textos que B dejó provisionales en el PR #2:**
- **Barra de barrios:** `barrios.titulo` pasa a «Ir a un barrio», porque la barra solo mueve el mapa. Nuevos: `barrios.todo` («Todo {distrito}») y `barrios.ayuda`.
- **«Qué falta»:** «Cambiar de zona» pasa a `falta.otra_zona` («Elegir otra zona»), el mismo texto que ya sale cuando la zona no existe.
- **Definitivos:**
  - de la lista: `falta.leyenda.titulo` («Cómo leer esta lista»), `falta.leyenda.a_pie`, `falta.fila.a_pie` con sus destinos, `a_pie.min`, `zona.falta.a_pie` y `falta.fila.fuente`, con el número de conjuntos;
  - del buscador apagado: `busqueda.pronto`, `leyenda.pronto` y `zona.encaje.pronto`;
  - de navegación y carga: `movil.hoja.mapa`, `zonas.*`, `carga.zonas` y `carga.fuentes`.
- **Nombres de fila:** `fila.mayores` y `fila.vivienda` igualan las etiquetas del catálogo: «Centros de mayores» y «Vivienda para familias».
- **Método nuevo (D-213, `gap-0.2`):** cada zona se compara con los demás municipios de su tipo y no con toda la Comunidad. Cambian `estado.falta`, `estado.justo`, `estado.cubierto`, `falta.intro`, `falta.fila.referencia` y `portada.paso3`; hay `falta.fila.region` nuevo.
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
| `hogar.hijos.edades` | Edades (si quieres) | Opcional (`minor_ages`). Ayuda: «Nos sirve para saber si buscas escuela infantil o colegio.» |
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
| `importa.colegios` | Colegios | Colegios públicos cerca de casa. | |
| `importa.zonas_verdes` | Zonas verdes | Parques y jardines cerca de casa. | **Pendiente de A** (DATA-018, 19–22 nov). Mientras no exista, el chip va desactivado con `importa.pronto` |
| `importa.seguridad` | Seguridad | Actuaciones policiales registradas por cada 1.000 habitantes. Solo hay datos de Madrid capital. | Texto neutro del brief. **Pendiente de A** (DATA-020) |
| `importa.sin_escaleras` | Sin escaleras | Estaciones de metro y Cercanías con acceso sin escaleras y edificios públicos accesibles. | Opcional (D-204). **Pendiente de A** (DATA-019) |
| `importa.pronto` | Muy pronto | Etiqueta pequeña del chip desactivado. Ayuda: «Estamos añadiendo estos datos.» | |
| `importa.orden` | Lo más importante para ti: {lista} | Resumen con la tarjeta plegada |

### «Trabajo en»
| Clave | Texto | Notas |
|---|---|---|
| `trabajo.titulo` | Trabajo en | |
| `trabajo.placeholder` | Escribe una calle, un barrio o un municipio | |
| `trabajo.ayuda` | Así miramos lo lejos que te queda cada zona. | |
| `trabajo.dias` | ¿Cuántos días vas a la semana? | Opcional (`days_per_week`) |
| `trabajo.max_min` | Tardar como mucho {n} min | **Pendiente de A** (CORE-009, tiempo en transporte público, 19–22 nov). Si no está, no se muestra |
| `trabajo.sin_resultados` | No encontramos ese lugar. Prueba con otra calle o con el nombre del municipio. | |
| `trabajo.quitar` | Quitar este lugar | |

### Cerca de casa (opcional, si B lo muestra)
`ScenarioState.nearby` admite servicios a un paseo. El caso de ejemplo pide colegio a 10 min andando como mínimo.

| Clave | Texto | Notas |
|---|---|---|
| `cerca.titulo` | Lo quiero a un paseo | |
| `cerca.item` | {servicio} a menos de {n} min andando | Servicios: escuela infantil, colegio, centro de salud, farmacia, mayores y transporte (`NeedKey`) |
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
| `presupuesto.compra.sin_datos` | Aún no tenemos precios oficiales de compra por zona, así que no podemos comprobar si entra en tu presupuesto. | Mientras falte DATA-021: la condición sale «sin dato» (D-203). **Pendiente de A** |
| `presupuesto.sin_limite` | Sin límite de presupuesto | Opción del slider (`budget: null`) |
| `presupuesto.slider.aria` | Presupuesto máximo | `aria-label` |
| `presupuesto.fuera_rango.alquiler` | El alquiler tiene que estar entre 100 y 20.000 € al mes. | |
| `presupuesto.fuera_rango.compra` | El precio de compra tiene que estar entre 10.000 y 5.000.000 €. | |

### Botón principal
| Clave | Texto |
|---|---|
| `busqueda.boton` | Ver zonas que encajan |
| `busqueda.boton.cargando` | Buscando zonas… |

### Mientras el buscador no esté
El buscador sale como «Muy pronto» hasta que exista `POST /api/v1/search` (CORE-003, **pendiente de A**). La web lo enciende con `NEXT_PUBLIC_FEATURE_SEARCH=true` (`apps/web/src/lib/capabilities.ts`).

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

---

## 4. Tarjeta de zona

| Clave | Texto | Notas |
|---|---|---|
| `zona.encaje` | {pct} % de encaje | Chip grande. Nunca «/100» |
| `zona.encaje.aria` | Esta zona encaja en un {pct} % con tu búsqueda | |
| `zona.encaje.ayuda` | Cuánto se parece esta zona a lo que buscas. No es una nota de la zona. | Al tocar «?» |
| `zona.puesto` | La {n}.ª que más encaja | Posición (`rank`) |
| `zona.hechos.titulo` | Lo que tienes aquí | Encima de los 3–5 hechos (`facts`) |
| `zona.hecho.confianza` | {nivel} | Junto a cada hecho, con los niveles de la sección 6 |
| `zona.coste.alquiler` | Alquiler estimado: unos {importe} € al mes | `estimated_cost_eur`. Ayuda: «Para una vivienda del tamaño que necesita tu hogar, según el precio medio publicado.» |
| `zona.coste.compra` | Precio estimado: unos {importe} € (orientativo) | |
| `zona.coste.sin_datos` | Precio: sin datos en esta zona | |
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

Desde D-213 (`gap-0.2`) cada zona se compara con **los demás municipios de su tipo**, urbanos o rurales (Ley 45/2007), y no con toda la región. La línea de explicación vale para cualquier fila, porque la API ya orienta la comparación: por encima de 1, la zona está mejor que su referencia (`ratio_to_reference`). El texto de cada fila (valor, referencia de su tipo y, entre paréntesis, la de toda la Comunidad) llega en `explanation` y se muestra debajo.

| Clave | Etiqueta | Línea de explicación | Icono (propuesta, **pendiente de B**) |
|---|---|---|---|
| `estado.falta` | FALTA | Tiene claramente menos que los municipios de su tipo, y no es por el tamaño de la zona. | Círculo con exclamación |
| `estado.justo` | JUSTO | Tiene menos que los municipios de su tipo, pero no tanto como para decir que falta. | Círculo con una raya |
| `estado.cubierto` | CUBIERTO | Tiene lo mismo o más que los municipios de su tipo. | Círculo con visto bueno |
| `estado.sin_datos` | SIN DATOS | No tenemos este dato para esta zona. No quiere decir que no haya. | Círculo con interrogación y borde discontinuo |

| Clave | Texto | Notas |
|---|---|---|
| `falta.titulo` | Qué falta en {zona} | |
| `falta.intro` | Comparamos cada servicio con los demás municipios de su tipo, urbanos o rurales, según cuánta gente vive aquí. | Cambia el 11 nov por D-213 |
| `falta.elige_zona` | Elige una zona en el mapa o escríbela aquí para ver qué le falta. | Sin zona elegida |
| `falta.buscador.placeholder` | Escribe un municipio o un distrito de Madrid | |
| `falta.fila.referencia` | {reference_label}: {referencia} | Si la web separa la referencia de `explanation`. `reference_label` llega de la API, por ejemplo «Otros municipios urbanos de la Comunidad de Madrid» |
| `falta.fila.region` | En toda la Comunidad de Madrid: {regional_reference} | Solo como contexto, en pequeño. `regional_reference` llega de la API |
| `fila.zona_pequena` | Zona pequeña para comparar | Etiqueta junto al estado cuando la API manda `reliable: false` (D-213, punto 3). La fila conserva su valor y nunca sale FALTA |
| `fila.zona_pequena.ayuda` | Aquí vive tan poca gente que no podemos saber con seguridad si falta. Por eso no la marcamos como FALTA. | Al tocar la etiqueta, y como línea en `falta.leyenda` |
| `falta.fila.ojo` | Ojo: {proxy_note} | Aviso de lo que el dato no mide. `proxy_note` llega de la API |
| `falta.otra_zona` | Elegir otra zona | Botón secundario junto a `zona.boton` («Ver la zona») y en el error `error.zona_no_existe`. Sustituye a «Cambiar de zona»: un solo texto para la misma acción |
| `falta.fila.fuente` | De dónde sale: {n} conjuntos de datos | Con 1: «De dónde sale: 1 conjunto de datos». Al abrirlo, los nombres de `datasets`, cada uno enlazado a su ficha |
| `falta.fila.a_pie` | A pie hasta {destino} | Con la cifra a la derecha (`a_pie.min`). Sale de `extra_indicators` (`min_a_pie_*`: mediana de las calles de la zona, a 4 km/h; D-210, D-211). La fila de vivienda no lleva |
| `falta.fila.a_pie.escuela_infantil` | la escuela infantil más cercana | {destino} |
| `falta.fila.a_pie.colegio` | el colegio más cercano | {destino} |
| `falta.fila.a_pie.centro_salud` | el centro de salud más cercano | {destino} |
| `falta.fila.a_pie.mayores` | el centro de mayores más cercano | {destino} |
| `falta.fila.a_pie.farmacia` | la farmacia más cercana | {destino} |
| `a_pie.min` | {n} min | Redondeado al minuto. Menos de 1: «menos de 1 min». Más de 60: «más de 60 min». Sin valor: «Sin datos», con su motivo (`null_reason`), nunca 0 |
| `falta.leyenda.titulo` | Cómo leer esta lista | Tarjeta con los 4 estados y su línea de explicación (`estado.*`), más la línea de `fila.zona_pequena` |
| `falta.leyenda.a_pie` | Los minutos a pie son andando por la calle, no en línea recta, a paso tranquilo (4 km/h). Desde la mitad de las calles de la zona se llega en ese tiempo o menos. | Debajo de los estados. Mismo método que `pitch/metodologia.md` §1.5 |
| `falta.filas_pendientes` | Estamos calculando el resto de servicios para esta zona. | Si la API avisa en `warnings` de filas aún no calculadas. Nunca se pintan como SIN DATOS |
| `falta.como` | ¿Cómo lo decidimos? | Enlace a «Cómo lo calculamos», sección «Qué falta» |

**Nombres de las 6 filas** (D-194). La API los manda en `label`; estos son los de respaldo, iguales que `gap_row.label` del catálogo (`data/catalog/features/`):

| Clave | Texto | Qué mide (lo manda la API en la fila) |
|---|---|---|
| `fila.escuela_infantil` | Escuelas infantiles | Escuelas infantiles por cada 1.000 niños de 0 a 4 años |
| `fila.colegio` | Colegios | Colegios con primaria, públicos o concertados, por cada 1.000 menores de 15 años |
| `fila.centro_salud` | Centros de salud | Centros de atención primaria por cada 10.000 habitantes |
| `fila.mayores` | Centros de mayores | Hogares, clubes y centros de día por cada 1.000 personas de 65 años o más |
| `fila.farmacia` | Farmacias | Farmacias por cada 10.000 habitantes |
| `fila.vivienda` | Vivienda para familias | Viviendas de más de 90 m² por cada 100 hogares de 4 o más personas. En los distritos de Madrid, SIN DATOS (`SOURCE_MISSING`) |

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

Aparece cuando salen pocas zonas o ninguna (brief). Las cifras y las etiquetas de cada opción (`label`, por ejemplo «+100 €/mes») llegan de la API. Al tocar una opción, la web reenvía `relaxed_scenario`.

| Clave | Texto | Notas |
|---|---|---|
| `rc.titulo` | ¿Y si cambias algo? | |
| `rc.ninguna` | Con tu búsqueda tal cual no sale ninguna zona. | `zones_passing = 0` |
| `rc.una` | Con tu búsqueda tal cual sale 1 zona. | |
| `rc.varias` | Con tu búsqueda tal cual salen {n} zonas. | |
| `rc.intro` | Mira cuántas salen si cambias una sola cosa: | |
| `rc.opcion` | {label}: {n} zonas | `zones_if_relaxed` |
| `rc.opcion.aria` | Probar con {label}. Saldrían {n} zonas. | |
| `rc.boton` | Probar así | En cada opción |
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
| `pie.contador` | Datos: {n} conjuntos de la Comunidad de Madrid + Ayuntamiento de Madrid + CRTM | Página «Cómo lo calculamos» | {n} = `cm_open_data_count` de `GET /api/v1/datasets`. Hoy 21. El Ayuntamiento ya se usa (padrón y panel de distritos, D-209) |
| `pie.cm` | Fuente: Comunidad de Madrid — Portal de Datos Abiertos (datos.comunidad.madrid), CC BY 4.0. | https://datos.comunidad.madrid | |
| `pie.crtm` | Powered by CRTM — datos del Consorcio Regional de Transportes de Madrid (www.crtm.es). Datos explotados: paradas y frecuencias calculadas por Vida Fácil a partir de sus horarios. | https://www.crtm.es | Obligatorio con enlace |
| `pie.ayto` | Fuente: Ayuntamiento de Madrid — datos.madrid.es, CC BY 4.0. | https://datos.madrid.es | En uso desde DATA-012 (padrón y panel de distritos). Condiciones vigentes: CC BY 4.0, uso comercial y no comercial (https://datos.madrid.es/pages/condiciones-de-uso, leída el 11 nov); no fijan un texto de cita, así que se usa el `attribution_text` del catálogo con la licencia añadida |
| `pie.osm` | © OpenStreetMap contributors, ODbL. | https://www.openstreetmap.org/copyright | Red peatonal (`osm_red_peatonal`) |
| `pie.mapa_base` | Mapa: OpenFreeMap © OpenMapTiles. Datos de © OpenStreetMap. | openfreemap.org · openmaptiles.org · openstreetmap.org/copyright | Texto del ejemplo de OpenFreeMap. **Pendiente de B:** confirmar el proveedor de teselas; si MapLibre ya pinta la atribución en el mapa, aquí no se repite |
| `pie.independiente` | Vida Fácil no es un servicio de la Comunidad de Madrid, del Ayuntamiento ni del CRTM. | | Cumple el «no sugerir respaldo» del CRTM y evita parecer un servicio oficial |
| `pie.proyecto` | Vida Fácil · Plataforma Housing Intelligence · Proyecto para DATAMAD 2026 | | «Housing Intelligence» solo como plataforma o equipo (D-199) |
| `pie.codigo` | Código abierto (Apache-2.0) | https://github.com/marianohernando/housing-intelligence | D-191 |
| `pie.como` | Cómo lo calculamos | Pestaña | |
