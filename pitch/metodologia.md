# «Cómo lo calculamos» — contenido de la pestaña

Para la línea B. La **parte 1** es el texto de la pestaña, en español llano. La **parte 2** es interna: de dónde sale cada afirmación y qué falta.

**Marcas en la parte 1:**
- Los párrafos con **[pendiente de A: …]** no se publican hasta que A lo tenga hecho. Si el 16 nov no existe, B quita el párrafo entero; no se deja un hueco ni un «próximamente».
- **Cambio del 11 nov (D-213):** la sección 1.4 sustituye la comparación con toda la región por la comparación con los municipios del mismo tipo. B tiene que cambiar la tabla de estados y el ejemplo de «Cómo lo calculamos», y la primera de las «Tres reglas» (1.1).
- **Cambio del 12 nov, noche (D-220, `fit-0.2`):** el trabajo cuenta en minutos de transporte público llegando a las 9:00 (sección 1.3). En producción desde el despliegue de `28a0f2f` (12 nov, `fit-0.3`).
- **Cambio del 12 nov, noche (D-222, D-223, D-224):** «Sin escaleras» puntúa los minutos andando hasta una estación accesible (`fit-0.4`, en producción desde el despliegue de `2761696`). Las zonas verdes ya están en la API (`fit-0.3`), pero la web todavía no enseña su chip. La seguridad no puntúa; en los distritos de Madrid, lo que dicen los vecinos va como contexto (D-226). Cambian las secciones 1.3, 1.7, 1.8 y 1.10.
- **Cambio del 12 nov (D-217, `gap-0.3`):** las filas de servicios ya no cuentan centros por habitante: miden la capacidad que se tiene a 15 minutos andando, repartida entre quienes la comparten (2SFCA), y los pueblos muy pequeños se comparan junto con sus vecinos. Cambian las secciones 1.4, 1.5, 1.7, 1.8 y 1.10. Este texto sustituye al provisional de B (PR #13).

**Estado en producción (12 nov):** B ya cambió la tabla de estados y la primera de las «Tres reglas» (1.1). Con gap-0.3 escribió un texto provisional del 2SFCA, de los vecinos y del hospital (`apps/web/src/app/(vida)/como-lo-calculamos/page.tsx`), que dice que «las camas de cada hospital tampoco las tenemos todavía». Desde D-218 la web sí enseña las camas de cada hospital en «Todos los centros». Las diferencias con este texto están en la descripción del PR #3 y en `pitch/textos_web.md`, «Novedades del 12 nov».

---

## Parte 1 · Texto de la pestaña

### 1.1 Tres reglas que seguimos siempre
- Comparamos cada zona con los demás municipios de la Comunidad de Madrid de su mismo tipo, urbanos o rurales, siempre según cuánta gente vive en ella.
- Si un dato no existe, lo decimos: «sin datos» no es lo mismo que cero.
- Cada dato dice de dónde sale y cuánto podemos fiarnos de él.

### 1.2 Qué zonas comparamos
Los 179 municipios de la Comunidad de Madrid. Madrid capital no va como un solo bloque: la dividimos en sus 21 distritos, porque no es lo mismo vivir en un distrito que en otro. En el buscador son 199 zonas: los otros 178 municipios y los 21 distritos. En «Qué falta» también puedes ver Madrid entera.

### 1.3 Cómo sale el % de encaje
El % de encaje dice **cuánto se parece una zona a lo que tú buscas**. No es una nota de la zona: la misma zona puede encajar mucho con una familia con niños y poco con una persona mayor que vive sola.

**Paso 1. Lo imprescindible.** Miramos tus condiciones en cada zona, por ejemplo tu presupuesto o tener un colegio cerca. Cada condición puede salir de tres maneras:
- **Cumple.**
- **No cumple.**
- **No lo sabemos**, porque falta el dato. En ese caso no la damos por buena.

Solo te enseñamos como «zonas que encajan» las que cumplen todo. Las que fallan en una sola cosa salen aparte, en «Casi encajan», para que decidas tú.

**Paso 2. Lo que te importa.** Entre las zonas que cumplen, cada cosa que te importa recibe una nota de 0 a 1, y pesa más lo que marcaste primero. Con 5 cosas, la primera cuenta un 33 %, la segunda un 27 %, la tercera un 20 %, la cuarta un 13 % y la quinta un 7 %. El % de encaje es la media de esas notas con sus pesos.

Así se pone cada nota:
- **Un servicio a pie** (colegio, centro de salud o parada): vale 1 si está a la distancia que consideramos cerca y baja hasta 0 al triple de ese tiempo. Un colegio a 10 min vale 1; a 20 min, 0,5; a 30 min o más, 0. Para el centro de salud, cerca son 15 min, y para la parada, 5.
- **El trabajo:** contamos los minutos reales en transporte público para llegar a las 9:00, con los horarios que publica el Consorcio Regional de Transportes: metro, Metro Ligero, Cercanías y autobuses. Es el tiempo de puerta a puerta, contando lo que se anda hasta la parada: la mitad de la zona llega en ese tiempo o menos. Vale 1 hasta 30 minutos y baja hasta 0 a los 90. Si con los horarios publicados no se llega a las 9:00, cuenta como lo peor, pero con menos fiabilidad, porque puede faltar algún horario.
- **El margen de presupuesto:** vale 1 si la zona te cuesta el 75 % de tu presupuesto o menos, y 0 si te lo come entero.
- **«Sin escaleras»** (solo si lo marcas): los minutos andando hasta la estación de metro, Metro Ligero o Cercanías accesible más cercana. Vale 1 hasta 10 min y baja hasta 0 a los 30. Si no hay ninguna a un paseo, vale 0, con poca fiabilidad, y la tarjeta lo dice.
- **Zonas verdes** (solo si lo marcas): igual, con el parque urbano más cercano. **[pendiente de B: el chip de zonas verdes. Si el 16 nov la web no lo enseña, B quita este punto.]**
- **Si a una zona le falta un dato,** nunca cuenta como 0: sale «sin datos» y baja la fiabilidad del %.
- **La seguridad no la puntuamos.** Te contamos por qué en la sección 1.8.

**Debajo del %** van entre 3 y 5 hechos que puedes comprobar, como «Colegio con primaria a 5 min andando», y cada uno dice cuánto nos fiamos del dato.

**Ejemplo real.** Una pareja con 2 hijos de 4 y 8 años trabaja en la Castellana, puede pagar 1.500 € al mes y quiere un colegio a 10 min andando como mucho. Le importan, por este orden, los colegios, el transporte y la salud. Encajan 33 de las 199 zonas. La primera es Fuencarral-El Pardo, con un 100 %: colegio a 9 min, parada a 3 min, centro de salud a 15 min, 29 min en transporte público hasta la Castellana llegando a las 9:00 y unos 1.107 € al mes por 77 m². Ciudad Lineal, a 33 min, y Hortaleza, a 32, empatan detrás con un 99 %. Lo que más zonas le quita es el colegio a 10 min: con 5 min más aparecen 17 zonas.

**El alquiler estimado** es el alquiler medio por metro cuadrado de la zona multiplicado por los metros de tu hogar. Si no nos dices cuántos necesitas, usamos los de la vivienda mediana de los hogares de tu tamaño en la Comunidad de Madrid, según el Censo 2021 del INE: 61 m² para una persona, 68 para dos, 71 para tres y 77 para cuatro o más. Si cabe en tu presupuesto, cumple; si no, no cumple; y si la zona no tiene alquiler publicado, no lo sabemos y no lo damos por bueno.

**Ojo: el alquiler estimado es orientativo y tira a la baja.** La Comunidad publica la media de los alquileres declarados a Hacienda, es decir, de los contratos ya firmados, no de los pisos que se anuncian hoy, y un contrato nuevo suele costar más. Además, esos metros son construidos, no útiles, así que el precio corresponde a un piso algo más pequeño. Por eso, si te decimos que una zona no entra en tu presupuesto, puedes fiarte; si te decimos que sí, cuenta con que puede costar algo más.

### 1.4 Cómo decidimos qué falta en una zona
**Lo que tienes a 15 minutos andando, repartido entre quienes lo comparten.** Para cada servicio miramos qué tiene la gente de la zona a 15 minutos andando: un kilómetro por la calle, a paso tranquilo (4 km/h). No basta con que esté cerca: si mucha gente vive alrededor de un colegio, sus aulas se reparten entre más niños. Por eso hacemos dos pasos:
1. Para cada centro, repartimos lo que ofrece entre todas las personas que viven a 15 minutos andando o menos de él.
2. Para cada calle, sumamos lo que le toca de cada centro que tiene a 15 minutos.

La zona tiene la media de sus calles, según cuánta gente vive en cada una. Así, un colegio en el límite de dos distritos sirve a los dos, y quien vive a más de 15 minutos de todos no suma nada en esa fila.

**Qué cuenta en cada servicio.** Solo lo que se publica; nunca nos lo inventamos centro a centro.
- **Escuelas infantiles,** para niños de 0 a 4 años: cada escuela, pública o privada, cuenta como una, porque nadie publica sus plazas.
- **Colegios,** para niños de 5 a 14 años: aulas de primaria públicas y concertadas. La Comunidad publica cuántas tiene cada municipio, no cada colegio, así que las repartimos a partes iguales entre sus colegios.
- **Centros de salud,** para todos los vecinos: cada centro de salud del SERMAS cuenta como uno. Los consultorios locales son del mismo equipo médico: cuentan para los minutos a pie, no como más capacidad.
- **Mayores,** para personas de 65 años o más: plazas autorizadas en hogares, clubes y centros de día. Las residencias van aparte.
- **Farmacias,** para todos los vecinos: cada farmacia cuenta como una.
- **Vivienda,** para hogares de 4 o más personas: no va a pie. Contamos las viviendas de más de 90 m² por cada 100 de esos hogares.

**Con qué comparamos.** Hacemos la misma cuenta en **los demás municipios de su mismo tipo** en la Comunidad de Madrid: los rurales con los rurales y los urbanos con los urbanos. Rural es lo que dice la ley de medio rural: menos de 30.000 habitantes y menos de 100 por km². Los distritos de Madrid son urbanos. Una zona nunca se compara consigo misma: un distrito de Madrid se compara con los demás municipios urbanos, sin contar Madrid.

¿Por qué no con toda la región? Porque un pueblo pequeño suele tener su escuela infantil y pocos niños: a pie y por niño, los municipios rurales tienen más del doble de escuelas infantiles que los urbanos (unas 12 por cada 1.000 niños, frente a menos de 5). Con la media de toda la región, a cualquier ciudad le faltaría de todo.

| Si la zona tiene… | Sale |
|---|---|
| menos del 80 % de lo que tienen los municipios de su tipo, y la diferencia no se explica por el tamaño de la zona | **FALTA** |
| menos de lo que tienen los municipios de su tipo, pero sin llegar a FALTA | **JUSTO** |
| lo mismo o más | **CUBIERTO** |
| tan poca gente que, ni junto con sus vecinos, podemos saber con seguridad si falta | **Zona pequeña para comparar** (nunca sale FALTA) |
| no tenemos el dato | **SIN DATOS** |

**¿Por qué el tamaño importa?** En una zona con poca gente, un centro más o menos cambia mucho la cuenta. Por eso, para decir FALTA pedimos además que la diferencia sea demasiado grande para ser casualidad. Es la misma prueba que usan los indicadores de salud pública de Inglaterra.

**Los pueblos pequeños, junto con sus vecinos.** Si en un municipio vive tan poca gente que no se puede comparar solo, lo juntamos con sus vecinos más cercanos del mismo tipo, a 15 km como mucho en línea recta, hasta tener un grupo con el que sí se puede. Es más o menos el tamaño de las zonas de salud rurales de la Comunidad, con las que esos pueblos ya se organizan. Su estado es entonces el del grupo, y la fila lo dice: «Comparado con municipios parecidos de la zona», con los nombres de esos vecinos. Si ni así se llega, sale **zona pequeña para comparar**. Por ejemplo, La Acebeda, con 70 habitantes, no tiene ninguna farmacia a 15 minutos andando, pero ni junto con sus vecinos hay gente suficiente para decir que le falta. Los distritos de Madrid no se juntan: tienen gente de sobra para compararlos solos.

**Ejemplo real.** En Puente de Vallecas la escuela infantil más cercana está a unos 6 minutos andando, pero son pocas para tantos niños: 2,8 al alcance a pie por cada 1.000 niños de 0 a 4 años, frente a 4,9 en los demás municipios urbanos. Con tantos niños, no es casualidad: sale **FALTA**. En Centro la cifra es parecida, pero con menos niños la diferencia podría ser casualidad: sale **JUSTO**.

**El hospital.** En la fila de centros de salud verás también los minutos a pie hasta el hospital general más cercano, público o privado. Es una pista de dónde pueden quedar las urgencias, no un dato de urgencias: ninguna fuente abierta dice qué hospitales las tienen abiertas las 24 horas. No cuenta para el estado de la fila: a un hospital no se va andando a elegir. En «Todos los centros» de cada zona verás el nombre y las camas instaladas de los hospitales que hemos podido identificar en el Catálogo Nacional de Hospitales del Ministerio de Sanidad; de unos pocos solo sabemos el tipo y el municipio.

Es una señal para saber dónde mirar primero, no un veredicto: comparamos con zonas parecidas, no con una norma oficial que diga cuánto debería haber.

### 1.5 Distancias a pie
Medimos lo que tardarías andando por las calles de verdad, no en línea recta, a un paso tranquilo de 4 km/h, con el mapa de calles de OpenStreetMap. Desde cada calle donde vive gente calculamos cuánto se tarda hasta lo más cercano: escuela infantil, colegio con primaria (público o concertado), centro de salud o consultorio, farmacia, centro de mayores, hospital general y parada de autobús, metro o Cercanías. En cada fila de «Qué falta» verás los minutos en los que se llega desde la mitad de las calles de la zona. Son los mismos 15 minutos de la sección 1.4: lo que queda más lejos no cuenta como «al alcance a pie». A ese paso, 10 minutos son unos 670 metros. Si en una zona no hay calles en el mapa, sale «sin datos», nunca cero. Usamos el mismo paso que el estudio «El Madrid de los 15 minutos» del Ayuntamiento.

### 1.6 Qué significa la fiabilidad
Cada dato lleva una de estas etiquetas:
- **Dato fiable:** sale de un registro oficial completo.
- **Dato aproximado:** es oficial, pero la zona tiene poca población o la fuente no está completa.
- **Dato poco seguro:** faltan bastantes datos en la fuente.
- **Sin datos:** no lo tenemos.

Usamos estas etiquetas según la fiabilidad del dato, que va de 0 a 1:
- **0,8 o más:** dato fiable.
- **De 0,5 a menos de 0,8:** dato aproximado.
- **Más de 0 y menos de 0,5:** dato poco seguro.
- **0:** sin datos.

El 0,5 cuenta como aproximado porque es la fiabilidad que reciben siempre las zonas con poca población.

La fiabilidad baja en estos casos:
- **Zonas con poca población.** En un pueblo pequeño, un solo centro más o menos cambia mucho la cuenta, así que el dato cuenta como aproximado. Pasa con menos de 200 niños de 0 a 4 años en escuelas infantiles, menos de 300 niños de 5 a 14 años en colegios, menos de 2.000 habitantes en centros de salud y en farmacias, menos de 300 personas mayores en mayores y menos de 100 hogares de 4 o más personas en vivienda.
- **Aulas repartidas.** En colegios el dato es aproximado como mucho, porque las aulas de cada municipio se reparten a partes iguales entre sus colegios. Esto mide cuánto nos fiamos del dato; si la zona es demasiado pequeña para comparar, se ve aparte (sección 1.4).
- **Fuentes incompletas.** Por ejemplo, si de algunas residencias no se publica cuántas plazas tienen, cuanto mayor es esa parte, menos nos fiamos.
- **Cuentas aproximadas.** Por ejemplo, la fuente agrupa los hogares de «5 o más personas» y los contamos como de 5.

### 1.7 Qué datos usamos
- **26 conjuntos de datos del Portal de Datos Abiertos de la Comunidad de Madrid:** población, hogares, vivienda, renta, alquiler, colegios y sus aulas, salud y camas de hospital de la región, mayores y farmacias. También los del Consorcio Regional de Transportes de Madrid, que se publican en ese mismo portal: las 6 redes de transporte público y la accesibilidad de las estaciones de metro, Metro Ligero y Cercanías.
- **Como apoyo,** sin contarlos como datos de la Comunidad:
  - el padrón y el panel de distritos del Ayuntamiento de Madrid, para la población y los hogares de cada distrito de Madrid capital;
  - el mapa de calles y los parques de OpenStreetMap, para las distancias a pie;
  - los catálogos de hospitales y de centros de atención primaria del Ministerio de Sanidad, para el nombre de los centros de salud y el nombre y las camas de los hospitales;
  - el geocodificador oficial CartoCiudad del IGN, solo para colocar los pocos centros que el registro publica sin coordenadas o con coordenadas que contradicen su dirección.
- **Antes de usar un conjunto,** pasa un control de calidad: que no haya registros repetidos, que cada municipio exista, que los errores queden apartados y que un dato que falta no se convierta en un cero.
- **Cada resultado** dice de qué conjuntos sale, con el enlace a su ficha en el portal, su versión y su licencia.
- **Ver la lista completa** (enlace a `pitch/datasets_cm.md` en el repositorio).

### 1.8 Lo que estos datos no te dicen
- **Solo usamos la capacidad que se publica.** De las escuelas infantiles, los centros de salud y las farmacias no se publican plazas ni médicos, así que cada uno cuenta como uno. Las aulas de primaria son las del municipio repartidas entre sus colegios. Las plazas de mayores son autorizadas: no sabemos cuántas están libres.
- **Medimos lo que tienes andando.** No lo que tienes en coche o en autobús, que en los pueblos también cuenta. Y quien vive a más de 15 minutos de cualquier centro no suma nada en esa fila.
- **Colocamos a la gente por calles.** Sabemos cuánta gente vive en cada municipio y en cada distrito de Madrid, no en cada portal: la repartimos entre sus calles según su longitud.
- **Las camas de hospital no cuentan en la lista.** Las enseñamos en los hospitales que hemos podido identificar, pero no deciden si a una zona le falta algo: para eso haría falta medir el viaje en coche o en transporte público.
- **Vivienda:** comparamos las viviendas grandes con los hogares grandes, no el mercado. No sabemos cuántas están libres ni a qué precio.
- **Alquiler:** la Comunidad publica el precio medio de 37 municipios (los de más de 20.000 habitantes con contratos suficientes) y el de los códigos postales de Madrid capital. En el resto no tenemos el dato y lo decimos. Para cada distrito de Madrid hacemos la media de sus códigos postales, y cada código pesa según cuántos colegios, centros de salud y centros sociales del distrito están en él, porque eso aproxima dónde vive la gente. Es una aproximación, así que cuenta con menos fiabilidad. Cuadra con la cifra oficial: con los distritos sale 14,5 € el metro cuadrado, y la Comunidad publica 15,1 para todo Madrid.
- **Compra:** todavía no tenemos precios oficiales de compra por zona, así que no podemos comprobar si una zona entra en tu presupuesto: sale «sin datos» y no inventamos un precio.
- **La seguridad no la puntuamos.** El dato oficial son los delitos conocidos por cada 1.000 vecinos. Pero los delitos se cuentan donde se denuncian o donde actúa la policía, no donde vive quien los sufre. Por eso un municipio con mucha actividad sale peor aunque sus vecinos no vivan con más riesgo. Además, solo existe para 36 de las 199 zonas, y para Madrid capital solo hay una cifra de toda la ciudad, no una por distrito. Ordenar zonas con ese dato señalaría municipios por la actividad que reciben, no por la seguridad de quien vive en ellos. Nunca usamos datos sobre las personas, como la nacionalidad, ni ponemos etiquetas a ninguna zona.
  - **En los 21 distritos de Madrid** te contamos, solo como contexto, cómo valoran los vecinos la seguridad de su barrio, de día y de noche, de 0 a 10. Sale de la Encuesta de calidad de vida del Ayuntamiento de 2025, con unas 400 personas por distrito. No puntúa, no ordena zonas y no entra en «Qué falta». **[pendiente de B: si la web no lo enseña el 16 nov, B quita este punto.]**
- **«Sin escaleras»:** solo miramos las estaciones de metro, Metro Ligero y Cercanías que el Consorcio da como totalmente accesibles. Las que lo son solo en parte no cuentan. No medimos los autobuses: según el Consorcio todos son accesibles, así que no distinguen una zona de otra. Tampoco medimos las aceras, los portales ni los ascensores de los edificios. Los minutos son a 4 km/h, como todo lo demás: si vas más despacio, tardarás más. Y solo cuenta si lo marcas: nunca lo deducimos de nada.
- **Zonas verdes:** contamos los parques de 1 hectárea o más de OpenStreetMap, medidos andando hasta su borde. No cuentan el campo ni los bosques de los pueblos, ni las plazas y jardines pequeños. **[pendiente de B: el chip de zonas verdes. Si el 16 nov la web no lo enseña, B quita este punto.]**
- **No enseñamos pisos en venta ni en alquiler.** Te ayudamos a elegir zona; el piso lo buscas donde prefieras.
- **Todavía no sabemos qué echan en falta los vecinos.** Hoy todo sale de datos oficiales. Más adelante queremos sumar lo que la gente diga que necesita, siempre de forma anónima y por zonas.
- **Transporte público:** usamos los horarios que publica el Consorcio para un día laborable, no los tiempos reales de cada día. Algunas líneas interurbanas no publican sus horarios completos, y desde algunas zonas de la Sierra Norte y del sureste no se llega al centro de Madrid a las 9:00 con esos horarios. Lo decimos, y nunca cuenta como 0.
- **Cada dato tiene su fecha.** Algunos horarios de transporte son los últimos publicados aunque ya estén caducados (el del metro venció en mayo de 2026). Lo avisamos.

### 1.9 Tu privacidad
No te pedimos nombre ni cuenta. Solo trabajamos con datos de zonas, nunca de personas.

### 1.10 Versiones
- Método de «Qué falta»: `{method.version}` (hoy, `gap-0.3`).
- Método del encaje: `{methodology_version}` (hoy, en producción, `fit-0.4`).

---

## Parte 2 · Notas internas: de dónde sale cada afirmación

| Sección | Afirmación | Fuente | Estado |
|---|---|---|---|
| 1.2 | 179 municipios + 21 distritos, con su nombre oficial («Redueña», «Griñón», «El Álamo», «Vicálvaro») | `evidence/gate-01/2026-10-20/cm_secciones_censales/row_counts.json` · D-200 · D-209 · nombres: D-212 (`evidence/gate-01/2026-11-11/phase-data022-f1.txt`) | Hecho (DATA-012, `be40c2f`; DATA-022, `c4f1bc0`) |
| 1.7 | Ayuntamiento como apoyo | `pitch/datasets_cm.md` §3 (`ayto_padron_municipal`, `ayto_panel_indicadores_distritos_barrios`) · D-209 | Hecho |
| 1.3 | Condiciones PASS / FAIL / UNKNOWN; UNKNOWN nunca es PASS; `results` solo con todo en PASS; `near_misses` con una sola condición fallida | D-215 (puntos 2 y 7) · `packages/domain/src/hi_domain/fit.py` y `search.py` · `CLAUDE.md` §14 · `docs/04_technical_architecture/31_public_api_routes.md` | Hecho en la API (CORE-003, `1507deb`, `915be3c`; `POST /api/v1/search`) y en producción desde el 11 nov (web de B, PR #10; encendido por C, PR #11: `evidence/gate-06/2026-11-11-deploy/deploy-12-buscador.md`) |
| 1.3 | % de encaje, no nota; 3–5 hechos con su confianza | D-202 · D-215 (punto 7, `facts`) · `search.py` (`match_pct`, `facts`) | Hecho (CORE-003) |
| 1.3 | Pesos por orden: con 5 criterios, 33 / 27 / 20 / 13 / 7 %; % = media ponderada × 100 | D-215 (puntos 3, 4 y 6: rank sum) · `fit.py` (`fit-0.1`) | Hecho |
| 1.3 | Curvas: servicio a pie, 1 hasta su ventana y 0 al triple (colegio 10/30, centro de salud 15/45, parada 5/15); trabajo, 1 hasta 30 min en transporte público (o el límite, si lo hay) y 0 al triple; margen, 1 con el 75 % del presupuesto o menos | D-215 (punto 5) · D-220 §8 (`fit-0.2`) · `fit.py` · ventanas de D-210 | Hecho y en producción desde el 12 nov (`fit-0.3`, despliegue de `28a0f2f`: `evidence/gate-06/2026-11-12-deploy/deploy-17-pub001.md`) |
| 1.3 | Sin datos nunca es 0 y baja la confianza | D-215 (puntos 5 y 6) | Hecho |
| 1.3 | «Sin escaleras» y zonas verdes: 1 hasta 10 min y 0 a los 30; a más de 30, 0 con confianza ≤ 0,5 y el hecho «Sin estación de metro o tren accesible a un paseo (no mide autobuses, aceras ni portales)» o «Sin parque urbano de 1 ha o más a un paseo (el campo no cuenta)». No es UNKNOWN porque un pueblo sin estación quedaría por delante de una ciudad con la estación a 25 min | D-223 §7 (`fit-0.4`) · D-222 §7 (`fit-0.3`) · `hi_domain/fit.py` (`PRIORITY_WALK`) · `evidence/gate-04/2026-11-12/golden-search-sin-escaleras.txt` | «Sin escaleras»: hecho y en producción desde el 12 nov (despliegue de `2761696`, `evidence/gate-06/2026-11-12-deploy/deploy-18-pub002.md`). Zonas verdes: en la API (`fit-0.3`, desplegado el 12 nov); el chip, **pendiente de B** |
| 1.3 | Trabajo: minutos de puerta a puerta en transporte público para llegar a las 9:00 (mediana de 8:30, 8:45 y 9:00), con los 6 GTFS del CRTM, desde las 4.417 secciones hasta 379 estaciones y el centro de cada zona; la zona, mediana de sus secciones; «no se llega» puntúa lo peor con confianza 0,5; confianza 0,7 hasta una estación y 0,6 hasta el centro de una zona | D-220 §1–4 y §8 · `packages/domain/src/hi_domain/access/transit.py` · `services/features/src/hi_features/commute.py` · `evidence/gate-03/2026-11-12/commute-matrix.md` | Hecho (CORE-009 F3) y en producción desde el 12 nov (despliegue de `28a0f2f`) |
| 1.3 | Caso de la Castellana con `fit-0.2`: 33 de 199 zonas; Fuencarral-El Pardo 100 % (colegio 9 min, parada 3, centro de salud 15, 29 min en transporte público, ≈ 1.107 €/mes por 77 m²); Ciudad Lineal (33 min) y Hortaleza (32 min), 99 %; colegio +5 min, +17 zonas | D-220 §8 · `evidence/gate-04/2026-11-12/golden-search-commute.txt` (`golden_family`, base local) · `data/fixtures/contracts/scenario_state.familia_castellana.fixture.json` | Hecho y en producción: `POST /api/v1/search` con el fixture (12 nov, `fit-0.3`) da 33 de 199, Fuencarral-El Pardo 100 % («29 min en transporte público hasta Paseo de la Castellana (Azca), llegando a las 9:00»), Ciudad Lineal y Hortaleza 99 %, y «+5 min a pie hasta colegio con primaria» saldrían 50 zonas, 17 más |
| 1.3 | Alquiler estimado = €/m² de la zona × m² del hogar; PASS / FAIL / UNKNOWN | D-214 (punto 1) · `packages/domain/src/hi_domain/affordability.py` · `data/catalog/features/alquiler_m2_mensual.yaml` | Hecho (CORE-006, `92eab6b`) |
| 1.3 | m² supuestos: 61 / 68 / 71 / 77 / 77 (mediana de los hogares de cada tamaño en la CM) | D-214 (punto 2) · INE, Censo de Población y Viviendas 2021, tabla 59524, «Viviendas familiares principales convencionales según tamaño del hogar por superficie» (https://www.ine.es/jaxi/Tabla.htm?tpx=59524&L=0, título comprobado el 11 nov) · `affordability.py` | Hecho |
| 1.3 | Orientativo y a la baja: media de contratos vigentes declarados en el IRPF, no de anuncios; m² construidos del Catastro | D-214 (punto 3) · ficha del portal CM, campo «Fuente»: «Estadística de Viviendas Declaradas en el Impuesto sobre la Renta de las Personas Físicas. Agencia Estatal de Administración Tributaria» (https://datos.comunidad.madrid/dataset/1934259, leída el 11 nov) · `limitations` de `alquiler_m2_mensual.yaml` | Hecho (límite declarado) |
| 1.4 | Referencia = los demás municipios del mismo tipo (rural o urbano, Ley 45/2007 art. 3.a: < 30.000 hab. y < 100 hab./km²), sin el municipio de la zona; los distritos heredan el tipo de su municipio | D-213 (punto 1), que D-217 mantiene · `apps/api/src/hi_api/services/gap_reference.py` · `evidence/gate-04/2026-11-11/phase-gap001-f5-review.txt` (84 rurales, 95 urbanos) | Hecho. En producción con `gap-0.3` desde el 12 nov: `GET /api/v1/gaps/distrito/2807913` da `method.version: gap-0.3` |
| 1.4 | ¿Por qué no con toda la región?: a pie y por niño, más del doble de escuelas infantiles en los rurales (unas 12 por cada 1.000 niños) que en los urbanos (menos de 5) | Cada zona tiene su referencia, porque deja fuera su propio municipio: «Otros municipios rurales», de 12,13 a 12,86, y «Otros municipios urbanos», de 4,531 a 4,87 (`GET /api/v1/gaps?level=municipio&row=escuela_infantil`, gap-0.3; `evidence/map-004/2026-11-12/cifras/cifras_api.json` de B, PR #18). El cociente va de 2,49 a 2,84: «más del doble» vale para todas. Con el mismo texto que la web (PR #18). Con `gap-0.2` eran 14,8 veces más centros de atención primaria (D-213, tabla χ²), pero contaban los consultorios, que ya no son capacidad | Hecho |
| 1.4 | FALTA = ratio < 0,8 y significativa (intervalo exacto de Poisson al 95 %); CUBIERTO = ratio ≥ 1; JUSTO, el resto | D-213 (punto 2: regla de los cuatro quintos, Garwood, Fingertips, Spiegelhalter 2005) | Hecho |
| 1.4 | Zona pequeña para comparar (casos esperados < 3,69, también con los vecinos): nunca FALTA; La Acebeda, sin farmacia a pie y con 70 habitantes | D-213 (punto 3) · D-217 §6 · en producción, `GET /api/v1/gaps?level=municipio&row=farmacia` (12 nov): La Acebeda, JUSTO, valor 0, `reliable: false`, `comparison_group: null` | Hecho |
| 1.4 | Ejemplo: Puente de Vallecas, escuelas infantiles, FALTA: 2,781 frente a 4,87 (ratio 0,571); la más cercana, a 6,258 min (mediana de las calles); Centro, ratio 0,661, JUSTO | Producción, 12 nov: `GET /api/v1/gaps/distrito/2807913` (`gap-0.3`, `data_version: 2026-11-12`) y `GET /api/v1/gaps?level=distrito&row=escuela_infantil` | Hecho. Sustituye al de Madrid capital, que con `gap-0.3` sale JUSTO en centros de salud (0,3603 frente a 0,3799; D-217 §7) |
| 1.4 | Las 6 filas, qué cuenta como capacidad y para quién | D-217 §3 (tabla) · `gap_row` y `formula` de `data/catalog/features/`: `escuelas_infantiles_a_pie_por_1000_ninos.yaml`, `aulas_primaria_a_pie_por_1000_ninos.yaml`, `centros_salud_a_pie_por_10000_hab.yaml`, `plazas_mayores_a_pie_por_100_mayores.yaml`, `farmacias_a_pie_por_10000_hab.yaml` y `viviendas_grandes_por_100_hogares_grandes.yaml` | Hecho (DATA-AUDIT T2a+T2b, `b88c4fb`). Las features de `gap-0.2` (centros por habitante) siguen como datos extra de cada fila. En la pestaña va como lista, no como tabla: con tres columnas, en el móvil quedaban dos o tres palabras por línea (revisión del PR #17, 12 nov) |
| 1.4 | 2SFCA: capacidad de cada centro entre la gente a 15 min o menos; cada calle suma sus cuotas; la zona, media ponderada por población; cruza fronteras; quien está a más de 15 min suma 0 | D-217 §2 (Luo y Wang, 2003) · `packages/domain/src/hi_domain/access/fca.py` · `services/features/src/hi_features/fca.py` (`two_step_fca`) · test de propiedades de capacidad conservada | Hecho |
| 1.4 | Pueblos pequeños con sus vecinos del mismo tipo a 15 km o menos en línea recta, hasta 3,69 casos esperados; el estado es el del grupo; distritos sin agrupar | D-217 §6 (Talbot et al., 2000; zonas básicas de salud rurales: radio equivalente mediano 7,7 km y extensión mediana 22,9 km) · `hi_domain/gaps.py` (`pool_with_neighbours`) · `comparison_group` en la API (Redueña, farmacia: 7 municipios, ratio del grupo 1,508; producción, 12 nov) | Hecho |
| 1.4 | Vivienda: SIN DATOS en los distritos de Madrid; no va a pie | `viviendas_grandes_por_100_hogares_grandes.yaml` (`levels.distrito: not_published`, `limitations`) · `phase-gap001-f3b.txt` (Chamartín: `SOURCE_MISSING`) · D-217 («vivienda no cambia») | Hecho |
| 1.4 | Hospital: minutos a pie al hospital general más cercano, público o privado, como pista de urgencias; no cuenta para el estado; camas de los hospitales identificados en «Todos los centros»; de unos pocos, solo el tipo y el municipio | D-217 §5 (`min_a_pie_hospital`, extra de la fila de centros de salud) · D-218 §6–7 (`capacity` = camas instaladas en `/places`; no entran en la lista) · producción, 12 nov: La Paz, 966 camas, en `GET /api/v1/places?category=health&admin_unit_id=ES.28.DIS.2807908&subcategory=Hospital general` | Hecho |
| 1.4 | Sensibilidad a la captación: con 10 o 20 min el orden casi no cambia | D-217 §2 (Spearman 0,995–0,997) · `evidence/gate-03/2026-11-12/fca-sensitivity.md` | Hecho (no va en la pestaña; respuesta para el jurado) |
| 1.5 | Por la red de calles de OSM, no en línea recta | D-210 · `packages/domain/src/hi_domain/access/walk.py` · `evidence/gate-01/2026-11-11/osm_red_peatonal/` | Hecho (CORE-005, `fc025b6`, Gate 3 PASS) |
| 1.5 | 4 km/h, el paso del estudio «El Madrid de los 15 minutos» del Ayuntamiento | Decisión de Mariano (11 nov), D-211. El estudio: «Velocidad de desplazamiento estimada en 4 Km/h» (https://geoportal.madrid.es/fsdescargas/IDEAM_WBGEOPORTAL/GEOPORTAL/Jornada/2022/SALA5_1130_PROXIMIDAD_POR_CALCULODEREDES.pdf) · `speed_kmh: 4.0` en `data/catalog/features/min_a_pie_*.yaml` y `pct_calle_*.yaml` (versión 2) | Hecho (CORE-005 Fase 5, `ad2129a`, Gate 3 PASS: `evidence/gate-03/2026-11-11/phase-core005-f5.txt`) |
| 1.5 | 10 minutos andando son unos 670 metros | D-211 («Efecto»: 5 min ≈ 333 m, 10 min ≈ 667 m, 15 min ≈ 1.000 m) | Hecho |
| 1.5 | 7 destinos (con el hospital general); en cada fila, los minutos de la mitad de las calles (mediana) | `data/catalog/features/min_a_pie_*.yaml` · D-210 · D-217 §5 · `/gaps` los da en `extra_indicators` (GAP-001 F1, `2d05d78`) · en producción, 12 nov: Puente de Vallecas, `min_a_pie_escuela_infantil` 6,258 y `min_a_pie_hospital` 51,32 | Hecho. La web redondea al minuto. El % de calle a 10 min (`pct_calle_*.yaml`) se calcula pero no se enseña, así que la parte 1 no lo nombra |
| 1.5 | Sin calles en el mapa: «sin datos», nunca 0 | D-210 (`SOURCE_NO_COVERAGE`, 24 secciones) · `null_policy` en los YAML · `evidence/gate-03/2026-11-11/walk-coverage.txt` · 15 casos golden y coherencia mediana/% en `scripts/check_walk_golden.py` y `evidence/gate-03/2026-11-11/phase-core005-f5.txt` (a 4 km/h; D-211) | Hecho (Gate 3 PASS) |
| 1.6 | Etiquetas: ≥ 0,8 fiable; 0,5 ≤ c < 0,8 aproximado; 0 < c < 0,5 poco seguro; 0 sin datos | Criterio de D (`pitch/textos_web.md` §6), confirmado por A el 11 nov. Tope de 0,5 en zonas pequeñas: D-189. Rango 0–1 y 0 = desconocido: `packages/contracts/src/hi_contracts/public/common.py` (`Confidence`) | Hecho |
| 1.6 | Confianza ≤ 0,5 en zonas pequeñas; umbrales 200 / 300 / 2.000 / 300 / 2.000 / 100 (escuela infantil, colegio, centro de salud, mayores, farmacia, vivienda); colegio con confianza 0,8 por las aulas repartidas | `services/features/src/hi_features/methods.py` (`SMALL_POPULATION_CONFIDENCE`) · `small_population_threshold` y `confidence` en los YAML de las filas de `gap-0.3` | Hecho. La confianza mide el dato; la «zona pequeña para comparar» va aparte (D-213 punto 3, D-217 §6) |
| 1.6 | Fuente incompleta: confianza = parte de residencias con plazas conocidas | `methods.py` (suma de atributos: «Places lacking it lower confidence») | Hecho |
| 1.6 | «5 o más» contado como 5 (confianza 0,9) | `data/catalog/features/tamano_medio_hogar.yaml` | Hecho |
| 1.7 | 26 conjuntos CM, 9 del CRTM con ficha en el portal (6 redes y 3 topologías con el grado de accesibilidad de las estaciones); los 2 de camas solo dan el total de la región | `pitch/datasets_cm.md` (12 nov) · D-196 · D-217 §4 · D-223 §2 · producción: `GET /api/v1/datasets?cm_only=true` da 26 (12 nov) | Hecho. El uso en pantalla de los 2 de camas, **pendiente de A** |
| 1.7 | Apoyo: Ministerio de Sanidad (nombres y camas), CartoCiudad (coordenadas de unos pocos centros) y parques de OpenStreetMap | D-218 · D-216 §3 · D-222 (`osm_parques`) · `pitch/datasets_cm.md` §3 · `README.md` («Qué datos usamos») | Hecho |
| 1.7 | Control de calidad | `evidence/gate-01/*/<dataset>/quality_report.json` | Hecho |
| 1.8 | Solo la capacidad publicada; a pie, no en coche; gente colocada por longitud de calle; camas fuera de la lista; vivienda: parque, no mercado | D-217 §3 y §9 (límites declarados) · D-218 §7 · `limitations` de los YAML de `gap-0.3` · `viviendas_grandes_por_100_hogares_grandes.yaml` (`limitations`) | Hecho. Mejora declarada: captación con decaimiento (E2SFCA) y tiempo en coche o transporte (CORE-009) |
| 1.8 | Transporte: horarios programados de un día laborable; líneas interurbanas sin horario completo (720 a 726 sin expediciones; 35 con la misma hora en todas sus paradas); 45–50 zonas sin llegada al centro a las 9:00 | D-220 §5–6 | Hecho (límite declarado) |
| 1.8 | Alquiler: solo municipios de más de 20.000 habitantes | `alquiler_m2_mensual.yaml` (`limitations`) · título del dataset en `pitch/datasets_cm.md` | Hecho |
| 1.8 | Compra: «sin datos» en todas las zonas, sin inventar precio | D-214 (punto 5) · D-203 | Hecho. Fuente oficial: DATA-021, del 19 al 22 nov (**pendiente de A**) |
| 1.8 | Alquiler: 37 de 179 municipios; distritos por la media de sus códigos postales, ponderada por lugares (confianza ≤ 0,8); 14,46 €/m² frente a 15,10 de la CM | D-214 (puntos 3 y 4) · `alquiler_m2_mensual.yaml` v2 (`postcode_weighted_mean`) · `evidence/gate-04/2026-11-11/phase-core006-f1.txt` | Hecho (CORE-006, `100cb29`) |
| 1.8 | Seguridad no puntúa: la tasa de hechos conocidos se divide por empadronados, pero cuenta donde se denuncia (Humanes de Madrid 116,2 y Madrid 58,6 frente a 47,9, en 2024); 36 de 199 zonas, ningún distrito; sin datos de personas ni etiquetas | D-224 · `evidence/gate-01/2026-11-12/seguridad-evaluacion.md` · D-204 · D-205 | Decidido (D-224). Abierto para Mariano: enseñarla como contexto en esos 36 municipios, sin puntuar (D-224 §3) |
| 1.8 | Madrid capital, solo contexto: percepción vecinal de seguridad en el barrio (noche y día, 0–10; Encuesta de calidad de vida 2025, 8.893 residentes, unas 400 por distrito; Madrid 6,4 de noche y 7,8 de día). Policía Municipal: solo desde la fuente mensual, nunca del panel. Atropellos: no puntúan | D-226 §1–5 · `evidence/gate-01/2026-11-12/seguridad-fuentes.md` · features `seguridad_percibida_noche` y `seguridad_percibida_dia` (sin `fit` ni `gap_row`) | Percepción: hecha en la API (`GET /features/{id}/values`); en la web, **pendiente de B**. Policía Municipal desde la fuente mensual, **pendiente de A** |
| 1.8 | «Sin escaleras»: solo grado T (accesibilidad total); P y N no cuentan; sin autobuses, aceras, portales ni ascensores; 4 km/h; opt-in, nunca inferido | D-223 §1, §3, §6 y §9 · CLAUDE.md §13 · `evidence/gate-01/2026-11-12/estaciones-accesibles.md` | Hecho y en producción desde el 12 nov (despliegue de `2761696`) |
| 1.8 | Zonas verdes: parques OSM de 1 ha o más (umbral de la OMS), medidos hasta el borde; sin campo ni jardines pequeños | D-222 §2, §4 y §6 | En la API (`fit-0.3`, desplegado el 12 nov); el chip, **pendiente de B** |
| 1.8 | Necesidad declarada: siguiente paso, nunca simulada | D-194 | Hecho (no está en la demo) |
| 1.8 | GTFS de metro vencido el 27-05-2026 | `evidence/gate-01/2026-11-10/crtm_gtfs_metro/quality_report.json` (`feed_current`) · D-196 | Hecho |
| 1.9 | Sin cuenta; solo datos de zonas | Brief de diseño (sin login) · D-186 · D-197 | Hecho. No se afirma nada sobre registros del servidor: C no lo ha documentado |
| 1.10 | Versiones de método | `GapMethod.version` · `SearchResult.methodology_version` | `gap-0.3` (D-217), en producción; `fit-0.4` (D-220, D-222 y D-223), en producción desde el 12 nov (despliegue de `2761696`) |
