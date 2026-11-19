# Guion de 5 minutos — Vida Fácil (final del 26 nov)

## Reglas del guion
- **Formato:** 5 min de exposición + 5 de preguntas (bases §9). Demo en directo sobre la web desplegada y slides solo al principio y al final.
- **Ritmo:** unas 130 palabras por minuto. En los bloques con demo se habla menos, porque los clics y las transiciones también ocupan tiempo.
- **Recuento por bloque** (texto entre los marcadores `habla:bN`):
  ```bash
  for b in 1 2 2s 3 4 5; do printf "b$b "; awk -v b=$b '$0 ~ "^<!-- habla:b"b":fin"{f=0} f; $0 ~ "^<!-- habla:b"b":inicio"{f=1}' pitch/guion.md | wc -w; done
  ```
- **Lo que va entre corchetes** (`[N]`, `[zona]`…) se lee en la pantalla en directo. Nunca se dice una cifra de memoria.
- **Textos de la web:** son los de la claridad en el móvil (D-244 y D-245), en producción desde el 15 nov con `55651c2` (`evidence/gate-06/2026-11-15-deploy/deploy-35-55651c2-ux3.md`, PR #84). Los comprobó D en producción el 18 nov, a 1440 px, con el caso de ejemplo; son los de las capturas C1, C2, C3 y C6 (`pitch/capturas/`), y lo que se vio, con sus cifras, está en `pitch/comprobacion_produccion_18nov.md`:
  - la lista se llama «Zonas que os convienen» («te» con una persona) y cada fila dice la zona, su banda en palabras («Muy buena opción», «Buena opción», «Opción regular» o «Poco recomendable») y «Unos … € al mes». En escritorio el % va pequeño detrás de la banda. La lista ya no dice «Empatan»: el empate sale dentro de «Ver más»;
  - «Casi encajan» pasa a «Casi valen» y «¿Y si cambias algo?» a «¿Queréis ver más zonas?»;
  - la tarjeta enseña lo esencial y lo demás va tras «Ver más sobre {zona}».
- **Textos de los botones de «Qué falta»:** son los de producción, comprobados en las capturas del 11 nov:
  - `evidence/map-004/2026-11-11/prod_c4_*`. La de Puente de Vallecas con gap-0.3 la hizo B en el PR #17 (`evidence/map-004/2026-11-12/deck/deck_c4_puente_de_vallecas_escuelas_infantiles_1440.png`).
- **Cifras:** las del bloque 3 se comprobaron en producción el 12 nov, con gap-0.3 (D-217) ya desplegado. Las del bloque 2 se comprobaron en producción el 15 nov, con `fit-0.9` (D-243, la fórmula «cerca y plazas») y el alquiler de referencia del Ministerio de Vivienda en los pueblos (D-242), y otra vez el 18 nov, con las palabras de la claridad en el móvil. Fuente: `POST /api/v1/search` con el caso de ejemplo y la web, a 1440 px.
- **Buscador:** encendido en producción desde el 11 nov y verificado por C: smoke 7/7, axe AA sin fallos y la consola limpia (`deploy-12-buscador.md`, misma rama y PR). El bloque 2 va con buscador.
- **El bloque 2 sin buscador queda de reserva.** Sirve solo si la demo vuelve a enseñar «Muy pronto», por ejemplo porque C ha vuelto a una versión sin buscador.
- **Paquete sin red (`make demo-offline`):** desde el 12 nov compila la web con el buscador encendido, comprobado con y sin red (`infra/deploy/offline/demo_offline.sh`, `evidence/gate-06/2026-11-12-deploy/offline-buscador.md`, `4cc3f84`). C lo regeneró el 12 nov con `28a0f2f` y el fondo de calles sin red. Los recorridos del pitch pasan 66/66 y 40/40 sin red. La búsqueda del caso de ejemplo y «Qué falta» de Madrid, Chamartín y Fuencarral-El Pardo dan lo mismo que producción (`evidence/gate-06/2026-11-12-deploy/deploy-17-pub001.md`).

| Bloque | Tiempo | Duración | Contenido | Palabras | Tiempo hablado a 130 ppm |
|---|---|---|---|---|---|
| 1 | 0:00–0:40 | 40 s | Problema: personas y ayuntamientos deciden a ciegas | 74 | 34 s |
| 2 | 0:40–2:15 | 95 s | Demo: una familia busca dónde vivir → zonas que le convienen, la tarjeta, «Ver más» y «¿Queréis ver más zonas?» | 130 | 60 s + unos 28 s de clics |
| 2 sin buscador (reserva) | 0:40–2:15 | 95 s | Demo: el mapa, una zona en 3D y sus minutos a pie | 136 | 63 s + unos 15 s de clics |
| 3 | 2:15–3:30 | 75 s | Puente de Vallecas, su lista de lo que falta y a cuántos niños afecta | 125 | 58 s + unos 15 s de clics |
| 4 | 3:30–4:25 | 55 s | Datos CM, código abierto, API y MCP gratis, quién paga y la versión para inversores | 106 | 49 s |
| 5 | 4:25–5:00 | 35 s | Impacto, prueba con usuarios (también la persona mayor) y cierre | 66 | 30 s |
| **Total** | | **300 s** | | **501 con buscador; 507 sin él** | **Con buscador: 231 s + unos 43 s de clics = unos 26 s de margen. Sin buscador: 234 s + unos 30 s de clics = unos 36 s de margen** |

**Recuento del 19 nov, tras el despliegue de `/desarrolladores`** (comando de arriba): b1 74, b2 130, b2s 136, b3 125, b4 106 y b5 66. El bloque 4 suma «La API y el MCP para agentes de IA son gratis para todos.» (13 palabras, unos 6 s), ahora que la página pública de la API y el MCP está en producción (D-249). Es una propuesta de D: Mariano lo dejó a su criterio. De 93 a 106 palabras: 501 con buscador y 507 sin él, y el margen baja de unos 32 a unos 26 s. Si no se quiere, se quita esa frase y el margen vuelve a unos 32 s.

**Recuento del 19 nov, tras el despliegue de la versión para inversores:** b4 93. El bloque 4 dice 39 conjuntos (mismas palabras que 36), y la versión para inversores pasa de siguiente paso a hecha (D-248, en producción): «Pagarán inversores y promotores, y su versión ya está en la web…» sustituye a «Pagan…, por saber qué falta antes de construir», a la frase del suelo público y al «Siguiente paso». La redacción es genérica a propósito («la viabilidad sobre una parcela y el contexto de su barrio»): la versión pasa a ser por parcela exacta (ver abajo, «Fuentes de lo que se dice»). Sin «de dónde vivir a dónde construir» (revisión del #98, R-02: hoy ninguna parcela se cruza con la vivienda que le falta a su zona). De 102 a 93 palabras: 488 con buscador y 494 sin él, y el margen sube a unos 32 s.

**Recuento del 19 nov, mañana:** b4 102. El bloque 4 cambia «¿Quién paga?» al modelo del 19 nov (personas y ayuntamientos gratis; pagan inversores y promotores): de 34 a 35 palabras, y el margen se queda en unos 28 s (229 s hablados con buscador; 232 s sin él).

**Recuento del 18 nov, noche:** b4 101. El bloque 4 suma la frase del suelo público, ya en producción (D-246, despliegue de `747cb65`), sin cifra por decisión de Mariano (10 palabras), y pierde la lista «población, vivienda, renta, colegios, salud, farmacias y el transporte del Consorcio» (11 palabras), que ya está por temas en la slide 2: de 102 a 101 palabras. El margen se queda en unos 28 s. Antes, el mismo día: b4 102 («letra más grande», revisión del #86; el bloque 2 ganó un clic, «Ver más», y perdió 12 palabras).

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

## Bloque 2 · 0:40–2:15 · Una familia busca dónde vivir
Con el buscador, encendido en producción desde el 11 nov. Si la demo vuelve a enseñar «Muy pronto», se salta al bloque 2 sin buscador, debajo.

**Caso precargado:** `data/fixtures/contracts/scenario_state.familia_castellana.fixture.json`:
- alquiler de hasta 1.500 €/mes;
- 2 adultos y 2 hijos de 4 y 8 años;
- trabajo en el Paseo de la Castellana (Azca), 4 días por semana;
- colegio a 10 min andando como mucho, obligatorio;
- le importan, por este orden, los colegios, el transporte y la salud.

**Resultado en producción** (15 nov, `fit-0.9`, D-243; palabras comprobadas otra vez el 18 nov con `55651c2`). Sale de `POST /api/v1/search` con el fixture y de la web, comprobados por D. Se lee en pantalla, nunca de memoria. El 25 nov se vuelve a comprobar en producción:
- **«Zonas que os convienen»:** arriba de la lista, «Hemos encontrado 42 zonas para vosotros.»; la leyenda del mapa cuenta 42 que cumplen todo, 157 que no y 0 sin datos, de las 199 zonas (178 municipios y los 21 distritos de Madrid). Eran 27 y 15 sin datos hasta que el alquiler de referencia del Ministerio rellenó los pueblos (D-242);
- **todas cumplen lo que pide la familia; el % dice cuánto le conviene todo lo demás.** Cada fila lo dice en palabras, en cuatro bandas: de las 42, 12 «Muy buena opción» (90 % o más), 5 «Buena opción» (75–89), 13 «Opción regular» (60–74) y 12 «Poco recomendable». Debajo de la banda, «Unos … € al mes»; en escritorio, el % pequeño detrás de la banda («Muy buena opción · 94 %»);
- **arriba, Puente de Vallecas y Latina, las dos «Muy buena opción · 94 %».** La web pone 1.ª a Puente de Vallecas porque, a igual %, tiene más cerca los servicios del día a día. La lista ya no dice «Empatan»: el empate sale en «Ver más» («Igual de buena que Latina (94 %).»). Siguen Usera y Moratalaz (93 %); Tetuán, Ciudad Lineal y Villaverde (92 %), y Carabanchel, Coslada y Leganés (90 %);
- **la tarjeta de Puente de Vallecas** (lo esencial, sin bajar):
  - «‹ Volver a la lista», «Puente de Vallecas» y «Distrito de Madrid · Muy buena opción»;
  - «Unos 1.129 € al mes», con «Precio orientativo»;
  - «Colegio con primaria a unos 4 min andando», «Parada de autobús a unos 2 min andando · Metro o Cercanías a unos 10 min» y «Centro de salud a unos 8 min andando»;
  - «41 min en transporte público hasta Paseo de la Castellana (Azca), llegando a las 9:00»;
  - «No le falta nada de lo que buscáis.»;
- **«Ver más sobre Puente de Vallecas»** (plegado):
  - «Muy buena opción · 94 %», «¿Qué es el %?», «La 1.ª que más os conviene» e «Igual de buena que Latina (94 %).»;
  - «Lo que tenéis aquí», cada hecho con su fiabilidad: «Dato fiable» en el colegio, la parada, el centro de salud y el alquiler («Alquiler unos 1.129 € al mes por 77 m² (14,7 €/m², contratos firmados en 2024)»), y «Dato aproximado» en los 41 min;
  - «Lo que le falta a esta zona»: «Tiene lo que pedís. Aun así, comparado con municipios parecidos, aquí faltan escuelas infantiles.», con colegios, centros de salud y farmacias CUBIERTO (a pie, 4, 8 y 3 min). Es el puente con el bloque 3;
  - «Ver todo lo que falta» y «Ver la zona»;
- **en Latina** (por si se abre): colegio a unos 6 min, parada a unos 2, centro de salud a unos 10, 39 min hasta la Castellana y unos 1.101 € al mes. Pierde unos 6 puntos: 3 por el trayecto, 1,1 por el colegio, 1,1 por la parada y 0,9 por el centro de salud, que va justo de plazas (D-243 §9);
- **«¿Queréis ver más zonas?»:** «Hemos encontrado 42 zonas para vosotros. Mirad cuántas salen si cambiáis una sola cosa:»
  - «+5 min a pie hasta colegio con primaria · saldrían 49 más: 91 zonas en total», con el botón «Ver esas zonas»;
  - «+150 €/mes · saldrían 3 más: 45 zonas en total»;
  - «Lo que más limita vuestra búsqueda es: Colegio con primaria a 10 min andando como mucho»;
- **«Casi valen (5)»** (plegado): «Les falta una sola cosa de lo que pedís.» Chamartín, Arganzuela, Centro, Chamberí y Retiro, sin %: cada una dice cuánto se pasa. Chamartín, «Se pasa unos 90 € al mes de vuestro presupuesto» (unos 1.590 € al mes);
- **antes** (`fit-0.6`, 12 nov): Latina 1.ª al 98 %, con cuatro empatadas; y con la distancia en línea recta (`fit-0.1`), Ciudad Lineal al 99 %.

<!-- habla:b2:inicio -->
Abro el caso de ejemplo: una pareja con dos hijos de cuatro y ocho años. Trabajan en la Castellana, pueden pagar hasta mil quinientos euros de alquiler y quieren un colegio a diez minutos andando como mucho. El mapa se colorea: cuanto más violeta, más les conviene. Les convienen [cuarenta y dos] de [ciento noventa y nueve] zonas, y todas cumplen lo que piden. Cada una dice si es buena opción y cuánto costaría. Abro la primera: [colegio con primaria a unos cuatro minutos andando], [cuarenta y un minutos en transporte público hasta su trabajo] y no le falta nada de lo que buscan. En «Ver más», cuánto nos fiamos de cada dato. ¿Y si quieren más zonas? Con [cinco minutos más] hasta el colegio salen [cuarenta y nueve] más.
<!-- habla:b2:fin -->

| # | Acción | Qué tiene que verse | Si falla |
|---|---|---|---|
| 2.1 | Clic en «Ejemplo: pareja con 2 hijos que trabaja en la Castellana» (portada) | Se rellena «Tu búsqueda» y la búsqueda sale sola: el mapa en violetas y, a la derecha, «Zonas que os convienen» con «Hemos encontrado 42 zonas para vosotros.» y las dos primeras, Puente de Vallecas y Latina, «Muy buena opción · 94 %» | Si tarda más de 3 s, seguir hablando del mapa; si no llega, pasar al vídeo (plan B) |
| 2.2 | Señalar el mapa, su leyenda y una fila de la lista | La leyenda cuenta 42 zonas que cumplen todo, 157 que no y 0 sin datos. Cada fila: la zona, su banda en palabras y «Unos … € al mes» (Puente de Vallecas, «Unos 1.129 € al mes») | — |
| 2.3 | Clic en la 1.ª de «Zonas que os convienen» y leer dos hechos | Tarjeta de Puente de Vallecas, lo esencial sin bajar: «Distrito de Madrid · Muy buena opción», «Unos 1.129 € al mes», «Colegio con primaria a unos 4 min andando», «41 min en transporte público hasta Paseo de la Castellana (Azca), llegando a las 9:00» y «No le falta nada de lo que buscáis.». Si sale otra zona, se leen los corchetes tal como salgan | Leer solo la banda y los dos hechos |
| 2.4 | Clic en «Ver más sobre Puente de Vallecas» y señalar la fiabilidad | «Muy buena opción · 94 %», «La 1.ª que más os conviene», «Igual de buena que Latina (94 %).» y, en «Lo que tenéis aquí», «Dato fiable» en el colegio y «Dato aproximado» en los 41 min (confianza 0,7: horarios programados de un día laborable) | Saltar «En “Ver más”…» y seguir |
| 2.5 | «‹ Volver a la lista», bajar hasta «¿Queréis ver más zonas?» y pulsar «Ver todas las opciones» | «+5 min a pie hasta colegio con primaria · saldrían 49 más: 91 zonas en total», «+150 €/mes · saldrían 3 más: 45 zonas en total» y «Lo que más limita vuestra búsqueda es: Colegio con primaria a 10 min andando como mucho» | Leer solo la primera opción, que se ve aunque el bloque esté plegado |

**«¿Queréis ver más zonas?» sale siempre.** Va plegado a la opción que más zonas suma y se despliega solo con 5 zonas o menos (decisión de datamad-10; PR #10). Con 42 zonas sale plegado: por eso el paso 2.5 pulsa «Ver todas las opciones» (comprobado en producción el 18 nov, `RealityCheck.tsx`). Si las cifras de la pantalla cambian, la frase hablada se ajusta a lo que se lea.

**«Casi valen» no se abre en la demo** (va plegado y no cabe en el tiempo). Si preguntan por las zonas que se quedan fuera por poco: Chamartín «Se pasa unos 90 € al mes de vuestro presupuesto».

### Bloque 2 sin buscador (reserva) · 0:40–2:15 · Qué tiene cerca una familia
**Cuándo:** solo si la demo vuelve a enseñar «Muy pronto» (ver «Reglas del guion»). No se nombra el buscador ni el % de encaje.

<!-- habla:b2s:inicio -->
Esta es Vida Fácil: el mapa de toda la Comunidad de Madrid, con sus ciento setenta y nueve municipios y Madrid capital dividida en sus veintiún distritos, porque no es lo mismo vivir en uno que en otro. Pensad en esa familia. Toco un distrito, por ejemplo [zona]. La cámara entra en tres dimensiones, con sus colegios, centros de salud y estaciones. A la derecha, qué falta aquí y cuánto se tarda andando: [N] minutos hasta el centro de salud más cercano. No en línea recta: por las calles de verdad, a paso tranquilo, el mismo que usa el Ayuntamiento. Y cada dato dice de dónde sale: pulso aquí y me lleva a la ficha del portal de datos abiertos de la Comunidad. Así la familia sabe qué tiene cerca antes de mirar un solo piso.
<!-- habla:b2s:fin -->

| # | Acción | Qué tiene que verse | Si falla |
|---|---|---|---|
| 2s.1 | Señalar el mapa de la región | Los 179 municipios y los 21 distritos | — |
| 2s.2 | Clic en un distrito (propuesta: Chamartín, el de la captura C5) | Vuelo de cámara y zona en 3D con etiquetas de cristal; tarjeta «Qué falta aquí» con «A pie: N min» | Sin 3D: seguir en 2D y quitar «en tres dimensiones» |
| 2s.3 | Leer los minutos a pie del centro de salud en la tarjeta | «A pie: [N] min» (`zona.falta.a_pie`; mediana de las calles a 4 km/h, D-211) | Saltar la frase de los minutos |
| 2s.4 | Clic en «Cómo lo calculamos» o en la fuente de una fila | Nombre del dataset y enlace a la ficha del portal CM | Enseñar el pie «Datos: 39 conjuntos de la Comunidad de Madrid…» (el número es `cm_open_data_count`, `apps/web/src/lib/provenance.ts`: 39 en producción el 19 nov) |

**Fuentes:** 179 municipios y 21 distritos: D-200 · D-209. Paso de 4 km/h, el del estudio «El Madrid de los 15 minutos» del Ayuntamiento: D-211. Captura de referencia: `evidence/map-004/2026-11-11/prod_c5_chamartin_3d_desktop.png` (producción, MAP-004).

---

## Bloque 3 · 2:15–3:30 · Qué le falta a una zona real
**Zona: Puente de Vallecas** (distrito 2807913). Desde el 12 nov la lista mide lo que la gente tiene a 15 minutos andando, repartido entre todos los que lo comparten (D-217, `gap-0.3`; en llano, `pitch/metodologia.md` §1.4). Con ese método, Madrid capital ya no sale FALTA en centros de salud: sale JUSTO (0,95). Puente de Vallecas tiene una FALTA clara que se entiende en una frase, y además es la 1.ª para la familia del bloque 2 (94 %, igual que Latina). Las dos cosas cuadran, y la web lo dice así: la tarjeta pone «No le falta nada de lo que buscáis.» y, en «Ver más», «Tiene lo que pedís. Aun así, comparado con municipios parecidos, aquí faltan escuelas infantiles.» (producción, 18 nov). La familia no marca escuela infantil, así que esa FALTA no le baja el %. Si la marcara, Puente de Vallecas se quedaría en el 89 % («Faltan escuelas infantiles: como mucho 89 %»; comprobado en producción el 15 nov, D-243). Datos reales, comprobados en producción el 12 nov con `GET /api/v1/gaps/distrito/2807913` (`gap-0.3`, `data_version: 2026-11-12`):
- Escuelas infantiles **FALTA**: 2,781 escuelas al alcance a pie por cada 1.000 niños de 0 a 4 años, frente a 4,87 en los «Otros municipios urbanos de la Comunidad de Madrid» (ratio 0,571; `reliable: true`; sin `comparison_group`). En pantalla: «2,8 escuelas infantiles al alcance a pie por cada 1.000 niños de 0 a 4 años; en los demás municipios urbanos de la Comunidad de Madrid, 4,9 (en toda la Comunidad, 4,7)».
- La mitad de la zona tiene la escuela infantil más cercana a 6 min o menos (`min_a_pie_escuela_infantil` = 6,258). Contando escuelas por habitante sale casi lo mismo (2,708): no es un efecto del método.
- Farmacias **CUBIERTO**: 4,5 frente a 3,1. Colegio, centro de salud y mayores, también CUBIERTO; vivienda, SIN DATOS (la CM no lo publica por distrito).
- **El 25 nov se vuelve a mirar:** si Puente de Vallecas ya no sale FALTA, se elige otra con `GET /api/v1/gaps?level=distrito&row=escuela_infantil` (hoy también Villaverde y Carabanchel) y se cambian las cifras de aquí y de la slide 3.
- **Si preguntan por Madrid capital:** sale JUSTO en centros de salud (0,3603 frente a 0,3799). La frase «un tercio menos» ya no vale (D-217 §7).

<!-- habla:b3:inicio -->
Ahora cambio de usuario: un ayuntamiento. A esta familia no le falta nada en Puente de Vallecas, pero a la zona sí. Abro su lista de lo que falta. No contamos centros: medimos lo que la gente tiene a quince minutos andando, repartido entre todos los que lo comparten, y lo comparamos con municipios parecidos. Aquí, escuelas infantiles: falta. Hay una a [seis] minutos, pero son pocas para tantos niños: aquí hay [cincuenta y siete] por cada cien que hay en municipios parecidos. [Leer una fila cubierta]. Y si no tenemos el dato, lo decimos: nunca inventamos una falta. En toda la región, [más de veinticinco mil] niños de cero a cuatro años viven donde faltan escuelas infantiles. Así ve un concejal dónde invertir primero.
<!-- habla:b3:fin -->

| # | Acción | Qué tiene que verse | Si falla |
|---|---|---|---|
| 3.1 | Pestaña «Qué falta» y elegir «Puente de Vallecas» en la lista de zonas | La lista del distrito con sus 6 filas FALTA / JUSTO / CUBIERTO / SIN DATOS, valor, referencia, fiabilidad, minutos a pie y datasets | Abrir la pestaña preparada con `/que-falta?zona=distrito/2807913` |
| 3.2 | Señalar la fila de escuelas infantiles y leer los minutos y la frase principal | «Aquí hay 57 por cada 100 que hay en municipios parecidos.», «Afecta a 9.433 niños de 0 a 4 años.» y, a pie hasta la escuela infantil más cercana, «6 min» (producción, 18 nov). La cifra técnica («2,8 escuelas infantiles al alcance a pie por cada 1.000 niños de 0 a 4 años; en los demás municipios urbanos…, 4,9») queda tras «Ver la cifra»: no se abre, salvo que pregunten | Leer solo el estado y la frase |
| 3.3 | Señalar la fila de farmacias (CUBIERTO) | «4,5 farmacias al alcance a pie por cada 10.000 habitantes; en los demás municipios urbanos…, 3,1» | Si no está CUBIERTO, saltar «[Leer una fila cubierta]» |
| 3.4 | Antes de «En toda la región…», volver a la pestaña de las slides, en la slide 3, y leer la cifra grande. El orden de «dónde invertir primero» está en la slide y en la web («Qué falta» sin zona, en producción desde el 12 nov) | «25.551 niños de 0 a 4 años viven donde faltan escuelas infantiles» y «Dónde invertir primero: Puente de Vallecas…, Carabanchel y Villaverde» | Si la slide no está, decir la frase sin la cifra: «En toda la región hay miles de niños pequeños donde faltan escuelas infantiles» |

**Barrios (D-232, D-238):** no se enseñan con un clic en la demo: elegir «Madrid capital» y buscar de nuevo cuesta unos 10 s, y el bloque 2 solo tiene unos 7 s de holgura. Se ven en el recuadro de la slide 4 («buscar por barrios»), en pantalla durante el cierre. Si preguntan, preguntas 48 y 52: con el caso de ejemplo y «Madrid capital» cumplen todo 78 de 131 barrios, con Puerta del Ángel, Vinateros y Lucero al 95 % (producción, 15 nov, `fit-0.9`).

**Cifra de impacto** (D-229, `impact-0.1`; `GET /api/v1/gaps/impact`; `evidence/gate-04/2026-11-12/impact-cifras.txt`, con los datos del 12 nov):
- 25.551 niños de 0 a 4 años (el 9,8 % de la región) viven en los 3 distritos con FALTA de escuelas infantiles: Puente de Vallecas 9.433 («Aquí hay 57 por cada 100»), Carabanchel 9.150 (68) y Villaverde 6.968 (61). Es el padrón de cada distrito.
- En la web, «Qué falta» sin zona enseña lo mismo en «Dónde invertir primero» (producción, 12 nov, comprobado por C).
- En voz alta se redondea: «más de veinticinco mil».
- **En producción desde el 12 nov** (`GET /api/v1/gaps/impact`, `impact-0.1`: 25.551 de 260.310 niños, en 3 zonas). El 25 nov se vuelve a comprobar con la ruta.

**Al terminar:** volver a la slide 2 para el bloque 4.

---

## Bloque 4 · 3:30–4:25 · Datos, código abierto, API y MCP gratis, quién paga y la versión para inversores
**Pantalla:** la slide 2 en «Treinta y nueve conjuntos…» y la slide 3 en «¿Quién paga?» (la columna «Viabilidad», que acaba con «Ya está, para inversores (piloto en Madrid): viabilidad sobre una parcela, con el contexto de su barrio.», lo mismo que se dice).

**«¿Quién paga?»:** el modelo que decidió Mariano el 19 nov, que sustituye al del 12 nov (`pitch/modelo_negocio.md`). Personas y ayuntamientos, gratis; pagarán inversores y promotores privados, con un plan de precios. «Pagarán» porque hoy no se cobra: durante el concurso la versión para inversores es de acceso libre, sin cuentas ni cobro (D-248 §1). Los precios son hipótesis y no se dicen en voz alta; si preguntan, pregunta 6 de `pitch/preguntas.md`.

<!-- habla:b4:inicio -->
¿Con qué datos? Treinta y nueve conjuntos del Portal de Datos Abiertos de la Comunidad de Madrid. Todos pasan un control de calidad antes de entrar, y cada cifra guarda de dónde viene. El código es abierto y cualquiera puede reproducirlo. La API y el MCP para agentes de IA son gratis para todos. ¿Quién paga? Gratis para personas y ayuntamientos: cada ayuntamiento ve qué le falta a su municipio. Nunca vendemos datos personales: solo zonas, siempre sumadas. Pagarán inversores y promotores, y su versión ya está en la web, con un piloto en Madrid: la viabilidad sobre una parcela y el contexto de su barrio.
<!-- habla:b4:fin -->

**Fuentes de lo que se dice:**
- «Treinta y nueve conjuntos» y «control de calidad»: `pitch/datasets_cm.md` (39 con Gate 1 en PASS, regenerado el 19 nov) y `GET /api/v1/datasets?cm_only=true` en producción (`cm_open_data_count: 39`, comprobado por D el 19 nov; 59 conjuntos en total). Eran 27 el 12 nov; suben a 29 con D-235 (infracciones penales y antigüedad de las viviendas), a 35 con D-237 (los aparcamientos de disuasión del Consorcio y las 3 fichas de la red de calidad del aire) y D-241 (compraventas de vivienda nueva y usada, y valor tasado por antigüedad), a 36 con D-246 (el Portal del Suelo 4.0) y a 39 con D-247 (el Catastro por uso de la Comunidad: por municipio y por distrito) y D-248 (los visados de obra, con su presupuesto). El 23 nov se regenera y, si cambia el número, se cambia la frase.
- Qué conjuntos son: ya no se dice en voz alta (sale el 18 nov para dejar sitio al suelo público). Están en la slide 2, por temas, también el transporte del Consorcio: sus 6 redes, las 3 topologías con la accesibilidad de las estaciones y los aparcamientos de disuasión, todos con ficha en el portal (D-196, D-223, D-237).
- «Código abierto»: `LICENSE` (Apache-2.0, D-191).
- «La API y el MCP para agentes de IA son gratis para todos» (13 palabras, unos 6 s): decisión de Mariano del 19 nov (`pitch/modelo_negocio.md`). Se explica en una página pública, `/desarrolladores`, **en producción desde el 19 nov** (D-249; despliegue de `20b46d9` verificado por C: `evidence/gate-06/2026-11-19-deploy/deploy-38-20b46d9-desarrolladores.md`, PR #99). La API: las 13 rutas de datos, sin clave, cada una con un `curl` probado contra producción. El MCP: 7 herramientas, marcado «Funciona en local». El MCP en remoto, las claves opcionales, los avisos de suelo nuevo y las descargas en CSV y GeoJSON están marcados «Aún no disponible», y no se dicen. No se dice «en remoto» ni que un agente se conecta por internet: hoy el MCP se arranca en local. Va sin cifras. Si preguntan, preguntas 1 y 2; si preguntan si se cobra, la 6. **En pantalla:** la slide 3 no cambia (no dice API ni MCP).
- «Quién paga» (24 palabras, unos 11 s): decisión de Mariano del 19 nov, que sustituye a la del 12 nov (`pitch/modelo_negocio.md`). «Cada ayuntamiento ve qué le falta a su municipio» es «Qué falta», en producción en los 179 municipios y los 21 distritos de Madrid (`GET /api/v1/gaps?level=municipio` y `?level=distrito`, comprobado por D el 19 nov), gratis y sin contrato. Los precios no se dicen: si preguntan, pregunta 6.
- «Pagarán inversores y promotores, y su versión ya está en la web…» (28 palabras, unos 13 s): **en producción desde el 19 nov** (D-247, los datos; D-248, la viabilidad, la API y la web; despliegue de `396d8f6` y sync, verificado por C antes y después del sync: `evidence/gate-06/2026-11-19-deploy/deploy-37-396d8f6-inversores.md`, PR #96).
  - «Pagarán»: es el modelo, no algo que ya se cobre. La web dice «Plan Inversor (acceso libre durante el concurso)»: sin cobro, sin cuentas y sin datos de nadie (D-248 §1; leído por D en `/inversores` el 19 nov).
  - «Un piloto en Madrid»: hoy, los barrios de Madrid capital dentro de la M-40 (D-247 §1; `GET /api/v1/investors/zones`: 108 barrios en 17 distritos, comprobado por D el 19 nov).
  - «La viabilidad sobre una parcela y el contexto de su barrio»: la calculadora de viabilidad v0 (método residual, `viability-0.1`, D-248 §3–5) parte de los m² edificables de una parcela pública del Portal del Suelo (D-246), de un ámbito del Plan General (D-247 §4) o de los que pone la persona. Con el precio del suelo da un semáforo: «Sale», «Ajustar» o «No sale». La ficha del barrio da el contexto: qué falta, los precios, el alquiler y la demanda. Sustituye a la frase del 18 nov «Ya enseñamos el suelo público para vivienda de la Comunidad»: ese suelo sigue en la web y está dentro de esta versión.
  - **Redacción genérica a propósito (datamad-10, 19 nov):** Mariano quiere la versión por parcela exacta: referencia catastral, dirección o clic en el mapa, con la calificación de la parcela, y la lista de barrios en segundo plano. Hasta que datamad-10 la confirme en producción, ni detalle ni capturas de la versión por barrios; entonces se revisan esta frase, la slide 3 y las preguntas 6 y 60, con capturas nuevas.
  - Va sin cifras: no están en pantalla, y la regla de arriba no deja decir una de memoria. En voz alta no se nombra ninguna empresa.
  - **Ya no se dice «de dónde vivir a dónde construir»** (revisión del #98, R-02). Hoy ninguna parcela se cruza con la vivienda que le falta a su zona, y dicho tras «su versión ya está en la web» prometería más de lo que hay. Ese cruce (Housing Gap: `docs/03_intelligence/16_housing_gap_product_recommender.md` y `51_housing_gap_math_spec.md`; capa PRO: `docs/01_product/05_pro_layer.md`) se dice en futuro y solo si preguntan (pregunta 60).

---

## Bloque 5 · 4:25–5:00 · Impacto y cierre
**Pantalla:** la slide 4 (pantallazo) con la URL y los QR.

<!-- habla:b5:inicio -->
Vida Fácil cambia la pregunta. No es solo dónde hay pisos: es dónde puedes vivir bien con lo que necesitas, y qué le falta a cada zona para que más gente pueda. La probaron siete personas, y ya tiene lo que pidieron. A una persona mayor le costó, y ya es más sencilla: letra más grande y lo esencial primero. Encuentra tu sitio en Madrid. Gracias.
<!-- habla:b5:fin -->

**Prueba con usuarios (del 13 al 15 nov):** la frase «La probaron siete personas…» sustituye a «Funciona con datos reales y oficiales de toda la Comunidad de Madrid.»; los datos oficiales ya se dicen en el bloque 4. Lo que pidieron no se enumera en voz alta: está en el recuadro «Probada con 7 personas» de la slide 4, en pantalla: «Lo que pidieron, ya en la web: buscar por barrios y un límite de tiempo al trabajo. Y, para una persona mayor, más sencilla en el móvil.» (lo de los barrios lo pidieron 4 de las 6 personas, D-238; las paradas de autobús, que también pidieron, salen de la slide para que quepa la persona mayor y siguen en la pregunta 43). Las citas están en la slide 3 y la respuesta larga en la pregunta 43.
- **Siete personas:** seis de 26 a 55 años y una persona mayor. Lo que pidieron las seis está en producción desde el 14 nov: «¿Dónde?» con Madrid capital por barrios (D-238, despliegue de `f1b6f5a`) y el límite de tiempo al trabajo (PR #53, despliegue de `ad4a8f2`).
- **La persona mayor** la probó el 15 nov en el móvil y le costó: letra y botones pequeños, palabras técnicas y demasiado a la vez. **Desde el 15 nov está en producción lo que se cambió por eso** (D-244 y D-245, despliegues de `e0417ae`, `c0e9d11` y `55651c2`: `evidence/gate-06/2026-11-15-deploy/deploy-33-e0417ae-ux1.md`, `deploy-34-c0e9d11-ux2.md` y `deploy-35-55651c2-ux3.md`):
  - letra de 16 px o más y botones de 44 px o más en todo el móvil: medido a 390 y a 360 px en todas las pantallas, 0 textos por debajo y 0 botones por debajo, y axe sin incidencias (`evidence/gate-06/2026-11-15-ux-1/ux-movil-1.md` y `2026-11-16-ux-2/ux-movil-2.md`). Antes, a 390 px, había 8 textos por debajo en la portada, 24 en el formulario, 36 en la lista y 25 en la tarjeta;
  - lenguaje llano, «tú» o «vosotros» según el hogar (D-245 §11);
  - una portada que dice para qué sirve: «Te decimos en qué zonas de la Comunidad de Madrid puedes vivir con tu presupuesto y con lo que necesitas cerca.»;
  - «Somos mayores», que pregunta «¿Cerca de dónde queréis vivir?» (D-244);
  - una lista con 4 cosas por fila en el móvil, en vez de 7 a 9;
  - una tarjeta con lo esencial (en el móvil, 12 cosas en la primera pantalla en vez de 17) y lo demás tras «Ver más»;
  - «No sabemos si le faltan…» cuando falta el dato.
- **Todavía no hay segunda prueba con personas.** Mariano manda ahora la segunda ronda: hasta que vuelva, se dice lo que se ha cambiado y medido, nunca que a la persona mayor ya le resulta fácil. Si llegan resultados antes del 26 nov, se añaden a la pregunta 43.

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
