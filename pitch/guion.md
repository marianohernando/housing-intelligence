# Guion de 5 minutos — Vida Fácil (final del 26 nov)

## Reglas del guion
- **Formato:** 5 min de exposición + 5 de preguntas (bases §9). Demo en directo sobre la web desplegada y slides solo al principio y al final.
- **Ritmo:** unas 130 palabras por minuto. En los bloques con demo se habla menos, porque los clics y las transiciones también ocupan tiempo.
- **Recuento por bloque** (texto entre los marcadores `habla:bN`):
  ```bash
  for b in 1 2 2s 3 4 5; do printf "b$b "; awk -v b=$b '$0 ~ "^<!-- habla:b"b":fin"{f=0} f; $0 ~ "^<!-- habla:b"b":inicio"{f=1}' pitch/guion.md | wc -w; done
  ```
- **Lo que va entre corchetes** (`[N]`, `[zona]`…) se lee en la pantalla en directo. Nunca se dice una cifra de memoria.
- **Textos de la web:** la entrega de UX (19 nov como tarde, decisión de Mariano tras la prueba con la persona mayor) cambia las palabras de las bandas, la lista del móvil y «Casi encajan». Por eso el guion no cita esas etiquetas: describe lo que se ve, y en pantalla se lee lo que salga.
- **Textos de los botones:** son los de producción, comprobados en las capturas del 11 nov:
  - buscador: `evidence/gate-06/2026-11-11-deploy/prod-buscador-*.png` y `prod-buscador-check.json` (PR #11);
  - «Qué falta»: `evidence/map-004/2026-11-11/prod_c4_*`. La de Puente de Vallecas con gap-0.3 la hizo B en el PR #17 (`evidence/map-004/2026-11-12/deck/deck_c4_puente_de_vallecas_escuelas_infantiles_1440.png`).
- **Cifras:** las del bloque 3 se comprobaron en producción el 12 nov, con gap-0.3 (D-217) ya desplegado. Las del bloque 2 se comprobaron en producción el 15 nov, con `fit-0.9` (D-243, la fórmula «cerca y plazas») y el alquiler de referencia del Ministerio de Vivienda en los pueblos (D-242). Fuente: `POST /api/v1/search` con el caso de ejemplo y la web, a 1440 px.
- **Buscador:** encendido en producción desde el 11 nov y verificado por C: smoke 7/7, axe AA sin fallos y la consola limpia (`deploy-12-buscador.md`, misma rama y PR). El bloque 2 va con buscador.
- **El bloque 2 sin buscador queda de reserva.** Sirve solo si la demo vuelve a enseñar «Muy pronto», por ejemplo porque C ha vuelto a una versión sin buscador.
- **Paquete sin red (`make demo-offline`):** desde el 12 nov compila la web con el buscador encendido, comprobado con y sin red (`infra/deploy/offline/demo_offline.sh`, `evidence/gate-06/2026-11-12-deploy/offline-buscador.md`, `4cc3f84`). C lo regeneró el 12 nov con `28a0f2f` y el fondo de calles sin red. Los recorridos del pitch pasan 66/66 y 40/40 sin red. La búsqueda del caso de ejemplo y «Qué falta» de Madrid, Chamartín y Fuencarral-El Pardo dan lo mismo que producción (`evidence/gate-06/2026-11-12-deploy/deploy-17-pub001.md`).

| Bloque | Tiempo | Duración | Contenido | Palabras | Tiempo hablado a 130 ppm |
|---|---|---|---|---|---|
| 1 | 0:00–0:40 | 40 s | Problema: personas y ayuntamientos deciden a ciegas | 74 | 34 s |
| 2 | 0:40–2:20 | 100 s | Demo: una familia busca dónde vivir → zonas, el porqué y «¿Y si cambias algo?» | 142 | 66 s + unos 25 s de clics |
| 2 sin buscador (reserva) | 0:40–2:20 | 100 s | Demo: el mapa, una zona en 3D y sus minutos a pie | 136 | 63 s + unos 15 s de clics |
| 3 | 2:20–3:40 | 80 s | Puente de Vallecas, su lista de lo que falta y a cuántos niños afecta | 127 | 59 s + unos 15 s de clics |
| 4 | 3:40–4:30 | 50 s | Datos CM, código abierto y quién paga | 95 | 44 s |
| 5 | 4:30–5:00 | 30 s | Impacto, prueba con usuarios y cierre | 58 | 27 s |
| **Total** | | **300 s** | | **496 con buscador; 490 sin él** | **Con buscador: 229 s + unos 40 s de clics = unos 31 s de margen. Sin buscador: 226 s + unos 30 s de clics = unos 44 s de margen** |

---

> Las decisiones del 11 nov están registradas como D-199 a D-207 (`docs/00_index/01_decisions_log.md`). El brief de diseño (`DISENO_VIDA_FACIL.md`, adoptado por D-201) sigue fuera del repo: se cita como documento interno, no como evidencia pública.

## Antes de empezar (en la sala, 13:30–17:00)
1. Portátil con cargador, wifi del evento probada, HDMI probado y resolución 1920 × 1080 (`docs/09_datamad/25_plan_competicion.md` §9).
2. Navegador en ventana limpia, zoom al 100 %, sin extensiones visibles y con las notificaciones desactivadas.
3. Pestaña 1: las slides en PDF, en la slide 1. Pestaña 2: la portada de la demo, ya cargada una vez para tener la caché caliente. URL: https://vidafacil-madrid.vercel.app (verificada el 11 nov con el buscador encendido: smoke 7/7, `evidence/gate-06/2026-11-11-deploy/deploy-12-buscador.md`, PR #11).
4. Plan B abierto en una pestaña oculta: el vídeo de 2 min (PITCH-003, `pitch/video_respaldo.md`; lo graba Mariano el 23 nov) y el paquete sin red de C (`make demo-offline`, `infra/deploy/offline/`), que ya tiene el buscador: con el paquete el guion no cambia.
5. Pestaña de respaldo del bloque 3, ya cargada: https://vidafacil-madrid.vercel.app/que-falta?zona=distrito/2807913 (Puente de Vallecas).

---

## Bloque 1 · 0:00–0:40 · El problema
**Pantalla:** slide 1 (título), y en «Otros servicios…» se pasa a la slide 2.

<!-- habla:b1:inicio -->
Buenas tardes. Imaginad una familia que busca piso en Madrid. El precio lo mira en una web, los colegios en otra y el transporte en otra. Nadie le dice qué zona va con su vida. Un ayuntamiento tiene el problema al revés: quiere saber dónde falta una escuela infantil o un centro de salud, y los datos le llegan sueltos. Otros servicios te enseñan lo que hay. Vida Fácil te enseña lo que falta.
<!-- habla:b1:fin -->

**Al terminar:** cambiar a la pestaña de la demo (Cmd + 2).

---

## Bloque 2 · 0:40–2:20 · Una familia busca dónde vivir
Con el buscador, encendido en producción desde el 11 nov. Si la demo vuelve a enseñar «Muy pronto», se salta al bloque 2 sin buscador, debajo.

**Caso precargado:** `data/fixtures/contracts/scenario_state.familia_castellana.fixture.json`:
- alquiler de hasta 1.500 €/mes;
- 2 adultos y 2 hijos de 4 y 8 años;
- trabajo en el Paseo de la Castellana (Azca), 4 días por semana;
- colegio a 10 min andando como mucho, obligatorio;
- le importan, por este orden, los colegios, el transporte y la salud.

**Resultado en producción** (15 nov, `fit-0.9`, D-243). Sale de `POST /api/v1/search` con el fixture y de la web, comprobados por D. Se lee en pantalla, nunca de memoria. El 25 nov se vuelve a comprobar en producción:
- encajan **42 de las 199 zonas** (178 municipios y los 21 distritos de Madrid), 157 no cumplen todo y ninguna sale sin datos. Eran 27 y 15 sin datos hasta que el alquiler de referencia del Ministerio rellenó los pueblos (D-242);
- **todas cumplen lo que pide la familia; el % dice cuánto encaja todo lo demás.** Junto al %, la web lo dice en palabras, en cuatro bandas: de las 42, 12 están en la más alta (90 % o más), 5 en la segunda (75–89), 13 en la tercera (60–74) y 12 en la última;
- **arriba empatan Puente de Vallecas y Latina al 94 %.** La web pone 1.ª a Puente de Vallecas porque, a igual %, tiene más cerca los servicios del día a día, y avisa del empate. Siguen Usera y Moratalaz (93 %); Tetuán, Ciudad Lineal y Villaverde (92 %), y Carabanchel, Coslada y Leganés (90 %);
- **en Puente de Vallecas** (la tarjeta que se abre):
  - «Colegio con primaria a unos 4 min andando» («Dato fiable»), «Parada de autobús a unos 2 min andando · Metro o Cercanías a unos 10 min» y «Centro de salud a unos 8 min andando»;
  - «41 min en transporte público hasta Paseo de la Castellana (Azca), llegando a las 9:00» («Dato aproximado»);
  - «Alquiler ≈ 1.129 €/mes por 77 m² (14,7 €/m², contratos firmados en 2024)»;
  - debajo, su resumen de lo que falta dice que faltan escuelas infantiles: es el puente con el bloque 3;
- **en Latina** (por si se abre): colegio a unos 6 min, parada a unos 2, centro de salud a unos 10, 39 min hasta la Castellana y ≈ 1.101 €/mes. Pierde unos 6 puntos: 3 por el trayecto, 1,1 por el colegio, 1,1 por la parada y 0,9 por el centro de salud, que va justo de plazas (D-243 §9);
- **«¿Y si cambias algo?»:**
  - «+5 min a pie hasta colegio con primaria: saldrían 91 zonas, 49 más»;
  - «+150 €/mes: saldrían 45 zonas, 3 más»;
  - lo que más limita sigue siendo el colegio a 10 min;
- **se quedan cerca, por el presupuesto,** Chamartín, Arganzuela, Centro, Chamberí y Retiro. La web no les pone %: dice cuánto se pasan; Chamartín, unos 90 € al mes (≈ 1.590 €/mes);
- **antes** (`fit-0.6`, 12 nov): Latina 1.ª al 98 %, con cuatro empatadas; y con la distancia en línea recta (`fit-0.1`), Ciudad Lineal al 99 %.

<!-- habla:b2:inicio -->
Abro el caso de ejemplo: una pareja con dos hijos de cuatro y ocho años. Trabajan en la Castellana, pueden pagar hasta mil quinientos euros de alquiler y quieren un colegio a diez minutos andando como mucho. El mapa se colorea: cuanto más violeta, mejor encaja. Encajan [cuarenta y dos] de [ciento noventa y nueve] zonas: todas cumplen lo que piden, y el porcentaje dice cuánto encaja todo lo demás. Arriba empatan [Puente de Vallecas] y [Latina], al [noventa y cuatro]. Abro la primera: [colegio con primaria a unos cuatro minutos andando] y [cuarenta y un minutos en transporte público hasta su trabajo], con los horarios del Consorcio. Cada hecho dice cuánto nos fiamos del dato. ¿Y si quieren más opciones? Con [cinco minutos más] hasta el colegio salen [cuarenta y nueve] zonas más: lo que más les limita es [el colegio].
<!-- habla:b2:fin -->

| # | Acción | Qué tiene que verse | Si falla |
|---|---|---|---|
| 2.1 | Clic en «Ver un ejemplo: pareja con 2 hijos que trabaja en la Castellana» (portada) | Se rellena «Tu búsqueda» y la búsqueda sale sola: el mapa en violetas y, a la derecha, la lista de zonas que encajan: 42, con las dos primeras empatadas al 94 % | Si tarda más de 3 s, seguir hablando del mapa; si no llega, pasar al vídeo (plan B) |
| 2.2 | Señalar el mapa y su leyenda | La leyenda cuenta 42 zonas que cumplen todo, 157 que no y 0 sin datos | — |
| 2.3 | Clic en la 1.ª de «Zonas que encajan» y leer dos hechos | Tarjeta de Puente de Vallecas: el 94 %, su banda en palabras, que es la 1.ª y que empata con Latina. En «Lo que tienes aquí», «Colegio con primaria a unos 4 min andando» («Dato fiable») y «41 min en transporte público hasta Paseo de la Castellana (Azca), llegando a las 9:00» («Dato aproximado»: confianza 0,7, horarios programados de un día laborable). Si sale otra zona, se leen los corchetes tal como salgan | Leer solo el % de encaje, su banda y la fiabilidad |
| 2.4 | Cerrar la tarjeta (×), bajar hasta «¿Y si cambias algo?» y pulsar «Ver todas las opciones» | «+5 min a pie hasta colegio con primaria: saldrían 91 zonas, 49 más» y «+150 €/mes: saldrían 45 zonas, 3 más», y «Lo que más limita tu búsqueda es: Colegio con primaria a 10 min andando como mucho» | Leer solo la opción, que se ve aunque el bloque esté plegado |

**«¿Y si cambias algo?» sale siempre.** Va plegado a la opción que más zonas suma y se despliega solo con 5 zonas o menos (decisión de datamad-10; PR #10). Con 42 zonas sale plegado: por eso el paso 2.4 pulsa «Ver todas las opciones» (comprobado en producción el 15 nov, `RealityCheck.tsx`). Si las cifras de la pantalla cambian, la frase hablada se ajusta a lo que se lea.

### Bloque 2 sin buscador (reserva) · 0:40–2:20 · Qué tiene cerca una familia
**Cuándo:** solo si la demo vuelve a enseñar «Muy pronto» (ver «Reglas del guion»). No se nombra el buscador ni el % de encaje.

<!-- habla:b2s:inicio -->
Esta es Vida Fácil: el mapa de toda la Comunidad de Madrid, con sus ciento setenta y nueve municipios y Madrid capital dividida en sus veintiún distritos, porque no es lo mismo vivir en uno que en otro. Pensad en esa familia. Toco un distrito, por ejemplo [zona]. La cámara entra en tres dimensiones, con sus colegios, centros de salud y estaciones. A la derecha, qué falta aquí y cuánto se tarda andando: [N] minutos hasta el centro de salud más cercano. No en línea recta: por las calles de verdad, a paso tranquilo, el mismo que usa el Ayuntamiento. Y cada dato dice de dónde sale: pulso aquí y me lleva a la ficha del portal de datos abiertos de la Comunidad. Así la familia sabe qué tiene cerca antes de mirar un solo piso.
<!-- habla:b2s:fin -->

| # | Acción | Qué tiene que verse | Si falla |
|---|---|---|---|
| 2s.1 | Señalar el mapa de la región | Los 179 municipios y los 21 distritos | — |
| 2s.2 | Clic en un distrito (propuesta: Chamartín, el de la captura C5) | Vuelo de cámara y zona en 3D con etiquetas de cristal; tarjeta «Qué falta aquí» con «A pie: N min» | Sin 3D: seguir en 2D y quitar «en tres dimensiones» |
| 2s.3 | Leer los minutos a pie del centro de salud en la tarjeta | «A pie: [N] min» (`zona.falta.a_pie`; mediana de las calles a 4 km/h, D-211) | Saltar la frase de los minutos |
| 2s.4 | Clic en «Cómo lo calculamos» o en la fuente de una fila | Nombre del dataset y enlace a la ficha del portal CM | Enseñar el pie «Datos: 35 conjuntos de la Comunidad de Madrid…» (producción, 15 nov) |

**Fuentes:** 179 municipios y 21 distritos: D-200 · D-209. Paso de 4 km/h, el del estudio «El Madrid de los 15 minutos» del Ayuntamiento: D-211. Captura de referencia: `evidence/map-004/2026-11-11/prod_c5_chamartin_3d_desktop.png` (producción, MAP-004).

---

## Bloque 3 · 2:20–3:40 · Qué le falta a una zona real
**Zona: Puente de Vallecas** (distrito 2807913). Desde el 12 nov la lista mide lo que la gente tiene a 15 minutos andando, repartido entre todos los que lo comparten (D-217, `gap-0.3`; en llano, `pitch/metodologia.md` §1.4). Con ese método, Madrid capital ya no sale FALTA en centros de salud: sale JUSTO (0,95). Puente de Vallecas tiene una FALTA clara que se entiende en una frase, y además es la 1.ª para la familia del bloque 2 (94 %, empatada con Latina). Las dos cosas cuadran: la familia no marca escuela infantil, así que esa FALTA no le baja el %. Si la marcara, Puente de Vallecas se quedaría en el 89 % («Faltan escuelas infantiles: como mucho 89 %»; comprobado en producción el 15 nov, D-243). Datos reales, comprobados en producción el 12 nov con `GET /api/v1/gaps/distrito/2807913` (`gap-0.3`, `data_version: 2026-11-12`):
- Escuelas infantiles **FALTA**: 2,781 escuelas al alcance a pie por cada 1.000 niños de 0 a 4 años, frente a 4,87 en los «Otros municipios urbanos de la Comunidad de Madrid» (ratio 0,571; `reliable: true`; sin `comparison_group`). En pantalla: «2,8 escuelas infantiles al alcance a pie por cada 1.000 niños de 0 a 4 años; en los demás municipios urbanos de la Comunidad de Madrid, 4,9 (en toda la Comunidad, 4,7)».
- La mitad de la zona tiene la escuela infantil más cercana a 6 min o menos (`min_a_pie_escuela_infantil` = 6,258). Contando escuelas por habitante sale casi lo mismo (2,708): no es un efecto del método.
- Farmacias **CUBIERTO**: 4,5 frente a 3,1. Colegio, centro de salud y mayores, también CUBIERTO; vivienda, SIN DATOS (la CM no lo publica por distrito).
- **El 25 nov se vuelve a mirar:** si Puente de Vallecas ya no sale FALTA, se elige otra con `GET /api/v1/gaps?level=distrito&row=escuela_infantil` (hoy también Villaverde y Carabanchel) y se cambian las cifras de aquí y de la slide 3.
- **Si preguntan por Madrid capital:** sale JUSTO en centros de salud (0,3603 frente a 0,3799). La frase «un tercio menos» ya no vale (D-217 §7).

<!-- habla:b3:inicio -->
Ahora cambio de usuario: un ayuntamiento. Para esta familia, Puente de Vallecas está arriba, pero encajar no quiere decir que no le falte nada. Abro su lista de lo que falta. No contamos centros: medimos lo que la gente tiene a quince minutos andando, repartido entre todos los que lo comparten, y lo comparamos con municipios parecidos. Aquí, escuelas infantiles: falta. Hay una a [seis] minutos, pero son pocas para tantos niños: aquí hay [cincuenta y siete] por cada cien que hay en municipios parecidos. [Leer una fila cubierta]. Y si no tenemos el dato, lo decimos: nunca inventamos una falta. En toda la región, [más de veinticinco mil] niños de cero a cuatro años viven donde faltan escuelas infantiles. Así ve un concejal dónde invertir primero.
<!-- habla:b3:fin -->

| # | Acción | Qué tiene que verse | Si falla |
|---|---|---|---|
| 3.1 | Pestaña «Qué falta» y elegir «Puente de Vallecas» en la lista de zonas | La lista del distrito con sus 6 filas FALTA / JUSTO / CUBIERTO / SIN DATOS, valor, referencia, fiabilidad, minutos a pie y datasets | Abrir la pestaña preparada con `/que-falta?zona=distrito/2807913` |
| 3.2 | Señalar la fila de escuelas infantiles y leer los minutos y la frase principal | «A pie: 6 min» y «Aquí hay 57 por cada 100 que hay en municipios parecidos». La cifra técnica («2,8 escuelas infantiles al alcance a pie por cada 1.000 niños de 0 a 4 años; en los demás municipios urbanos…, 4,9») queda tras «Ver la cifra»: no se abre, salvo que pregunten | Leer solo el estado y la frase |
| 3.3 | Señalar la fila de farmacias (CUBIERTO) | «4,5 farmacias al alcance a pie por cada 10.000 habitantes; en los demás municipios urbanos…, 3,1» | Si no está CUBIERTO, saltar «[Leer una fila cubierta]» |
| 3.4 | Antes de «En toda la región…», volver a la pestaña de las slides, en la slide 3, y leer la cifra grande. El orden de «dónde invertir primero» está en la slide y en la web («Qué falta» sin zona, en producción desde el 12 nov) | «25.551 niños de 0 a 4 años viven donde faltan escuelas infantiles» y «Dónde invertir primero: Puente de Vallecas…, Carabanchel y Villaverde» | Si la slide no está, decir la frase sin la cifra: «En toda la región hay miles de niños pequeños donde faltan escuelas infantiles» |

**Barrios (D-232, D-238):** no se enseñan con un clic en la demo: elegir «Madrid capital» y buscar de nuevo cuesta unos 10 s, y el bloque 2 solo tiene unos 8 s de holgura. Se nombran en el cierre (bloque 5, «buscar por barrios»), con el recuadro de la slide 4. Si preguntan, preguntas 48 y 52: con el caso de ejemplo y «Madrid capital» encajan 78 de 131 barrios, con Puerta del Ángel, Vinateros y Lucero al 95 % (producción, 15 nov, `fit-0.9`).

**Cifra de impacto** (D-229, `impact-0.1`; `GET /api/v1/gaps/impact`; `evidence/gate-04/2026-11-12/impact-cifras.txt`, con los datos del 12 nov):
- 25.551 niños de 0 a 4 años (el 9,8 % de la región) viven en los 3 distritos con FALTA de escuelas infantiles: Puente de Vallecas 9.433 («Aquí hay 57 por cada 100»), Carabanchel 9.150 (68) y Villaverde 6.968 (61). Es el padrón de cada distrito.
- En la web, «Qué falta» sin zona enseña lo mismo en «Dónde invertir primero» (producción, 12 nov, comprobado por C).
- En voz alta se redondea: «más de veinticinco mil».
- **En producción desde el 12 nov** (`GET /api/v1/gaps/impact`, `impact-0.1`: 25.551 de 260.310 niños, en 3 zonas). El 25 nov se vuelve a comprobar con la ruta.

**Al terminar:** volver a la slide 2 para el bloque 4.

---

## Bloque 4 · 3:40–4:30 · Datos, código abierto y quién paga
**Pantalla:** la slide 2 en «Treinta y cinco conjuntos…» y la slide 3 en «¿Quién paga?».

**«¿Quién paga?»:** el modelo que eligió Mariano el 12 nov (`pitch/modelo_negocio.md`). Ayuntamientos: informe de 990–1.500 € por contrato menor. Promotoras y consultoras: estudios de 490 a 1.500 €. Las cifras no se dicen en voz alta; si preguntan, pregunta 6 de `pitch/preguntas.md`.

<!-- habla:b4:inicio -->
¿Con qué datos? Treinta y cinco conjuntos del Portal de Datos Abiertos de la Comunidad de Madrid: población, hogares, vivienda, renta, alquiler, colegios, salud, mayores, farmacias, aire, el transporte del Consorcio y la accesibilidad de sus estaciones. Todos pasan un control de calidad antes de entrar, y cada cifra guarda de dónde viene. El código es abierto y cualquiera puede reproducirlo. ¿Quién paga? Los ayuntamientos, por el informe de lo que les falta, y las promotoras, por estudios de zona. Para las personas es gratis. Y nunca vendemos datos de personas: solo zonas, siempre sumadas.
<!-- habla:b4:fin -->

**Fuentes de lo que se dice:**
- «Treinta y cinco conjuntos» y «control de calidad»: `pitch/datasets_cm.md` (35 con Gate 1 en PASS, regenerado el 15 nov) y `GET /api/v1/datasets?cm_only=true` en producción (`cm_open_data_count: 35`, comprobado el 15 nov; 52 conjuntos en total). Eran 27 el 12 nov; suben a 29 con D-235 (infracciones penales y antigüedad de las viviendas) y a 35 con D-237 (los aparcamientos de disuasión del Consorcio y las 3 fichas de la red de calidad del aire) y D-241 (compraventas de vivienda nueva y usada, y valor tasado por antigüedad). El 23 nov se regenera y, si cambia el número, se cambia la frase.
- «El transporte del Consorcio»: sus 6 redes, las 3 topologías con la accesibilidad de las estaciones y los aparcamientos de disuasión, todos con ficha en el portal (D-196, D-223, D-237).
- «Aire»: las 3 fichas de la red de calidad del aire de la Comunidad (D-237). Es contexto de la zona: no puntúa.
- «Código abierto»: `LICENSE` (Apache-2.0, D-191).
- «Quién paga»: modelo del documento de la idea, `docs/09_datamad/25_plan_competicion.md` §1.

---

## Bloque 5 · 4:30–5:00 · Impacto y cierre
**Pantalla:** la slide 4 (pantallazo) con la URL y los QR.

<!-- habla:b5:inicio -->
Vida Fácil cambia la pregunta. No es solo dónde hay pisos: es dónde puedes vivir bien con lo que necesitas, y qué le falta a cada zona para que más gente pueda. La probaron siete personas, y ya tiene lo que pidieron: buscar por barrios y un límite de tiempo al trabajo. Encuentra tu sitio en Madrid. Gracias.
<!-- habla:b5:fin -->

**Prueba con usuarios (del 13 al 15 nov):** la frase «La probaron siete personas…» sustituye a «Funciona con datos reales y oficiales de toda la Comunidad de Madrid.», para no bajar de 30 s de margen; los datos oficiales ya se dicen en el bloque 4. Tiene una palabra menos que la versión del 14 nov, que nombraba las paradas de autobús: «buscar por barrios» va en su lugar porque lo pidieron 4 de las 6 personas (D-238). Las citas están en la slide 3, el recuadro «Probada con 7 personas» en la slide 4, que está en pantalla, y la respuesta larga en la pregunta 43.
- **Siete personas:** seis de 26 a 55 años y una persona mayor, que la probó el 15 nov en el móvil y a la que le costó (letra y botones pequeños, palabras técnicas, demasiado a la vez). Se ha auditado y Mariano ha decidido el alcance (portada clara, letra de 16 px como mínimo, botones de 44 px, lenguaje llano y lo esencial primero); llega con la entrega de UX, el 19 nov como tarde (**pendiente de B**), y no se dice como hecho hasta que esté desplegado. Lo dicho está en producción desde el 14 nov: «¿Dónde?» con Madrid capital por barrios (D-238, despliegue de `f1b6f5a`) y el límite de tiempo al trabajo (PR #53, despliegue de `ad4a8f2`).

**Fuente de la frase de reserva:** «toda la Comunidad» = los 179 municipios de `evidence/gate-01/2026-10-20/cm_secciones_censales/row_counts.json`. El buscador cubre las 199 zonas: 178 municipios y los 21 distritos de Madrid, que sustituyen al municipio (D-215, punto 1). La lista de lo que falta responde en municipios y distritos.

---

## Ensayos (25 nov, 5 cronometrados; PITCH-004)
- Cronómetro por bloque y anotar el tiempo real en esta tabla. Si un bloque se pasa más de 5 s, recortar su texto y volver a contar las palabras.
- Un ensayo con la wifi apagada, usando el plan B, para practicar el cambio sin perder el hilo.

| Ensayo | B1 | B2 | B3 | B4 | B5 | Total | Notas |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | | |
| 2 | | | | | | | |
| 3 | | | | | | | |
| 4 | | | | | | | |
| 5 | | | | | | | |
