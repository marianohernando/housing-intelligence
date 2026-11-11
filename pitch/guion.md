# Guion de 5 minutos — Vida Fácil (final del 26 nov)

## Reglas del guion
- **Formato:** 5 min de exposición + 5 de preguntas (bases §9). Demo en directo sobre la web desplegada y slides solo al principio y al final.
- **Ritmo:** unas 130 palabras por minuto. En los bloques con demo se habla menos, porque los clics y las transiciones también ocupan tiempo.
- **Recuento por bloque** (texto entre los marcadores `habla:bN`):
  ```bash
  for b in 1 2 3 4 5; do printf "b$b "; awk -v b=$b '$0 ~ "^<!-- habla:b"b":fin"{f=0} f; $0 ~ "^<!-- habla:b"b":inicio"{f=1}' pitch/guion.md | wc -w; done
  ```
- **Lo que va entre corchetes** (`[N]`, `[zona]`…) se lee en la pantalla en directo. Nunca se dice una cifra de memoria.
- **Textos de los botones:** salen del brief (`~/Desktop/DATAMAD/prompts/DISENO_VIDA_FACIL.md`). Siguen marcados **«pendiente de B»** hasta comprobarlos en la web real.

| Bloque | Tiempo | Duración | Contenido | Palabras | Tiempo hablado a 130 ppm |
|---|---|---|---|---|---|
| 1 | 0:00–0:40 | 40 s | Problema: personas y ayuntamientos deciden a ciegas | 79 | 36 s |
| 2 | 0:40–2:40 | 120 s | Demo: una familia busca dónde vivir → zonas, el porqué y Reality Check | 187 | 86 s + clics |
| 3 | 2:40–3:40 | 60 s | Una zona real y su lista de lo que falta | 111 | 51 s + clics |
| 4 | 3:40–4:30 | 50 s | Datos CM, código abierto y quién paga | 95 | 43 s |
| 5 | 4:30–5:00 | 30 s | Impacto y cierre | 50 | 23 s |
| **Total** | | **300 s** | | **522** | **241 s + unos 35 s de clics = unos 24 s de margen** |

---

> Las decisiones del 11 nov están registradas como D-199 a D-207 (`docs/00_index/01_decisions_log.md`). El brief de diseño (`~/Desktop/DATAMAD/prompts/DISENO_VIDA_FACIL.md`, adoptado por D-201) sigue fuera del repo: se cita como documento interno, no como evidencia pública.

## Antes de empezar (en la sala, 13:30–17:00)
1. Portátil con cargador, wifi del evento probada, HDMI probado y resolución 1920 × 1080 (`docs/09_datamad/25_plan_competicion.md` §9).
2. Navegador en ventana limpia, zoom al 100 %, sin extensiones visibles y con las notificaciones desactivadas.
3. Pestaña 1: las slides en PDF, en la slide 1. Pestaña 2: la portada de la demo, ya cargada una vez para tener la caché caliente. URL: https://vidafacil-madrid.vercel.app (verificada el 11 nov: smoke 6/6, `evidence/gate-06/2026-11-11-deploy/deploy-4-supabase-smoke.md` (rama `claude/s1-deploy`, PR #6)).
4. Plan B abierto en una pestaña oculta: el vídeo de 2 min y el snapshot offline (PITCH-003, **pendiente de C**).

---

## Bloque 1 · 0:00–0:40 · El problema
**Pantalla:** slide 1 (título), y en «Otros servicios…» se pasa a la slide 2.

<!-- habla:b1:inicio -->
Buenas tardes. Imaginad una familia que busca piso en Madrid. El precio lo mira en una web, los colegios en otra y el transporte en otra. Nadie le dice qué zona va con su vida. Un ayuntamiento tiene el problema al revés: quiere saber dónde falta una escuela infantil o un centro de salud, y los datos le llegan sueltos. Otros servicios te enseñan lo que hay. Vida Fácil te enseña lo que falta. Os lo enseño en directo.
<!-- habla:b1:fin -->

**Al terminar:** cambiar a la pestaña de la demo (Cmd + 2).

---

## Bloque 2 · 0:40–2:40 · Una familia busca dónde vivir
**Caso precargado:** `data/fixtures/contracts/scenario_state.familia_castellana.fixture.json`:
- alquiler de hasta 1.500 €/mes;
- 2 adultos y 2 hijos de 4 y 8 años;
- trabajo en el Paseo de la Castellana (Azca), 4 días por semana;
- colegio a 10 min andando como mínimo.

<!-- habla:b2:inicio -->
Esta es Vida Fácil. Abro el caso de ejemplo: una pareja con dos hijos de cuatro y ocho años. Trabajan en la Castellana, pueden pagar hasta mil quinientos euros de alquiler y quieren un colegio a diez minutos andando. No rellenan un formulario: marcan su hogar, lo que les importa y dónde trabajan. Pulso «Ver zonas que encajan». El mapa se colorea: cuanto más violeta, mejor encaja la zona con esta familia. A la derecha, la zona que más encaja. No le damos una nota sobre cien. Le damos un porcentaje de encaje y, debajo, hechos que cualquiera entiende: [leer dos hechos de la tarjeta]. Y cada hecho dice cuánto nos fiamos del dato. ¿Y si lo que buscan no existe? Esto es el Reality Check. Con su búsqueda tal cual salen [N] zonas. Si suben [X] euros, salen [N]. Si aceptan [otra condición], [N]. No le decimos a nadie «gastad más»: le enseñamos sus alternativas y lo que cuesta cada una. Y cada dato tiene su origen: pulso aquí y me lleva a la ficha del portal de datos abiertos de la Comunidad de donde sale.
<!-- habla:b2:fin -->

| # | Acción | Qué tiene que verse | Si falla |
|---|---|---|---|
| 2.1 | Clic en «Pareja con 2 hijos que trabaja en la Castellana» (portada; **pendiente de B**) | Tarjeta «Tu búsqueda» rellena: «Con hijos (2)», «Colegios», «Trabajo en: Castellana», alquiler hasta 1.500 €/mes | Rellenar a mano los chips: es más lento, así que acortar la frase del formulario |
| 2.2 | Clic en «Ver zonas que encajan» (**pendiente de B**) | Coropleta violeta y tarjeta de zona con el % de encaje y 3–5 hechos con su confianza | Si tarda más de 3 s, seguir hablando del mapa; si no llega, pasar al vídeo (plan B) |
| 2.3 | Señalar la tarjeta de zona y leer dos hechos | Hechos tipo «Colegio público a [N] min andando» y «Metro a [N] min» (**pendiente de A**: CORE-003; los minutos a pie ya existen, CORE-005, y falta recalcularlos a 4 km/h) | Leer solo el % de encaje y la confianza |
| 2.4 | Señalar el bloque Reality Check (**pendiente de A y B**) | «Con tu búsqueda: [N] zonas · +[X] €/mes: [N] · …» con cifras de la API | Ver la nota sobre el Reality Check, debajo |
| 2.5 | Clic en una opción del Reality Check | El mapa se recalcula con la condición relajada | Solo señalarla, sin pulsar |
| 2.6 | Clic en la fuente de un hecho o en «Cómo lo calculamos» (**pendiente de B**) | Nombre del dataset y enlace a la ficha del portal CM | Enseñar el pie «Datos: N conjuntos de la Comunidad de Madrid…» |

**Nota sobre el Reality Check (**pendiente de A y B**):** el bloque solo aparece si salen pocas zonas o ninguna (`~/Desktop/DATAMAD/prompts/DISENO_VIDA_FACIL.md`).
- **Antes del 16 nov hay que comprobar con datos reales** si el caso precargado lo dispara.
- **Si no lo dispara**, el guion añade en el paso 2.4: «Bajo el presupuesto a [Y] €/mes» con el slider. A elige [Y] con la API para que salgan 0–3 zonas.
- **La frase hablada** se ajusta a la acción que se haga.

---

## Bloque 3 · 2:40–3:40 · Qué le falta a una zona real
**Zona:** **pendiente de A** (GAP-001 completo).
- **Criterio:** una zona real con al menos una fila FALTA, una CUBIERTO y, si la hay, una SIN DATOS, para enseñar las tres. Mejor un distrito de Madrid que se conozca.
- **El texto hablado depende de GAP-001 (pendiente de A):** «Seis filas» solo se dice si salen las 6. Si no, se dice «[N] filas» y se nombran solo las que estén.
- **No usar colegios como ejemplo de CUBIERTO** hasta que GAP-001 corrija el filtro: hoy cuenta también escuelas infantiles e institutos (`proxy_note` de `colegios_publicos_por_1000_menores`).
- **Zona propuesta: Chamartín** (distrito de Madrid), con datos reales de la demo pública. Centros de salud FALTA (0,47 por cada 10.000 habitantes frente a 0,59 en la región) y colegios FALTA (0,88 por cada 1.000 menores frente a 2,18). Confianza 1,0 y 3 datasets por fila. Fuente: `GET /api/v1/gaps/distrito/2807905` (comprobado en la demo pública el 11 nov) · `evidence/gate-06/2026-11-11-deploy/deploy-4-supabase-smoke.md` (rama `claude/s1-deploy`, PR #6), «Manual check: Chamartín». Cortes provisionales `gap-0.1`.
- **Dato a pie de la fila de centros de salud:** la mitad de las calles de Chamartín está a 8,4 min o menos de un centro de salud (`min_a_pie_centro_salud`, distrito 2807905, CORE-005 `fc025b6`, a 4,5 km/h). **Pendiente de recálculo** a 4 km/h (A): unos 9,5 min. Los minutos se ven en pantalla y no se leen. La frase «Están cerca…» solo se dice si la pestaña enseña el dato a pie (`falta.fila.a_pie`, **pendiente de A**: API con GAP-001); si no, se salta.
- **Hoy no tiene ninguna fila CUBIERTO:** «[Leer una fila cubierta]» solo se dice si GAP-001 trae una (**pendiente de A**); si no, se salta. La fila que se lee en voz alta es la de centros de salud.

<!-- habla:b3:inicio -->
Ahora cambio de usuario: un ayuntamiento. Pulso «Ver la zona». La cámara entra en [zona] en tres dimensiones, con sus colegios, centros de salud y estaciones. Abro la pestaña «Qué falta». Seis filas: escuela infantil, colegio, centro de salud, mayores, farmacia y vivienda. Aquí, centros de salud: falta. [valor] por cada diez mil habitantes, frente a [referencia] en la región. [Si se ve el dato a pie:] Están cerca, pero son pocos para tanta gente. [Leer una fila cubierta]. Y cuando no tenemos el dato, lo decimos: sin datos. No inventamos nada. Cada fila dice de qué dataset sale, con su enlace. Un concejal ve en un minuto dónde invertir primero.
<!-- habla:b3:fin -->

| # | Acción | Qué tiene que verse | Si falla |
|---|---|---|---|
| 3.1 | Clic en «Ver la zona» (**pendiente de B**) | Vuelo de cámara a unos 60° y zona en 3D con contorno violeta y etiquetas de cristal | Sin 3D: seguir en 2D y quitar «en tres dimensiones» de la frase |
| 3.2 | Clic en la pestaña «Qué falta» (**pendiente de B**) | 6 filas FALTA / JUSTO / CUBIERTO / SIN DATOS con valor, referencia, confianza y datasets | Si faltan filas, leer solo las que estén y no nombrar las demás |
| 3.3 | Señalar una fila FALTA y una CUBIERTO; leer el valor y la referencia | Texto tipo «0,47 centros de atención primaria por cada 10.000 habitantes; en el conjunto de la Comunidad de Madrid, 0,59» | — |
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

**Fuente:** «toda la Comunidad» = los 179 municipios de `evidence/gate-01/2026-10-20/cm_secciones_censales/row_counts.json`. **Pendiente de A:** confirmar antes del 26 que el buscador cubre los 179 municipios en la demo. La lista ya responde en municipios y distritos (smoke de C, PR #6). Si no, se dice «con datos reales y oficiales de la Comunidad de Madrid», sin «toda».

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
