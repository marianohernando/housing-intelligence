# Guion de 5 minutos — Vida Fácil (final del 26 nov)

## Reglas del guion
- **Formato:** 5 min de exposición + 5 de preguntas (bases §9). Demo en directo sobre la web desplegada y slides solo al principio y al final.
- **Orden desde el 23 nov** (decisión de Mariano, tras el jurado simulado): se abre con lo que no hacía el ganador de 2024. En la formación del 5 nov (APIs, MCP y espacios de datos), el formador lo describió como un buscador de pisos con el ambulatorio y el metro cerca y un perfil ponderado, hecho con scraping, y lo llamó «calderilla» ([00:01:26] y [01:20:39]–[01:21:34] de esa sesión). Por eso:
  1. qué le falta a cada zona, para ayuntamientos;
  2. la ficha de la parcela exacta, para inversores;
  3. la base, para personas: la zona que les conviene, comparada en voz alta con lo de 2024;
  4. los datos (con MELODA), la IA, la API abierta y quién paga;
  5. el cierre, con el lema nuevo.
- **Ritmo:** unas 130 palabras por minuto. En los bloques con demo se habla menos, porque los clics y las transiciones también ocupan tiempo. Objetivo de Mariano: unas 500–550 palabras habladas.
- **Recuento por bloque** (texto entre los marcadores `habla:bN`):
  ```bash
  for b in 1 2 3 4 5 6; do printf "b$b "; awk -v b=$b '$0 ~ "^<!-- habla:b"b":fin"{f=0} f; $0 ~ "^<!-- habla:b"b":inicio"{f=1}' pitch/guion.md | wc -w; done
  ```
- **Lo que va entre corchetes** (`[N]`, `[zona]`…) se lee en la pantalla en directo. Nunca se dice una cifra de memoria.
- **Lema:** «La zona que te conviene, y lo que le falta» (decisión de Mariano del 23 nov). Es la última frase del guion y va en la slide 1. Sustituye al lema anterior (D-199).
- **Frases honestas (23 nov, jurado simulado):**
  - «cada falta lleva su probabilidad», y no «nunca inventamos una falta»: sin corrección por comparaciones múltiples, una falta puede salir por azar (pregunta 46);
  - «viven en 3 distritos donde faltan escuelas infantiles», para que no se oiga como «niños sin escuela»;
  - «cumplen lo que piden 42 zonas», y no «les convienen»: 12 de las 42 salen «Poco recomendable»;
  - el precio: «es el precio de los contratos de 2024; un anuncio de hoy suele pedir más», como dice la tarjeta desde el deploy-46 (pregunta 57);
  - «API y MCP abiertos y gratuitos, sin clave»: desde el 23 nov el MCP funciona en remoto (D-255). Comprobar en producción antes de decirlo.
- **Farmacias:** no se presume de ellas en la parte de personas (segunda prueba de P6, 23 nov: a un ciudadano no le sirve el dato; la web las quita de la tarjeta de zona si no se piden). En «Qué falta», para ayuntamientos, se quedan.
- **Capturas:** C5 (slide 1), C1 (slide 4), C3 (slide 3) y C6 (slide 4) rehechas el 23 nov en producción con el deploy-46 (`542283b8`): lema nuevo, pestaña «Inversores» y «39 conjuntos» (`pitch/slides.md`, «Capturas necesarias»).

| Bloque | Tiempo | Duración | Pantalla | Contenido | Palabras | Tiempo hablado a 130 ppm |
|---|---|---|---|---|---|---|
| 1 | 0:00–0:30 | 30 s | Slide 1 → slide 2 | Tres preguntas: ayuntamiento, promotor y API; sin scraping | 62 | 29 s |
| 2 | 0:30–1:45 | 75 s | Demo: «Qué falta» | Dónde invertir primero y Puente de Vallecas | 108 | 50 s + unos 12 s de clics |
| 3 | 1:45–2:45 | 60 s | Demo: «Inversores» | La ficha de una parcela exacta: Méndez Álvaro 47 | 89 | 41 s + unos 15 s de bajar por la ficha |
| 4 | 2:45–3:40 | 55 s | Demo: «Mapa» | La base: la zona que te conviene, frente a lo de 2024 | 109 | 50 s + unos 10 s de clics |
| 5 | 3:40–4:35 | 55 s | Slide 2 → slide 3 | Datos, MELODA, la IA, la API y quién paga | 133 | 61 s |
| 6 | 4:35–5:00 | 25 s | Slide 4 | Pruebas con personas y cierre con el lema | 44 | 20 s |
| **Total** | | **300 s** | | | **545** | **252 s + unos 41 s de clics y cambios = unos 7 s de margen** |

**Recuento del 23 nov, tras el deploy-46** (comando de arriba): b1 62, b2 108, b3 89, b4 109, b5 133 y b6 44; 545 palabras, dentro de las 500–550 que pidió Mariano. Tras el deploy-46, el bloque 3 dice «en qué fase está su ámbito» (antes, «si su urbanización está terminada»: +1 palabra) y el bloque 4, «un anuncio de hoy suele pedir más», como la tarjeta (+1). Antes, tras la revisión del #122: 543. El bloque 4 atribuye lo de 2024 a la formación (+6 palabras, R-06) y el bloque 5 pierde «Cada conjunto pasa nuestro control de calidad.» (lo dice la slide 2). El margen baja de unos 26 s a unos 8 s porque hay un recorrido más (la parcela) y la frase de MELODA, que pasó el coordinador con las cifras de `pitch/meloda_cm_snapshot.json`. Los clics son una estimación: se miden en los ensayos. Si no llega, se quita, por este orden:
1. «Una de ellas repitió esta semana: «ha mejorado un montón».», del bloque 6 (9 palabras, unos 4 s; la cita sigue en la slide 3);
2. «Y, para quien busca casa, la zona que le conviene.», del bloque 1 (10 palabras, unos 5 s; el bloque 4 ya lo cuenta).

### Recuentos anteriores (orden del 19 nov: personas, ayuntamiento, datos)
- **19 nov, tras la búsqueda por parcela (D-250):** b1 74, b2 130, b2s 136, b3 125, b4 105 y b5 66: 500 palabras con buscador y 506 sin él, con unos 26 s de margen.
- **19 nov, tras `/desarrolladores` (D-249):** el bloque 4 sumó «La API y el MCP para agentes de IA son gratis para todos.» (13 palabras).
- **19 nov, tras la versión para inversores (D-248):** b4 93; el bloque 4 dijo 39 conjuntos y la versión para inversores pasó de siguiente paso a hecha.
- **18 nov:** b4 101, con la frase del suelo público (D-246) y sin la lista de temas, que ya estaba en la slide 2.
- El texto completo de entonces está en el historial de git de este fichero.

---

> Las decisiones del 11 nov están registradas como D-199 a D-207 (`docs/00_index/01_decisions_log.md`). El brief de diseño (`DISENO_VIDA_FACIL.md`, adoptado por D-201) sigue fuera del repo: se cita como documento interno, no como evidencia pública.

## Antes de empezar (en la sala, 13:30–17:00)
1. Portátil con cargador, wifi del evento probada, HDMI probado y resolución 1920 × 1080 (`docs/09_datamad/25_plan_competicion.md` §9).
2. Navegador en ventana limpia, zoom al 100 %, sin extensiones visibles y con las notificaciones desactivadas.
3. Pestañas, en este orden y todas cargadas una vez para tener la caché caliente:
   - **1:** las slides en PDF, en la slide 1;
   - **2:** «Qué falta» sin zona, con «Dónde invertir primero»: https://vidafacil-madrid.vercel.app/que-falta;
   - **3:** la ficha de Méndez Álvaro 47: https://vidafacil-madrid.vercel.app/inversores/parcela/2122202VK4722A. La primera consulta de una parcela tarda unos 11 s, porque pregunta al Catastro y al Ayuntamiento; las siguientes, unos 0,3 s (deploy-39, punto 13). Por eso se carga antes;
   - **4:** la portada de la demo: https://vidafacil-madrid.vercel.app.
4. Plan B abierto en una pestaña oculta: el vídeo de 2 min (PITCH-003, `pitch/video_respaldo.md`) y el paquete sin red de C (`make demo-offline`, `infra/deploy/offline/`). **Ojo:** el vídeo sigue el recorrido del 19 nov (personas y luego «Qué falta») y no enseña la parcela.
5. Pestaña de respaldo de «Qué falta», ya cargada: https://vidafacil-madrid.vercel.app/que-falta?zona=distrito/2807913 (Puente de Vallecas).

---

## Bloque 1 · 0:00–0:30 · Tres preguntas
**Pantalla:** slide 1 (título y lema). En «Un ayuntamiento» se pasa a la slide 2, cuya columna del problema va en el mismo orden: ayuntamientos, promotores e inversores, y personas.

<!-- habla:b1:inicio -->
Buenas tardes. Vida Fácil responde a tres preguntas con datos abiertos. Un ayuntamiento: ¿qué le falta a cada zona? Un promotor: ¿qué pasa en esta parcela exacta y quién vive alrededor? Y un agente de IA: lo mismo, por una API abierta. Todo con datos abiertos descargados de sus portales, sin scraping. Y, para quien busca casa, la zona que le conviene.
<!-- habla:b1:fin -->

**Fuentes:** «descargados de sus portales» (revisión del #122, R-03: no todo es «oficial» ni todo llega «por API»): los 29 conjuntos de la Comunidad salen de la API CKAN de su portal (`data/catalog/sources/comunidad_madrid_ckan.yaml`, `api_type: ckan`) y los 10 del Consorcio, de la API de su portal (`crtm_open_data.yaml`, `api_type: arcgis_hub`). «Sin scraping»: `CLAUDE.md` §15 y pregunta 35; Google Maps y Gosom, descartados (D-175 y D-185). La parcela llega a toda Madrid capital (D-250 §6); no se dice «toda la región».

**Al terminar:** cambiar a la pestaña 2 (Cmd + 2).

---

## Bloque 2 · 0:30–1:45 · Qué le falta a una zona (ayuntamientos)
**Zona: Puente de Vallecas** (distrito 2807913). La lista mide lo que la gente tiene a 15 minutos andando, repartido entre todos los que lo comparten (D-217, `gap-0.3`; en llano, `pitch/metodologia.md` §1.4), y lo compara con los municipios de su tipo.

**Cifras** (`GET /api/v1/gaps/impact` y `GET /api/v1/gaps/distrito/2807913`, `data_version` 2026-11-19, leídas el 21 nov para el jurado simulado; las del 12 nov eran las mismas):
- «Dónde invertir primero», escuelas infantiles: 25.551 niños de 0 a 4 años (el 9,8 % de la región) viven en los 3 distritos con FALTA: Puente de Vallecas 9.433 (57 por cada 100; p = 0,00114), Carabanchel 9.150 (68; p = 0,0161) y Villaverde 6.968 (61; p = 0,0107). Es el padrón de cada distrito. En la web: «25.551 niños de 0 a 4 años viven donde faltan escuelas infantiles» y «El 9,8 % de toda la Comunidad, en 3 zonas.» (`invertir.cifra` e `invertir.contexto`).
- **Es una señal, no un veredicto:** con Holm sobre los 21 distritos de Madrid solo aguanta Puente de Vallecas, y sobre las 199 zonas ninguna (pregunta 46). Por eso se dice «cada falta lleva su probabilidad».
- Escuelas infantiles **FALTA** en Puente de Vallecas: 2,781 escuelas al alcance a pie por cada 1.000 niños de 0 a 4 años, frente a 4,87 en los «Otros municipios urbanos de la Comunidad de Madrid» (ratio 0,571). La mitad de la zona tiene la más cercana a 6 min o menos (`min_a_pie_escuela_infantil` = 6,258). Contando escuelas por habitante sale casi lo mismo (2,708): no es un efecto del método.
- Farmacias **CUBIERTO**: 4,5 frente a 3,1. Colegio, centro de salud y mayores, también CUBIERTO. Desde el despliegue del 23 nov la vivienda ya no es una fila de falta, sino contexto (D-254, `gap-0.4`; pregunta 63).
- **El 25 nov se vuelve a mirar:** si Puente de Vallecas ya no sale FALTA, se elige otra con `GET /api/v1/gaps?level=distrito&row=escuela_infantil` y se cambian las cifras de aquí y de la slide 3.
- **Si preguntan por Madrid capital:** sale JUSTO en centros de salud (0,3603 frente a 0,3799). La frase «un tercio menos» ya no vale (D-217 §7).
- **«Qué pedir primero y dónde reservar suelo»:** las farmacias, la salud y los colegios los decide la Comunidad; el ayuntamiento pone el suelo (pregunta 64).

<!-- habla:b2:inicio -->
Empiezo por el ayuntamiento. Abro «Qué falta»: en toda la región, [más de veinticinco mil] niños de cero a cuatro años viven en [tres] distritos donde faltan escuelas infantiles. El primero, Puente de Vallecas. No contamos centros: medimos lo que la gente tiene a quince minutos andando, repartido entre todos los que lo comparten, y lo comparamos con municipios parecidos. Escuelas infantiles: falta. Hay una a [seis] minutos, pero son pocas para tantos niños: [cincuenta y siete] por cada cien de los municipios parecidos. Si no tenemos el dato, lo decimos, y cada falta lleva su probabilidad. Así un ayuntamiento sabe qué pedir primero y dónde reservar suelo.
<!-- habla:b2:fin -->

| # | Acción | Qué tiene que verse | Si falla |
|---|---|---|---|
| 2.1 | Pestaña 2, «Qué falta» sin zona: señalar «Dónde invertir primero» | La tarjeta de escuelas infantiles: «25.551 niños de 0 a 4 años viven donde faltan escuelas infantiles», «El 9,8 % de toda la Comunidad, en 3 zonas.» y el orden Puente de Vallecas, Carabanchel y Villaverde | Si no carga, pasar a la pestaña de respaldo y decir «miles de niños pequeños» sin la cifra |
| 2.2 | Clic en Puente de Vallecas | Su lista con las filas FALTA / JUSTO / CUBIERTO / SIN DATOS, valor, referencia, fiabilidad, minutos a pie y datasets | Abrir la pestaña de respaldo (`/que-falta?zona=distrito/2807913`) |
| 2.3 | Señalar la fila de escuelas infantiles y leer los minutos y la frase principal | «Aquí hay 57 por cada 100 que hay en municipios parecidos.», «Afecta a 9.433 niños de 0 a 4 años.» y «6 min» hasta la más cercana (producción, 18 nov). La cifra técnica queda tras «Ver la cifra»: no se abre, salvo que pregunten | Leer solo el estado y la frase |
| 2.4 | Solo si va sobrado de tiempo: señalar la fila de farmacias (CUBIERTO) y leerla | «4,5 farmacias al alcance a pie por cada 10.000 habitantes; en los demás municipios urbanos…, 3,1» | Saltarlo: desde el 23 nov no está en el texto (unas 12 palabras) |

**Barrios (D-232, D-238):** no se enseñan en la demo. Si preguntan, preguntas 48 y 52.

**Al terminar:** cambiar a la pestaña 3 (Cmd + 3).

---

## Bloque 3 · 1:45–2:45 · La ficha de una parcela exacta (inversores)
**Parcela: Méndez Álvaro 47**, en el barrio de Atocha (Arganzuela), referencia catastral 2122202VK4722A. Es una de las 4 parcelas de demostración y la que tiene todo con dato oficial (pregunta 6). La ficha va en este orden (D-253): datos de la parcela, planeamiento, edificabilidad, servicios y suministros, quién vive en el barrio, precios, qué falta, suelo y «¿Sale la promoción?».

**Lo que se lee** (API de producción, 21 nov, `parcel_2122202VK4722A`; F-B cambia hoy la ficha, así que el 25 nov se vuelve a mirar):
- edificabilidad: 13.121 m² de «RESIDENCIAL VIVIENDA COLECTIVA», «VEDA Madrid (Ayuntamiento de Madrid), julio de 2026», marcada «Dato»;
- el ámbito APR.02.06, «Méndez Álvaro Norte I», con el enlace a la ficha oficial y sus fases, según el Ayuntamiento a 1 de julio de 2026: «Proyecto de urbanización: finalizado · Obras de urbanización: finalizado · VEDA: en fase de edificación, según el Ayuntamiento: no quiere decir que se pueda construir ya (hace falta licencia)» (producción, 23 nov, deploy-46);
- servicios: unas 164 viviendas, al menos 499,1 kW, marcado «Supuesto», con el aviso del centro de transformación;
- el contexto de demanda del barrio de Atocha (piloto de la M-40): quién vive, precios, qué falta y suelo.
- **No se dice en voz alta la cifra del suelo** (lo máximo que se podría pagar). El jurado simulado (A1) la vio poco creíble sin los costes que deja fuera; se enseña solo si preguntan, con lo que excluye (pregunta 6).

<!-- habla:b3:inicio -->
Ahora, un promotor busca una parcela de Madrid capital: Méndez Álvaro cuarenta y siete. La ficha le da su planeamiento, con el enlace oficial; [trece mil] metros edificables de vivienda que publica el Ayuntamiento; en qué fase está su ámbito y la potencia eléctrica que pediría; y al lado, la demanda de su zona: quién vive, a qué precios y qué le falta. Con eso calcula cuánto podría pagar por el suelo, con cada supuesto a la vista. Es un primer filtro de minutos, antes de pagar un estudio.
<!-- habla:b3:fin -->

| # | Acción | Qué tiene que verse | Si falla |
|---|---|---|---|
| 3.1 | Pestaña 3: señalar la cabecera de la ficha | La pestaña «Inversores» marcada, Méndez Álvaro 47, barrio de Atocha y el aviso «Esto es un primer filtro de minutos, gratis y con fuentes…» | Si no carga, buscar `2122202VK4722A` en «Busca tu parcela» y seguir hablando: tarda unos 11 s |
| 3.2 | Bajar a «2. Planeamiento» y «3. Edificabilidad» | El ámbito APR.02.06 con el enlace oficial, y «13.121 m²» marcado «Dato», de VEDA | Leer «[trece mil]» de donde esté |
| 3.3 | Señalar las fases del ámbito, en «2. Planeamiento», y bajar a «4. Servicios y suministros» | «Obras de urbanización: finalizado · VEDA: en fase de edificación…» y la potencia, «Supuesto» | Saltar «en qué fase está su ámbito…» |
| 3.4 | Bajar a «5. Quién vive en el barrio» y señalar «¿Sale la promoción?» sin leer cifras | El contexto de demanda y la calculadora con sus supuestos | — |

**Fuentes de lo que se dice:**
- «Busca una parcela de Madrid capital»: D-250 §6 (`/inversores` abre con «Busca tu parcela», por referencia catastral, dirección o clic en el mapa; un punto de fuera da «Ese punto está fuera de Madrid capital»).
- «Su planeamiento, con el enlace oficial»: el Ayuntamiento, con «Información urbanística sin valor jurídico» (D-250, D-252 §3).
- «Metros edificables de vivienda que publica el Ayuntamiento»: VEDA (`ayto_edificabilidad_remanente_ambitos`); si la parcela no tiene cifra oficial, la ficha dice «Supuesto» o «Sin dato» (D-252 §1–4).
- «En qué fase está su ámbito y la potencia eléctrica que pediría»: las fases que publica el Ayuntamiento (D-252 §3) y D-253 §1–5. Desde el deploy-46 la ficha añade «VEDA: en fase de edificación… no quiere decir que se pueda construir ya (hace falta licencia)», así que no se dice que la parcela esté lista para construir. Ningún dato abierto dice si la parcela tiene los servicios; se da el estado de la urbanización y una potencia mínima supuesta.
- «La demanda de su zona»: la ficha del barrio de D-248 (completa en los 108 barrios del piloto dentro de la M-40; fuera, con las cifras del distrito o de la ciudad, D-250 §5). No es todavía el cruce con la vivienda que le falta a la zona (pregunta 60).
- «Cuánto podría pagar por el suelo»: sin precio del suelo, la calculadora da lo máximo que se podría pagar; con él, el semáforo (`viability-0.2`, D-252 §6). Cada supuesto va marcado.
- «Un primer filtro de minutos, antes de pagar un estudio»: el aviso de la ficha (D-253 §8; pregunta 61).
- Si sale el Catastro en las preguntas: «datos de la parcela, elaborados a partir de los del Catastro», nunca «información catastral» (D-250 §1).

**Al terminar:** cambiar a la pestaña 4 (Cmd + 4).

---

## Bloque 4 · 2:45–3:40 · La base: la zona que te conviene (personas)
**El ganador de 2024**, según el formador de la sesión del 5 nov: «te daba los pisos pero te daba también… donde había un ambulatorio, donde estaba la estación de metro… podías hacerte una especie de perfil adaptado a tus necesidades» [01:20:39]–[01:21:20], y «utilizaba un scrapeo» [01:21:34]. No se dice nada más de él (pregunta 66).

**Caso precargado:** `data/fixtures/contracts/scenario_state.familia_castellana.fixture.json`:
- alquiler de hasta 1.500 €/mes;
- 2 adultos y 2 hijos de 4 y 8 años;
- trabajo en el Paseo de la Castellana (Azca), 4 días por semana;
- colegio a 10 min andando como mucho, obligatorio;
- le importan, por este orden, los colegios, el transporte y la salud.

**Resultado en producción** (15 nov, `fit-0.9`, D-243; palabras comprobadas otra vez el 18 nov con `55651c2`; se vuelve a comprobar el 25 nov). Se lee en pantalla, nunca de memoria:
- «Hemos encontrado 42 zonas para vosotros.»; la leyenda cuenta 42 que cumplen todo, 157 que no y 0 sin datos, de las 199 zonas (178 municipios y los 21 distritos de Madrid);
- todas cumplen lo que pide la familia; el % dice cuánto le conviene todo lo demás: 12 «Muy buena opción», 5 «Buena opción», 13 «Opción regular» y 12 «Poco recomendable». Por eso se dice «cumplen lo que piden», no «les convienen»;
- arriba, Puente de Vallecas y Latina, las dos «Muy buena opción · 94 %»; la web pone 1.ª a Puente de Vallecas porque tiene más cerca los servicios del día a día;
- la tarjeta de Puente de Vallecas: «Unos 1.129 € al mes» y, debajo, «Precio de los contratos de alquiler de 2024: un anuncio de hoy suele pedir más.» (desde el deploy-46; antes, «Precio orientativo»), «Colegio con primaria a unos 4 min andando», «41 min en transporte público hasta Paseo de la Castellana (Azca), llegando a las 9:00» y «No le falta nada de lo que buscáis.»;
- el precio es el de los contratos firmados en 2024 (Agencia Tributaria, D-228): en varias zonas baratas, un anuncio de hoy pide entre 1,28 y 1,33 veces esa cifra (pregunta 57).

<!-- habla:b4:inicio -->
Y la base, para quien busca casa. En la formación nos contaron que lo que ganó en 2024 daba pisos sacados con scraping, con el ambulatorio y el metro cercanos. Nosotros lo hacemos en los ciento setenta y nueve municipios, solo con datos oficiales, con el trayecto al trabajo y con lo que le falta. Una pareja con dos hijos, mil quinientos euros y trabajo en la Castellana: cumplen lo que piden [cuarenta y dos] zonas. La primera: [colegio a cuatro minutos], [cuarenta y un minutos al trabajo] y [unos mil ciento veintinueve euros]: es el precio de los contratos de 2024; un anuncio de hoy suele pedir más.
<!-- habla:b4:fin -->

| # | Acción | Qué tiene que verse | Si falla |
|---|---|---|---|
| 4.1 | Pestaña 4: clic en «Ejemplo: pareja con 2 hijos que trabaja en la Castellana» | Se rellena «Tu búsqueda» y sale «Zonas que os convienen», con «Hemos encontrado 42 zonas para vosotros.» | Si tarda más de 3 s, seguir hablando de lo de 2024; si no llega, pasar al vídeo (plan B) |
| 4.2 | Clic en la 1.ª de la lista y leer tres hechos | Tarjeta de Puente de Vallecas: «Colegio con primaria a unos 4 min andando», «41 min en transporte público hasta Paseo de la Castellana (Azca)…» y «Unos 1.129 € al mes». Si sale otra zona, se leen los corchetes tal como salgan | Leer solo la banda y el precio |

**«179 municipios»:** el buscador cubre las 199 zonas: 178 municipios y los 21 distritos de Madrid, que sustituyen al municipio (D-215, punto 1). **El trayecto al trabajo:** horarios publicados de las 6 redes del Consorcio, llegando a las 9:00 (D-220). **«Lo que le falta a cada zona»:** la tarjeta lo dice en «Ver más» («Tiene lo que pedís. Aun así, comparado con municipios parecidos, aquí faltan escuelas infantiles.»).

**No se abren** «Ver más», «¿Queréis ver más zonas?» ni «Casi valen»: no caben en el tiempo. Si preguntan: «+5 min a pie hasta colegio con primaria · saldrían 49 más: 91 zonas en total» y Chamartín, «Se pasa unos 90 € al mes de vuestro presupuesto» (preguntas 18 y 48).

**Al terminar:** volver a la pestaña 1, en la slide 2 (Cmd + 1).

---

## Bloque 5 · 3:40–4:35 · Datos, MELODA, la IA, la API y quién paga
**Pantalla:** la slide 2 en «¿Con qué datos?», con las dos líneas de MELODA bajo la tabla («MELODA: 16 sobre 49 de media; 1 de 5 en actualización. Las 10 fichas del Consorcio sacan 8 en este portal, frente a 24,7 de media en el portal del Consorcio (281 conjuntos).»), de donde se leen los corchetes, y la slide 3 en «¿Quién paga?». La columna «Viabilidad» de la slide 3 dice lo mismo: «Gratis siempre…», «Pagarán las empresas…», «API abierta y gratuita; MCP de código abierto.» y «Ninguna cifra la genera una IA…».

<!-- habla:b5:inicio -->
¿Con qué datos? [Treinta y nueve] conjuntos del Portal de Datos Abiertos de la Comunidad de Madrid, y medimos su reutilización con MELODA: [dieciséis] sobre cuarenta y nueve de media. Lo más flojo es la actualización: [uno de cinco] en todos. Las diez fichas del Consorcio sacan [ocho] en el portal de la Comunidad, frente a [veinticuatro coma siete] de media en su propio portal. Ninguna cifra la genera una IA: salen de cálculos deterministas sobre datos oficiales, cada una con su fuente. El código es abierto; la API, abierta y gratuita, y el MCP, de código abierto. ¿Quién paga? Gratis siempre: los datos, las zonas, qué falta, cada ficha de parcela y la API. Pagarán las empresas un plan con carteras de parcelas y avisos de suelo nuevo, e informes a medida.
<!-- habla:b5:fin -->

**Fuentes de lo que se dice:**
- «Treinta y nueve conjuntos» y «control de calidad»: `pitch/datasets_cm.md` (39 con Gate 1 en PASS) y `GET /api/v1/datasets?cm_only=true` en producción (`cm_open_data_count: 39`). Eran 27 el 12 nov y 39 desde el 19 nov (D-235, D-237, D-241, D-246, D-247 y D-248). El 23 nov se regenera y, si cambia el número, se cambia la frase.
- **MELODA** (P6 del informe del jurado simulado; MELODA es la métrica que se enseñó en la formación del 5 nov). La frase la pasó el coordinador el 23 nov, y sus cifras están comprobadas aquí contra `pitch/meloda_cm_snapshot.json` (los 39 emparejados por la URL de su ficha) y `pitch/datasets_cm.md`, «Reutilización según MELODA»:
  - media de los 39 en el Monitorizador de spain.meloda.org: 15,97 sobre 49, que se dice «dieciséis» (`datasets_cm.md`: 16,0);
  - la frecuencia de actualización (`d6_frequency`): 1 de 5 en los 39. Es la dimensión que más pesa (15 de 49 puntos). No se dice por qué: no lo sabemos con lo que hay en el repo;
  - las 10 fichas del Consorcio en el portal de la Comunidad: 8 cada una; el portal del propio Consorcio, 24,7 de media en 281 conjuntos. Son medias de portal: los conjuntos del Consorcio no se han emparejado uno a uno (pregunta 62), así que no se dice que «el mismo conjunto» saque 24,7;
  - si preguntan por los de la Comunidad sola: los 29 que publica tienen 18,7 de media, y todo su portal, 18,1 (2.275 conjuntos);
  - el Monitorizador puntúa seis dimensiones de las ocho de MELODA 5: nunca decir «MELODA mide seis dimensiones». Detalle, en la pregunta 62.
- «Ninguna cifra la genera una IA»: `CLAUDE.md` §3 (IA: «El LLM no calcula si existe una función determinista»; «El LLM no inventa cifras faltantes») y pregunta 32. La IA se usó para programar, como permiten las bases (§7).
- «El código es abierto»: `LICENSE` (Apache-2.0, D-191).
- «La API, abierta y gratuita, y el MCP, de código abierto»: la API pública está en producción, sin claves, con su OpenAPI en `/api/v1/openapi.json` y una página pública, `/desarrolladores` (D-249). El MCP, 7 herramientas de solo lectura, funciona en local (`make mcp`) con el código abierto: no se dice «en remoto» (preguntas 1 y 2).
- «¿Quién paga?»: decisión de Mariano del 23 nov (`pitch/modelo_negocio.md`). Gratis siempre: los datos, las zonas, «Qué falta», cada ficha de parcela y la API. De pago: el plan empresarial (carteras de parcelas, avisos de suelo nuevo y la API y el MCP a gran volumen con clave) y los informes personalizados (estudios de suelo a medida). «Pagarán»: hoy no se cobra nada. Los precios no se dicen; si preguntan, pregunta 6.
- La privacidad («nunca vendemos datos de personas») ya no se dice en voz alta, por tiempo: está en la slide 3 («Solo zonas, nunca datos de personas.») y en la pregunta 33.

---

## Bloque 6 · 4:35–5:00 · Pruebas y cierre
**Pantalla:** la slide 4 (pantallazo) con la URL. El recuadro dice «Probada con 8 personas».

<!-- habla:b6:inicio -->
La probaron ocho personas: siete que buscan casa, una de ellas mayor, y un inversor; y se hizo lo que pidieron. Una de ellas repitió esta semana: «ha mejorado un montón». Vida Fácil: la zona que te conviene, y lo que le falta. Gracias.
<!-- habla:b6:fin -->

**Las ocho personas:**
- **Siete que buscan casa, del 13 al 15 nov:** P1 a P6, de 26 a 55 años, y una persona mayor. Lo que pidieron está en producción desde el 14 nov: «¿Dónde?» con Madrid capital por barrios (D-238, lo pidieron 4 de las 6) y el límite de tiempo al trabajo (PR #53). La persona mayor la probó el 15 nov en el móvil y le costó: desde ese día la web es otra (D-244 y D-245; letra de 16 px o más y botones de 44 px o más, medidos; pregunta 43). Todavía no la ha vuelto a probar: no se dice que ahora le resulte fácil.
- **Un inversor, el 19 nov:** P7, con experiencia en promoción, probó la versión para inversores. Lo que pidió (los servicios de la parcela, la edificabilidad por uso y de dónde sale el coste) está en la ficha desde el 20 nov (D-252 y D-253; pregunta 61).
- **Segunda ronda, 23 nov:** P6 volvió a probar la versión actual: «Ha mejorado un montón… ahora sí que te arroja cosas interesantes» y, con un caso parecido al suyo, «me hace una buena criba». Es la misma persona: el recuento no cambia. Su crítica: el dato de farmacias no le sirve a un ciudadano, y la web las quita de la tarjeta de zona si no se piden.
- Nunca se nombra a nadie: solo P1 a P7 y «una persona mayor».

**Lema:** «La zona que te conviene, y lo que le falta», decisión de Mariano del 23 nov. Lo propuso A4 en el jurado simulado. Sustituye al lema anterior (D-199) en el deck, en este cierre, en `pitch/README_publico.md` y en `pitch/textos_web.md`.

---

## Reserva del 19 nov: el bloque de personas sin buscador
**Cuándo:** solo si la demo vuelve a enseñar «Muy pronto» en lugar del buscador. Sustituye al bloque 4, pero **no está ajustada al orden ni al tiempo del 23 nov**: tiene 136 palabras, 36 más que el bloque 4, y dejaría el margen en unos 0 s. Si se usa, se acorta en el momento a su primera y su última frase.

<!-- habla:b4s:inicio -->
Esta es Vida Fácil: el mapa de toda la Comunidad de Madrid, con sus ciento setenta y nueve municipios y Madrid capital dividida en sus veintiún distritos, porque no es lo mismo vivir en uno que en otro. Pensad en esa familia. Toco un distrito, por ejemplo [zona]. La cámara entra en tres dimensiones, con sus colegios, centros de salud y estaciones. A la derecha, qué falta aquí y cuánto se tarda andando: [N] minutos hasta el centro de salud más cercano. No en línea recta: por las calles de verdad, a paso tranquilo, el mismo que usa el Ayuntamiento. Y cada dato dice de dónde sale: pulso aquí y me lleva a la ficha del portal de datos abiertos de la Comunidad. Así la familia sabe qué tiene cerca antes de mirar un solo piso.
<!-- habla:b4s:fin -->

| # | Acción | Qué tiene que verse | Si falla |
|---|---|---|---|
| 4s.1 | Señalar el mapa de la región | Los 179 municipios y los 21 distritos | — |
| 4s.2 | Clic en un distrito (propuesta: Chamartín, el de la captura C5) | Vuelo de cámara y zona en 3D con etiquetas de cristal; tarjeta «Qué falta aquí» con «A pie: N min» | Sin 3D: seguir en 2D y quitar «en tres dimensiones» |
| 4s.3 | Leer los minutos a pie del centro de salud en la tarjeta | «A pie: [N] min» (`zona.falta.a_pie`; mediana de las calles a 4 km/h, D-211) | Saltar la frase de los minutos |
| 4s.4 | Clic en «Cómo lo calculamos» o en la fuente de una fila | Nombre del dataset y enlace a la ficha del portal CM | Enseñar el pie «Datos: 39 conjuntos de la Comunidad de Madrid…» |

**Fuentes:** 179 municipios y 21 distritos: D-200 · D-209. Paso de 4 km/h, el del estudio «El Madrid de los 15 minutos» del Ayuntamiento: D-211.

---

## Ensayos (25 nov, 5 cronometrados; PITCH-004)
- Cronómetro por bloque y anotar el tiempo real en esta tabla. Si un bloque se pasa más de 5 s, recortar su texto y volver a contar las palabras.
- Un ensayo con la wifi apagada, usando el plan B, para practicar el cambio sin perder el hilo.

| Ensayo | B1 | B2 | B3 | B4 | B5 | B6 | Total | Notas |
|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | |
| 2 | | | | | | | | |
| 3 | | | | | | | | |
| 4 | | | | | | | | |
| 5 | | | | | | | | |
