# Textos de la web — Vida Fácil

Para la línea B: estos son los textos de la web, listos para usar tal cual. Si un texto no cabe o no encaja en el diseño, cámbialo en la web y avisa en el PR #2 para que lo actualice aquí.

**Claridad en el móvil, primera entrega (15 nov, línea B; auditoría `prompts/UX_AUDITORIA_MOVIL.md`, opción 1 y D-244).** Una persona mayor probó la web en el móvil: «difícil de entender, muchos datos juntos». Decidido por Mariano con el orquestador. Lo que cambia en pantalla:
- **Letra de 16 px o más** en todo lo que se lee para decidir, y 18 px de cuerpo en el móvil (`--text-xs`, `--text-sm` a 1 rem y la raíz al 112,5 % hasta 760 px). **Botones de 44 px o más,** también «¿Dónde?», «Alquilar/Comprar», «Ver todo lo que falta» y los enlaces de la portada, que van subrayados.
- **Lenguaje llano (§4 de la auditoría):** «encaja» sale de la vista principal y queda en «Cómo lo calculamos», que es la página del método. Cambian el botón (`busqueda.boton`), la lista (`resultados.titulo`, `rc.*`, `resultados.de*`, `resultados.casi.*`, `zona.cerca_de_encajar.titulo`), las bandas (`resultados.banda.*`), la tarjeta (`zona.*`, `encaje.aviso_*`), la leyenda (`leyenda.*`) y «¿Quieres ver más zonas?» (sección 7). «≈» pasa a «unos» en la tarjeta y en «Casi valen»; en las filas de la lista sigue «≈» hasta la entrega 2, que rehace la fila. Sin siglas sin explicar: fuera «EMT», «SERMAS», «CRTM» e «INE» de las ayudas y de la tarjeta (las atribuciones de licencia no cambian). Los valores de la API (`muy_bien`, `bien`, `regular`, `poco`) no cambian.
- **Las explicaciones que estaban en `title`** (en el móvil no se ven) pasan a texto visible o a un botón «¿Qué es esto?» (`ayuda.que_es`): ayudas del formulario, qué cuenta cada botón de «¿Qué quieres tener cerca?», qué es el % (`zona.encaje.que_es`), qué quieren decir FALTA, JUSTO y CUBIERTO (`zona.falta.estados`, a la vista bajo las filas de la tarjeta) y la fiabilidad de los hechos (`confianza.que_es`).
- **Formulario más corto a la vista:** «Lo quiero a un paseo», «Cerca de mi familia o amigos» y el tamaño del piso van plegados en «Más opciones» (`mas.*`), que dice cuántas cosas tiene elegidas. «Trabajo en (opcional)». Importes rápidos para el presupuesto y «Otra cantidad» (`presupuesto.importes`, `presupuesto.otra`); el deslizador se queda.
- **«Somos mayores» (D-244, diseño de Mariano tras la revisión del PR #79):** `hogar.somos_mayores`; en lugar de «Trabajo en», «¿Cerca de dónde queréis vivir?» (`lugar.*`: donde viven ahora o cerca de su familia, 30 min como mucho); «¿Dónde?» empieza en «Madrid capital» si no hay sitio; se marcan «Centro de salud», «Metro o tren sin escaleras» y «Transporte»; la tarjeta pone primero, a igual estado, centros de salud, farmacias y centros de mayores; y el segundo ejemplo de la portada (`portada.ejemplo.mayores`).
- **Revisión del PR #79:** el hecho del coste de la tarjeta dice «unos 1.101 € al mes» (`hecho.coste.en_la_tarjeta`); «Dato aproximado» se explica en la ayuda de la tarjeta y en «Qué falta», no en un `title`; espacio que no se parte antes de cada «%» también en «Empatan al 94 %», la tabla de bandas, las cifras con «%», los vecinos y «Dónde invertir primero»; los hechos de la API «… el encaje se queda en la mitad» pasan a «… el % se queda en la mitad»; «SERMAS» se explica en «Qué falta»; las filas de «Los barrios que más te convienen» siguen a las de la lista.
- **Portada en el móvil:** la hoja abre desplegada, con la frase de `portada.subtitulo`, los dos ejemplos y el formulario a la vista; el mapa queda tras «Ver el mapa». En el escritorio no cambia nada de sitio (mapa primero).
- **«Cómo lo calculamos»:** el desempate dice ahora que va primero la zona que tiene **más cerca** los servicios del día a día (cuenta cada minuto andando, no cuántos servicios hay, `fit-0.9`), las bandas con sus palabras nuevas, «Casi valen», y un espacio que no se parte entre cada cifra y su «%».
- **Ejemplos de este documento** puestos al día con la respuesta de la API `fit-0.9` del 15 nov (lote 4): ya no quedan cifras de `fit-0.6` ni de `fit-0.7`.
- Entrega 2, después: la fila y la tarjeta esenciales, «Volver a la lista» y el botón atrás del móvil, y plegar la pantalla de zona.

**Fórmula «cerca y plazas» (15 nov, D-243, `fit-0.9`).** Mariano eligió la variante A del banco de fórmulas. Cambian el % y el orden; las zonas que encajan son las mismas. En el ejemplo, Puente de Vallecas y Latina empatan arriba al 94 % y encajan 42 zonas (antes, Latina 1.ª al 98 %).
- **Nuevas, de la API** (sección 4, tarjeta de zona): `hecho.limite.mitad`, `hecho.limite.no_llega`, `hecho.limite.falta` y `hecho.limite.trayecto`. Son hechos como los demás: van primero en `facts` cuando fijan el %, y solo uno.
- **De la web** (sección 4): el % con su banda, `resultados.banda.*`, en el bloque siguiente.

**Fórmula `fit-0.9` en la web (15 nov, decisiones de Mariano en F5).** La web enseña el % con su banda, dice qué zonas empatan y, en «Casi encajan», qué les falta en lugar del %. La banda es `match_band` de la API (`fit-0.9`); con una API anterior, sin el campo, sale del % con los mismos umbrales (90, 75 y 60), y solo en las zonas que cumplen todo. Hecho por B:
- **Nuevas:** `resultados.banda.*`, `resultados.empate.grupo`, `zona.empate`, `resultados.casi.*`, `resultados.aviso_2024`, `zona.precio.aviso_2024` y `resultados.sin_lugar` (sección 4).
- **Cambian:** `zona.encaje` y `zona.encaje.aria` (la banda va con el número), `zona.cerca_de_encajar.motivo` (solo si la API no da cifras) y `hecho.alquiler.referencia` (la tarjeta ya no repite «un anuncio de hoy puede pedir más»: lo dice `zona.precio.aviso_2024`). `trabajo.tarda` deja de salir: lo sustituye `resultados.casi.trayecto`.
- **«Cómo lo calculamos»:** el apartado del % sigue el método nuevo (cada minuto a pie cuenta, lo imprescindible puntúa, cercanía y plazas, suelo y cola del presupuesto, los tres topes, las bandas y el desempate «a igual %»). Los topes del trayecto van sobre la ventana del trayecto, como en la API (`trip_window`): sin límite, como mucho 74 % con más de 1 h y la mitad desde 1 h 30 (o sin llegar a las 9:00); con tu límite, el doble y el triple de tus minutos; los dos, solo si vas 3 días o más a la semana. `pitch/metodologia.md` §1.3 tiene que seguirlo (línea D).
- **«Ejemplo real» de «Cómo lo calculamos»,** con la respuesta de la API `fit-0.9` al caso de ejemplo (datos del lote 4, la misma del golden y de D-243 §9): encajan 42 de las 199 zonas (12 muy bien, 5 bien, 13 regular y 12 poco); arriba empatan Puente de Vallecas y Latina al 94 %, y va primera Puente de Vallecas porque tiene más cerca los servicios del día a día; detrás, Usera y Moratalaz (93 %), Tetuán, Ciudad Lineal y Villaverde (92 %), y Carabanchel, Coslada y Leganés (90 %). Latina pierde unos 6 puntos: 3 por los 39 min de trayecto y 1,1 por el colegio (6 min), 1,1 por la parada (2 min) y 0,9 por el centro de salud (10 min), casi todo por los minutos a pie; las plazas apenas restan y el alquiler (1.101 €, menos del 75 % de 1.500) nada. Casi encajan Chamartín, Arganzuela, Centro, Chamberí y Retiro, todas por el presupuesto, y «¿Y si cambias algo?» no cambia: +5 min al colegio, 49 zonas más; +150 €/mes, 3. Ya no dice «lo único que le quita puntos es el trayecto». `pitch/metodologia.md` §1.3 tiene que seguirlo (línea D).
- **Nombres largos en la tarjeta:** «Casarrubuelos» ya no se parte a mitad de palabra junto al %: el nombre corta solo entre palabras y, si su palabra más larga no cabe junto a la pastilla del %, la pastilla baja bajo el nombre (revisión R-02 del PR #75).

**Alquiler en los pueblos (15 nov, D-242, `fit-0.8`).** Usuarios de prueba: con «Pueblos» casi todo salía «Sin datos», y «el precio por zona no me queda claro». Donde la Comunidad no publica el alquiler (142 de los 179 municipios y el barrio de Sol), ahora sale la referencia del Ministerio de Vivienda (SERPAVI, 2024), con fiabilidad 0,7 («Dato aproximado») y el rango en el que está la mitad de los contratos. Donde la Comunidad sí lo publica, no cambia nada. Hecho por A+B:
- **Nuevas:** `zona.precio.rango` y `zona.precio.rango.aria` (sección 4), `hecho.alquiler.referencia` y `hecho.alquiler.referencia.casas` (sección 4) y `pie.mivau` (sección 10). Cambian `pie.contador` y `pie.independiente`, que suman el Ministerio de Vivienda.
- **Hasta el sync:** los textos de «Pueblos» que dan por hecho el relleno solo salen cuando `mivau_serpavi_alquiler` está en `/datasets`, como la casilla de «Ocio» (D-236); antes se quedan los de D-238.
- **Cambian:** `donde.ayuda.pueblos` (sección 2), `resultados.pueblos_sin_alquiler` y `zona.sin_alquiler` (sección 4): ya no dicen que casi ningún pueblo publica el alquiler. Solo quedan sin él los 16 municipios con tan pocas viviendas alquiladas que la fuente no publica la mediana.
- El párrafo «Alquiler» de «Cómo lo calculamos» explica el relleno.

**Pulido de experiencia (15 nov, línea B; prueba con usuarios y Mariano).** Solo pantalla: ni la API ni el ejemplo cambian.
- **Hospitales con pastillas:** `centros.hospital.pastilla`, `centros.hospital.fila` y `centros.hospital.que_significa` (sección 5b). El nombre primero, «Público» o «Privado» delante, las camas con un icono de cama y la nota plegada tras «¿Qué significa público y privado?». Cambian `centros.hospital.dependencia` y `centros.hospital.gestion_privada`.
- **Metros cuadrados editables:** `presupuesto.m2*` (sección 2) y `zona.precio.m2` (sección 4). Un usuario no veía su zona con lo que paga: el precio era para los m² de su hogar y no lo sabía. El ejemplo sigue con `min_floor_area_m2: null`.
- **«Cerca, pero no alcanza para todos»:** `zona.cerca_pocas` y `zona.falta.ayuda` (sección 4); cambia `falta.intro` (sección 5). Un usuario no se creía «100 % de encaje» con «faltan escuelas infantiles».
- **Madrid capital por barrios:** cambian `leyenda.zonas` y `mapa.aria.encaje.barrios`, y hay `mapa.aria.barrios` nueva (sección 3).
- **Un solo «Son datos informativos…»** bajo las tarjetas de contexto y de vivienda nueva (`zona.contexto.no_puntua`, `zona.vivienda_nueva.no_puntua`), y las casillas de «¿Qué ocio quieres cerca?» del mismo tamaño aunque su nombre ocupe dos líneas (línea C, 15 nov).

**Comprar en Madrid capital (14 nov, D-234, `fit-0.8`).** Dos usuarios de prueba buscaron «Comprar» y no les salió ningún distrito ni barrio de Madrid. Ahora salen, con un precio **estimado** que la web y la API dicen siempre como estimación. Ya está en la web (líneas A y B):
- **Nuevas:** `presupuesto.compra.fuente` (sección 2), `zona.compra.sin_precio`, `hecho.compra.estimado` (sección 4), `rc.sin_dato.compra` (sección 7). El párrafo «Compra» de «Cómo lo calculamos» sigue a `pitch/metodologia.md` §1.3.
- **Cambian:** `presupuesto.compra.sin_datos` (ya no vale: sustituida por `presupuesto.compra.fuente`), `rc.limite` (solo cuenta las zonas que no cumplen, no las que no tienen dato) y `rc.sin_opciones`.
- **Fiabilidad:** el precio estimado llega con fiabilidad 0,5, así que la web lo marca como «Dato aproximado» (sección 6), sin texto nuevo.
- **Precio de cada zona a la vista (prueba con usuarios):** `zona.precio.*` (sección 4). «≈ 385.000 €» o «≈ 1.101 €/mes» junto al % de cada fila, y «Comprar ≈ 385.000 €» bajo el nombre de la zona en su tarjeta. Si es una estimación, con «Dato aproximado».

**Prueba con usuarios (13 y 14 nov): lo que llega esta semana.** Lo que sigue pendiente va marcado **pendiente de A** (dato o texto de la API) **o de B** (pantalla):
- **«Tardar como mucho N min» en el trabajo:** `trabajo.max_min` y sus opciones (sección 2). En producción desde el 14 nov (PR #53, despliegue de `ad4a8f2`).
- **Paradas de autobús aparte del metro y de Cercanías:** `hecho.paradas*` (sección 4, tarjeta de zona). Sustituye al hecho de «Parada de transporte público». En producción desde el 14 nov (D-233, despliegue de `ad4a8f2` y sync).
- **El barrio que más encaja de cada distrito de Madrid, en la lista de zonas:** `resultados.barrio` (sección 4).
- **Delitos por cada 1.000 habitantes, como contexto:** `zona.delitos*` (sección 4, «Contexto de la zona»). No puntúa ni ordena, sin colores ni etiquetas, y siempre con el aviso de que se cuentan donde se denuncian (D-224 §3, D-226).
- **Antigüedad de las viviendas** (% posteriores a 2000): `zona.antiguedad*` (sección 4, «Contexto de la zona»).
- **«Entorno» de la zona: ruido de la calle, aire y aparcamientos** (D-237): `zona.entorno.*` (sección 4, «Contexto de la zona») y `centros.recuento.aparcamiento` (sección 5b). Hecho por A+B.
- **«¿Dónde?»: toda la Comunidad, Madrid capital, alrededores o pueblos** (D-238), con Madrid capital por barrios: `donde.*` (sección 2), `resultados.de.*`, `zona.barrio.*` (sección 4) y `mapa.aria.encaje.barrios` (sección 3). Hecho por A+B, en producción desde el 14 nov (despliegue de `f1b6f5a`).
- **Desempate y hospitales públicos o privados** (D-239): `resultados.empate` (sección 4) y `centros.hospital.*` (sección 5b). Hecho por A+B, en producción desde el 14 nov (despliegue de `f1b6f5a`).
- **Días de oficina y teletrabajo:** `trabajo.dias*` (sección 2, D-240). Hecho por B.
- **¿Las casas son nuevas o viejas? ¿Qué se va a construir?:** `zona.vivienda_nueva.*` (sección 4, «Vivienda nueva y lo que viene», D-241). Hecho por A+B.
- **Cerca de la familia o de amigos, como segundo lugar:** `familia.*` (sección 2, D-240). Hecho por B.
- **La lista de zonas de «Qué falta», plegada en el móvil:** `zonas.ver_todas` y `zonas.ver_menos` (sección 3). Hecho por B.
- **Ocio (bares, restaurantes, gimnasios y cultura: museos, bibliotecas, teatros y cines):** `importa.ocio*` (sección 2, «Me importa»), `hecho.ocio*` (sección 4) y `centros.ocio*` (sección 5b). Hecho por A+B el 14 nov (D-236). Los locales salen de OpenStreetMap y solo cuentan si la persona marca «Ocio».

Lo que pidieron y no entra antes del freeze (proyectos futuros y filtrar pisos por metros u obra nueva) va en las preguntas 49 y 50 de `pitch/preguntas.md`.

**Revisión de los borradores de B en el PR #32 (12 nov, noche).** Aprobados tal cual salvo lo que se indica. Todos van en la sección 5c («Dónde invertir primero», el esquema y lo demás):
- **«Dónde invertir primero»:** aprobados el título, la intro, el ranking, «Resto de zonas…», «Ver N zonas más», «El 9,8 % de toda la Comunidad, en 3 zonas.» y la frase de la cifra. Cambia la nota (`invertir.nota`): en los distritos la gente sale del padrón escalado al censo (D-209, D-216), así que «no estimamos nada» no es del todo cierto y un estadístico lo puede discutir. La misma frase sale de la página «Cómo lo calculamos».
- **Esquema de cinco pasos:** aprobado. Un cambio: el título del paso 3 va en plural, «Repartido entre quienes lo comparten».
- **`fila.zona_pequena`:** aprobados «No comparable» y su ayuda.
- **`centros.elige`:** aprobado «Toca uno o varios tipos de centro para verlos en el mapa.».
- **Frase del alquiler en «Lo que estos datos no te dicen»:** aprobada. El 5 % y el 26 % son el factor de D-228 (de 1,05 a 1,26).

**Fase de mejora (12 nov): textos para un jurado no técnico.** El jurado simulado se perdió en cinco sitios. Todo es **pendiente de B**, y lo que sale de la API, también **pendiente de A**:
- **«100 %» con JUSTO debajo:** una línea bajo el %, `encaje.aviso_*` (sección 4). Mariano decidió explicarlo, no cambiar el nombre del %.
  - **Lo que publicó B el 12 nov** (`fitsButShortText` en `gaps.ts`, borrador): «Encaja con lo que pides; aun así, en la zona van justos de: escuelas infantiles, centros de salud.». Va el texto de `encaje.aviso_*`, por tres cosas: dice con qué se compara («frente a municipios parecidos»), une la lista con «y» («escuelas infantiles y centros de salud») y no lleva dos puntos tras «de». Además, las filas de zona muy pequeña no deberían contar como justas (**pendiente de B**).
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
  - En pantalla se dice «conjunto de datos», «zonas que te convienen» y «¿Quieres ver más zonas?». «Encaje» y el % se explican en «Cómo lo calculamos» (15 nov, UX móvil 1).
- **Encaje siempre en %**, con su banda en palabras delante y hechos debajo. Nunca «92/100» ni barras (D-202).
- **Letra de 16 px o más** en todo lo que se lee para decidir y **botones de 44 px o más** (15 nov, UX móvil 1). Nada de explicaciones solo en `title`: en el móvil no se ven.
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
| `meta.description` | En qué zonas de la Comunidad de Madrid puedes vivir con tu presupuesto y con lo que necesitas cerca, y qué le falta a cada una, con datos abiertos. | **Cambia (15 nov, revisión del PR #79).** Sin «encaja» (`layout.tsx`). |
| `cabecera.nombre` | Vida Fácil | Logo de texto |
| `cabecera.lema` | Encuentra tu sitio en Madrid | |
| `pestana.mapa` | Mapa | |
| `pestana.que_falta` | Qué falta | |
| `pestana.como` | Cómo lo calculamos | Nunca «Metodología» ni «Análisis» |
| `a11y.saltar` | Saltar al contenido | Enlace oculto hasta recibir el foco |
| `portada.titulo` | Encuentra tu sitio en Madrid | Ya está así en la web de B |
| `portada.subtitulo` | Te decimos en qué zonas de la Comunidad de Madrid puedes vivir con tu presupuesto y con lo que necesitas cerca. | **Cambia (15 nov, UX móvil 1).** Dice para qué sirve (auditoría §3 C5). Antes: «Te decimos qué zonas encajan con tu vida y qué le falta a cada una, con datos oficiales.» |
| `portada.como_funciona.titulo` | Así funciona | Ya está así en la web de B |
| `portada.paso1` | **Cuéntanos cómo es tu hogar** y lo que quieres tener cerca: colegios, centro de salud, transporte… | **Cambia (15 nov, revisión del PR #79).** Antes «… y lo que te importa: colegios, salud, transporte…», como el formulario |
| `portada.paso2` | **Mira las zonas que te convienen** y por qué, con hechos que puedes comprobar. | **Cambia (15 nov, UX móvil 1).** Antes «Mira las zonas que encajan» |
| `portada.paso3` | **Entra en una zona** y mira qué le falta comparada con zonas parecidas. | Cambia el 11 nov por D-213. **Cambia (15 nov, UX móvil 1).** «frente a» pasa a «comparada con» |
| `portada.ejemplo.boton` | Ejemplo: pareja con 2 hijos que trabaja en la Castellana | Abre el caso precargado con un toque. **Cambia (15 nov, UX móvil 1).** Sin «Ver un»: los dos ejemplos caben en el móvil |
| `portada.ejemplo.mayores` | Ejemplo: pareja jubilada que quiere vivir cerca de su familia | **Nueva (15 nov, D-244).** **Cambia (15 nov, revisión del PR #79).** El diseño de Mariano: 2 personas, «Somos mayores», alquiler hasta 1.200 € al mes, «Cerca de nuestra familia» en Ciudad Lineal (la estación de metro de `/api/v1/places`, un sitio público, nunca una dirección) con 30 min como mucho y 3 días, «Madrid capital» y los tres de `hogar.somos_mayores` (`retiredExampleScenario`). Con la API `fit-0.9` del 15 nov salen 22 de los 131 barrios: Alameda de Osuna y Casco Histórico de Barajas (92 %), Ventas, Pueblo Nuevo, Quintana y San Pascual (89 %)… Antes, «… que quiere el centro de salud cerca» con 900 € y sin sitio: salían 155 zonas con pueblos pequeños arriba |
| `portada.ejemplo.ayuda` | Rellenamos la búsqueda por ti. Luego puedes cambiar lo que quieras. | Bajo los dos ejemplos. **Cambia (15 nov, UX móvil 1).** Antes «… por ti para que veas cómo funciona. …» |
| `portada.empezar` | Empezar mi búsqueda | |

---

## 2. Tarjeta «Tu búsqueda»

| Clave | Texto | Notas |
|---|---|---|
| `busqueda.titulo` | Tu búsqueda | |
| `busqueda.plegar` | Ocultar mi búsqueda | Tarjeta plegable en la pantalla de zona |
| `busqueda.desplegar` | Ver mi búsqueda | |
| `busqueda.reiniciar` | Empezar de nuevo | |
| `ayuda.que_es` | ¿Qué es esto? | **Nueva (15 nov, UX móvil 1).** Botón con aspecto de enlace (detalles nativos, 44 px) que despliega una ayuda. Sustituye a las ayudas siempre visibles del formulario y a los `title`, que en el móvil no se ven (auditoría §3 A5). El lector de pantalla oye de qué es: «¿Qué es esto? ¿Dónde?» |

### «¿Dónde?» (D-238)
Primer bloque de la tarjeta. Cuatro opciones excluyentes (radios nativos en 2 × 2, `ScenarioState.scope`). Las partes son las zonas estadísticas del Instituto de Estadística de la Comunidad de Madrid: la capital, las 4 metropolitanas y el resto. Prueba con usuarios (14 nov).

| Clave | Texto | Notas |
|---|---|---|
| `donde.titulo` | ¿Dónde? | |
| `donde.toda` | Toda la Comunidad | Por defecto. La web **no envía** `scope`, así que la búsqueda es la de siempre (el ejemplo y los enlaces compartidos no cambian) |
| `donde.madrid` | Madrid capital | Envía `scope: madrid`: compara los 131 barrios en lugar de los 21 distritos |
| `donde.alrededores` | Alrededores de Madrid | `scope: alrededores` |
| `donde.pueblos` | Pueblos | `scope: pueblos` |
| `donde.ayuda.toda` | Madrid capital por distritos y el resto de la Comunidad por municipios. | Según la opción marcada, tras «¿Qué es esto?» (desde el 15 nov; antes, línea siempre visible bajo el selector) y unida al selector con `aria-describedby` |
| `donde.ayuda.madrid` | Comparamos sus 131 barrios. | |
| `donde.ayuda.alrededores` | Los 40 municipios del área metropolitana, según el Instituto de Estadística de la Comunidad de Madrid. | Aranjuez, Valdemoro o Ciempozuelos están aquí: son del Sur Metropolitano del Instituto |
| `donde.ayuda.pueblos` | Los 138 municipios de fuera del área metropolitana, según el Instituto de Estadística de la Comunidad de Madrid. Su alquiler es la referencia del Ministerio de Vivienda, un dato aproximado; los que tienen muy pocas viviendas alquiladas salen «Sin datos». | **Cambia (D-242):** antes decía «Casi ninguno publica su alquiler…» (revisión del PR #58). Con la referencia del Ministerio, 122 de los 138 pueblos tienen alquiler; los 16 sin él tienen menos de 10 viviendas alquiladas |
| `donde.resumen` | · {opción} | Tras `hogar.resumen` y el presupuesto con la tarjeta plegada, salvo con «Toda la Comunidad» |

### «Tu hogar» («¿Quién va a vivir en la casa?» desde el 15 nov)
| Clave | Texto | Notas |
|---|---|---|
| `hogar.titulo` | ¿Quién va a vivir en la casa? | **Cambia (15 nov, UX móvil 1).** Antes «Tu hogar», con `hogar.ayuda` al lado |
| `hogar.ayuda` | ~~¿Quién va a vivir contigo?~~ | **Retirada (15 nov):** la pregunta es ahora el título |
| `hogar.solo` | Solo/a | Chip del brief |
| `hogar.pareja` | En pareja | |
| `hogar.hijos` | Con hijos | Al marcarlo aparece el contador |
| `hogar.hijos.cuantos` | ¿Cuántos hijos? | Contador de 1 a 8 (`Household.minors`, máximo 8) |
| `hogar.hijos.edades` | Edades (si quieres) | Opcional (`minor_ages`). Ayuda: «Nos sirve para saber si buscas escuela infantil o colegio.» Hoy no se muestra: las rellena el caso de ejemplo (4 y 8 años) y la web no deja cambiarlas |
| `hogar.mayores` | Con una persona mayor a la que cuidas | Al marcarlo aparece el contador. Suma una persona al hogar (`seniors_in_care`). **Cambia (15 nov, UX móvil 1).** Antes «Con mayores a cargo», que la persona mayor de la prueba leyó como su opción. Ocupa toda la fila |
| `hogar.mayores.cuantos` | ¿Cuántas personas mayores? | Contador de 1 a 4 (`seniors_in_care`, máximo 4) |
| `hogar.somos_mayores` | Somos mayores | **Nueva (15 nov, D-244).** La persona o la pareja tiene 65 años o más. No suma personas: va con «Solo/a» o «En pareja». Envía `household.seniors: true`. **Cambia (15 nov, revisión del PR #79).** Al marcarlo: se marcan «Centro de salud», «Metro o tren sin escaleras» y «Transporte», por este orden y detrás de lo que ya hubiera (todos se pueden quitar); en lugar de «Trabajo en» sale `lugar.titulo`, y «Trabajo en» pasa a «Más opciones»; si no hay ningún sitio y «¿Dónde?» está en «Toda la Comunidad», pasa a «Madrid capital» (se puede cambiar). No sale `resultados.sin_lugar` |
| `hogar.somos_mayores.ayuda` | Para personas de 65 años o más. Elige también si vives solo/a o en pareja. | **Nueva.** Bajo los botones, solo con «Somos mayores» marcado |
| `lugar.titulo` | ¿Cerca de dónde queréis vivir? (opcional) | **Nueva (15 nov, D-244, diseño de Mariano).** Solo con «Somos mayores», a la vista y donde estaba «Trabajo en». Dos opciones (`lugar.ahora`, `lugar.familia`) y el mismo buscador de sitios que el trabajo |
| `lugar.ahora` | Donde vivimos ahora | Envía un lugar `kind: other` con la etiqueta «Donde vivimos ahora», nunca el nombre del sitio elegido (en la tarjeta: «27 min en transporte público hasta Donde vivimos ahora…»). En la línea del sitio elegido: «Donde vivimos ahora: Ciudad Lineal (metro)» |
| `lugar.familia` | Cerca de nuestra familia | Envía un lugar `kind: family` con el nombre del sitio. Cambiar de opción con un sitio elegido conserva el punto y el límite |
| `lugar.buscar` | ¿Dónde vivís ahora? · ¿Dónde vive vuestra familia? | Etiqueta del buscador, según la opción |
| `lugar.ayuda` | Miramos cuánto se tarda en transporte público hasta ese sitio, llegando a las 9:00 de un día laborable, y contamos el trayecto como si fuerais 3 días a la semana. Ponemos 30 min como mucho: puedes cambiarlo o quitarlo. | Tras «¿Qué es esto?». El lugar va con `max_minutes: 30` y `days_per_week: 3`; «Tardar como mucho» (`trabajo.max_min`) deja cambiarlo. El selector se llama «Tardar como mucho hasta donde vivimos ahora, en transporte público» o «… hasta mi familia o amigos, …» |
| `hogar.contador.menos` | Quitar uno | `aria-label` del botón «−» |
| `hogar.contador.mas` | Añadir uno | `aria-label` del botón «+» |
| `hogar.resumen` | {n} personas en casa | Resumen cuando la tarjeta está plegada |

### «¿Qué quieres tener cerca?» (antes «Me importa», D-204)
Se pueden marcar varios. El orden en que se marcan es el orden de importancia (`priorities`, la más importante primero). Desde el 15 nov las ayudas van en una lista tras «¿Qué es esto?» («Transporte: Paradas cerca de casa…»), no al pasar el ratón.

| Clave | Chip | Ayuda (tras «¿Qué es esto?») | Notas |
|---|---|---|---|
| `importa.titulo` | ¿Qué quieres tener cerca? | Toca primero lo más importante: cuenta más. | **Cambia (15 nov, UX móvil 1).** Antes «Me importa» y «Marca lo que más te importa. Lo primero que marques cuenta más.» (auditoría §4 n.º 20) |
| `importa.transporte` | Transporte | Paradas cerca de casa y con autobuses o trenes a menudo. | |
| `importa.salud` | Centro de salud | Centro de salud cerca de casa. | **Cambia (15 nov, UX móvil 1).** Antes «Salud»: que era el centro de salud solo lo decía un `title`. Se marca con «Somos mayores» (D-244), con «Metro o tren sin escaleras» y «Transporte» |
| `importa.colegios` | Colegios | Colegios con primaria, públicos o concertados, cerca de casa. | Los mismos que cuenta la fila de colegios (GAP-001 F2) |
| `importa.zonas_verdes` | Zonas verdes | Parques de una hectárea o más, cerca de casa. | Cambia el 12 nov: los jardines pequeños no cuentan (D-222 §2). En la API desde `fit-0.3`, desplegado el 12 nov, con el hecho «Parque urbano a N min andando desde la mitad de sus calles». En la web desde el 12 nov (chip «Zonas verdes», icono de árboles) |
| `importa.seguridad` | — | — | **No hay chip** (D-224): la tasa oficial de hechos conocidos cuenta dónde se denuncia, no dónde se vive, y solo cubre 36 de las 199 zonas. No se promete en `importa.pronto_lista`. La explicación va en «Cómo lo calculamos» (`metodologia.md` §1.8). Mariano abrió la opción de D-224 §3 el 14 nov (D-235): va como contexto en la vista de zona (`zona.contexto.delitos`), nunca como chip. Hecho de la API para la prioridad (D-226 §5): «Seguridad: no la puntuamos (no hay un dato oficial que la mida para quien vive en cada zona)» |
| `zona.seguridad_vecinos` | Así valoran sus vecinos la seguridad de su barrio: {noche} de noche y {dia} de día, de 0 a 10 (en todo Madrid, {noche_madrid} y {dia_madrid}). Encuesta de calidad de vida del Ayuntamiento de Madrid, {año}, unas 400 personas por distrito. | Solo en los 21 distritos de Madrid, como contexto en la vista de zona (D-226 §1): sin colores de estado ni de alarma, y nunca «peligroso» ni «inseguro». No puntúa, no ordena y no entra en «Qué falta». Valores de `seguridad_percibida_noche` y `seguridad_percibida_dia` (`GET /features/{id}/values`); la referencia es la fila de la ciudad (28079). Con una coma decimal: «6,4». **Pendiente de B** |
| `zona.contexto.titulo` | Otros datos de la zona | Tarjeta de contexto de la vista de zona (D-235), debajo de `zona.seguridad_vecinos`. Tres líneas cortas, cada una con su fuente y su año, en tinta normal: sin colores de estado ni de alarma, sin ranking y sin comparar zonas. Una línea cuyo dato la API no tiene todavía no sale; sin ninguna, no sale la tarjeta |
| `zona.contexto.no_puntua` | Son datos informativos: no cambian qué zonas te convienen ni su orden. | **Cambia (15 nov, UX móvil 1).** Antes «… no cambian el encaje ni el orden de las zonas.». Pie de la tarjeta. **Cambia el 15 nov:** con la tarjeta de vivienda nueva debajo (D-241), sale una sola vez, bajo la última de las dos |
| `zona.contexto.delitos` | Infracciones penales conocidas: {tasa} por cada 1.000 habitantes (Ministerio del Interior, vía Instituto de Estadística de la Comunidad de Madrid, {año}). | Municipios de más de 20.000 habitantes. {tasa} con un decimal: criminalidad convencional, el total menos la cibercriminalidad (D-224 §3), sobre los vecinos del mismo año. Nunca «delincuencia», «peligroso» ni «inseguro» |
| `zona.contexto.delitos.aviso` | Mide hechos conocidos por la policía, sin los delitos por internet; sube donde hay mucha gente de paso. | Debajo de la cifra, siempre que hay cifra |
| `zona.contexto.delitos.ciudad` | Dato de toda la ciudad de Madrid; no se publica por distrito. | A continuación de `zona.contexto.delitos` en los 21 distritos (y en el barrio elegido), con la cifra de Madrid |
| `zona.contexto.delitos.sin_dato` | Infracciones penales conocidas: sin dato. El Ministerio solo lo publica para municipios de más de 20.000 habitantes. | Los demás municipios. Nunca 0 |
| `zona.contexto.antiguedad.municipio` | Viviendas construidas desde 2001: {pct} % (censo anual de la Comunidad de Madrid, {año}). | Solo municipios. {pct} con un decimal y un espacio de no separación antes de «%» (no se parte al final de la línea). Sin dato: «Viviendas construidas desde 2001: sin dato.» |
| `zona.contexto.antiguedad.madrid` | Año medio de construcción de los edificios de viviendas: {año_medio} (Catastro, {año}). | Solo distritos de Madrid; con un barrio elegido en el mapa, «… de viviendas en {barrio}: …». {año_medio} sin punto de millar. No es comparable con el % de los municipios: nunca en la misma escala ni con la misma etiqueta |
| `zona.contexto.renta.municipio` | Renta disponible bruta por persona: {importe} € al año (Instituto de Estadística de la Comunidad de Madrid, {año}). | Solo municipios. Nunca «zona rica» ni «zona pobre»: es una cifra con su fuente |
| `zona.contexto.renta.madrid` | Renta neta media por hogar: {importe} € al año (Instituto Nacional de Estadística, panel del Ayuntamiento de Madrid, {año}). | **Cambia (15 nov, UX móvil 1).** Sin siglas (antes «INE»). Solo distritos de Madrid; con un barrio elegido, «Renta neta media por hogar en {barrio}: …». Es la renta neta media por hogar de Urban Audit, del panel del Ayuntamiento: no es comparable con la renta por persona de los municipios |
| `importa.sin_escaleras` | Metro o tren sin escaleras | Estación de metro o tren accesible (sin escaleras) según el Consorcio Regional de Transportes, cerca de casa. | **Cambia (15 nov, UX móvil 1).** El botón dice qué mide (antes «Sin escaleras») y la ayuda, sin siglas (antes «según el CRTM»). Opcional y sin marcar (D-204, D-223). Definitiva el 12 nov (PR #26 de B). Icono: `TrainFront`, no la silla de ruedas. Hechos de la API: «Estación de metro o tren accesible (sin escaleras) a N min andando desde la mitad de sus calles» y «Sin estación de metro o tren accesible a un paseo (no mide autobuses, aceras ni portales)». En producción desde el 12 nov (despliegue de `2761696`). El icono, **pendiente de B** |
| `importa.ocio` | Ocio | Bares, restaurantes, gimnasios y cultura (museos, bibliotecas, teatros y cines) cerca de casa: tú eliges cuáles. | Nuevo el 14 nov (D-236, feedback de usuarios de prueba; la cultura, a petición de un usuario de prueba). Icono: `Wine`. Solo sale cuando los datos de ocio están publicados (`osm_ocio` en `/datasets`). Al marcarlo se abre el bloque de abajo, con «Bares y cafeterías» y «Restaurantes» ya marcados |
| `importa.ocio.titulo` | ¿Qué ocio quieres cerca? | Título del bloque que se abre bajo los chips | |
| `importa.ocio.bares` | Bares y cafeterías | Casilla | Bares, pubs y cafeterías |
| `importa.ocio.restaurantes` | Restaurantes | Casilla | La comida rápida no cuenta |
| `importa.ocio.gimnasios` | Gimnasios y deporte | Casilla | Gimnasios y centros deportivos, también los polideportivos municipales |
| `importa.ocio.cultura` | Cultura | Casilla | Museos, bibliotecas, teatros, cines y centros culturales. Antes «Cines y teatros» (14 nov) |
| `importa.ocio.cultura.ayuda` | Cultura: museos, bibliotecas, teatros, cines y centros culturales. | Línea pequeña bajo las casillas | Siempre visible: dice qué cuenta como cultura |
| `importa.ocio.minutos` | A [{n}] min andando como mucho | Los minutos son un selector dentro de la frase (5, 10 o 15), como en `cerca.item`. Valen para todas las casillas marcadas | `aria-label` del selector: «Minutos andando hasta el ocio» |
| `importa.ocio.obligatorio` | Solo zonas que lo tengan | Casilla, **sin marcar al principio** («Me importa» ordena, no filtra, y en los pueblos OSM no tiene todos los locales). Ayuda: «Si lo marcas, solo verás zonas que lo cumplen.» | **Cambia (15 nov, UX móvil 1).** Antes «Imprescindible», que se explicaba en un `title`. Como `cerca.obligatorio`. Sin marcar, el ocio solo sube o baja el % |
| `importa.ocio.ninguna` | Marca al menos una casilla para que el ocio cuente. | Si no hay ninguna casilla marcada | Sin casillas, el ocio no puntúa |
| `importa.ocio.fuente` | Según OpenStreetMap, un mapa hecho por voluntarios: en los pueblos pequeños puede faltar algún local. | Línea pequeña al final del bloque | La cobertura está en D-236 |
| `importa.pronto` | Muy pronto | Etiqueta pequeña del chip desactivado. Ayuda: «Estamos añadiendo estos datos.» | |
| `importa.pronto_lista` | — | Línea bajo los chips | **Ya no sale** (12 nov): la web enseña el chip de zonas verdes y la seguridad no se promete (D-224) |
| `importa.orden` | Lo más importante para ti: {lista} | Resumen con la tarjeta plegada |

### «Trabajo en»
| Clave | Texto | Notas |
|---|---|---|
| `trabajo.titulo` | Trabajo en (opcional) | **Cambia (15 nov, UX móvil 1).** «(opcional)», como la familia (auditoría §3 C4). Con «Somos mayores» va plegado en «Más opciones» y en su sitio sale `lugar.titulo` (D-244). La lista de lugares se sigue llamando «Trabajo en» |
| `trabajo.placeholder` | Escribe una estación, un distrito o un municipio | Sin calles: no hay búsqueda de calles sin un geocodificador externo. Los lugares son las estaciones del CRTM (`/places`) y las zonas del mapa |
| `trabajo.ayuda` | Miramos cuánto tardarías en llegar a las 9:00 en transporte público: metro, autobús, Cercanías y Metro Ligero. | **Cambia (15 nov, UX móvil 1).** Sin siglas (antes «autobús (EMT e interurbanos)») y tras «¿Qué es esto?». **Cambia el 14 nov** (feedback de usuarios de prueba: uno se mueve en autobús y no sabía que el trayecto lo cuenta). Antes: «Miramos cuánto tardarías en transporte público para llegar a las 9:00.» La lista sale del cálculo (`services/features/src/hi_features/commute.py`): usa los seis GTFS del CRTM (metro, Cercanías, Metro Ligero, EMT, interurbanos y urbanos de otros municipios), más el paseo hasta la parada |
| `trabajo.dias` | ¿Cuántos días vas a la oficina? | **Activo el 14 nov** (D-240, feedback de usuarios de prueba). Selector bajo el lugar de trabajo, con las opciones de `trabajo.dias.opcion`. Envía `days_per_week`; hasta que la persona lo cambia no se envía y vale 5. El caso de ejemplo va 4 días y sus cifras no cambian: desde 3 días el trayecto pesa como siempre. Antes: «¿Cuántos días vas a la semana?», sin mostrarse |
| `trabajo.dias.opcion` | 5 días · 4 días · 3 días · 2 días · 1 día · Teletrabajo total | «Teletrabajo total» envía `days_per_week: 0`. Un enlace compartido con 6 o 7 días también los ofrece |
| `trabajo.dias.pocos` | Como vas pocos días, el trayecto cuenta la mitad. | Bajo el selector, con 1 o 2 días: el trayecto pesa la mitad en el % (D-240) |
| `trabajo.dias.teletrabajo` | Con teletrabajo total, el trayecto no cuenta para ordenar las zonas. Si pones un límite, lo respetamos. | **Cambia (15 nov, UX móvil 1).** Antes «… no cuenta en el encaje. …». Bajo el selector, con «Teletrabajo total»: el trayecto no puntúa, pero `trabajo.max_min` se sigue aplicando (D-240). Con límite, la tarjeta enseña los minutos como dato, sin peso. Las dos ayudas de los días van unidas al selector con `aria-describedby` |
| `trabajo.max_min` | Tardar como mucho [{n}] min en transporte público | **Activo el 14 nov** (feedback de usuarios de prueba: «me salían sitios muy lejos»). Los minutos son un selector dentro de la frase, como en `cerca.item`: «Sin límite» (por defecto, envía `max_minutes: null`), «30 min», «45 min», «60 min» y «90 min». Solo sale cuando hay un lugar de trabajo, también con «Teletrabajo total» (D-240). Con límite, cada zona sale cumple, no cumple o sin dato (CORE-009, D-220 §8). El ejemplo de la portada va siempre sin límite: sus cifras son las del pitch |
| `trabajo.max_min.aria` | Tardar como mucho hasta el trabajo, en transporte público | `aria-label` del selector. **Cambia el 14 nov** (revisión del PR #60): nombra el lugar, como `familia.max_min.aria`. Antes: «Tardar como mucho, en transporte público». El e2e y `check-search` buscan este texto |
| `trabajo.sin_limite` | Sin límite | **Nueva, 14 nov** (feedback de usuarios de prueba). Primera opción del selector de `trabajo.max_min` |
| `trabajo.tarda` | {condición} (tardarías {n} min) | **Deja de salir (15 nov, F5 de `fit-0.9`):** lo sustituye `resultados.casi.trayecto` («Tarda ≈ 12 min más de lo que pides»). **Nueva, 14 nov** (feedback de usuarios de prueba). Va en «Casi encajan» y en «No cumple:» de la tarjeta de zona cuando falla el trayecto: «Trayecto a Paseo de la Castellana (Azca) de 45 min como mucho (tardarías 46 min)». Los minutos son los del hecho de la API (al minuto más cercano), salvo que nunca se leen como el propio límite (45,2 contra 45 sale «46 min»); por encima de 120, «más de 2 h» |
| `trabajo.transporte_pronto` | Tiempo en transporte: muy pronto | Etiqueta pequeña bajo el campo. **Se quita** cuando `fit-0.2` llegue a producción: el tiempo en transporte ya está calculado (D-220) |
| `trabajo.sin_resultados` | No encontramos ese lugar. Prueba con una estación o con el nombre del municipio. | |
| `trabajo.encontrados` | {n} lugares encontrados. Usa las flechas para elegir uno. | Región viva del combobox. Con 1: «1 lugar encontrado. Usa las flechas para elegirlo.» |
| `trabajo.lugar.estacion` | {estación} ({tipo}) | {tipo}: «metro», «Cercanías» o «Metro Ligero». Por ejemplo, «Nuevos Ministerios (metro)» |
| `trabajo.lugar.distrito` | {distrito} (Madrid) | Por ejemplo, «Chamartín (Madrid)». Los municipios van solo con su nombre |
| `trabajo.quitar` | Quitar este lugar | |

### «Cerca de mi familia o amigos» (D-240)
Segundo lugar, opcional, en «Más opciones» desde el 15 nov. Con «Somos mayores» no sale: la familia va en `lugar.familia`. Es el mismo campo: estaciones y zonas, con `trabajo.placeholder`, `trabajo.sin_resultados`, `trabajo.encontrados`, `trabajo.lugar.*` y `trabajo.quitar`. Sin días: cuenta como un lugar al que se va a menudo.

| Clave | Texto | Notas |
|---|---|---|
| `familia.titulo` | Cerca de mi familia o amigos (opcional) | **Cambia (15 nov, UX móvil 1).** En «Más opciones».  **Nueva, 14 nov** (idea de Mariano y feedback de usuarios de prueba). Envía un lugar `kind: "family"`, siempre detrás del trabajo |
| `familia.ayuda` | Miramos cuánto tardarías en transporte público llegando a las 9:00 de un día laborable. | **Cambia (15 nov, UX móvil 1).** Sin «Opcional.», que ya dice el título, y tras «¿Qué es esto?». Se mide como el trabajo, y el texto lo declara porque a la familia se suele ir a otras horas (revisión del PR #60). El hecho de la tarjeta lo dice también: «28 min en transporte público hasta Getafe Central (Cercanías), llegando a las 9:00». Antes: «Opcional. Miramos cuánto tardarías en llegar en transporte público.» |
| `familia.max_min` | Tardar como mucho [{n}] min en transporte público | Como `trabajo.max_min`, con su propio límite y «Sin límite» por defecto. Si falla, va con `trabajo.tarda`: «Trayecto a Getafe Central (Cercanías) de 30 min como mucho (tardarías {n} min)» |
| `familia.max_min.aria` | Tardar como mucho hasta mi familia o amigos, en transporte público | `aria-label` del selector, distinto del del trabajo |

### «Lo quiero a un paseo»
`ScenarioState.nearby`: servicios a un paseo. El caso de ejemplo pide colegio a 10 min andando como mucho, imprescindible. Desde el 15 nov va plegado en «Más opciones».

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
| `cerca.servicio.transporte` | Parada de autobús o metro | **Cambia (15 nov, UX móvil 1).** Antes «Parada de transporte público» (auditoría §4 n.º 23) |
| `cerca.anadir` | Añadir un servicio… | Primera opción del selector |
| `cerca.anadir.aria` | Añadir un servicio a un paseo | `aria-label` del selector |
| `cerca.quitar` | Quitar {servicio} | Con {servicio} en minúscula: «Quitar colegio» |
| `cerca.obligatorio` | Solo zonas que lo tengan | Interruptor (`required`), marcado al añadir un servicio, como antes. **Cambia (15 nov, UX móvil 1).** Antes «Imprescindible», con su ayuda («Si lo marcas, solo verás zonas que lo cumplen.») en un `title`; la ayuda sigue para el lector de pantalla |

### «Más opciones» (15 nov, UX móvil 1)
Plegado bajo el presupuesto (auditoría, opción 1): lo que menos gente necesita. Nada se pierde: el botón dice qué hay dentro y cuántas cosas tiene elegidas, y «Dinos dónde» (`resultados.sin_lugar`) lo abre si hace falta.

| Clave | Texto | Notas |
|---|---|---|
| `mas.titulo` | Más opciones | Botón (detalles nativos) |
| `mas.que_hay` | Servicios a un paseo, familia o amigos y tamaño del piso | Bajo el título. Con «Somos mayores»: «Trabajo, servicios a un paseo y tamaño del piso» (la familia va en `lugar.*`) |
| `mas.elegidas` | · {n} elegidas | Detrás de `mas.que_hay` si hay algo elegido dentro: servicios a un paseo, familia, metros elegidos y, con «Somos mayores», el trabajo en lugar de la familia. Con 1: «· 1 elegida» |

### Presupuesto (D-203)
| Clave | Texto | Notas |
|---|---|---|
| `presupuesto.titulo` | Presupuesto | |
| `presupuesto.alquilar` | Alquilar | Selector de dos opciones |
| `presupuesto.comprar` | Comprar | |
| `presupuesto.alquiler.valor` | Hasta {importe} € al mes | Rango del slider: 100–20.000 € (`RENT_RANGE_EUR`) |
| `presupuesto.compra.valor` | Hasta {importe} € | Rango del slider: 10.000–5.000.000 € (`BUY_RANGE_EUR`) |
| `presupuesto.importes` | 600 € · 900 € · 1.200 € · 1.500 € · Otra cantidad (alquilar); 150.000 € · 250.000 € · 400.000 € · 600.000 € · Otra cantidad (comprar) | **Nueva (15 nov, UX móvil 1, auditoría A1).** Botones de opción bajo «Alquilar/Comprar» (`QUICK_BUDGETS` en `lib/scenario.ts`); el grupo se llama «¿Hasta cuánto al mes?» o «¿Hasta cuánto?». El deslizador se queda y mueve la misma cifra. «Comprar» empieza en 250.000 € (antes 300.000 €), uno de los botones |
| `presupuesto.otra` | Escribe la cantidad, en euros al mes · Escribe la cantidad, en euros | **Nueva.** Etiqueta del campo que sale con «Otra cantidad». Acepta «900», «1.250» o «1 250 €» y lo envía tal cual, sin redondear al paso del deslizador |
| `presupuesto.compra.etiqueta` | Orientativo | Etiqueta junto al importe de compra, siempre visible |
| `presupuesto.compra.ayuda` | No hay un precio oficial de compra por zona tan completo como el del alquiler. Lo usamos solo como orientación. | |
| `presupuesto.compra.sin_datos` | ~~Aún no tenemos precios oficiales de compra por zona, así que no podemos comprobar si entra en tu presupuesto.~~ | **Retirada** (D-227, D-234): ya hay precio en 28 municipios y una estimación en los distritos y barrios de Madrid. La sustituye `presupuesto.compra.fuente` |
| `presupuesto.compra.fuente` | Precio de compra: el valor tasado medio de la vivienda libre (Ministerio de Vivienda), que solo se publica por municipio y en los de más de 25.000 habitantes. En los distritos y barrios de Madrid, el precio que veas es una estimación: el valor tasado de Madrid repartido según el valor catastral de cada zona. Donde no hay precio, no podemos comprobar tu presupuesto. | **Nueva (D-234).** Tras «¿Qué es esto?» (desde el 15 nov), con «Comprar» elegido (`buySource` en `SearchCard.tsx`) |
| `presupuesto.sin_limite` | Sin límite de presupuesto | Opción del slider (`budget: null`) |
| `presupuesto.slider.aria` | Presupuesto máximo | `aria-label` |
| `presupuesto.fuera_rango.alquiler` | Escribe una cantidad entre 300 y 5.000 € al mes. | Bajo «Otra cantidad» si lo escrito no vale. **Cambia (15 nov, UX móvil 1).** El rango del deslizador, no el del contrato (antes «El alquiler tiene que estar entre 100 y 20.000 € al mes.», que no se enseñaba) |
| `presupuesto.fuera_rango.compra` | Escribe una cantidad entre 50.000 y 2.000.000 €. | Igual al comprar. **Cambia (15 nov, UX móvil 1).** |
| `presupuesto.m2` | Los precios son para un piso de unos {m2} metros cuadrados. | **Cambia (15 nov, UX móvil 1).** En «Más opciones», bajo el selector `presupuesto.m2.etiqueta`. Antes, una línea bajo el presupuesto, «Para unos {m2} m² (cámbialo)», que abría el selector (prueba con usuarios del 15 nov). Sin «unos» si la persona eligió los metros. {m2} son los que la API supone para el hogar con `min_floor_area_m2: null` (D-214: 61, 68, 71 y 77 m² para 1, 2, 3 y 4 o más personas) |
| `presupuesto.m2.etiqueta` | Tamaño del piso | Etiqueta del selector. **Cambia (15 nov, UX móvil 1).** Antes «Metros cuadrados» |
| `presupuesto.m2.normal` | Lo normal para tu hogar ({m2} m²) | Primera opción: vuelve a `min_floor_area_m2: null` |
| `presupuesto.m2.opcion` | {m2} m² | De 40 a 150 m², de 5 en 5. Un enlace compartido con otro valor también lo ofrece |
| `presupuesto.m2.ayuda` | Lo normal para tu hogar es la superficie habitual de las viviendas de hogares como el tuyo en la Comunidad de Madrid (Censo 2021): la mitad tiene menos metros y la otra mitad, más. El precio de cada zona es para estos metros. | Tras «¿Qué es esto?» (desde el 15 nov), unida al selector con `aria-describedby`. Es la mediana del Censo, no la superficie más frecuente (revisión del PR #70) |
| `presupuesto.m2.resumen` | · {m2} m² | Con la tarjeta plegada, tras el presupuesto, solo si la persona eligió los m² |

### Botón principal
| Clave | Texto |
|---|---|
| `busqueda.boton` | Buscar zonas para mí (desde el 15 nov; antes «Ver zonas que encajan») |
| `busqueda.boton.cargando` | Buscando zonas… |

### Si el buscador se apaga
Producción tiene el buscador encendido desde el 11 nov (`NEXT_PUBLIC_FEATURE_SEARCH=true`, `apps/web/src/lib/capabilities.ts`; `evidence/gate-06/2026-11-11-deploy/deploy-12-buscador.md`, PR #11). Estos textos solo salen en dos casos:
- si C vuelve a una versión sin buscador;
- en el paquete sin red (`make demo-offline`), que compila la web sin ninguna variable `NEXT_PUBLIC_*` salvo la URL de la API (`infra/deploy/offline/demo_offline.sh`).

| Clave | Texto | Notas |
|---|---|---|
| `busqueda.pronto` | Muy pronto podrás ver qué zonas te convienen. Mientras, toca una zona del mapa para ver qué le falta. | En la tarjeta «Tu búsqueda», en lugar del botón. **Cambia (15 nov, UX móvil 1).** Antes «… qué zonas encajan contigo. …» |
| `leyenda.pronto` | Muy pronto verás aquí qué zonas te convienen. | Leyenda del mapa. **Cambia (15 nov, UX móvil 1).** |

---

## 3. Mapa

| Clave | Texto | Notas |
|---|---|---|
| `mapa.aria` | Mapa de la Comunidad de Madrid por municipios, con Madrid capital dividida en sus 21 distritos. | `aria-label` del lienzo (D-200) |
| `mapa.alternativa` | Ver las zonas en una lista | Enlace siempre visible para quien no use el mapa |
| `leyenda.titulo` | Zonas que te convienen | También es la primera opción de «¿Qué quieres ver?». **Cambia (15 nov, UX móvil 1).** Antes «Encaje con tu búsqueda» |
| `leyenda.menos` | Te conviene menos | Extremo claro. **Cambia (15 nov, UX móvil 1).** Antes «Encaja menos» |
| `leyenda.mas` | Te conviene más | Extremo violeta. **Cambia (15 nov, UX móvil 1).** Antes «Encaja más» |
| `leyenda.sin_datos` | Sin datos | Gris con borde discontinuo (`match_pct: null` nunca es 0) |
| `leyenda.antes_de_buscar` | Haz tu búsqueda para ver qué zonas te convienen. | Antes del primer resultado. **Cambia (15 nov, UX móvil 1).** También en la tarjeta de una zona antes de buscar |
| `leyenda.cumple` | Cumple todo | Tras buscar: zonas con todas las condiciones en PASS |
| `leyenda.no_cumple` | No cumple todo | Falla alguna condición |
| `leyenda.zonas` | {n} zonas | Junto a cada clase. Con 1: «1 zona». **Cambia el 15 nov:** con «¿Dónde?» va la palabra del ámbito, como en la lista: «Cumple todo 78 barrios», «34 municipios», «2 pueblos» (D-238) |
| `leyenda.ver` | ¿Qué quieres ver? | Selector del mapa (decisión de datamad-10). Opciones: «Zonas que te convienen» (`leyenda.titulo`) y los nombres de las 6 filas (sección 5). **Cambia (15 nov, revisión del PR #79).** |
| `leyenda.fila.frente` | comparado con los municipios de su tipo (urbanos o rurales); los pueblos muy pequeños, junto con sus vecinos. | **Cambia (15 nov, UX móvil 1).** «frente a» pasa a «comparado con» (auditoría §4 n.º 11). Tras la definición de la fila elegida. Con los vecinos de gap-0.3 (D-217 §6): definitivo el 12 nov |
| `leyenda.sin_calcular` | {n} zonas sin calcular todavía. | Con 1: «1 zona sin calcular todavía.» |
| `leyenda.nivel_caido` | No hemos podido cargar {los municipios \| los distritos de Madrid}: salen sin calcular. | Con «Reintentar» |
| `leyenda.barrios_caidos` | No hemos podido cargar los barrios de Madrid: la capital sale sin pintar. | Con «Reintentar», tras buscar con «Madrid capital» si fallan los contornos de los barrios (D-238). La siguiente búsqueda por barrios los vuelve a pedir |
| `leyenda.lista` | Ver estas zonas en una lista | Abre `/zonas?fila=…` |
| `mapa.aria.encaje` | Cada zona tiene un color según lo que te conviene; la leyenda lo explica y la lista de zonas que te convienen está junto al mapa. | `aria-label` del mapa tras buscar. **Cambia (15 nov, UX móvil 1).** |
| `mapa.aria.barrios` | Mapa de la Comunidad de Madrid por municipios, con Madrid capital dividida en sus barrios. | **Nueva, 15 nov.** Sustituye a `mapa.aria` cuando el mapa pinta los barrios de Madrid capital tras buscar con «Madrid capital». Antes decía «dividida en sus 21 distritos» y después «sale por barrios» |
| `mapa.aria.encaje.barrios` | Cada barrio tiene un color según lo que te conviene y el resto de la Comunidad queda sin pintar; la leyenda lo explica y la lista de barrios que te convienen está junto al mapa. | **Cambia (15 nov, UX móvil 1).** `aria-label` del mapa tras buscar con «Madrid capital» (D-238), detrás de `mapa.aria.barrios`. **Cambia el 15 nov:** ya no empieza por «Madrid capital sale por barrios», que lo dice `mapa.aria.barrios`. Mientras no han cargado los contornos de los barrios (o si fallan), el mapa enseña los distritos sin pintar: van `mapa.aria` y nada más |
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
| `movil.hoja.tirador` | Toca aquí para ver más | Hoja inferior plegada en el móvil. **Cambia (15 nov, UX móvil 1).** Un toque, no un gesto (antes «Desliza hacia arriba para ver más», auditoría §4 n.º 37). La portada abre con la hoja desplegada: lo primero es la búsqueda |
| `movil.hoja.mapa` | Ver el mapa | Botón que pliega la hoja y deja el mapa a la vista. **Cambia (15 nov, UX móvil 1).** En la portada del móvil es lo primero que se ve, sobre la frase y los ejemplos |
| `zonas.buscar` | Busca una zona | Lista de zonas (alternativa al mapa y elección de zona en «Qué falta») |
| `zonas.distritos` | Distritos de Madrid | Grupo de la lista |
| `zonas.municipios` | Municipios | Grupo de la lista |
| `zonas.ninguna` | No hay ninguna zona con ese nombre. | Búsqueda sin resultados |
| `zonas.ver_todas` | Ver las {n} zonas | **Nueva, 14 nov** (feedback de usuarios de prueba: en el móvil, la lista de «Qué falta» era larguísima). Solo en «Qué falta» sin zona: los distritos y municipios van plegados tras este botón, como `resultados.primeras`. {n} = distritos + municipios (199). «Madrid (toda la ciudad)» sigue a la vista y, al escribir un nombre, sus zonas salen aunque la lista esté plegada. `/zonas` no se pliega |
| `zonas.ver_menos` | Ver menos | El mismo botón con la lista abierta |
| `zonas.ciudad_entera` | {ciudad} (toda la ciudad) | «Madrid (toda la ciudad)»: lleva a su lista de «Qué falta». En el mapa, Madrid capital son sus distritos |
| `zonas.titulo` | Todas las zonas | Página `/zonas` |
| `zonas.fila.intro` | Con su estado en {fila} frente a los municipios de su tipo: FALTA, JUSTO, CUBIERTO o SIN DATOS. Los pueblos muy pequeños se comparan junto con sus vecinos. | `/zonas?fila=…`, con {fila} en minúscula. Definitivo el 12 nov, con los vecinos de gap-0.3 |
| `carga.estado_zonas` | Cargando el estado de cada zona… | Lista de zonas con una fila elegida |

---

## 4. Zonas que te convienen y tarjeta de zona

### Lista «Zonas que te convienen» (antes «Zonas que encajan»)
Columna derecha tras buscar, mientras no hay una zona elegida. En el móvil va en la hoja inferior.

| Clave | Texto | Notas |
|---|---|---|
| `resultados.titulo` | Zonas que te convienen | **Cambia (15 nov, UX móvil 1).** Antes «Zonas que encajan» (auditoría §4 n.º 1) |
| `resultados.de` | Hemos mirado las {n} zonas de la Comunidad de Madrid. | Bajo `rc.varias` («Hemos encontrado 42 zonas para ti.»). {n} = `zones_evaluated` (hoy 199). Con «Toda la Comunidad». **Cambia (15 nov, UX móvil 1).** Antes «De {n} zonas de la Comunidad de Madrid.» |
| `resultados.de.madrid` | Hemos mirado los {n} barrios de Madrid capital. | Con «Madrid capital» (D-238): {n} = 131 |
| `resultados.de.alrededores` | Hemos mirado los {n} municipios de los alrededores de Madrid. | {n} = 40 |
| `resultados.de.pueblos` | Hemos mirado los {n} pueblos de la Comunidad de Madrid. | {n} = 138 |
| `resultados.barrio_fila` | {barrio} · {distrito} | Con «Madrid capital», cada fila de la lista; debajo, «Barrio de Madrid» (`zona.barrio.antetitulo`) en lugar de «Distrito de Madrid». El distrito sale del código del barrio |
| `resultados.pueblos_sin_alquiler` | {n} de los {total} pueblos salen «Sin datos», sobre todo porque tienen tan pocas viviendas alquiladas que no se publica su alquiler: no podemos comprobar tu presupuesto. | Bajo `resultados.de` con «Pueblos», presupuesto de alquiler y alguna zona sin datos (`zones_unknown`). Con 1: «1 de los 138 pueblos sale…». Sustituye a `rc.sin_dato` en ese bloque. Revisión del PR #58. **Cambia (D-242):** antes decía que el alquiler solo se publica en los municipios de más de 20.000 habitantes. Ejemplo real, pareja con 1.500 €: «16 de los 138 pueblos salen…» |
| `resultados.primeras` | Ver las {n} primeras | Se ven 5 y el botón abre hasta 10 |
| `resultados.menos` | Ver menos | |
| `resultados.resto` | Y {n} zonas más en el mapa. | Con 1: «Y 1 zona más en el mapa.» Con «¿Dónde?» va la palabra del ámbito: «Y 3 barrios más en el mapa.» (D-238) |
| `resultados.barrio` | Barrio que más te conviene: {barrio} ({pct} %) | Segunda línea de cada distrito de Madrid en la lista, bajo su nombre. Sale del mismo cálculo que «Los barrios que más te convienen» (D-232). Con empate: «Barrios que más te convienen: {a}, {b} y {c} ({pct} %)», y con más de tres, «{a}, {b} y {n} más». Con `fit-0.9` (API del 15 nov, lote 4), San Blas-Canillejas con el caso de ejemplo tiene cinco barrios empatados al 89 %: Arcos, Canillejas, Amposta, Simancas y Rosas. Si ningún barrio cumple todo, no va la línea. Los municipios no la llevan. En pantalla nunca «ranking» ni «el mejor barrio»: es el que más se parece a lo que buscas, no una nota del barrio. Prueba con usuarios (14 nov). **Pendiente de A** (que `/search` lo devuelva, o una llamada por distrito) **y de B** |
| `zona.precio.compra` | ≈ {importe} € | **Nueva (D-234, prueba con usuarios del 14 nov: «si tuviera un precio aproximado por zona, se entendería mejor»).** Junto al % de cada fila de «Zonas que te convienen», «Casi valen» y «Los barrios que más te convienen», al comprar (nombres del 15 nov). {importe} = `estimated_cost_eur` (precio para los m² del hogar, el mismo del hecho de la tarjeta). Sin precio, no va nada: el aviso `rc.sin_dato.compra` ya dice por qué |
| `zona.precio.alquiler` | ≈ {importe} €/mes | **Nueva (D-234).** Igual, al alquilar o sin límite de presupuesto (alquiler mensual de los m² del hogar) |
| `zona.precio.m2` | por {m2} m² | **Nueva, 15 nov.** Bajo la cifra de cada fila y detrás de la de la tarjeta: «Alquiler ≈ 994 €/mes por 60 m²». {m2} son los de la búsqueda (`presupuesto.m2`), los mismos con que la API calcula `estimated_cost_eur` y su hecho de coste |
| `zona.precio.aria.compra` | Comprar: unos {importe} € por {m2} m² | **Nueva (D-234).** Lo que lee un lector de pantalla en lugar de «≈ {importe} €». En alquiler, `zona.precio.aria.alquiler`: «Alquiler: unos {importe} € al mes por {m2} m²». **Cambia el 15 nov:** suma los m² |
| `zona.precio.fiabilidad` | {Dato aproximado} | **Nueva (D-234).** Bajo la cifra, en pequeño, cuando no es un dato fiable: las palabras de la sección 6 con la confianza del precio (`estimated_cost_confidence`). El precio estimado de los distritos y barrios de Madrid (0,5) sale «Dato aproximado»; un alquiler de barrio con pocos datos, «Dato poco seguro». Con un dato fiable no va nada |
| `resultados.casi.ayuda` | Les falta una sola cosa de lo que pides. | Bajo `zona.cerca_de_encajar.titulo` («Casi valen»). **Cambia (15 nov, UX móvil 1).** Antes «Cumplen todo menos una cosa.» y, antes aún, «Fallan en una sola cosa.» |
| `resultados.cambiada` | Has cambiado tu búsqueda. Pulsa «Buscar zonas para mí» para ponerla al día. | Los resultados son de la búsqueda anterior. **Cambia (15 nov, UX móvil 1).** |
| `resultados.empate` | Hay {n} zonas igual de buenas: marca qué quieres tener cerca o dónde trabajas para afinar el orden. | Sobre la lista, solo si más de 10 zonas que cumplen todo tienen el mismo % que la primera (D-239). {n} = esas zonas. Con mucho presupuesto y nada marcado todas llegan al 100 %; el orden entre ellas ya no es alfabético: primero la que tiene **más cerca** los servicios del día a día (escuela infantil, colegio, centro de salud, farmacia, centro de mayores y transporte), los haya marcado o no. Con `fit-0.9` cuenta cada minuto andando, no cuántos servicios hay (`everyday_walk`, D-243). Con «Madrid capital», «Hay 106 barrios igual de buenos…» (D-238). Con «Somos mayores», «… marca qué quieres tener cerca o elige cerca de dónde queréis vivir para afinar el orden.» (D-244, revisión del PR #79). **Cambia (15 nov, UX móvil 1).** Antes «Encajan {n} zonas igual de bien: marca qué te importa…» |
| `resultados.banda.muy_bien` | Muy buena opción | Con 90 % o más. **Cambia (15 nov, UX móvil 1).** Antes «Encaja muy bien» (auditoría §4 n.º 3; palabras del orquestador). En cada fila de «Zonas que te convienen» y de «Los barrios que más te convienen», y en la tarjeta, la banda va encima del número, dentro de la misma pastilla («Muy buena opción» / «94 %»); en una fila, en dos líneas cortas si hace falta. En una línea y para el lector de pantalla: «Muy buena opción · 94 %». La banda es `match_band` de la API (`fit-0.9`, D-243 §4), con los valores de siempre (`muy_bien`, `bien`, `regular`, `poco`); con una API sin el campo (o con `null`), sale del % con los mismos umbrales (`lib/match.ts`). Solo en zonas que cumplen todo: en «Casi valen» y en las que no cumplen, la API manda `null` y la web no la deriva (`passes_all`) |
| `resultados.banda.bien` | Buena opción | De 75 a 89 %. Una zona con FALTA en algo que la persona marca no pasa de aquí (89 %, `hecho.limite.falta`). **Cambia (15 nov, UX móvil 1).** Antes «Encaja bien» |
| `resultados.banda.regular` | Opción regular | De 60 a 74 %. Con más de 1 h de trayecto 3 días o más, una zona no pasa de aquí (74 %, `hecho.limite.trayecto`). **Cambia (15 nov, UX móvil 1).** Antes «Encaja regular» |
| `resultados.banda.poco` | Poco recomendable | Por debajo del 60 %. Sin % (sin datos) no hay banda: nunca «Poco recomendable». Los umbrales (90, 75 y 60) no cambian sin avisar a A y a B. **Cambia (15 nov, UX móvil 1).** Antes «Encaja poco» |
| `resultados.empate.grupo` | Empatan al {pct} % | **Nueva (F5).** Encima de las filas a la vista con el mismo %, que además quedan unidas por una barra a la izquierda; también en «Los barrios que más te convienen». Si el empate sigue más allá de las filas a la vista, cuenta todas las zonas empatadas, también sobre una sola fila con la lista plegada: «Empatan al 92 % (3 zonas)», «Empatan al 100 % (45 zonas)». Cada fila empatada lo dice al lector de pantalla tras su %: «…, empata con Latina». **Cambia (15 nov, revisión del PR #79).** Con un espacio que no se parte antes de «%». Sigue igual el 15 nov: la entrega 2 de la auditoría lo quita de la lista (§6) |
| `zona.empate` | Igual de buena que {zonas} ({pct} %). | En la tarjeta, bajo `zona.puesto`. {zonas}: hasta tres nombres, en el orden de la lista («Moratalaz, Ciudad Lineal y Puente de Vallecas»); con más, «12 zonas más» con la palabra del ámbito («12 barrios más»). Un barrio, municipio o pueblo: «Igual de bueno que…». Solo zonas que cumplen todo. **Cambia (15 nov, UX móvil 1).** Antes «Empata al {pct} % con {zonas}.» (auditoría §4 n.º 4) |
| `resultados.casi.presupuesto` | Se pasa unos {importe} € de tu presupuesto | **Nueva (F5).** En «Casi valen» (lista, barrios y tarjeta), en lugar del %. {importe} es `value − threshold` de la condición del presupuesto, en miles de euros al comprar y en decenas al alquilar: «Se pasa unos 11.000 € de tu presupuesto» (Tetuán, comprar con 400.000 €) o «Se pasa unos 90 € al mes de tu presupuesto» (Chamartín, el caso de ejemplo, `fit-0.9`). **Cambia (15 nov, UX móvil 1).** «unos» también en pantalla, no solo en voz alta (antes «≈», y «€/mes») |
| `resultados.casi.trayecto` | Tarda unos {n} min más de lo que pides | **Nueva (F5).** Con el límite del trayecto. Por debajo de 1 min, «Tarda menos de 1 min más de lo que pides»; por encima de 2 h, «Tarda más de 2 h; pides {límite} min como mucho». Con dos lugares con límite, añade «hasta {lugar}». Sustituye a `trabajo.tarda`. **Cambia (15 nov, UX móvil 1).** «unos», no «≈» |
| `resultados.casi.a_pie` | {Servicio}: unos {n} min más andando de lo que pides | **Nueva (F5).** Con «Lo quiero a un paseo» imprescindible: «Colegio con primaria: unos 26 min más andando de lo que pides» (Rejas, `fit-0.9`). A más de 60 min andando, que ya no es un paseo, sin minutos: «{Servicio} a más de 1 h andando; pides {n} min como mucho» |
| `resultados.casi.varias` | {lo que falta} y otra condición | **Nueva (F5).** Si falla más de una, la primera (en el orden de la API: presupuesto, servicios, trayectos) y «y otra condición» o «y {n} condiciones más». La tarjeta las dice todas, separadas por « · »: primero las que tienen cifras y después las que van por su nombre, con un solo «No cumple:» («No cumple: A · B»). Sin cifras (falta `value` o `threshold`), la condición por su nombre, como antes: «No cumple: {condición}» (`zona.cerca_de_encajar.motivo`). Nunca se inventa una cifra |
| `resultados.aviso_2024` | Precio orientativo: hoy puede ser algo más caro. | **Cambia (15 nov, UX móvil 1).** Antes «Precio de contratos firmados en 2024. Los anuncios de hoy suelen pedir más.» (auditoría §4 n.º 17); de dónde sale el precio lo dice «Cómo lo calculamos». **Nueva (F5, opción b).** Una vez, bajo `resultados.de`, cuando los precios de la lista son alquileres (alquilar o sin límite de presupuesto). Al comprar no sale |
| `resultados.sin_lugar` | ¿Trabajas fuera de casa? [Dinos dónde] o elige «Madrid capital» en [«¿Dónde?»] y afinamos el orden. | **Nueva (15 nov, orquestador).** Bajo `resultados.de`, solo con «Toda la Comunidad» y sin ningún lugar (ni trabajo ni familia), y si no sale ya `resultados.empate`, que también lo pide. **Desde el 15 nov, nunca con «Somos mayores»** (D-244): a una pareja jubilada le pedía un lugar que no tiene (auditoría §3 C4). Si «Trabajo en» está plegado, «Dinos dónde» abre «Más opciones». Sin un lugar, la fórmula no sabe que quieres vivir cerca de Madrid y pueden salir arriba pueblos pequeños bien dotados (con `fit-0.9`, Titulcia 2.ª para una pareja con un bebé). «Dinos dónde» y «¿Dónde?» son botones con aspecto de enlace: llevan a «Trabajo en» o a «¿Dónde?» y ponen el foco en el campo |

### Tarjeta de zona

| Clave | Texto | Notas |
|---|---|---|
| `zona.encaje` | {banda} / {pct} % | Chip grande. Nunca «/100». La banda (`resultados.banda.*`) va en pequeño encima del número (F5). Solo en zonas que cumplen todo: una zona de «Casi valen» o que no cumple dice lo que le falta (`resultados.casi.*`), no su %. **Cambia (15 nov, UX móvil 1).** Las palabras de la banda («Muy buena opción») |
| `zona.encaje.aria` | {Banda} para tu búsqueda: {pct} % | «Muy buena opción para tu búsqueda: 94 %». **Cambia (15 nov, UX móvil 1).** Antes «Esta zona encaja muy bien con tu búsqueda: 94 %» |
| `zona.precio.aviso_2024` | Precio orientativo: hoy puede ser algo más caro. | **Cambia (15 nov, UX móvil 1).** El mismo texto que `resultados.aviso_2024`. **Nueva (F5, opción b).** En la tarjeta, en su propia línea bajo el alquiler (y su rango). Al comprar no sale. Como ya lo dice aquí, el hecho del alquiler de la API se enseña sin su «; un anuncio de hoy puede pedir más» (`factText` en `lib/fit.ts`) |
| `zona.precio.rango` | Lo normal: entre {p25} y {p75} € al mes<br>{fuente} | **Nueva (D-242).** **Cambia (15 nov, UX móvil 1).** Antes «La mitad de los contratos, entre {p25} y {p75} €/mes» (auditoría §4 n.º 18). En la tarjeta de zona, en dos líneas bajo `zona.precio.cabecera.alquiler` (y su fiabilidad, en su propia línea): primero el rango y debajo, más pequeña, la fuente. Solo cuando el alquiler es la referencia del Ministerio de Vivienda (`estimated_cost_range`). {p25} y {p75} son los percentiles 25 y 75 de los alquileres de la zona, llevados a contrato nuevo con el mismo factor de la Agencia Tributaria y para los m² del hogar, en decenas de euros; el cociente que acerca la mediana a la media de la Comunidad no los mueve (revisión R-02 del PR #71). Entre la cifra y «€» va un espacio que no se parte. {fuente} viaja con el dato: «Elaboración propia a partir del Ministerio de Vivienda (SERPAVI), 2024» y, en un barrio, «…; rango: media de sus {n} secciones censales». Ejemplo real, Casarrubuelos con 68 m²: «Alquiler: unos 571 € al mes», «Dato aproximado», «Lo normal: entre 500 y 790 € al mes» y la fuente. En las filas no va: solo «≈ 571 €/mes» con `zona.precio.fiabilidad` |
| `zona.precio.rango.aria` | Lo normal: entre {p25} y {p75} € al mes, según {fuente} | **Nueva (D-242).** Lo que lee un lector de pantalla en lugar de la línea anterior. **Cambia (15 nov, UX móvil 1).** |
| `zona.precio.cabecera.compra` | Comprar: unos {importe} € | **Nueva (D-234).** Bajo el nombre de la zona, con «Dato aproximado» si no es fiable (`zona.precio.fiabilidad`). Para cualquier zona evaluada, también la que no sale en la lista (`all_zones[].estimated_cost_eur`). En alquiler, `zona.precio.cabecera.alquiler`: «Alquiler: unos {importe} € al mes». Sin precio, no va nada. **Cambia (15 nov, UX móvil 1).** «unos» y «al mes» en lugar de «≈» y «/mes» |
| `zona.encaje.ayuda` | Cuánto se parece esta zona a lo que buscas. No es una nota de la zona. | **Cambia (15 nov, UX móvil 1).** Tras «¿Qué es el %?» (`zona.encaje.que_es`), bajo el precio; antes, un `title` sobre el %, que en el móvil no se veía |
| `zona.encaje.que_es` | ¿Qué es el %? | **Nueva (15 nov, UX móvil 1).** Como `ayuda.que_es`, solo con el % a la vista |
| `hecho.limite.mitad` | Tardas {duración} o más en llegar a {lugar}: el % se queda en la mitad | **Nueva (D-243), de la API.** **Cambia (15 nov, revisión del PR #79).** Antes «…: el encaje se queda en la mitad» (`unreachable_fact` en `hi_domain/fit.py`; la fórmula no cambia). Trayecto de 3 días o más a la semana que tarda 3 veces lo que se pide o más: 1 h 30 con los 30 min de siempre; con «como mucho 45 min», «2 h 15». El encaje se multiplica por 0,5. Ejemplo real, el estudiante con 500 €: «Tardas 1 h 30 o más en llegar a URJC Vicálvaro: el % se queda en la mitad» (Pinilla del Valle, 32 %). Icono del trayecto |
| `hecho.limite.no_llega` | No llegas a {lugar} a las 9:00 en transporte público: el % se queda en la mitad | **Nueva (D-243), de la API.** Lo mismo cuando con los horarios publicados no se llega a las 9:00. **Cambia (15 nov, revisión del PR #79).** Antes «…: el encaje se queda en la mitad» |
| `hecho.limite.falta` | Faltan {lista}: como mucho 89 % | **Nueva (D-243), de la API.** «Qué falta» dice FALTA en un servicio que la persona marca («Me importa» o «Lo quiero a un paseo»), y la zona habría salido por encima: se queda en 89 %, nunca «Muy buena opción». {lista} con `fila.lista.*` («escuelas infantiles», «centros de salud y colegios»). En un barrio, «Faltan escuelas infantiles en Puente de Vallecas: como mucho 89 %»: es el «Qué falta» de su distrito. Icono del servicio |
| `hecho.limite.trayecto` | Más de {duración} de trayecto hasta {lugar}: como mucho 74 % | **Nueva (D-243), de la API.** Trayecto de 3 días o más a la semana de más del doble de lo que se pide (1 h con los 30 min de siempre; 1 h 30 con «como mucho 45 min»): la zona se queda en 74 %, nunca «Buena opción». Icono del trayecto |
| `hecho.ocio` | Ocio a pie: bares y cafeterías a unos {n} min, restaurantes a unos {n} min, cultura a unos {n} min | Hecho de la API (`fit-0.8`, D-236) cuando la persona marca «Ocio»: un solo hecho con las casillas marcadas, en su orden. Ejemplo real, Latina con el caso del ejemplo más ocio: «Ocio a pie: bares y cafeterías a unos 3 min, restaurantes a unos 4 min, cultura a unos 11 min». Icono `Wine`. Un grupo sin dato sale «…: sin datos» y no convierte el hecho en punto débil; a más de una hora, «a más de 60 min» |
| `hecho.ocio.sin_datos` | Ocio: sin datos de distancia a pie en esta zona | Si no hay dato de ninguna casilla |
| `condicion.ocio` | Bares y cafeterías a {n} min andando como mucho · Restaurantes a… · Gimnasios y deporte a… · Cultura a… | Condición de la API por cada casilla con «Imprescindible». Explicación: «A unos 3 min andando de un bar o una cafetería (lo que tarda la mitad de la zona)». En el Reality Check, las casillas se relajan juntas: «+5 min a pie hasta el ocio» y, al tope, «Ocio cerca como preferencia, no como requisito» |
| `encaje.aviso_justo` | Tiene lo que pides. Aun así, comparado con municipios parecidos, aquí van justos de {lista}. | Bajo el % de la tarjeta, si alguna fila de «Qué falta» sale JUSTO y ninguna FALTA. Ejemplo real, Latina, la 2.ª del caso de ejemplo con `fit-0.9` (94 %): sus filas de escuelas infantiles y de centros de salud salen JUSTO (`GET /api/v1/gaps/distrito/2807910`, 15 nov). Como la búsqueda encontró el centro de salud a unos 10 min, esa fila la explica `zona.cerca_pocas` y la línea dice «… aquí van justos de escuelas infantiles.» **Cambia (15 nov, UX móvil 1).** Antes «Encaja con lo que pides. Aun así, frente a municipios parecidos, …». Las filas, con `fila.lista.*`. No cuentan las filas de zona muy pequeña para comparar. Fase de mejora, **pendiente de B** |
| `encaje.aviso_falta` | Tiene lo que pides. Aun así, comparado con municipios parecidos, aquí faltan {lista}. | Si alguna fila sale FALTA y ninguna JUSTO. Ejemplo: Puente de Vallecas, «… aquí faltan escuelas infantiles.» |
| `encaje.aviso_falta_justo` | Tiene lo que pides. Aun así, comparado con municipios parecidos, aquí faltan {lista_falta} y van justos de {lista_justo}. | Si hay filas FALTA y JUSTO. Si todas salen CUBIERTO o SIN DATOS, no va ninguna línea |
| `fila.lista.escuela_infantil` | escuelas infantiles | Nombres de fila dentro de una frase, en minúscula. Se unen como «a», «a y b», «a, b y c» |
| `fila.lista.colegio` | colegios | |
| `fila.lista.centro_salud` | centros de salud | |
| `fila.lista.mayores` | centros de mayores | |
| `fila.lista.farmacia` | farmacias | |
| `fila.lista.vivienda` | viviendas grandes para familias | |
| `zona.puesto` | La {n}.ª que más te conviene | Posición (`rank`). Con «Madrid capital», «Alrededores» o «Pueblos» la zona es un barrio, municipio o pueblo: «El {n}.º que más te conviene» (D-238). **Cambia (15 nov, UX móvil 1).** Antes «La {n}.ª que más encaja» |
| `zona.hechos.titulo` | Lo que tienes aquí | Encima de los 3–5 hechos (`facts`) |
| `zona.hecho.confianza` | {nivel} | Junto a cada hecho, con los niveles de la sección 6. Desde el 15 nov, qué quiere decir cada nivel va tras `confianza.que_es` («¿Qué quiere decir «Dato fiable»?»), bajo los hechos, solo con los niveles que salen, también el del precio de la cabecera («Dato aproximado»); antes, un `title`. **Cambia (15 nov, revisión del PR #79).** En «Qué falta», la palabra de cada fila es el botón que abre lo que quiere decir |
| `hecho.coste.en_la_tarjeta` | Alquiler unos {importe} € al mes por {m2} m² (…) · Comprar unos {importe} € por {m2} m² (…) | **Nueva (15 nov, revisión R-03 del PR #79).** El hecho del coste de la API se enseña en la tarjeta con «unos» en lugar de «≈ » y «€ al mes» en lugar de «€/mes» (`factText` en `lib/fit.ts`; el e2e sigue la misma regla en `shown_text.mjs`). Los €/m² no cambian |
| `hecho.paradas` | Parada de autobús a unos {n} min andando · Metro o Cercanías a unos {m} min | Texto del hecho de la API. Sustituye a «Parada de transporte público a unos {n} min andando». Prueba con usuarios (14 nov): quien va en autobús quería ver sus paradas. «Metro» incluye Metro Ligero. Los minutos, con el método de siempre: lo que tarda la mitad de la zona a 4 km/h. En producción desde el 14 nov (D-233 §2, `transit_walk_text`; despliegue de `ad4a8f2` y sync): Latina, «Parada de autobús a unos 2 min andando · Metro o Cercanías a unos 8 min» (`evidence/gate-06/2026-11-14-deploy/deploy-27-ad4a8f2-d233.md`). La nota del transporte no cambia |
| `hecho.paradas.un_modo` | Parada de autobús a unos {n} min andando | Como quedó en D-233 §2: si un tipo no tiene minutos o queda a más de 60 min andando, se deja fuera y sale solo el otro («Metro o Cercanías a unos {m} min andando» si falta el autobús). Sin ninguno, el texto de siempre. Ejemplo: Navacerrada, autobús a 6 min y metro a 93 → solo el autobús. Sustituye a la propuesta `hecho.paradas.sin_tren` («Sin metro ni Cercanías a un paseo»), que no se hizo. En producción desde el 14 nov |
| `zona.coste.compra` | Precio estimado: unos {importe} € (orientativo) | Sin usar hoy: con compra no hay coste (D-214, punto 5). El alquiler llega como hecho de la API, con la cifra, los m² y el aviso (con `fit-0.9`, Latina en el caso de ejemplo: «Alquiler ≈ 1.101 €/mes por 77 m² (14,3 €/m², contratos firmados en 2024; un anuncio de hoy puede pedir más)»), y no lleva clave aquí |
| `zona.coste.sin_datos` | Precio: sin datos en esta zona | Sin usar hoy, como `zona.coste.compra` |
| `zona.no_cumple` | No cumple todo lo que pides. | Si la API no nombra la condición que falla |
| `zona.no_sabemos` | No lo sabemos: nos falta el dato para comprobar lo que pides. No lo damos por bueno. | Zona con alguna condición `UNKNOWN` |
| `zona.encaje.antiguo` | Esto es de tu búsqueda anterior. | Tarjeta abierta tras cambiar la búsqueda (`resultados.cambiada`). **Cambia (15 nov, UX móvil 1).** Antes «Este encaje es de tu búsqueda anterior.» |
| `zona.falta.titulo` | Lo que le falta a esta zona | Mini lista de 3 filas: lo que falta primero y, a igual estado, con «Somos mayores» o con una persona mayor a la que se cuida, centros de salud, farmacias y centros de mayores, en ese orden (`householdRows` en `lib/gaps.ts`, D-244). **Cambia (15 nov, revisión del PR #79).** **Cambia (15 nov, UX móvil 1).** Antes «Qué falta aquí» (auditoría §4 n.º 9). La pestaña sigue llamándose «Qué falta» |
| `zona.falta.estados` | FALTA: hay claramente menos que en zonas parecidas. · JUSTO: hay algo menos que en zonas parecidas. · CUBIERTO: hay lo mismo o más que en zonas parecidas. · SIN DATOS: no tenemos el dato; no quiere decir que no haya. · No comparable: vive tan poca gente que no se puede comparar. · Junto con sus vecinos: es un pueblo pequeño: lo comparamos junto con los de al lado. | **Nueva (15 nov, UX móvil 1).** Bajo las filas de la tarjeta, una línea por cada etiqueta que sale en ellas (`GAP_STATUS[*].short`, `SMALL_ZONE.short`, `GROUP.short` en `lib/gaps.ts`). Antes, el significado solo estaba en un `title` (auditoría §3 A5) |
| `zona.falta.ayuda` | Un servicio puede estar cerca y aun así ir lleno: aquí miramos si hay bastante para toda la gente de la zona. | Bajo `zona.falta.titulo`, siempre. «¿Qué quieres tener cerca?» y «Lo quiero a un paseo» miden minutos andando; «Qué falta», si alcanza para todos frente a zonas parecidas (2SFCA, D-217). **Cambia (15 nov, UX móvil 1).** Antes «Compara si hay bastante para toda la gente de la zona con lo que hay en zonas parecidas: algo puede estar cerca y aun así faltar.» (auditoría §4 n.º 31) |
| `zona.cerca_pocas` | {Servicio} a unos {n} min andando, pero {hay pocas para tantos …}: por eso sale {FALTA \| JUSTO}. | **Nueva, 15 nov.** En «Qué falta aquí», encima de las filas, cuando la búsqueda encontró cerca un servicio (una condición de «Lo quiero a un paseo» que cumple o un hecho a pie de «Lo que tienes aquí»), a 15 min andando como mucho, que es lo que mide la fila (`fila.mide.*`), y su fila sale FALTA o JUSTO. Esa fila ya no se repite en `encaje.aviso_*` (revisión del PR #70): si era la única, la línea de aviso no sale. Ejemplo real, Puente de Vallecas con escuela infantil a 10 min como mucho: «Escuela infantil a unos 6 min andando, pero hay pocas para tantos niños: por eso sale FALTA.». **Cambia (15 nov, UX móvil 1).** Sin las edades (antes «… para tantos niños de 0 a 4 años …», auditoría §4 n.º 32). Las palabras de cada fila siguen a `fila.mide.*`: escuelas infantiles «hay pocas / van justas para tantos niños» (nadie publica sus plazas), colegios «hay pocas aulas / las aulas van justas para tantos niños», centros de salud «hay pocos / van justos para tanta gente», mayores «hay pocas plazas / las plazas van justas para tantas personas mayores», farmacias «hay pocas / van justas para tanta gente». En la tarjeta de un barrio, «pero en {distrito} …». No sale en filas «No comparable» ni «Junto con sus vecinos»: ese estado no es el de la zona sola. Solo texto: la fórmula no cambia (se revisa el 17-18 nov) |
| `zona.falta.ver_todo` | Ver todo lo que falta | Abre la pestaña «Qué falta» con esta zona |
| `zona.boton` | Ver la zona | Del brief |
| `zona.fuente` | ¿De dónde sale? | Enlace que abre la procedencia (sección 9) |
| `zona.cerca_de_encajar.titulo` | Casi valen | Zonas que fallan una condición (`near_misses`). **Cambia (15 nov, UX móvil 1).** Antes «Casi encajan» (auditoría §4 n.º 7) |
| `zona.cerca_de_encajar.motivo` | No cumple: {condición} | {condición} = `label` de la condición que falla. **Cambia (F5):** solo cuando la API no da cifras para decir lo que falta (`resultados.casi.*`) |
| `zona.condicion.cumple` | Cumple | `PASS` |
| `zona.condicion.no_cumple` | No cumple | `FAIL` |
| `zona.compra.sin_precio` | Sin precio de compra en esta zona: el valor tasado del Ministerio de Vivienda solo se publica para los municipios de más de 25.000 habitantes. | **Nueva (D-234).** En la tarjeta de un municipio «sin datos» sin precio, al comprar (`buySource` en `FitDetails.tsx`). Solo si la zona no trae precio: una con precio puede ser «sin datos» por otra condición |
| `zona.compra.sin_precio.madrid` | Sin precio de compra en esta zona: el valor tasado del Ministerio de Vivienda se publica para Madrid entero, no por distrito ni por barrio. | **Nueva (D-234).** Lo mismo en un distrito o barrio de Madrid sin precio: solo pasa con el código desplegado y la estimación sin sincronizar. Nunca promete una estimación que no hay |
| `hecho.alquiler.referencia` | Alquiler ≈ {importe} €/mes por {m2} m² ({precio} €/m², referencia del Ministerio de Vivienda llevada a contratos firmados en 2024; un anuncio de hoy puede pedir más); la mitad de los contratos, entre {p25} y {p75} € | **Nueva (D-242).** Llega escrita de la API, en `facts` y en la condición del presupuesto, solo donde la Comunidad no publica el alquiler. La nota viaja con el dato (`fit.note`): el SERPAVI son alquileres vigentes declarados en el IRPF, no contratos de 2024, así que dice «llevada a» (revisión R-02 del PR #71). Fiabilidad 0,7 («Dato aproximado»); con menos de 30 contratos, 0,4 («Dato poco seguro»). En un barrio (hoy Sol) la nota añade «el rango es la media de los de sus {n} secciones censales». Ejemplo real, Casarrubuelos: «Alquiler ≈ 571 €/mes por 68 m² (8,4 €/m², referencia del Ministerio de Vivienda llevada a contratos firmados en 2024; un anuncio de hoy puede pedir más); la mitad de los contratos, entre 500 y 790 €». Donde la Comunidad sí lo publica sigue «…, contratos firmados en 2024; …)», sin rango. **En la tarjeta (F5):** sin «; un anuncio de hoy puede pedir más», que ya dice `zona.precio.aviso_2024` junto al precio |
| `hecho.alquiler.referencia.casas` | … ({precio} €/m², precio de casas unifamiliares, porque se alquilan pocos pisos; referencia del Ministerio de Vivienda …) | **Nueva (D-242).** En los 26 municipios donde solo hay mediana de casas unifamiliares. Fiabilidad 0,5 como máximo: con el €/m² de una casa, el coste de los m² del hogar se queda corto |
| `hecho.compra.estimado` | Comprar ≈ {importe} € por {m2} m² ({precio} €/m², precio estimado: valor tasado de Madrid repartido según el valor catastral del distrito; Ministerio de Vivienda y Catastro vía Ayuntamiento) | **Nueva (D-234).** Llega escrita de la API, en `facts` y en la condición del presupuesto. En un barrio dice «del barrio». Fiabilidad 0,5: «Dato aproximado». En los municipios sigue «…, valor tasado medio de la vivienda libre, no el precio de un anuncio)» |
| `zona.condicion.sin_dato` | No lo sabemos | `UNKNOWN`. Ayuda: «Nos falta el dato para comprobarlo. No lo damos por bueno.» |
| `zona.falta.a_pie` | A pie: {minutos} | Bajo el nombre de cada fila de la mini lista. {minutos} con `a_pie.min` (sección 5) |
| `zona.barrio.antetitulo` | Barrio de Madrid | Tarjeta de un barrio tras buscar con «Madrid capital» (D-238), donde los distritos dicen «Distrito de Madrid» |
| `zona.barrio.nombre` | {barrio} · {distrito} | Título de la tarjeta, por ejemplo «Berruguete · Tetuán» o «Lucero · Latina» |
| `zona.barrio.falta.titulo` | Lo que le falta a {distrito} | En lugar de `zona.falta.titulo`: el barrio no tiene «Qué falta» propio (D-232). Sin la línea `encaje.aviso_*`, que diría «aquí» de todo el distrito. **Cambia (15 nov, UX móvil 1).** Antes «Qué falta en {distrito}» |
| `zona.barrio.falta.ayuda` | Las cifras de «Qué falta» son del distrito entero. | Bajo el título. La misma frase que `barrios.ayuda` |
| `zona.barrio.boton` | Ver el distrito | En lugar de `zona.boton`: lleva a la vista del distrito, con «Los barrios que más te convienen» |
| `zona.fuera` | Fuera de tu búsqueda ({ámbito}). | Tarjeta de una zona del mapa que no está en «¿Dónde?», por ejemplo Getafe tras buscar en «Madrid capital». {ámbito} es la opción elegida. Revisión del PR #58 |
| `zona.sin_alquiler` | Con «Alquilar», puede faltar el alquiler: en los municipios con muy pocas viviendas alquiladas no se publica su precio. | Tarjeta de un municipio con encaje «No lo sabemos» y presupuesto de alquiler, como la nota de compra (D-227 §3). Dicho como posibilidad: puede faltar otra condición. Los barrios ya traen su motivo de la API (D-232 §4). **Cambia (D-242):** antes decía que la Comunidad solo lo publica en los municipios de más de 20.000 habitantes y que casi ningún pueblo lo tiene |
| `zona.encaje.pronto` | Muy pronto verás si esta zona te conviene. | En lugar de «Haz tu búsqueda…» mientras el buscador esté apagado (`busqueda.pronto`) |
| `zona.antetitulo` | Distrito de Madrid · Barrio de Madrid · Municipio | Encima del nombre de la tarjeta. **Cambia (15 nov, UX móvil 1):** en minúsculas, no en mayúsculas («DISTRITO DE MADRID» se lee peor y suena a alarma, auditoría M2) |
| `zona.titulo` | {zona}: lo que hay cerca | **Nueva (15 nov, UX móvil 1).** Título de la pantalla de zona, con el nombre en violeta. Sustituye a «Explora {zona}» y a «Mira sus servicios y puntos clave, con datos oficiales.» (auditoría §4 n.º 36) |

### Contexto de la zona (no puntúa)
Datos que se enseñan en la vista de zona para conocerla mejor. No cambian el % de encaje, no ordenan zonas y no entran en «Qué falta». Van junto a `zona.seguridad_vecinos` (sección 2), sin colores de estado ni de alarma. Prueba con usuarios (14 nov).

| Clave | Texto | Notas |
|---|---|---|
| `zona.delitos` | Delitos conocidos por la policía: {tasa} por cada 1.000 habitantes en {año} (en los municipios de más de 20.000 habitantes, {referencia}). | Es la opción abierta de D-224 §3: la cifra, la referencia, el año y el aviso, y nada más. Criminalidad convencional: sin la cibercriminalidad, que no ocurre en un sitio. Con los datos de 2024, la referencia de los 37 municipios es 47,9 (`evidence/gate-01/2026-11-12/seguridad-evaluacion.md`). Solo en los municipios que publica la fuente (36 zonas del mapa). Nunca «peligroso», «inseguro», «más seguro» ni «menos seguro». **Pendiente de A** (pipeline, y el nombre de cada municipio a código INE, porque la fuente no lo trae) **y de B** |
| `zona.delitos.aviso` | Se cuentan donde se denuncian, no donde vive quien los sufre: donde hay mucho comercio u ocio salen más. No mide el riesgo de vivir aquí. | Siempre debajo de la cifra y nunca plegado: es el aviso del denominador que pide D-224 §3. **Pendiente de B** |
| `zona.delitos.fuente` | Ministerio del Interior, Balance de Criminalidad, en el Portal de Datos Abiertos de la Comunidad de Madrid. | Con enlace a la ficha del portal (CC BY 4.0). **Pendiente de B** |
| `zona.delitos.sin_datos` | La fuente solo publica los municipios de más de 20.000 habitantes. | En los demás municipios. Es SIN DATOS: nunca 0 ni un hueco sin explicar. **Pendiente de B** |
| `zona.delitos.madrid` | En Madrid, la fuente da la ciudad entera: {tasa} por cada 1.000 habitantes en {año}. No la repartimos por distritos. | Solo si A decide enseñar la cifra de la ciudad en los 21 distritos; si no, en los distritos no va nada de delitos y se queda `zona.seguridad_vecinos`, que sí es por distrito. Repartirla supondría barrios iguales por dentro (D-224 §2). Madrid daba 58,6 en 2024. **Pendiente de A** (decide si se enseña) |
| `zona.antiguedad` | Viviendas construidas después del año 2000: {pct} % (en toda la Comunidad, {pct_comunidad} %). | Junto a «Vivienda para familias». Fuente candidata, comprobada por D en el portal el 14 nov: «Censo anual Comunidad de Madrid. Viviendas por año de antigüedad. Municipios» (`censo_anual_vivienda_por_antiguedad`, CC BY 4.0), años 2022 y 2023, por municipio. Cálculo de D con 2023, sumando los tramos de 2001 a 2025 sobre el total sin «No consta»: Comunidad 24,6 %, Madrid 16,5 %, Getafe 31,8 % y Valdemoro 59,8 %. Si A la carga, es un conjunto CM más. **Pendiente de A y de B** |
| `zona.antiguedad.ayuda` | Es la edad de todas las viviendas de la zona, no solo de las que se venden o se alquilan. | Al tocar «?». Evita leerlo como un filtro de pisos nuevos (pregunta 50). **Pendiente de B** |
| `zona.antiguedad.madrid` | Dato de toda la ciudad de Madrid: la fuente no lo da por distritos. | En los 21 distritos, si se enseña la cifra de la ciudad; si no, SIN DATOS, como la fila de vivienda. **Pendiente de A** (decide si se enseña) |

#### Entorno (D-237)
Bloque «Entorno» en la vista de un municipio, de un distrito de Madrid o de un barrio, debajo de «Vivienda nueva y lo que viene» (D-241). Lo pidieron en la prueba con usuarios: «pensando en comprar una casa, el ruido también importa», «facilidad de aparcar». Contexto: no puntúa, no ordena zonas y no entra en «Qué falta». Sin colores de estado ni de alarma, y nunca «peligroso», «tóxico» ni «insalubre». Hecho por A+B (`apps/web/src/lib/environment.ts`).

| Clave | Texto | Notas |
|---|---|---|
| `zona.entorno.titulo` | Entorno | |
| `zona.entorno.ruido` | Calles con ruido alto: {dia} % de las calles de día, {noche} % de noche (Mapa Estratégico de Ruido 2021, Ayuntamiento de Madrid) | Porcentaje de la longitud de las calles donde vive la gente (las mismas que los minutos a pie), leída cada 10 m a lo largo de cada tramo, por encima de 65 dB Ld (de 7 a 19 h) y de 55 dB Ln (de 23 a 7 h): los objetivos del RD 1367/2007 (revisión del PR #65, R-02 y R-03). Sin decimales, con espacio irrompible antes de «%». Solo Madrid capital: la ciudad, los 21 distritos y los 131 barrios. Valores de `pct_calle_ruido_dia` y `pct_calle_ruido_noche`. Usera: «14 % de las calles de día, 32 % de noche». Nunca «vecinos expuestos» (R-07) |
| `zona.entorno.ruido.sin_dato` | Calles con ruido alto: sin dato publicado | Fuera de Madrid capital, donde no hay mapa de ruido en abierto. Nunca 0 |
| `zona.entorno.ruido.ayuda` | Ruido del tráfico calculado por el Ayuntamiento en la propia calle, no en la fachada de las casas: no es el porcentaje de vecinos expuestos. Cuenta la calle por encima de 65 dB de día o de 55 dB de noche, los objetivos de calidad acústica de las zonas residenciales. | Bajo la cifra, solo cuando la hay. «Calculado», nunca «medido»: es un modelo del Ayuntamiento, no un sonómetro (R-07). La OMS solo como referencia, sin su cifra |
| `zona.entorno.aire` | Aire: NO₂ medio {año}, {valor} µg/m³ en la estación de {estación} (límite UE: 40; 20 desde 2030) | Media de las horas válidas de 2025 de la estación de la zona (`no2_media_anual`, `detail.own`). Si es de tráfico (`detail.traffic`), «en la estación de tráfico de {estación}» (R-08). Una cifra decimal. Getafe: «Aire: NO₂ medio 2025, 25,6 µg/m³ en la estación de tráfico de Getafe (límite UE: 40; 20 desde 2030)». Siempre con la estación: sin ella no sale la cifra |
| `zona.entorno.aire.cercana` | Aire: NO₂ medio {año}, {valor} µg/m³ en la estación de {estación}, la más cercana de su zona de calidad del aire, a {km} km (límite UE: 40; 20 desde 2030) | Si la zona no tiene estación propia: la más cercana del centro de sus calles dentro de su zona de calidad del aire de la Comunidad, una de fondo antes que una de tráfico (R-08). Usera: «… 21,2 µg/m³ en la estación de Méndez Álvaro, la más cercana de su zona de calidad del aire, a 2,7 km …» |
| `zona.entorno.aire.sin_dato` | Aire: sin dato publicado | Si la API no da cifra o no dice la estación |
| `zona.entorno.aire.fuente` | Redes de calidad del aire de la Comunidad de Madrid y del Ayuntamiento de Madrid, horas válidas del año. | Bajo la cifra |
| `zona.entorno.aparcamiento` | Aparcamiento público a unos {n} min andando | Mediana de las calles de la zona hasta el aparcamiento público, mixto o disuasorio más cercano de los publicados en abierto (`min_a_pie_aparcamiento_publico`, 4 km/h). Los de residentes no cuentan |
| `zona.entorno.aparcamiento.lejos` | Ningún aparcamiento público de los publicados en abierto a menos de 30 min andando | Si la mediana pasa de 30 min. No dice que no haya dónde aparcar |
| `zona.entorno.disuasorio` | Aparcamiento disuasorio {gratuito} ({n} plazas) en {zona}: {nombre} | Si la zona tiene uno (de «Todos los centros», tipo «Aparcamientos»). {gratuito}: «gratuito», «de pago» o «gratuito y de pago», según el CRTM. Usera tendría «Aparcamiento disuasorio gratuito (210 plazas) en Usera: Doce de Octubre» si solo tuviera ese |
| `zona.entorno.disuasorios` | {n} aparcamientos disuasorios en {zona}, con {plazas} plazas (todos gratuitos) | Con varios. «(2 gratuitos)» solo si todos publican si son gratuitos; si alguno no lo publica, «(de 1 no consta si es gratuito)», nunca contado como de pago (segunda revisión del PR #65, R-02). Sin las plazas si alguno no las publica (los del Ayuntamiento). Getafe: «6 aparcamientos disuasorios en Getafe, con 2.446 plazas (todos gratuitos)»; Fuencarral-El Pardo: «4 aparcamientos disuasorios en Fuencarral-El Pardo (de 1 no consta si es gratuito)» |
| `zona.entorno.aparcamiento.fuente` | Aparcamientos publicados en abierto: los de disuasión del Consorcio Regional de Transportes y los del Ayuntamiento de Madrid. Lo fácil que es aparcar en la calle no tiene dato abierto. | Bajo las líneas de aparcamiento. No se inventa la facilidad de aparcar en la calle |
| `zona.entorno.contexto` | Datos de contexto: no cambian qué zonas te convienen ni «Qué falta». | **Cambia (15 nov, UX móvil 1).** Al pie del bloque |

### Vivienda nueva y lo que viene (no puntúa, D-241)
Una tarjeta en la vista de zona, debajo de «Otros datos de la zona» (D-235), para la pregunta de la prueba con usuarios «¿las casas son nuevas o viejas?» y «¿qué se va a construir?». Cada línea dice su fuente y su fecha. No cambia el % de encaje, no ordena zonas y no entra en «Qué falta». Sin colores de estado ni de alarma. Si la API no tiene una feature, su línea no sale; si la fuente no publica el dato de una zona, tampoco: nunca un 0.

| Clave | Texto | Notas |
|---|---|---|
| `zona.vivienda_nueva.titulo` | Vivienda nueva y lo que viene | Título de la tarjeta |
| `zona.vivienda_nueva.compraventas` | {nuevas} de las {total} compraventas de vivienda del último año fueron de obra nueva ({pct} %). | `compraventas_obra_nueva_pct` con `detail` (los 4 últimos trimestres). Getafe: «650 de las 2.311 … (28 %)». Con menos de un 10 %, un decimal («3,8 %»). Variantes: «Ninguna de las {total} compraventas de vivienda del último año fue de obra nueva.», «No hubo compraventas de vivienda en el último año.» y «La única compraventa de vivienda del último año fue de obra nueva / de segunda mano.». Se quita el «Aquí se construye:» del encargo: donde la obra nueva es el 3 % (Madrid) o el 1 %, diría lo contrario de la cifra |
| `zona.vivienda_nueva.provisional` | Incluye datos aún provisionales. | Detrás de la frase, si algún trimestre sumado viene marcado «Provisional» en la fuente (hoy, el 2.º de 2026) |
| `zona.vivienda_nueva.compraventas.fuente` | Ministerio de Transportes, Movilidad y Agenda Urbana, en el portal de datos abiertos de la Comunidad de Madrid, del {trimestre} al {trimestre}. | «del 3.er trimestre de 2025 al 2.º trimestre de 2026» |
| `zona.vivienda_nueva.tasacion` | Una vivienda de menos de 5 años se tasa a {valor} €/m², un {pct} % más que la usada. | `valor_tasado_vivienda_nueva_m2` y `…_usada_m2`, del mismo año. Pozuelo: «5.432 €/m², un 13 % más». Si es más barata: «un {pct} % menos que la usada» (Alcorcón, 7 %); si redondea a 0: «casi lo mismo que la usada». Solo en los 20 municipios con los dos valores. No es el precio de compra del buscador (D-227) |
| `zona.vivienda_nueva.tasacion.fuente` | Valor tasado medio de {año} del Ministerio de Vivienda y Agenda Urbana, en el portal de datos abiertos de la Comunidad de Madrid; «usada» es la de más de 5 años. | |
| `zona.vivienda_nueva.ciudad` | En toda la ciudad de Madrid, {frase en minúscula} | En los 21 distritos, las compraventas y la tasación son de la ciudad entera |
| `zona.vivienda_nueva.ciudad.nota` | La fuente no lo da por distritos. | Debajo, en los distritos |
| `zona.vivienda_nueva.plan_vive` | Lo que viene: Plan Vive, {viviendas} viviendas de alquiler asequible {fase} ({ubicación}). | `plan_vive_viviendas` con sus `items`. {fase}: «Construcción» → «en obras», «Entrega» → «en entrega», «Comercialización» → «en comercialización», unidas con «y». Alcobendas: «756 viviendas de alquiler asequible en obras (avda. Olímpica y avda. Camilo José Cela)». En Hortaleza y Vicálvaro sale la entrada de Madrid (Valdebebas y Los Ahijones), con la nota de la fila |
| `zona.vivienda_nueva.plan_vive.nota` | La Comunidad no publica cuántas de estas viviendas hay en cada uno de los dos sitios. | Viene en el dato (`note` de la entrada de Madrid), no en el código |
| `zona.vivienda_nueva.plan_vive.fuente` | Página del Plan Vive de la Comunidad de Madrid, consultada el {fecha}. | Su aviso legal pide citar la fuente y la fecha de extracción |
| `zona.vivienda_nueva.ambitos.obras` | En desarrollo: {ámbitos} (urbanización en obras). | Solo distritos: `ambitos_residenciales_en_desarrollo`. Hasta 4 nombres y «y N más». Vicálvaro: «Los Berrocales, Los Ahijones, Los Cerros y Camino Viejo de Vicálvaro» |
| `zona.vivienda_nueva.ambitos.tramitacion` | En tramitación: {ámbitos} (planeamiento, gestión o proyecto en marcha). | |
| `zona.vivienda_nueva.ambitos.sin_empezar` | Previstos: {ámbitos} (aún sin empezar). | Algunos llevan años así: no se dice «lo que viene» de ellos |
| `zona.vivienda_nueva.ambitos.ninguno` | En este distrito no queda ningún ámbito de vivienda del Plan General por terminar. | Hoy, Puente de Vallecas y Moratalaz: la fuente no tiene ninguno, así que es un 0 confirmado |
| `zona.vivienda_nueva.ambitos.fuente` | Ayuntamiento de Madrid, estado de desarrollo de los ámbitos del Plan General a {fecha}. Dice dónde se prepara suelo para vivienda, no cuántas viviendas habrá ni cuándo. | «a 1 de julio de 2026» |
| `zona.vivienda_nueva.no_puntua` | Son datos informativos: no cambian qué zonas te convienen ni su orden. | **Cambia (15 nov, UX móvil 1).** Pie de la tarjeta: es el mismo texto que `zona.contexto.no_puntua` y, con las dos tarjetas, sale una sola vez, bajo la última (15 nov) |

### Barra de barrios (solo distritos de Madrid)
La barra **mueve el mapa** a un barrio. Desde el 13 nov (D-232, `fit-0.7`), después de una búsqueda la vista de un distrito sí tiene cifras por barrio, en «Los barrios que más te convienen» (abajo). «Qué falta» sigue siendo del distrito entero. Al pulsar un barrio de esa sección se marca también su chip de la barra.

| Clave | Texto | Notas |
|---|---|---|
| `barrios.titulo` | Ir a un barrio | Título de la barra inferior (MAP-004). Sustituye a «Barrios de la zona», que hacía esperar cifras de cada barrio |
| `barrios.todo` | Todo {distrito} | Primer chip: vuelve a encuadrar el distrito entero, por ejemplo «Todo Chamartín». Marcado al entrar en la zona |
| `barrios.ayuda` | Mueve el mapa a ese barrio. Las cifras de «Qué falta» son del distrito entero. | `aria-description` de la barra, o línea pequeña si cabe. Sigue siendo cierto: el encaje por barrio va en su sección, no en «Qué falta» |

### «Los barrios que más te convienen» (antes «Los barrios que mejor encajan»; vista de un distrito, tras buscar; D-232, PR #37 de B, en producción desde `e7025fb`)
Revisión de los borradores de B (13 nov). Ejemplo real con el caso de ejemplo, comprobado con `POST /api/v1/search/barrios` (`fit-0.9`, API del 15 nov sobre los datos del lote 4, distrito 2807920): San Blas-Canillejas, 7 de 8 barrios; Arcos, Canillejas, Amposta, Simancas y Rosas al 89 %, y El Salvador y Hellín al 87 %; Rejas, en «Casi valen», por el colegio (unos 26 min más andando de lo que pide).

| Clave | Texto | Notas |
|---|---|---|
| `barrios.encajan.titulo` | Los barrios que más te convienen | De Mariano (13 nov), con las palabras del 15 nov. **Cambia (15 nov, UX móvil 1).** Antes «Los barrios que mejor encajan» |
| `barrios.encajan.resumen` | {n} de sus {total} barrios te convienen. | Con 1: «1 de sus {total} barrios te conviene.». Todos: «Sus {total} barrios te convienen.». Ninguno: «Ninguno de sus {total} barrios cumple todo lo que pides.». **Cambia (15 nov, UX móvil 1).** Antes «… encajan con tu búsqueda.» |
| `barrios.encajan.pulsa` | Toca uno para verlo en el mapa. | **Cambia** «Pulsa» por «Toca», como el resto de la web («Toca un tipo de centro…», «toca una zona del mapa»). Aplicado por B y en producción desde `5101c93` |
| `barrios.encajan.carga` | Buscando los barrios de {distrito} que te convienen… | **Cambia (15 nov, UX móvil 1).** |
| `barrios.encajan.todos` | Ver los {n} barrios | Aprobado |
| `barrios.encajan.ayuda` | Cuánto se parece este barrio a lo que buscas. No es una nota del barrio. | Igual que `zona.encaje.ayuda`. Aprobado |
| `barrios.encajan.casi` | Casi valen | Con lo que le falta a cada barrio (`resultados.casi.*`) y, si la API no lo dice, «No cumple todo lo que pides.». **Cambia (15 nov, UX móvil 1).** Antes «Casi encajan» |

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
| `falta.intro` | Miramos lo que tiene la gente a 15 minutos andando, repartido entre todos los que lo comparten, y lo comparamos con los demás municipios de su tipo, urbanos o rurales. Por eso algo puede estar cerca y aun así faltar: hay poco para tanta gente. | **Cambia el 15 nov** (prueba con usuarios): suma la última frase, para quien ve un servicio a pocos minutos y FALTA. Cambió el 12 nov por D-217 (antes: «Comparamos cada servicio con los demás municipios de su tipo…») |
| `falta.resumen.falta` | Aquí falta: {lista}. | **Primera línea de «Qué falta»**, encima de las filas y en negrita. {lista} con `fila.lista.*`. Ejemplo: Puente de Vallecas, «Aquí falta: escuelas infantiles.». Fase de mejora, **pendiente de B** |
| `falta.resumen.nada_claro` | Aquí no falta nada claro. | Sin ninguna FALTA pero con alguna JUSTO. Va seguida de `falta.resumen.justo` |
| `falta.resumen.justo` | Van justos: {lista}. | Detrás de `falta.resumen.falta` o de `falta.resumen.nada_claro`. Ejemplo: Fuencarral-El Pardo, «Aquí no falta nada claro. Van justos: escuelas infantiles, colegios y centros de salud.» |
| `falta.resumen.cubierto` | Aquí no falta nada, comparado con municipios parecidos. | **Cambia (15 nov, UX móvil 1).** Todas las filas comparables, CUBIERTO |
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
| `falta.leyenda.a_pie` | Los minutos son andando por la calle, no en línea recta, a paso tranquilo (4 km/h). Es lo que tarda la mitad de la zona: unos vecinos lo tienen más cerca y otros más lejos. | Debajo de los estados. Mismo método que `pitch/metodologia.md` §1.5. Cambia el 12 nov: fuera «desde la mitad de las calles». La misma idea, como ayuda bajo «Lo que tienes aquí» en la tarjeta (`a_pie.mediana`) |
| `a_pie.mediana` | Son los minutos de un vecino típico de la zona: unos lo tienen más cerca y otros más lejos. | Una vez, bajo los hechos de la tarjeta. Es la mediana, dicha en llano. **Cambia (15 nov, UX móvil 1).** Antes «Los minutos andando son los de la mitad de la zona: …» (auditoría §4 n.º 30) |
| `hospital.distancia` | Hospital más cercano: a {n} min andando | Sustituye a «A pie hasta el hospital: {n} min». Hasta 30 min, en minutos. **Más de 30 min: «Hospital más cercano: a unos {km} km»**, con {km} = minutos × 4 / 60, con un decimal (51 min → «a unos 3,4 km»). Andar 51 minutos hasta un hospital no es un dato útil, la distancia sí. Sigue con `hospital.nota`. **Pendiente de B** |
| `falta.filas_pendientes` | Estamos calculando el resto de servicios para esta zona. | Si la API avisa en `warnings` de filas aún no calculadas. Nunca se pintan como SIN DATOS |
| `falta.como` | ¿Cómo lo decidimos? | Enlace a «Cómo lo calculamos», sección «Qué falta» |

**Nombres de las 6 filas** (D-194). La API los manda en `label`; estos son los de respaldo, iguales que `gap_row.label` del catálogo (`data/catalog/features/`):

| Clave | Texto | `fila.mide.*`: qué mide (gap-0.3; la API manda su propia etiqueta en `indicator.label`) |
|---|---|---|
| `fila.escuela_infantil` | Escuelas infantiles | Escuelas infantiles a 15 min andando por cada 1.000 niños de 0 a 4 años, repartidas entre todos los que las tienen cerca |
| `fila.colegio` | Colegios | Aulas de primaria, públicas y concertadas, a 15 min andando por cada 1.000 niños de 5 a 14 años, repartidas entre todos los que las tienen cerca |
| `fila.centro_salud` | Centros de salud | Centros de salud de la red pública de salud de la Comunidad (SERMAS) a 15 min andando por cada 10.000 habitantes, repartidos entre todos los que los tienen cerca |
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

## 5c. «Dónde invertir primero», esquema del método y «No comparable» (PR #32 de B)

| Clave | Texto | Notas |
|---|---|---|
| `invertir.titulo` | Dónde invertir primero | En «Qué falta» sin zona, antes del selector. Aprobado |
| `invertir.intro` | Cuánta gente vive en zonas donde falta cada servicio, y qué zonas van primero porque tienen más gente afectada. | Aprobado |
| `invertir.cifra` | {N} {gente} viven donde faltan {servicio} | Ejemplo: «25.551 niños de 0 a 4 años viven donde faltan escuelas infantiles». {servicio} con `fila.lista.*`. Aprobado |
| `invertir.contexto` | El {pct} % de toda la Comunidad, en {n} zonas. | Con 1: «en 1 zona». Aprobado |
| `invertir.ranking` | Zonas donde faltan {servicio}, de más a menos gente afectada | Aprobado |
| `invertir.resto` | Resto de zonas donde faltan {servicio} | Aprobado |
| `invertir.mas` | Ver {n} zonas más | Con 1: «Ver 1 zona más». Aprobado |
| `invertir.nota` | Solo cuentan las zonas en FALTA. Contamos a toda la gente de la zona que usa ese servicio (por ejemplo, los niños de 0 a 4 años para las escuelas infantiles), con el censo y, en los distritos de Madrid, el padrón. Dentro de una zona, unas calles están mejor servidas que otras. | **Cambia** respecto al borrador de B: fuera «no estimamos nada», porque en los distritos el padrón va escalado al censo (D-209, D-216), y «a la que sirve cada servicio» pasa a «que usa ese servicio». Lo mismo en el párrafo «Dónde invertir primero» de «Cómo lo calculamos» (`metodologia.md` §1.4) |
| `metodo.pasos.titulo` | Cómo decidimos qué falta, en cinco pasos | Aprobado |
| `metodo.paso1` | **Datos abiertos.** Dónde está cada centro y cuánta gente vive en cada zona, de la Comunidad de Madrid y otras fuentes oficiales. | Aprobado |
| `metodo.paso2` | **Lo que hay a 15 min andando.** Por las calles de verdad, a paso tranquilo: un kilómetro. | Aprobado (15 min a 4 km/h = 1 km) |
| `metodo.paso3` | **Repartido entre quienes lo comparten.** Si mucha gente vive alrededor de un centro, lo que ofrece toca a menos. | **Cambia** el título: plural, «quienes lo comparten» (borrador: «quien lo comparte») |
| `metodo.paso4` | **Comparado con municipios parecidos.** Urbanos con urbanos y rurales con rurales. Un distrito de Madrid, con las demás ciudades. | Aprobado |
| `metodo.paso5` | **FALTA, JUSTO o CUBIERTO.** FALTA solo si la diferencia es clara y no es casualidad. | Aprobado |
| `metodo.ejemplo` | Ejemplo, con los datos del 12 de noviembre de 2026: en Puente de Vallecas hay 2,8 escuelas infantiles al alcance a pie por cada 1.000 niños de 0 a 4 años, frente a 4,9 en los municipios parecidos. Es decir, aquí hay 57 por cada 100: FALTA. | Aprobado |
| `fila.zona_pequena` | No comparable | Sustituye a «Zona pequeña para comparar» (D-230). Aprobado |
| `fila.zona_pequena.ayuda` | Aquí vive tan poca gente que, ni siquiera junto con sus vecinos, podemos saber si falta. Por eso no la comparamos. | Aprobado |
| `centros.elige` | Toca uno o varios tipos de centro para verlos en el mapa. | Con varios tipos a la vez. Aprobado |
| `limites.alquiler.ajuste` | Esa media es de todos los contratos en vigor, así que la ajustamos a lo que se pagó en los contratos firmados en 2024 en la misma zona, según la Agencia Tributaria: entre un 5 % y un 26 % más. Aun así, un anuncio de hoy puede pedir más. | Detrás del párrafo del alquiler en «Lo que estos datos no te dicen» (`metodologia.md` §1.8). Aprobado |

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
| `centros.hospital.reparto` | : {a} públicos y {b} privados | Detrás de `centros.recuento.hospital` («5 hospitales en Chamartín: 2 públicos y 3 privados»). En singular, «1 público», «1 privado»; si solo hay de una clase, solo esa. Sin el dato, no sale (D-239) |
| `centros.hospital.dependencia` | Público: de la red del Servicio Madrileño de Salud, aunque lo gestione una empresa («gestión privada»). Privado: el resto. Según el registro de centros sanitarios y la red de hospitales públicos de la Comunidad de Madrid. | Bajo el recuento de hospitales (D-239). **Cambia el 15 nov:** va plegada tras `centros.hospital.que_significa`. Sustituyó a «gestión pública» y «gestión privada» detrás de las camas (D-218): un usuario de la prueba pidió distinguirlos y ahí no se veía |
| `centros.hospital.que_significa` | ¿Qué significa público y privado? | **Nueva, 15 nov** (Mariano: «si tengo que leer todo eso me da algo»). Despliega `centros.hospital.dependencia`. Dice de qué habla, porque va sola bajo el recuento (revisión del PR #70) |
| `centros.hospital.pastilla` | Público · Privado | **Nueva, 15 nov.** Pastilla corta delante del nombre de cada hospital, en la lista y en la etiqueta del punto en el mapa: «Público» rellena y «Privado» con contorno, en el color de los hospitales y con icono (un escudo con una cruz y un edificio de oficinas; no el edificio con columnas, que es el de «Cultura»). Es una palabra, nunca solo un color o un símbolo (WCAG 1.4.1). Sin el dato, no va pastilla |
| `centros.hospital.fila` | [{pastilla}] {nombre} · debajo, en pequeño: {tipo} · gestión privada · ubicación aproximada · a la derecha: [cama] {camas} | **Nueva, 15 nov.** Sustituye a «Hospital público · gestión privada · Hospital Universitario Fundación Jiménez Díaz · 651 camas instaladas». El nombre primero. Debajo, solo lo que haga falta: el tipo si no es un hospital general («Hospital de salud mental»), `centros.hospital.gestion_privada` y «ubicación aproximada». Las camas, con el icono de cama (`BedDouble`) y la cifra; el lector de pantalla oye «651 camas instaladas». Sin nombre, el tipo hace de nombre. En la etiqueta del mapa: «[Privado] Hospital de salud mental» y debajo «Clínica López Ibor · [cama] 67»; en el móvil, solo la primera línea. Esa línea no se parte: si no cabe, el tipo se corta con «…» y la pastilla queda entera (revisión del PR #70) |
| `centros.hospital.gestion_privada` | gestión privada | En pequeño bajo el nombre de los cinco hospitales de la red del Servicio Madrileño de Salud que gestiona una empresa por concesión o concierto singular: Fundación Jiménez Díaz, Rey Juan Carlos, Infanta Elena, Villalba y Torrejón (D-239, `management` de `/places`). **Cambia el 15 nov:** antes iba detrás de «Hospital público ·». En el recuento cuentan como públicos. Nunca junto a «Privado» |
| `centros.recuento.farmacia` | {n} farmacias en {zona} · 1 farmacia en {zona} · Ninguna farmacia en {zona} | |
| `centros.recuento.mayores` | {n} centros de mayores en {zona} · 1 centro de mayores en {zona} · Ningún centro de mayores en {zona} | Hogares, clubes y centros de día; las residencias no salen (la fila es la misma) |
| `centros.recuento.bares` | {n} bares y cafeterías en {zona} · 1 bar o cafetería en {zona} · OpenStreetMap no tiene ningún bar ni cafetería en {zona} | Ocio (D-236). Botón «Bares y cafeterías», icono `Wine`. En la lista, cada local dice si es bar, pub o cafetería. Con 0, la frase dice lo que falta en el mapa, no en la zona |
| `centros.recuento.restaurantes` | {n} restaurantes en {zona} · 1 restaurante en {zona} · OpenStreetMap no tiene ningún restaurante en {zona} | Botón «Restaurantes», icono `Utensils`. Sin comida rápida |
| `centros.recuento.gimnasios` | {n} gimnasios y centros deportivos en {zona} · 1 gimnasio o centro deportivo en {zona} · OpenStreetMap no tiene ningún gimnasio ni centro deportivo en {zona} | Botón «Gimnasios y deporte», icono `Dumbbell` |
| `centros.recuento.cultura` | {n} espacios culturales en {zona} · 1 espacio cultural en {zona} · OpenStreetMap no tiene ningún espacio cultural en {zona} | Botón «Cultura», icono `Landmark`. En la lista, cada sitio dice si es museo, biblioteca, teatro, cine o centro cultural. Antes «Cines y teatros» (14 nov) |
| `centros.ocio.fuente` | Según OpenStreetMap, un mapa hecho por voluntarios: puede faltar algún local o salir sin nombre. | Bajo el recuento de cada tipo de ocio. Los cuatro tipos van en un mismo color en el mapa (`--fac-ocio`) y salen cuando `osm_ocio` está en `/datasets`. Cada tipo se pide a la API al pulsar su botón, nunca con la zona, y «Todos» no los enciende: son servicios de la zona los otros siete |
| `centros.ocio.cargando` | Buscando {tipo} en {zona}… | Mientras llega la petición de un tipo de ocio recién pulsado («Buscando bares y cafeterías en Centro…»). Sin número en su botón hasta entonces |
| `centros.recuento.aparcamiento` | {n} aparcamientos en {zona} · 1 aparcamiento en {zona} · Ningún aparcamiento de los publicados en abierto en {zona} | Botón «Aparcamientos» (D-237): los disuasorios del CRTM junto a estaciones y los públicos, mixtos y para residentes del Ayuntamiento de Madrid. En la lista va su nombre, que ya dice el tipo («Aparcamiento público. Plaza de España»), y del CRTM las plazas y si es gratuito («210 plazas · gratuito»). Contexto: no lo cuenta ninguna fila de «Qué falta». El botón solo sale cuando `/datasets` trae sus datasets, para no enseñar un 0 falso antes de sincronizar, y «Todos» no lo enciende (R-05 y R-06) |
| `centro.detalle` | {nombre} · {capacidad} · ubicación aproximada | Cada parte solo si la API la manda. {capacidad} = `capacity.value` y `capacity.unit` («966 camas instaladas», «120 plazas autorizadas»). «ubicación aproximada» si `coordinates` es `geocoded` (D-216 §3) |

---

## 6. Confianza en palabras

**Cortes de D, confirmados por A el 11 nov.** El 0,5 cuenta como «Dato aproximado» porque es el tope que reciben las zonas con poca población (D-189). La API da la confianza de 0 a 1. En zonas con poca población la baja a 0,5 como máximo, y 0 significa desconocido (`docs/04_technical_architecture/31_public_api_routes.md`, «Reglas que la web puede dar por hechas»).

| Confianza | Clave | Texto | Ayuda (al tocar) |
|---|---|---|---|
| 0,8 o más | `confianza.alta` | Dato fiable | Sale de un registro oficial completo. |
| De 0,5 a menos de 0,8 | `confianza.media` | Dato aproximado | Es una aproximación: la zona tiene poca población, la fuente no está completa o el dato es una estimación. Tómalo como orientativo. **Cambia (D-234, revisión del PR #59):** antes decía «El dato es oficial…», que no vale para el precio estimado de compra (un reparto del valor tasado de Madrid, no un dato publicado) |
| Más de 0 y menos de 0,5 | `confianza.baja` | Dato poco seguro | Faltan bastantes datos en la fuente. Úsalo con cuidado. |
| 0 o sin valor | `confianza.ninguna` | Sin datos | No tenemos este dato. |

| Clave | Texto |
|---|---|
| `confianza.aria` | Fiabilidad del dato: {texto} |

---

## 7. «¿Quieres ver más zonas?» (antes «¿Y si cambias algo?», Reality Check)

Siempre visible bajo «Zonas que te convienen». Va plegado a la opción que más zonas añade y se despliega solo con 5 zonas o menos (decisión de datamad-10; `FEW_ZONES`, PR #10). No salen las opciones que añaden 0 zonas. Las cifras y las etiquetas de cada opción (`label`, por ejemplo «+150 €/mes») llegan de la API. Al tocar una opción, la web reenvía `relaxed_scenario`.

| Clave | Texto | Notas |
|---|---|---|
| `rc.titulo` | ¿Quieres ver más zonas? | **Cambia (15 nov, UX móvil 1).** Antes «¿Y si cambias algo?» (auditoría §4 n.º 8) |
| `rc.ninguna` | No hemos encontrado ninguna zona para ti. | `zones_passing = 0`. **Cambia (15 nov, UX móvil 1).** Antes «Con tu búsqueda tal cual no sale ninguna zona.» |
| `rc.una` | Hemos encontrado 1 zona para ti. | **Cambia (15 nov, UX móvil 1).** |
| `rc.varias` | Hemos encontrado {n} zonas para ti. | **Cambia (15 nov, UX móvil 1).** Antes «Con tu búsqueda tal cual salen {n} zonas.» (auditoría §4 n.º 5). Con «¿Dónde?», el nombre del ámbito: «Hemos encontrado 78 barrios para ti», «34 municipios», «2 pueblos»; con 0, «No hemos encontrado ningún barrio para ti.» (D-238). Igual en `rc.ninguna`, `rc.una`, `rc.cambio`, `rc.opcion.cuenta`, `rc.sin_dato` («No los contamos como buenos») y `vacio.sin_resultados` («Ningún pueblo cumple…») |
| `rc.cambio` | Con este cambio salen {n} zonas. | En lugar de `rc.varias` tras aplicar una opción. Con 1: «Con este cambio sale 1 zona.»; con 0: «Con este cambio no sale ninguna zona.» |
| `rc.intro` | Mira cuántas salen si cambias una sola cosa: | |
| `rc.opcion` | {label} | Primera línea de cada opción |
| `rc.opcion.cuenta` | saldrían {añadidas} más: {n} zonas en total | Segunda línea. {n} = `zones_if_relaxed`, {añadidas} = `added_zones`. Con 1 más: «saldría 1 más: 28 zonas en total». **Cambia (15 nov, UX móvil 1).** Lo que se gana, primero (antes «saldrían {n} zonas, {añadidas} más»). El nombre accesible de la opción es su texto visible (WCAG 2.5.3) |
| `rc.boton` | Ver esas zonas | En cada opción. **Cambia (15 nov, UX móvil 1).** Antes «Probar así» |
| `rc.mas` | Ver todas las opciones | Con el bloque plegado |
| `rc.menos` | Ver menos | |
| `rc.sin_opciones` | Cambiar una sola cosa no añade zonas. | Ninguna opción añade zonas. **Cambia (D-234):** la API ya no manda la opción de una condición que ninguna zona incumple y que no añade zonas (por ejemplo, «+40.000 €» cuando lo que falta es el precio) |
| `rc.sin_dato` | En {n} zonas no podemos comprobarlo todo por falta de datos. No las contamos como buenas. | `zones_unknown` > 0 |
| `rc.sin_dato.compra` | En {n} zonas no podemos comprobarlo todo: sin precio de compra publicado en {m} municipios (solo lo tienen los de más de 25.000 habitantes). No las contamos como buenas. | **Nueva (D-234).** En lugar de `rc.sin_dato` al comprar. {m} = zonas de `all_zones` sin precio (`estimated_cost_eur` vacío), sin ningún FAIL y sin cumplir todo, y todas municipios. Con 1: «en 1 municipio». En «Pueblos», «pueblos». En la búsqueda por barrios se queda `rc.sin_dato` |
| `rc.sin_dato.compra.zonas` | En {n} zonas no podemos comprobarlo todo: sin precio de compra en {m} zonas (el valor tasado de la vivienda solo se publica por municipio, y solo en los de más de 25.000 habitantes). No las contamos como buenas. | **Nueva (D-234).** Si entre las zonas sin precio hay distritos o barrios (código desplegado y estimación sin sincronizar): nunca los llama municipios. Con «¿Dónde?» en Madrid capital, «barrios» |
| `rc.limite` | Lo que más limita tu búsqueda es: {condición} | `binding_constraint`, solo si sus FAIL son al menos tantos como las zonas sin datos (`zones_unknown`). La API también cuenta como excluida una zona donde la condición es UNKNOWN: con alquiler en «Pueblos» decía «Alquiler» sin que ningún pueblo lo superase. Revisión del PR #58 (D-238 §10) |
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
| `carga.busqueda` | Buscando zonas para ti… | **Cambia (15 nov, UX móvil 1).** Antes «Buscando zonas que encajan…» |
| `carga.zona` | Preparando la zona… | Vuelo de cámara y 3D |
| `carga.falta` | Calculando qué falta en {zona}… | |
| `carga.lento` | Está tardando un poco más de lo normal. Gracias por esperar. | Más de 5 s |
| `vacio.sin_busqueda` | Cuéntanos cómo es tu hogar y pulsa «Buscar zonas para mí». | **Cambia (15 nov, UX móvil 1).** |
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
| `pie.contador` | Datos: {n} conjuntos de la Comunidad de Madrid (con los del Consorcio Regional de Transportes) + Ayuntamiento de Madrid + Ministerio de Sanidad + Agencia Tributaria + Ministerio de Vivienda | Página «Cómo lo calculamos» | **Cambia (15 nov, UX móvil 1).** Sin la sigla «CRTM». {n} = `cm_open_data_count` de `GET /api/v1/datasets`: 35 en producción desde el 15 nov (27 el 12 nov; 29 con D-235; 35 con D-237 y D-241). En pantalla, «Datos: 35 conjuntos…» (`evidence/gate-06/2026-11-15-deploy/deploy-31-59187f8-lote4.md`). Cambia el 12 nov: los 6 del CRTM ya están dentro de {n}, y el Ministerio de Sanidad se usa desde D-218. Cambia el 12 nov: suma la Agencia Tributaria (D-228), que no cuenta en {n}; hecho en `counterText` y en producción. Cambia el 15 nov: suma el Ministerio de Vivienda (D-242, el SERPAVI), que tampoco cuenta en {n}; hecho en `counterText` |
| `pie.cm` | Fuente: Comunidad de Madrid — Portal de Datos Abiertos (datos.comunidad.madrid), CC BY 4.0. | https://datos.comunidad.madrid | |
| `pie.crtm` | Powered by CRTM — datos del Consorcio Regional de Transportes de Madrid (www.crtm.es). En bruto: los nombres de las estaciones. Explotados: los minutos hasta las paradas y en transporte público, que calcula Vida Fácil con sus paradas y horarios. | https://www.crtm.es | Obligatorio con enlace. La licencia (§2.2) pide decir si los datos son en bruto o explotados. El `attribution_text` del catálogo, que es lo que enseña la web, dice «Datos en bruto / explotados según el caso» y no dice cuál: **pendiente de A** cambiarlo por este texto en `data/catalog/sources/crtm_open_data.yaml`. Cambia el 12 nov (revisión del PR #22) por el trabajo en minutos de transporte público (D-220) |
| `pie.ayto` | Fuente: Ayuntamiento de Madrid — datos.madrid.es, CC BY 4.0. | https://datos.madrid.es | En uso desde DATA-012 (padrón y panel de distritos). Condiciones vigentes: CC BY 4.0, uso comercial y no comercial (https://datos.madrid.es/pages/condiciones-de-uso, leída el 11 nov); no fijan un texto de cita, así que se usa el `attribution_text` del catálogo con la licencia añadida |
| `pie.osm` | © OpenStreetMap contributors, ODbL. | https://www.openstreetmap.org/copyright | Red peatonal (`osm_red_peatonal`) |
| `pie.sanidad` | Fuente: Ministerio de Sanidad — Catálogo Nacional de Hospitales 2025 (actualizado a 31/12/2024) y Catálogo de Centros de Atención Primaria del SNS 2026 (actualizado a 31/12/2025). | https://www.sanidad.gob.es/estadEstudios/estadisticas/sisInfSanSNS/ofertaRecursos/hospitales/home.htm | **Nuevo, obligatorio:** el aviso legal pide citar la fuente y la fecha de actualización (`data/catalog/sources/ministerio_sanidad.yaml`, D-218 §1). Hoy la web no lo cita |
| `pie.cartociudad` | Geocodificación: © Instituto Geográfico Nacional (CartoCiudad), CC BY 4.0 scne.es. | https://www.cartociudad.es | **Nuevo, obligatorio.** Es la forma de cita que pide el IGN (PR #18, 12 nov). coloca los centros marcados «ubicación aproximada» (`data/catalog/sources/ign_cartociudad.yaml`, D-216 §3). Hoy la web no lo cita |
| `pie.mapa_base` | Mapa: OpenFreeMap © OpenMapTiles. Datos de © OpenStreetMap. | openfreemap.org · openmaptiles.org · openstreetmap.org/copyright | Texto del ejemplo de OpenFreeMap. Hecho: el mapa de producción ya pinta «OpenFreeMap © OpenMapTiles Data from OpenStreetMap» en su esquina, así que en el pie no se repite (capturas `prod_*` de `evidence/map-004/2026-11-11/`) |
| `pie.independiente` | Vida Fácil no es un servicio de la Comunidad de Madrid, del Ayuntamiento, del CRTM, del Ministerio de Sanidad, de la Agencia Tributaria ni del Ministerio de Vivienda. | | Cumple el «no sugerir respaldo» del CRTM y evita parecer un servicio oficial. Cambia el 12 nov: suma el Ministerio. Cambia el 12 nov: suma la Agencia Tributaria (D-228). **Pendiente de B** (`SiteFooter.tsx`). Cambia el 15 nov: suma el Ministerio de Vivienda (D-242); hecho en `SiteFooter.tsx` |
| `pie.mivau` | Ministerio de Vivienda y Agenda Urbana, Sistema Estatal de Referencia del Precio del Alquiler de Vivienda (SERPAVI), base de datos 2011-2024, actualizada el 9 de marzo de 2026. | https://www.mivau.gob.es/vivienda/alquila-bien-es-tu-derecho/serpavi | **Nuevo, obligatorio (D-242):** el aviso legal del Ministerio pide citar la fuente y la fecha de actualización. Es el `attribution_text` de `data/catalog/sources/ministerio_vivienda.yaml`: el pie y el (i) del mapa lo enseñan al leer `/datasets` tras el sync, con su enlace. No está en `ATTRIBUTIONS_FALLBACK`, que sigue al fixture `dataset_list.all` (se regenera tras el despliegue) |
| `pie.aeat` | Agencia Tributaria, Estadística de viviendas declaradas en IRPF, ejercicio 2024 (metodología de 01/07/2026): alquiler medio y m² medios de todos los contratos y de los contratos formalizados en 2024. | https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/irpfvivienda/2024/home.html | **Nuevo, obligatorio:** el aviso legal de la AEAT pide citar la fuente y la fecha de la última actualización. Es el `attribution_text` de `data/catalog/sources/agencia_tributaria.yaml`, así que el pie y el (i) del mapa ya lo enseñan si leen `/datasets`. Falta en `ATTRIBUTIONS_FALLBACK` (**pendiente de B**) |
| `pie.proyecto` | Vida Fácil · Proyecto para DATAMAD 2026 | | Cambia el 12 nov: un solo nombre visible, «Vida Fácil» (jurado simulado). «Housing Intelligence» solo queda en el nombre del repositorio, que se ve en el enlace del código. **Pendiente de B** (`SiteFooter.tsx`, `TEXT.project`) |
| `pie.codigo` | Código abierto (Apache-2.0) | https://github.com/marianohernando/housing-intelligence | D-191 |
| `pie.como` | Cómo lo calculamos | Pestaña | |
