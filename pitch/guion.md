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
  - buscador: `evidence/gate-06/2026-11-11-deploy/prod-buscador-*.png` y `prod-buscador-check.json`, en la rama `claude/s1-deploy` (PR #11);
  - «Qué falta»: `evidence/map-004/2026-11-11/prod_c4_*`.
- **Buscador:** encendido en producción desde el 11 nov y verificado por C: smoke 7/7, axe AA sin fallos y la consola limpia (`deploy-12-buscador.md`, misma rama y PR). El bloque 2 va con buscador.
- **El bloque 2 sin buscador queda de reserva.** Sirve si la demo vuelve a enseñar «Muy pronto», en dos casos:
  - C ha vuelto a una versión sin buscador;
  - hay que usar el paquete sin red (`make demo-offline`), que hoy compila la web sin el buscador (`infra/deploy/offline/demo_offline.sh` quita las variables `NEXT_PUBLIC_*`).

| Bloque | Tiempo | Duración | Contenido | Palabras | Tiempo hablado a 130 ppm |
|---|---|---|---|---|---|
| 1 | 0:00–0:40 | 40 s | Problema: personas y ayuntamientos deciden a ciegas | 79 | 36 s |
| 2 | 0:40–2:40 | 120 s | Demo: una familia busca dónde vivir → zonas, el porqué y «¿Y si cambias algo?» | 189 | 87 s + clics |
| 2 sin buscador (reserva) | 0:40–2:40 | 120 s | Demo: el mapa, una zona en 3D y sus minutos a pie | 136 | 63 s + clics |
| 3 | 2:40–3:40 | 60 s | Madrid capital y su lista de lo que falta | 111 | 51 s + clics |
| 4 | 3:40–4:30 | 50 s | Datos CM, código abierto y quién paga | 95 | 43 s |
| 5 | 4:30–5:00 | 30 s | Impacto y cierre | 50 | 23 s |
| **Total** | | **300 s** | | **524 con buscador; 471 sin él** | **Con buscador: 242 s + unos 40 s de clics = unos 18 s de margen. Sin buscador: 217 s + unos 30 s de clics = unos 53 s de margen** |

---

> Las decisiones del 11 nov están registradas como D-199 a D-207 (`docs/00_index/01_decisions_log.md`). El brief de diseño (`~/Desktop/DATAMAD/prompts/DISENO_VIDA_FACIL.md`, adoptado por D-201) sigue fuera del repo: se cita como documento interno, no como evidencia pública.

## Antes de empezar (en la sala, 13:30–17:00)
1. Portátil con cargador, wifi del evento probada, HDMI probado y resolución 1920 × 1080 (`docs/09_datamad/25_plan_competicion.md` §9).
2. Navegador en ventana limpia, zoom al 100 %, sin extensiones visibles y con las notificaciones desactivadas.
3. Pestaña 1: las slides en PDF, en la slide 1. Pestaña 2: la portada de la demo, ya cargada una vez para tener la caché caliente. URL: https://vidafacil-madrid.vercel.app (verificada el 11 nov con el buscador encendido: smoke 7/7, `evidence/gate-06/2026-11-11-deploy/deploy-12-buscador.md`, rama `claude/s1-deploy`, PR #11).
4. Plan B abierto en una pestaña oculta: el vídeo de 2 min (PITCH-003, `pitch/video_respaldo.md`; lo graba Mariano el 23 nov) y el paquete sin red de C (`make demo-offline`, `infra/deploy/offline/`). Sin red no hay buscador: con el paquete va el bloque 2 sin buscador.
5. Pestaña de respaldo del bloque 3, ya cargada: https://vidafacil-madrid.vercel.app/que-falta?zona=municipio/28079.

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

**Resultado en producción** (11 nov, 22:27 UTC · `evidence/gate-06/2026-11-11-deploy/prod-buscador-check.json`, rama `claude/s1-deploy`, PR #11; las mismas cifras que D-215, punto 9, en la base local). Se lee en pantalla, nunca de memoria; el 25 nov se vuelve a comprobar:
- encajan 32 de las 199 zonas (178 municipios y los 21 distritos de Madrid), y en 15 falta algún dato;
- 1.ª, Ciudad Lineal, 99 %: «Colegio con primaria a 5 min andando», parada a 2 min, centro de salud a 11 min, a 3,2 km en línea recta de Azca y «Alquiler medio ≈ 1.075 €/mes por 77 m²»;
- después, Tetuán, Hortaleza y Moratalaz, empatadas al 97 %: no se dice un orden entre ellas. Chamartín sale 8.ª (95 %);
- «¿Y si cambias algo?»: «+5 min a pie hasta colegio con primaria: saldrían 49 zonas, 17 más» y «+150 €/mes: saldrían 33 zonas, 1 más». Lo que más limita es el colegio a 10 min;
- casi encaja Salamanca, que solo falla por presupuesto (≈ 1.526 €/mes; base local, D-215, punto 9).

<!-- habla:b2:inicio -->
Esta es Vida Fácil. Abro el caso de ejemplo: una pareja con dos hijos de cuatro y ocho años. Trabajan en la Castellana, pueden pagar hasta mil quinientos euros de alquiler y quieren un colegio a diez minutos andando como mucho. No rellenan un formulario: marcan su hogar, lo que les importa y dónde trabajan. La búsqueda sale sola y el mapa se colorea: cuanto más violeta, mejor encaja la zona con esta familia. Encajan [treinta y dos] de [ciento noventa y nueve] zonas. Abro la primera, [Ciudad Lineal]. No le damos una nota sobre cien. Le damos un porcentaje de encaje y, debajo, hechos que cualquiera entiende: [colegio con primaria a cinco minutos andando], [parada a dos minutos]. Y cada hecho dice cuánto nos fiamos del dato. ¿Y si quieren más opciones? Este bloque se llama «¿Y si cambias algo?». Con [cinco minutos más] hasta el colegio salen [diecisiete] zonas más. Con [ciento cincuenta euros más] al mes, solo [una]. Lo que más les limita es [el colegio], no el dinero. No le decimos a nadie «gastad más»: le enseñamos sus alternativas y lo que cuesta cada una.
<!-- habla:b2:fin -->

| # | Acción | Qué tiene que verse | Si falla |
|---|---|---|---|
| 2.1 | Clic en «Ver un ejemplo: pareja con 2 hijos que trabaja en la Castellana» (portada) | Se rellena «Tu búsqueda» y la búsqueda sale sola: el mapa en violetas y, a la derecha, «Zonas que encajan» con «Con tu búsqueda tal cual salen 32 zonas.» | Si tarda más de 3 s, seguir hablando del mapa; si no llega, pasar al vídeo (plan B) |
| 2.2 | Señalar el mapa y su leyenda | «Cumple todo: 32 zonas · No cumple todo: 152 zonas · Sin datos: 15 zonas» | — |
| 2.3 | Clic en la 1.ª de «Zonas que encajan» y leer dos hechos | Tarjeta de Ciudad Lineal: «99 % de encaje», «La 1.ª que más encaja» y, en «Lo que tienes aquí», «Colegio con primaria a 5 min andando…» y «Parada de transporte público a 2 min andando…», cada uno con «Dato fiable». Si preguntan por el trabajo: «A 3,2 km en línea recta de Paseo de la Castellana (Azca)», con «Dato aproximado»; el tiempo en transporte público llega con CORE-009 | Leer solo el % de encaje y la fiabilidad |
| 2.4 | Cerrar la tarjeta (×), bajar hasta «¿Y si cambias algo?» y pulsar «Ver todas las opciones» | «+5 min a pie hasta colegio con primaria: saldrían 49 zonas, 17 más», «+150 €/mes: saldrían 33 zonas, 1 más» y «Lo que más limita tu búsqueda es: Colegio con primaria a 10 min andando como mucho» | Leer solo la primera opción, que se ve aunque el bloque esté plegado |
| 2.5 | (Opcional, si va sobrado de tiempo) «Probar así» en la opción del colegio y después «Volver a mi búsqueda» | 49 zonas y el selector a 15 min; al volver, 32 zonas y 10 min | Solo señalar la opción, sin pulsar |

**«¿Y si cambias algo?» sale siempre.** Va plegado a la opción que más zonas suma y se despliega solo con 5 zonas o menos (decisión de datamad-10; PR #10). Con 32 zonas sale plegado: por eso el paso 2.4 pulsa «Ver todas las opciones». Si las cifras de la pantalla cambian, la frase hablada se ajusta a lo que se lea.

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
| 2s.4 | Clic en «Cómo lo calculamos» o en la fuente de una fila | Nombre del dataset y enlace a la ficha del portal CM | Enseñar el pie «Datos: 21 conjuntos de la Comunidad de Madrid…» |

**Fuentes:** 179 municipios y 21 distritos: D-200 · D-209. Paso de 4 km/h, el del estudio «El Madrid de los 15 minutos» del Ayuntamiento: D-211. Captura de referencia: `evidence/map-004/2026-11-11/prod_c5_chamartin_3d_desktop.png` (producción, MAP-004).

---

## Bloque 3 · 2:40–3:40 · Qué le falta a una zona real
**Zona: Madrid capital** (municipio 28079). Se elige tras D-213 (`gap-0.2`), que compara cada zona con los demás municipios de su tipo: con ese método, Chamartín ya no sale FALTA en centros de salud. Madrid capital tiene una FALTA fuerte y una fila CUBIERTO, con datos reales:
- Centros de salud **FALTA**: 0,37 por cada 10.000 habitantes frente a 0,56 en los demás municipios urbanos (ratio 0,67, significativa). Fuente: D-213 («Efecto») · `data/fixtures/contracts/zone_gap_list.madrid.fixture.json` (= `GET /api/v1/gaps/municipio/28079`) · `evidence/gate-04/2026-11-11/phase-gap001-f5-review.txt`.
- Farmacias **CUBIERTO**: 5,2 frente a 3,1 (mismo fixture). Mayores, CUBIERTO; escuela infantil, colegio y vivienda, JUSTO.
- A pie, la mitad de las calles de Madrid está a 11,6 min o menos de un centro de salud; la web lo redondea a «12 min» (`min_a_pie_centro_salud`, municipio 28079, `feature_value`). Se ve en pantalla y no se lee.
- **Comprobado en producción el 11 nov:** `GET /api/v1/gaps/municipio/28079` da `gap-0.2` con estas filas (centros de salud: 0,371 frente a 0,5553, ratio 0,6681; captura `evidence/map-004/2026-11-11/prod_c4_madrid_que_falta_desktop.png`). El 25 nov se vuelve a mirar: si Madrid ya no sale FALTA, se elige otra zona con una FALTA de fiabilidad alta y se cambian las cifras de aquí y de la slide 3.
- **Si preguntan por los distritos:** ningún distrito por sí solo basta para afirmar la falta (los 21 salen JUSTO en centros de salud; D-213). Es Madrid entera la que tiene un tercio menos.

<!-- habla:b3:inicio -->
Ahora cambio de usuario: un ayuntamiento. Abro «Qué falta» de Madrid capital. Seis filas: escuela infantil, colegio, centro de salud, mayores, farmacia y vivienda. Cada una se compara con municipios parecidos: Madrid, con los demás municipios urbanos; un pueblo, con los rurales. Aquí, centros de salud: falta. [valor] por cada diez mil habitantes, frente a [referencia] en los demás municipios urbanos. Un tercio menos, y con tanta gente no es casualidad. [Leer una fila cubierta]. Y si no tenemos el dato, o la zona es demasiado pequeña para saberlo, lo decimos: nunca inventamos una falta. Cada fila dice de qué dataset sale. Un concejal ve en un minuto dónde invertir primero.
<!-- habla:b3:fin -->

| # | Acción | Qué tiene que verse | Si falla |
|---|---|---|---|
| 3.1 | Pestaña «Qué falta» y elegir «Madrid (toda la ciudad)» en la lista de zonas | La lista de Madrid capital con sus 6 filas FALTA / JUSTO / CUBIERTO, valor, referencia, fiabilidad, minutos a pie y datasets | Abrir la pestaña preparada con `/que-falta?zona=municipio/28079` |
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
