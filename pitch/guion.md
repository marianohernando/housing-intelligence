# Guion de 5 minutos — Vida Fácil (final del 26 nov)

## Reglas del guion
- **Formato:** 5 min de exposición + 5 de preguntas (bases §9). Demo en directo sobre la web desplegada y slides solo al principio y al final.
- **Ritmo:** unas 130 palabras por minuto. En los bloques con demo se habla menos, porque los clics y las transiciones también ocupan tiempo.
- **Recuento por bloque** (texto entre los marcadores `habla:bN`):
  ```bash
  for b in 1 2 2s 3 4 5; do printf "b$b "; awk -v b=$b '$0 ~ "^<!-- habla:b"b":fin"{f=0} f; $0 ~ "^<!-- habla:b"b":inicio"{f=1}' pitch/guion.md | wc -w; done
  ```
- **Lo que va entre corchetes** (`[N]`, `[zona]`…) se lee en la pantalla en directo. Nunca se dice una cifra de memoria.
- **Textos de los botones:** salen del brief (`~/Desktop/DATAMAD/prompts/DISENO_VIDA_FACIL.md`). Siguen marcados **«pendiente de B»** hasta comprobarlos en la web real.
- **Buscador:** el bloque 2 se hace con el buscador **solo si** el 26 nov la demo desplegada lo tiene encendido: ya no sale «Muy pronto» (`NEXT_PUBLIC_FEATURE_SEARCH`, `apps/web/src/lib/capabilities.ts`). El cálculo ya funciona en la API con datos reales (`POST /api/v1/search`, CORE-003 y CORE-006, D-214 y D-215); faltan la conexión en la web (**pendiente de B**) y el encendido en producción (**pendiente de C**; avisa el orquestador). Si no, se usa el **bloque 2 sin buscador**, que no lo nombra ni lo promete.

| Bloque | Tiempo | Duración | Contenido | Palabras | Tiempo hablado a 130 ppm |
|---|---|---|---|---|---|
| 1 | 0:00–0:40 | 40 s | Problema: personas y ayuntamientos deciden a ciegas | 79 | 36 s |
| 2 | 0:40–2:40 | 120 s | Demo: una familia busca dónde vivir → zonas, el porqué y Reality Check (con buscador) | 187 | 86 s + clics |
| 2 sin buscador | 0:40–2:40 | 120 s | Demo: el mapa, una zona en 3D y sus minutos a pie | 136 | 63 s + clics |
| 3 | 2:40–3:40 | 60 s | Madrid capital y su lista de lo que falta | 111 | 51 s + clics |
| 4 | 3:40–4:30 | 50 s | Datos CM, código abierto y quién paga | 95 | 43 s |
| 5 | 4:30–5:00 | 30 s | Impacto y cierre | 50 | 23 s |
| **Total** | | **300 s** | | **522 con buscador; 471 sin él** | **Con buscador: 241 s + unos 35 s de clics = unos 24 s de margen. Sin buscador: 217 s + unos 30 s de clics = unos 53 s de margen** |

---

> Las decisiones del 11 nov están registradas como D-199 a D-207 (`docs/00_index/01_decisions_log.md`). El brief de diseño (`~/Desktop/DATAMAD/prompts/DISENO_VIDA_FACIL.md`, adoptado por D-201) sigue fuera del repo: se cita como documento interno, no como evidencia pública.

## Antes de empezar (en la sala, 13:30–17:00)
1. Portátil con cargador, wifi del evento probada, HDMI probado y resolución 1920 × 1080 (`docs/09_datamad/25_plan_competicion.md` §9).
2. Navegador en ventana limpia, zoom al 100 %, sin extensiones visibles y con las notificaciones desactivadas.
3. Pestaña 1: las slides en PDF, en la slide 1. Pestaña 2: la portada de la demo, ya cargada una vez para tener la caché caliente. URL: https://vidafacil-madrid.vercel.app (verificada el 11 nov: smoke 6/6, `evidence/gate-06/2026-11-11-deploy/deploy-4-supabase-smoke.md` (rama `claude/s1-deploy`, PR #6)).
4. Plan B abierto en una pestaña oculta: el vídeo de 2 min y el snapshot offline (PITCH-003, **pendiente de C**).
5. Pestaña de respaldo del bloque 3, ya cargada: https://vidafacil-madrid.vercel.app/que-falta?zona=municipio/28079.

---

## Bloque 1 · 0:00–0:40 · El problema
**Pantalla:** slide 1 (título), y en «Otros servicios…» se pasa a la slide 2.

<!-- habla:b1:inicio -->
Buenas tardes. Imaginad una familia que busca piso en Madrid. El precio lo mira en una web, los colegios en otra y el transporte en otra. Nadie le dice qué zona va con su vida. Un ayuntamiento tiene el problema al revés: quiere saber dónde falta una escuela infantil o un centro de salud, y los datos le llegan sueltos. Otros servicios te enseñan lo que hay. Vida Fácil te enseña lo que falta. Os lo enseño en directo.
<!-- habla:b1:fin -->

**Al terminar:** cambiar a la pestaña de la demo (Cmd + 2).

---

## Bloque 2 · 0:40–2:40 · Una familia busca dónde vivir (con buscador)
**Solo si el buscador está encendido** en la demo desplegada (ver «Reglas del guion»). Si no, se salta al bloque 2 sin buscador, debajo.

**Caso precargado:** `data/fixtures/contracts/scenario_state.familia_castellana.fixture.json`:
- alquiler de hasta 1.500 €/mes;
- 2 adultos y 2 hijos de 4 y 8 años;
- trabajo en el Paseo de la Castellana (Azca), 4 días por semana;
- colegio a 10 min andando como mucho, obligatorio;
- le importan, por este orden, los colegios, el transporte y la salud.

**Resultado real** (D-215, punto 9 · `evidence/gate-04/2026-11-11/phase-core003-f2.txt`, base local del 11 nov). Se lee en pantalla, nunca de memoria; antes del 26 se comprueba en la demo, que lee Supabase (sincronización pendiente de Mariano, `board/BOARD.md`):
- encajan 32 de las 199 zonas (178 municipios y los 21 distritos de Madrid);
- 1.ª, Ciudad Lineal, 99 %: «Colegio con primaria a 5 min andando», parada a 2 min, centro de salud a 11 min, a 3,2 km en línea recta de Azca y unos 1.075 €/mes por 77 m²;
- después, Hortaleza, Tetuán y Moratalaz (97 %);
- Reality Check: lo que más quita es el colegio a 10 min (+17 zonas con 5 min más; +1 con 150 €/mes más);
- casi: Salamanca, que solo falla por presupuesto (≈ 1.526 €/mes).

<!-- habla:b2:inicio -->
Esta es Vida Fácil. Abro el caso de ejemplo: una pareja con dos hijos de cuatro y ocho años. Trabajan en la Castellana, pueden pagar hasta mil quinientos euros de alquiler y quieren un colegio a diez minutos andando. No rellenan un formulario: marcan su hogar, lo que les importa y dónde trabajan. Pulso «Ver zonas que encajan». El mapa se colorea: cuanto más violeta, mejor encaja la zona con esta familia. A la derecha, la zona que más encaja. No le damos una nota sobre cien. Le damos un porcentaje de encaje y, debajo, hechos que cualquiera entiende: [leer dos hechos de la tarjeta]. Y cada hecho dice cuánto nos fiamos del dato. ¿Y si lo que buscan no existe? Esto es el Reality Check. Con su búsqueda tal cual salen [N] zonas. Si suben [X] euros, salen [N]. Si aceptan [otra condición], [N]. No le decimos a nadie «gastad más»: le enseñamos sus alternativas y lo que cuesta cada una. Y cada dato tiene su origen: pulso aquí y me lleva a la ficha del portal de datos abiertos de la Comunidad de donde sale.
<!-- habla:b2:fin -->

| # | Acción | Qué tiene que verse | Si falla |
|---|---|---|---|
| 2.1 | Clic en «Pareja con 2 hijos que trabaja en la Castellana» (portada; **pendiente de B**) | Tarjeta «Tu búsqueda» rellena: «Con hijos (2)», «Colegios», «Trabajo en: Castellana», alquiler hasta 1.500 €/mes | Rellenar a mano los chips: es más lento, así que acortar la frase del formulario |
| 2.2 | Clic en «Ver zonas que encajan» (**pendiente de B**) | Coropleta violeta y tarjeta de zona con el % de encaje y 3–5 hechos con su confianza | Si tarda más de 3 s, seguir hablando del mapa; si no llega, pasar al vídeo (plan B) |
| 2.3 | Señalar la tarjeta de zona y leer dos hechos | En Ciudad Lineal: «Colegio con primaria a 5 min andando» y «Parada de transporte público a 2 min andando» (D-215). Si preguntan por el trabajo: cuenta por distancia en línea recta (3,2 km), porque el tiempo en transporte público llega con CORE-009 | Leer solo el % de encaje y la confianza |
| 2.4 | Señalar el bloque Reality Check (la API lo calcula: D-215; pantalla **pendiente de B**) | «Con tu búsqueda: [N] zonas · +[X] €/mes: [N] · …» con cifras de la API | Ver la nota sobre el Reality Check, debajo |
| 2.5 | Clic en una opción del Reality Check | El mapa se recalcula con la condición relajada | Solo señalarla, sin pulsar |
| 2.6 | Clic en la fuente de un hecho o en «Cómo lo calculamos» (**pendiente de B**) | Nombre del dataset y enlace a la ficha del portal CM | Enseñar el pie «Datos: N conjuntos de la Comunidad de Madrid…» |

**Nota sobre el Reality Check (**pendiente de B**):** el bloque solo aparece si salen pocas zonas o ninguna (`~/Desktop/DATAMAD/prompts/DISENO_VIDA_FACIL.md`).
- **Con datos reales, el caso precargado deja 32 zonas** (D-215). Si B solo enseña el bloque cuando salen pocas, no aparecerá: hay que confirmarlo con B.
- **Si no aparece**, el paso 2.4 enseña la opción que más zonas suma, el colegio a 15 min (+17 zonas), o se baja el presupuesto con el slider a [Y] €/mes. [Y] se elige con la API para que salgan 0–3 zonas.
- **La frase hablada** se ajusta a la acción que se haga.

### Bloque 2 sin buscador · 0:40–2:40 · Qué tiene cerca una familia
**Cuándo:** mientras el buscador salga como «Muy pronto». No se nombra el buscador ni el % de encaje.

<!-- habla:b2s:inicio -->
Esta es Vida Fácil: el mapa de toda la Comunidad de Madrid, con sus ciento setenta y nueve municipios y Madrid capital dividida en sus veintiún distritos, porque no es lo mismo vivir en uno que en otro. Pensad en esa familia. Toco un distrito, por ejemplo [zona]. La cámara entra en tres dimensiones, con sus colegios, centros de salud y estaciones. A la derecha, qué falta aquí y cuánto se tarda andando: [N] minutos hasta el centro de salud más cercano. No en línea recta: por las calles de verdad, a paso tranquilo, el mismo que usa el Ayuntamiento. Y cada dato dice de dónde sale: pulso aquí y me lleva a la ficha del portal de datos abiertos de la Comunidad. Así la familia sabe qué tiene cerca antes de mirar un solo piso.
<!-- habla:b2s:fin -->

| # | Acción | Qué tiene que verse | Si falla |
|---|---|---|---|
| 2s.1 | Señalar el mapa de la región | Los 179 municipios y los 21 distritos | — |
| 2s.2 | Clic en un distrito (propuesta: Chamartín, el de la captura C5) | Vuelo de cámara y zona en 3D con etiquetas de cristal; tarjeta «Qué falta aquí» con «A pie: N min» | Sin 3D: seguir en 2D y quitar «en tres dimensiones» |
| 2s.3 | Leer los minutos a pie del centro de salud en la tarjeta | «A pie: [N] min» (`zona.falta.a_pie`; mediana de las calles a 4 km/h, D-211) | Saltar la frase de los minutos |
| 2s.4 | Clic en «Cómo lo calculamos» o en la fuente de una fila | Nombre del dataset y enlace a la ficha del portal CM | Enseñar el pie «Datos: 21 conjuntos de la Comunidad de Madrid…» |

**Fuentes:** 179 municipios y 21 distritos: D-200 · D-209. Paso de 4 km/h, el del estudio «El Madrid de los 15 minutos» del Ayuntamiento: D-211. Captura de referencia: `evidence/map-004/2026-11-11/c_zona_3d_desktop.png` (MAP-004).

---

## Bloque 3 · 2:40–3:40 · Qué le falta a una zona real
**Zona: Madrid capital** (municipio 28079). Se elige tras D-213 (`gap-0.2`), que compara cada zona con los demás municipios de su tipo: con ese método, Chamartín ya no sale FALTA en centros de salud. Madrid capital tiene una FALTA fuerte y una fila CUBIERTO, con datos reales:
- Centros de salud **FALTA**: 0,37 por cada 10.000 habitantes frente a 0,56 en los demás municipios urbanos (ratio 0,67, significativa). Fuente: D-213 («Efecto») · `data/fixtures/contracts/zone_gap_list.madrid.fixture.json` (= `GET /api/v1/gaps/municipio/28079`) · `evidence/gate-04/2026-11-11/phase-gap001-f5-review.txt`.
- Farmacias **CUBIERTO**: 5,2 frente a 3,1 (mismo fixture). Mayores, CUBIERTO; escuela infantil, colegio y vivienda, JUSTO.
- A pie, la mitad de las calles de Madrid está a 11,6 min o menos de un centro de salud; la web lo redondea a «12 min» (`min_a_pie_centro_salud`, municipio 28079, `feature_value`). Se ve en pantalla y no se lee.
- **Antes del 26:** la demo pública aún da `gap-0.1`. Hay que comprobar estas filas en `/gaps` de la demo cuando C despliegue `gap-0.2` (**pendiente de C**). Si Madrid ya no sale FALTA, se elige otra zona con una FALTA de fiabilidad alta y se cambian las cifras de aquí y de la slide 3.
- **Si preguntan por los distritos:** ningún distrito por sí solo basta para afirmar la falta (los 21 salen JUSTO en centros de salud; D-213). Es Madrid entera la que tiene un tercio menos.

<!-- habla:b3:inicio -->
Ahora cambio de usuario: un ayuntamiento. Abro «Qué falta» de Madrid capital. Seis filas: escuela infantil, colegio, centro de salud, mayores, farmacia y vivienda. Cada una se compara con municipios parecidos: Madrid, con los demás municipios urbanos; un pueblo, con los rurales. Aquí, centros de salud: falta. [valor] por cada diez mil habitantes, frente a [referencia] en los demás municipios urbanos. Un tercio menos, y con tanta gente no es casualidad. [Leer una fila cubierta]. Y si no tenemos el dato, o la zona es demasiado pequeña para saberlo, lo decimos: nunca inventamos una falta. Cada fila dice de qué dataset sale. Un concejal ve en un minuto dónde invertir primero.
<!-- habla:b3:fin -->

| # | Acción | Qué tiene que verse | Si falla |
|---|---|---|---|
| 3.1 | Pestaña «Qué falta» y elegir «Madrid» en «Municipios» | La lista de Madrid capital con sus 6 filas FALTA / JUSTO / CUBIERTO, valor, referencia, fiabilidad, minutos a pie y datasets | Abrir la pestaña preparada con `/que-falta?zona=municipio/28079`. **Pendiente de B:** comprobar que Madrid entero se puede elegir en la lista de zonas |
| 3.2 | Señalar la fila de centros de salud y leer el valor y la referencia | «0,37 centros de atención primaria por cada 10.000 habitantes; en los demás municipios urbanos de la Comunidad de Madrid, 0,56 (en toda la Comunidad, 0,59)» | — |
| 3.3 | Señalar la fila de farmacias (CUBIERTO) | «5,2 farmacias por cada 10.000 habitantes; en los demás municipios urbanos…, 3,1» | Si no está CUBIERTO, saltar «[Leer una fila cubierta]» |
| 3.4 | (Opcional, si va sobrado de tiempo) clic en el enlace de un dataset | Ficha del portal CM en una pestaña nueva | Saltarlo |

**Al terminar:** volver a la pestaña de las slides, en la slide 3.

---

## Bloque 4 · 3:40–4:30 · Datos, código abierto y quién paga
**Pantalla:** la slide 2 en «Veintiún conjuntos…» y la slide 3 en «¿Quién paga?».

<!-- habla:b4:inicio -->
¿Con qué datos? Veintiún conjuntos del Portal de Datos Abiertos de la Comunidad de Madrid: población, hogares, vivienda, renta, alquiler, colegios, salud, mayores, farmacias y las seis redes de transporte del Consorcio. Todos pasan un control de calidad antes de entrar, y cada cifra guarda de dónde viene. El código es abierto y cualquiera puede reproducirlo. ¿Quién paga? Las empresas: promotoras, comercios o residencias quieren saber qué falta en cada zona y pagan por análisis agregados y por la API. Para las personas es gratis. Y nunca vendemos datos de personas: solo zonas, siempre sumadas.
<!-- habla:b4:fin -->

**Fuentes de lo que se dice:**
- «Veintiún conjuntos» y «control de calidad»: `pitch/datasets_cm.md` y `evidence/gate-01/2026-11-10/real-run-quality.txt`. El 23 nov se regenera y, si cambia el número, se cambia la frase.
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
