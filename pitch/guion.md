# Guion de 5 minutos — Vida Fácil (final del 26 nov)

## Reglas del guion
- **Formato:** 5 min de exposición + 5 de preguntas (bases §9). Demo en directo sobre la web desplegada y slides solo al principio y al final.
- **Ritmo:** unas 130 palabras por minuto. En los bloques con demo se habla menos, porque los clics y las transiciones también ocupan tiempo.
- **Recuento por bloque** (texto entre los marcadores `habla:bN`):
  ```bash
  for b in 1 2 2s 3 4 5; do printf "b$b "; awk -v b=$b '$0 ~ "^<!-- habla:b"b":fin"{f=0} f; $0 ~ "^<!-- habla:b"b":inicio"{f=1}' pitch/guion.md | wc -w; done
  ```
- **Lo que va entre corchetes** (`[N]`, `[zona]`…) se lee en la pantalla en directo. Nunca se dice una cifra de memoria.
- **Textos de los botones:** son los de producción, comprobados en las capturas del 11 nov:
  - buscador: `evidence/gate-06/2026-11-11-deploy/prod-buscador-*.png` y `prod-buscador-check.json` (PR #11);
  - «Qué falta»: `evidence/map-004/2026-11-11/prod_c4_*`. La captura de Puente de Vallecas con gap-0.3 está **pendiente de B**.
- **Cifras:** las del bloque 2 y del bloque 3 se comprobaron en producción el 12 nov, con gap-0.3 (D-217) ya desplegado.
- **Buscador:** encendido en producción desde el 11 nov y verificado por C: smoke 7/7, axe AA sin fallos y la consola limpia (`deploy-12-buscador.md`, misma rama y PR). El bloque 2 va con buscador.
- **El bloque 2 sin buscador queda de reserva.** Sirve solo si la demo vuelve a enseñar «Muy pronto», por ejemplo porque C ha vuelto a una versión sin buscador.
- **Paquete sin red (`make demo-offline`):** desde el 12 nov compila la web con el buscador encendido, comprobado con y sin red (`infra/deploy/offline/demo_offline.sh`, `evidence/gate-06/2026-11-12-deploy/offline-buscador.md`, `4cc3f84`). Pero sus datos son de `1913393`, de antes de gap-0.3: **pendiente de C** regenerarlo después de gap-0.3, para que Puente de Vallecas salga igual que en producción.

| Bloque | Tiempo | Duración | Contenido | Palabras | Tiempo hablado a 130 ppm |
|---|---|---|---|---|---|
| 1 | 0:00–0:40 | 40 s | Problema: personas y ayuntamientos deciden a ciegas | 79 | 36 s |
| 2 | 0:40–2:40 | 120 s | Demo: una familia busca dónde vivir → zonas, el porqué y «¿Y si cambias algo?» | 186 | 86 s + clics |
| 2 sin buscador (reserva) | 0:40–2:40 | 120 s | Demo: el mapa, una zona en 3D y sus minutos a pie | 136 | 63 s + clics |
| 3 | 2:40–3:40 | 60 s | Puente de Vallecas y su lista de lo que falta | 114 | 53 s + clics |
| 4 | 3:40–4:30 | 50 s | Datos CM, código abierto y quién paga | 95 | 43 s |
| 5 | 4:30–5:00 | 30 s | Impacto y cierre | 50 | 23 s |
| **Total** | | **300 s** | | **524 con buscador; 474 sin él** | **Con buscador: 242 s + unos 40 s de clics = unos 18 s de margen. Sin buscador: 219 s + unos 30 s de clics = unos 51 s de margen** |

---

> Las decisiones del 11 nov están registradas como D-199 a D-207 (`docs/00_index/01_decisions_log.md`). El brief de diseño (`~/Desktop/DATAMAD/prompts/DISENO_VIDA_FACIL.md`, adoptado por D-201) sigue fuera del repo: se cita como documento interno, no como evidencia pública.

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
Buenas tardes. Imaginad una familia que busca piso en Madrid. El precio lo mira en una web, los colegios en otra y el transporte en otra. Nadie le dice qué zona va con su vida. Un ayuntamiento tiene el problema al revés: quiere saber dónde falta una escuela infantil o un centro de salud, y los datos le llegan sueltos. Otros servicios te enseñan lo que hay. Vida Fácil te enseña lo que falta. Os lo enseño en directo.
<!-- habla:b1:fin -->

**Al terminar:** cambiar a la pestaña de la demo (Cmd + 2).

---

## Bloque 2 · 0:40–2:40 · Una familia busca dónde vivir
Con el buscador, encendido en producción desde el 11 nov. Si la demo vuelve a enseñar «Muy pronto», se salta al bloque 2 sin buscador, debajo.

**Caso precargado:** `data/fixtures/contracts/scenario_state.familia_castellana.fixture.json`:
- alquiler de hasta 1.500 €/mes;
- 2 adultos y 2 hijos de 4 y 8 años;
- trabajo en el Paseo de la Castellana (Azca), 4 días por semana;
- colegio a 10 min andando como mucho, obligatorio;
- le importan, por este orden, los colegios, el transporte y la salud.

**Resultado en producción** (12 nov, tras gap-0.3 y D-216: `POST /api/v1/search` con el fixture; las mismas cifras que la base local de A en `evidence/gate-04/2026-11-12/golden-search.txt`, `golden_family`). Se lee en pantalla, nunca de memoria; el 25 nov se vuelve a comprobar:
- encajan 33 de las 199 zonas (178 municipios y los 21 distritos de Madrid), y en 15 falta algún dato;
- 1.ª, Ciudad Lineal, 99 %: «Colegio con primaria a 5 min andando», parada a 2 min, centro de salud a 10 min, a 3,2 km en línea recta de Azca y «Alquiler medio ≈ 1.070 €/mes por 77 m²»;
- 2.ª, Tetuán (98 %); después, Hortaleza y Moratalaz, empatadas al 97 %: no se dice un orden entre ellas. Puente de Vallecas sale 7.ª (96 %) y Chamartín 8.ª (95 %);
- «¿Y si cambias algo?»: «+5 min a pie hasta colegio con primaria: saldrían 50 zonas, 17 más». Subir 150 €/mes no añade ninguna, y la web no enseña las opciones que no suman. Lo que más limita es el colegio a 10 min;
- casi encajan Moncloa-Aravaca, Ciempozuelos y San Sebastián de los Reyes, que solo fallan por el colegio. Salamanca ya encaja (94 %): D-216 sacó las clínicas privadas del alquiler por distrito.

<!-- habla:b2:inicio -->
Esta es Vida Fácil. Abro el caso de ejemplo: una pareja con dos hijos de cuatro y ocho años. Trabajan en la Castellana, pueden pagar hasta mil quinientos euros de alquiler y quieren un colegio a diez minutos andando como mucho. No rellenan un formulario: marcan su hogar, lo que les importa y dónde trabajan. La búsqueda sale sola y el mapa se colorea: cuanto más violeta, mejor encaja la zona con esta familia. Encajan [treinta y tres] de [ciento noventa y nueve] zonas. Abro la primera, [Ciudad Lineal]. No le damos una nota sobre cien. Le damos un porcentaje de encaje y, debajo, hechos que cualquiera entiende: [colegio con primaria a cinco minutos andando], [parada a dos minutos]. Y cada hecho dice cuánto nos fiamos del dato. ¿Y si quieren más opciones? Este bloque se llama «¿Y si cambias algo?». Con [cinco minutos más] hasta el colegio salen [diecisiete] zonas más. Y la web les dice qué es lo que más les limita: [el colegio], no el dinero. No le decimos a nadie «gastad más»: le enseñamos sus alternativas y lo que cuesta cada una.
<!-- habla:b2:fin -->

| # | Acción | Qué tiene que verse | Si falla |
|---|---|---|---|
| 2.1 | Clic en «Ver un ejemplo: pareja con 2 hijos que trabaja en la Castellana» (portada) | Se rellena «Tu búsqueda» y la búsqueda sale sola: el mapa en violetas y, a la derecha, «Zonas que encajan» con «Con tu búsqueda tal cual salen 33 zonas.» | Si tarda más de 3 s, seguir hablando del mapa; si no llega, pasar al vídeo (plan B) |
| 2.2 | Señalar el mapa y su leyenda | «Cumple todo: 33 zonas · No cumple todo: 151 zonas · Sin datos: 15 zonas» | — |
| 2.3 | Clic en la 1.ª de «Zonas que encajan» y leer dos hechos | Tarjeta de Ciudad Lineal: «99 % de encaje», «La 1.ª que más encaja» y, en «Lo que tienes aquí», «Colegio con primaria a 5 min andando…» y «Parada de transporte público a 2 min andando…», cada uno con «Dato fiable». Si preguntan por el trabajo: «A 3,2 km en línea recta de Paseo de la Castellana (Azca)», con «Dato aproximado»; el tiempo en transporte público llega con CORE-009 | Leer solo el % de encaje y la fiabilidad |
| 2.4 | Cerrar la tarjeta (×), bajar hasta «¿Y si cambias algo?» y pulsar «Ver todas las opciones» | «+5 min a pie hasta colegio con primaria: saldrían 50 zonas, 17 más» (la única opción: el presupuesto no suma), «Lo que más limita tu búsqueda es: Colegio con primaria a 10 min andando como mucho» y «En 15 zonas no podemos comprobarlo todo por falta de datos. No las contamos como buenas.» | Leer solo la opción, que se ve aunque el bloque esté plegado |
| 2.5 | (Opcional, si va sobrado de tiempo) «Probar así» en la opción del colegio y después «Volver a mi búsqueda» | 50 zonas y el selector a 15 min; al volver, 33 zonas y 10 min | Solo señalar la opción, sin pulsar |

**«¿Y si cambias algo?» sale siempre.** Va plegado a la opción que más zonas suma y se despliega solo con 5 zonas o menos (decisión de datamad-10; PR #10). Con 33 zonas sale plegado: por eso el paso 2.4 pulsa «Ver todas las opciones». El botón sale porque hay zonas sin datos y una condición que limita (`RealityCheck.tsx`). Si las cifras de la pantalla cambian, la frase hablada se ajusta a lo que se lea.

### Bloque 2 sin buscador (reserva) · 0:40–2:40 · Qué tiene cerca una familia
**Cuándo:** solo si la demo vuelve a enseñar «Muy pronto» (ver «Reglas del guion»). No se nombra el buscador ni el % de encaje.

<!-- habla:b2s:inicio -->
Esta es Vida Fácil: el mapa de toda la Comunidad de Madrid, con sus ciento setenta y nueve municipios y Madrid capital dividida en sus veintiún distritos, porque no es lo mismo vivir en uno que en otro. Pensad en esa familia. Toco un distrito, por ejemplo [zona]. La cámara entra en tres dimensiones, con sus colegios, centros de salud y estaciones. A la derecha, qué falta aquí y cuánto se tarda andando: [N] minutos hasta el centro de salud más cercano. No en línea recta: por las calles de verdad, a paso tranquilo, el mismo que usa el Ayuntamiento. Y cada dato dice de dónde sale: pulso aquí y me lleva a la ficha del portal de datos abiertos de la Comunidad. Así la familia sabe qué tiene cerca antes de mirar un solo piso.
<!-- habla:b2s:fin -->

| # | Acción | Qué tiene que verse | Si falla |
|---|---|---|---|
| 2s.1 | Señalar el mapa de la región | Los 179 municipios y los 21 distritos | — |
| 2s.2 | Clic en un distrito (propuesta: Chamartín, el de la captura C5) | Vuelo de cámara y zona en 3D con etiquetas de cristal; tarjeta «Qué falta aquí» con «A pie: N min» | Sin 3D: seguir en 2D y quitar «en tres dimensiones» |
| 2s.3 | Leer los minutos a pie del centro de salud en la tarjeta | «A pie: [N] min» (`zona.falta.a_pie`; mediana de las calles a 4 km/h, D-211) | Saltar la frase de los minutos |
| 2s.4 | Clic en «Cómo lo calculamos» o en la fuente de una fila | Nombre del dataset y enlace a la ficha del portal CM | Enseñar el pie «Datos: 23 conjuntos de la Comunidad de Madrid…» |

**Fuentes:** 179 municipios y 21 distritos: D-200 · D-209. Paso de 4 km/h, el del estudio «El Madrid de los 15 minutos» del Ayuntamiento: D-211. Captura de referencia: `evidence/map-004/2026-11-11/prod_c5_chamartin_3d_desktop.png` (producción, MAP-004).

---

## Bloque 3 · 2:40–3:40 · Qué le falta a una zona real
**Zona: Puente de Vallecas** (distrito 2807913). Desde el 12 nov la lista mide lo que la gente tiene a 15 minutos andando, repartido entre todos los que lo comparten (D-217, `gap-0.3`; en llano, `pitch/metodologia.md` §1.4). Con ese método, Madrid capital ya no sale FALTA en centros de salud: sale JUSTO (0,95). Puente de Vallecas tiene una FALTA clara que se entiende en una frase, y además sale 7.ª para la familia del bloque 2. Datos reales, comprobados en producción el 12 nov con `GET /api/v1/gaps/distrito/2807913` (`gap-0.3`, `data_version: 2026-11-12`):
- Escuelas infantiles **FALTA**: 2,781 escuelas al alcance a pie por cada 1.000 niños de 0 a 4 años, frente a 4,87 en los «Otros municipios urbanos de la Comunidad de Madrid» (ratio 0,571; `reliable: true`; sin `comparison_group`). En pantalla: «2,8 escuelas infantiles al alcance a pie por cada 1.000 niños de 0 a 4 años; en los demás municipios urbanos de la Comunidad de Madrid, 4,9 (en toda la Comunidad, 4,7)».
- La escuela infantil más cercana está a 6 min o menos desde la mitad de las calles (`min_a_pie_escuela_infantil` = 6,258). Contando escuelas por habitante sale casi lo mismo (2,708): no es un efecto del método.
- Farmacias **CUBIERTO**: 4,5 frente a 3,1. Colegio, centro de salud y mayores, también CUBIERTO; vivienda, SIN DATOS (la CM no lo publica por distrito).
- **El 25 nov se vuelve a mirar:** si Puente de Vallecas ya no sale FALTA, se elige otra con `GET /api/v1/gaps?level=distrito&row=escuela_infantil` (hoy también Villaverde y Carabanchel) y se cambian las cifras de aquí y de la slide 3.
- **Si preguntan por Madrid capital:** sale JUSTO en centros de salud (0,3603 frente a 0,3799). La frase «un tercio menos» ya no vale (D-217 §7).

<!-- habla:b3:inicio -->
Ahora cambio de usuario: un ayuntamiento. Para esta familia, Puente de Vallecas encaja. Abro su lista de lo que falta. Seis filas: escuela infantil, colegio, centro de salud, mayores, farmacia y vivienda. No contamos centros: medimos lo que la gente tiene a quince minutos andando, repartido entre todos los que lo comparten, y lo comparamos con municipios parecidos. Aquí, escuelas infantiles: falta. Hay una a [seis] minutos, pero son pocas para tantos niños: [dos coma ocho] por cada mil, frente a [cuatro coma nueve] en los demás municipios urbanos. [Leer una fila cubierta]. Y si no tenemos el dato, lo decimos: nunca inventamos una falta. Un concejal ve en un minuto dónde invertir primero.
<!-- habla:b3:fin -->

| # | Acción | Qué tiene que verse | Si falla |
|---|---|---|---|
| 3.1 | Pestaña «Qué falta» y elegir «Puente de Vallecas» en la lista de zonas | La lista del distrito con sus 6 filas FALTA / JUSTO / CUBIERTO / SIN DATOS, valor, referencia, fiabilidad, minutos a pie y datasets | Abrir la pestaña preparada con `/que-falta?zona=distrito/2807913` |
| 3.2 | Señalar la fila de escuelas infantiles y leer los minutos, el valor y la referencia | «A pie: 6 min» y «2,8 escuelas infantiles al alcance a pie por cada 1.000 niños de 0 a 4 años; en los demás municipios urbanos de la Comunidad de Madrid, 4,9 (en toda la Comunidad, 4,7)» | Leer solo el estado y la frase |
| 3.3 | Señalar la fila de farmacias (CUBIERTO) | «4,5 farmacias al alcance a pie por cada 10.000 habitantes; en los demás municipios urbanos…, 3,1» | Si no está CUBIERTO, saltar «[Leer una fila cubierta]» |
| 3.4 | (Opcional, si va sobrado de tiempo) clic en el enlace de un dataset | Ficha del portal CM en una pestaña nueva | Saltarlo |

**Al terminar:** volver a la pestaña de las slides, en la slide 3.

---

## Bloque 4 · 3:40–4:30 · Datos, código abierto y quién paga
**Pantalla:** la slide 2 en «Veintitrés conjuntos…» y la slide 3 en «¿Quién paga?».

<!-- habla:b4:inicio -->
¿Con qué datos? Veintitrés conjuntos del Portal de Datos Abiertos de la Comunidad de Madrid: población, hogares, vivienda, renta, alquiler, colegios, salud, mayores, farmacias y las seis redes de transporte del Consorcio. Todos pasan un control de calidad antes de entrar, y cada cifra guarda de dónde viene. El código es abierto y cualquiera puede reproducirlo. ¿Quién paga? Las empresas: promotoras, comercios o residencias quieren saber qué falta en cada zona y pagan por análisis agregados y por la API. Para las personas es gratis. Y nunca vendemos datos de personas: solo zonas, siempre sumadas.
<!-- habla:b4:fin -->

**Fuentes de lo que se dice:**
- «Veintitrés conjuntos» y «control de calidad»: `pitch/datasets_cm.md` (23 con Gate 1 en PASS, regenerado el 12 nov) y `GET /api/v1/datasets?cm_only=true` en producción (`cm_open_data_count: 23`). El 23 nov se regenera y, si cambia el número, se cambia la frase.
- «Seis redes del Consorcio»: D-196.
- «Código abierto»: `LICENSE` (Apache-2.0, D-191).
- «Quién paga»: modelo del documento de la idea, `docs/09_datamad/25_plan_competicion.md` §1.

---

## Bloque 5 · 4:30–5:00 · Impacto y cierre
**Pantalla:** la slide 4 (pantallazo) con la URL y los QR.

<!-- habla:b5:inicio -->
Vida Fácil cambia la pregunta. No es solo dónde hay pisos: es dónde puedes vivir bien con lo que necesitas, y qué le falta a cada zona para que más gente pueda. Funciona con datos reales y oficiales de toda la Comunidad de Madrid. Encuentra tu sitio en Madrid. Gracias.
<!-- habla:b5:fin -->

**Fuente:** «toda la Comunidad» = los 179 municipios de `evidence/gate-01/2026-10-20/cm_secciones_censales/row_counts.json`. El buscador cubre las 199 zonas: 178 municipios y los 21 distritos de Madrid, que sustituyen al municipio (D-215, punto 1). La lista de lo que falta responde en municipios y distritos.

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
