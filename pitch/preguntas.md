# Banco de preguntas del jurado — Vida Fácil

**Cómo usarlo:**
- 5 minutos de preguntas (bases §9).
- Cada respuesta tiene 3 frases como máximo: primero la respuesta, después el dato y por último el límite, si lo hay.
- La evidencia es para Mariano; no se lee en voz alta.
- Si algo no se sabe: «No lo sé con certeza; lo compruebo y os lo envío». Nunca se inventa una cifra.

**Perfiles:** salen de `docs/09_datamad/25_plan_competicion.md` §4. Lo que valora cada miembro del jurado es una inferencia a partir de su trayectoria pública.

> Las decisiones del 11 y el 12 nov están registradas como D-199 a D-224 (`docs/00_index/01_decisions_log.md`). El brief de diseño (`DISENO_VIDA_FACIL.md`, adoptado por D-201) sigue fuera del repo: se cita como documento interno, no como evidencia pública.

**Marcas:** «pendiente de A/B/C» = todavía no existe. Se revisa el 23 nov (freeze) y el 25 nov (ensayos).

**Las más probables** están al final y hay que prepararlas primero: de la 41 a la 45 (jurado simulado del 12 nov) y la 46 y la 47 (cifras de impacto, 12 nov).

---

## Alberto Abella · Gaia-X España (APIs, interoperabilidad, espacios de datos)

**1. ¿Cómo se integra esto con otros sistemas?**
Con una API pública versionada (`/api/v1`) cuyos contratos están publicados como JSON Schema. Las zonas se identifican con el código INE del municipio, así que se cruzan con cualquier otra fuente oficial.
- Evidencia: `docs/04_technical_architecture/31_public_api_routes.md` · `data/schemas/api/*.schema.json` (4 esquemas) · `GET /api/v1/gaps/municipio/28092`.

**2. ¿Tenéis MCP para agentes de IA?**
Sí: un servidor MCP con cinco herramientas de solo lectura (buscar zonas, qué falta, explicar una zona, encontrar una zona por su nombre y las fuentes de datos). Llaman a los mismos servicios que la API, nunca a SQL libre, así que un agente no puede inventar ni cambiar datos, y los tests comprueban que cada herramienta responde lo mismo que su ruta de la API. Hoy funciona en local (`make mcp`); el siguiente paso es servirlo en remoto.
- Evidencia: D-225 · `services/mcp/` · `make mcp` · `CLAUDE.md` §3 (Arquitectura).
- Si quieren verlo: un clip de 20 s con un agente preguntando «¿qué le falta a Parla?» (**pendiente de A**).

**3. ¿Vuestro catálogo de datos es reutilizable?**
Sí. Cada fuente, dataset, métrica y feature está descrito en YAML legible por máquina, con licencia, propietario y enlace, y ese catálogo se publica en CC BY 4.0. De ahí sale, por ejemplo, la lista de datasets que habéis visto, generada con un script.
- Evidencia: `data/catalog/` · D-191 · `pitch/build_datasets_cm.py`.

**4. ¿Podría ser un producto de datos en un espacio de datos?**
Encaja, porque cada resultado sale ya con su fuente, versión, licencia y nivel de confianza. Exportarlo en DCAT-AP o con un conector de espacio de datos todavía no está hecho: sería el siguiente paso.
- Evidencia: el campo `datasets` con `version` y `license` de cada fila (`data/fixtures/contracts/zone_gap_list.mostoles.fixture.json`).

**5. ¿Y si cambia un dataset del portal?**
Cada ingesta compara la huella (sha256) del fichero. Si no cambia, se salta; si cambia, crea una versión nueva. Si la nueva versión falla los controles, se sigue sirviendo la última válida.
- Evidencia: `evidence/gate-01/2026-11-10/idempotent-rerun.txt` · `last-valid-versions.txt` · `lineage.json` de cada dataset.

---

## Olga Quirós · ASEDIE (sector infomediario, negocio)

**6. ¿Quién paga?**
Las empresas que necesitan saber qué falta en una zona (promotoras, cadenas, residencias, comercios) pagan por análisis agregados y por la API. Las personas lo usan gratis y los ayuntamientos lo usan para planificar.
- Evidencia: `docs/09_datamad/25_plan_competicion.md` §1 · `CLAUDE.md` §16 (cliente inicial: promotoras e inmobiliarias medianas).
- Si piden concretar (decisión de Mariano, 12 nov; `pitch/modelo_negocio.md`):
  - un ayuntamiento paga 990–1.500 € por el informe de lo que falta en su municipio, que cabe en un contrato menor;
  - las promotoras y consultoras pagan estudios de zona de 490 a 1.500 €, y son los primeros ingresos;
  - para las personas es gratis, y la API y el MCP también, sin uso comercial.

**7. Si los datos son abiertos, ¿por qué pagaría alguien?**
Por el trabajo que hay encima: cruzar 27 conjuntos con formatos distintos, controlar su calidad, comparar cada zona con otras parecidas y explicarlo con su fuente. Hacer eso a mano para cada estudio cuesta semanas; aquí está hecho, se recarga con un comando y detecta qué fuente ha cambiado.
- Evidencia: `pitch/datasets_cm.md` · `evidence/gate-01/2026-11-10/summary.md` · `evidence/gate-01/2026-11-10/idempotent-rerun.txt`.

**8. ¿La licencia de los datos permite un uso comercial?**
Sí. Los datos del portal CM son CC BY y la licencia del CRTM permite reutilizarlos citando la fuente. En ambos casos cumplimos la atribución y no vendemos el dato en bruto, sino el análisis.
- Evidencia: licencias por dataset en `pitch/datasets_cm.md` · `data/catalog/sources/comunidad_madrid_ckan.yaml` y `crtm_open_data.yaml` (`commercial_use: true`, `attribution_text`).

**9. ¿En qué os diferenciáis de los portales inmobiliarios o de las consultoras?**
Los portales enseñan la oferta de pisos; nosotros enseñamos la necesidad y el encaje de cada zona. Frente a un estudio de consultora, aquí todo es abierto, reproducible y cita cada dato.
- Evidencia: `docs/09_datamad/25_plan_competicion.md` §8.

**10. ¿Cuánto cuesta mantenerlo?**
Hoy, 0 € al mes: la web y la API van en el plan gratuito de Vercel y la base en el de Supabase, y los datos se recargan copiando tablas ya validadas. Para un uso comercial habría que pasar a planes de pago, porque el gratuito de Vercel no lo admite.
- Evidencia: `evidence/gate-06/2026-11-11/supabase-sync-demo.txt` (base de la demo: 100 MB de los 500 del plan gratuito) · D-188.
- Alojamiento: `infra/deploy/README.md` y `evidence/gate-06/2026-11-11-deploy/deploy-1-production.md` (plan Hobby: «solo personal y no comercial»).
- Si preguntan cuánto para cobrar: unos 45 $/mes como mínimo, con Vercel Pro (20 $) y Supabase Pro (desde 25 $). La base ocupa 100 MB de los 8 GB incluidos, así que lo que crece con el uso es el cómputo de la API (`pitch/modelo_negocio.md`, precios del 12 nov).

---

## Loren Escot · UCM, Estudios Estadísticos (rigor de los indicadores)

**11. ¿Cómo decidís que algo «falta»?**
Medimos lo que la gente de la zona tiene a 15 minutos andando, repartido entre todos los que lo comparten, y lo comparamos con los demás municipios de su tipo, rurales o urbanos. FALTA exige dos cosas: menos del 80 % de esa referencia (la regla de los cuatro quintos) y que la diferencia no se explique por el azar del tamaño de la zona; CUBIERTO es llegar al 100 %, y lo demás es JUSTO. Es una señal para priorizar, no un veredicto, y el método está declarado y versionado (`gap-0.3`).
- Evidencia: D-213 (puntos 1 y 2: 29 CFR 1607.4(D); intervalo exacto de Poisson de Garwood al 95 %, como en Fingertips y en los gráficos en embudo de Spiegelhalter, 2005) · D-217 (2SFCA: mismos cortes y misma prueba) · `packages/domain/src/hi_domain/gaps.py` · `apps/api/src/hi_api/services/gap_reference.py` · `evidence/gate-04/2026-11-12/gap-status-gap03.md`.
- Estado: hecho en la API y en producción (GAP-001 F5; DATA-AUDIT T2, `b88c4fb`). `GET /api/v1/gaps/distrito/2807913` da `gap-0.3` (comprobado el 12 nov).

**12. ¿Qué es eso de «al alcance a pie»? ¿Por qué no contáis centros sin más?**
Porque contar centros por habitante trata igual una clínica pequeña que un centro grande y no ve lo que hay al otro lado del límite de un distrito. Usamos el método 2SFCA (Luo y Wang, 2003): lo que ofrece cada centro se reparte entre todos los que viven a 15 minutos andando de él, cada calle suma lo que le toca de cada centro, y la zona es la media de sus calles según cuánta gente vive en cada una. Los 15 minutos a 4 km/h son los del estudio «El Madrid de los 15 minutos» del Ayuntamiento, y con 10 o 20 minutos el orden de los municipios casi no cambia (Spearman de 0,995 a 0,997).
- Evidencia: D-217 §1–2 · `packages/domain/src/hi_domain/access/fca.py` · `services/features/src/hi_features/fca.py` (`two_step_fca`) · test de propiedades de capacidad conservada · `evidence/gate-03/2026-11-12/fca-sensitivity.md`.
- Límite, si insiste: la captación es binaria, dentro o fuera, sin decaimiento con la distancia (E2SFCA, Luo y Qi 2009, es la mejora declarada), y la gente se coloca en las calles según su longitud, no por portal (D-217 §9).
- Estado: hecho y en producción desde el 12 nov (`gap-0.3`).

**13. ¿Por qué comparáis con municipios del mismo tipo y no con toda la región?**
Porque la oferta depende del tipo de territorio: a pie y por niño, los municipios rurales tienen más del doble de escuelas infantiles que los urbanos (unas 12 por cada 1.000 niños, frente a menos de 5). Con la media de la región a cualquier ciudad le faltaría de todo, y con el método anterior la diferencia entre rural y urbano ya era significativa en las 6 filas (χ², p < 0,05). Usamos la definición legal de medio rural de la Ley 45/2007 (menos de 30.000 habitantes y menos de 100 por km²), y ninguna zona se compara consigo misma: Madrid es la mitad de la población urbana.
- Evidencia: referencias de `gap-0.3` en `GET /api/v1/gaps?level=municipio&row=escuela_infantil`. Cada zona deja fuera su municipio, así que la rural va de 12,13 a 12,86 y la urbana de 4,531 a 4,87 (`evidence/map-004/2026-11-12/cifras/cifras_api.json`, PR #18): «más del doble» vale para todas · D-213 (punto 1 y tabla χ²: de p = 0,039 en farmacias a p < 10⁻³⁰⁰ en vivienda; 84 municipios rurales y 95 urbanos) · `evidence/gate-04/2026-11-11/phase-gap001-f5-review.txt`.
- Límite, si insiste: el tipo se asigna por municipio, la superficie es la de la geometría de 2019 y el modelo de Poisson no trata la sobredispersión (D-213, punto 5).
- Estado: hecho (GAP-001 F5; D-217 mantiene la referencia).

**14. ¿Qué pasa con los municipios pequeños, donde una ratio se dispara?**
Si en un municipio se esperan menos de 3,69 casos, el límite superior al 95 % de un recuento de cero, lo comparamos junto con sus vecinos más cercanos del mismo tipo, a 15 km o menos, hasta que el grupo llega a ese mínimo; la fila lo dice y nombra a los vecinos. Si ni así se llega, sale «zona pequeña para comparar» y nunca FALTA: La Acebeda, con 70 habitantes y sin farmacia a pie, sale JUSTO con esa marca. Con los vecinos, los municipios que no se podían comparar en colegios bajan de 140 a 65, y por debajo de un umbral de población el dato se publica con confianza 0,5.
- Evidencia: D-213 (punto 3, `reliable: false`) · D-217 §6–7 (filtros espaciales adaptativos, Talbot et al., 2000; radio de 15 km, del orden de las zonas básicas de salud rurales) · `comparison_group` en la API · `small_population_threshold` en los YAML de las filas · `null_policy`.
- Estado: hecho en la API y en producción (12 nov): La Acebeda, farmacia, JUSTO con `reliable: false` y sin grupo; Redueña, farmacia, CUBIERTO junto con 6 vecinos (ratio del grupo 1,51) (`GET /api/v1/gaps?level=municipio&row=farmacia`). En la web: «Junto con sus vecinos» y «Comparado con municipios parecidos de la zona» (PR #13 de B).

**15. Puente de Vallecas y Centro tienen cifras parecidas en escuelas infantiles. ¿Por qué uno sale FALTA y el otro no?**
Porque FALTA pide además que la diferencia no pueda ser casualidad. Puente de Vallecas tiene 0,57 de la referencia y tantos niños que la diferencia es clara; Centro tiene 0,66, pero con menos niños podría ser azar, así que sale JUSTO. Preferimos no marcar una falta que no podemos sostener.
- Evidencia: `GET /api/v1/gaps?level=distrito&row=escuela_infantil` (producción, 12 nov: Puente de Vallecas 2,781 frente a 4,87, FALTA; Centro 3,218, ratio 0,6608, JUSTO; los dos con `reliable: true`) · D-213 punto 2.
- Si preguntan por otros: Villaverde (0,61) y Carabanchel (0,68) también salen FALTA; Vicálvaro (0,65), JUSTO.

**16. ¿Contáis centros o plazas?**
La capacidad que se publica: aulas de primaria en colegios y plazas autorizadas en hogares, clubes y centros de día de mayores. Las aulas se publican por municipio, no por colegio, así que las repartimos a partes iguales y el dato baja a «aproximado»; de escuelas infantiles, centros de salud y farmacias nadie publica plazas ni médicos, y cada uno cuenta como uno. Cada fila lo declara, y nunca estimamos una capacidad centro a centro.
- Evidencia: D-217 §3–4 (tabla de capacidad; población asignada por centro de salud y cupos médicos no existen en abierto) · `proxy_note` en `data/catalog/features/*.yaml` y en cada fila de la API · `confidence: 0.8` en `aulas_primaria_a_pie_por_1000_ninos.yaml`.

**17. Madrid capital tiene 3 millones de habitantes. ¿No esconde la media todo?**
Sí, por eso Madrid se divide en sus 21 distritos, y lo que se tiene a pie se calcula calle a calle, mucho más fino que el municipio. Así sale, por ejemplo, que en Puente de Vallecas faltan escuelas infantiles aunque Madrid entera no sale FALTA en ninguna fila de servicios. Y lo que hay al otro lado del límite de un distrito también cuenta, porque se mide andando.
- Evidencia: D-200 · D-209 · D-210 · D-217 §2 y §7 · `evidence/gate-04/2026-11-12/gap-status-gap03.md` (Madrid, escuela infantil, JUSTO, 0,87) · `GET /api/v1/gaps/distrito/2807913` (producción, 12 nov).
- Si preguntan por la frase de antes («Madrid tiene un tercio menos de centros de atención primaria»): era con el método de contar centros por habitante. Midiendo lo que se alcanza a pie, Madrid sale JUSTO en centros de salud (0,95), cerca de los demás municipios urbanos (D-217 §7).
- Estado: hecho. Distritos con el padrón municipal (D-209); distancia a pie a 4 km/h (CORE-005, D-211); 2SFCA en la API y en la web desde el 12 nov.

**18. ¿Cómo calculáis el % de encaje?**
Primero, las condiciones: cada una sale PASS, FAIL o «sin dato», y «sin dato» nunca cuenta como PASS; solo encajan las zonas que lo cumplen todo. Después, cada criterio puntúa de 0 a 1 con una curva declarada (un colegio vale 1 hasta 10 min y 0 desde 30), y lo que la persona marca primero pesa más: con 5 criterios, 33, 27, 20, 13 y 7 %. El % es la media ponderada; lo que no tiene datos no cuenta como 0, sino que baja la confianza, y el método va versionado (`fit-0.3` en producción).
- Evidencia: D-215 (puntos 2 a 6) · `packages/domain/src/hi_domain/fit.py` · `CLAUDE.md` §14 · caso real: `evidence/gate-04/2026-11-11/phase-core003-f2.txt` (Ciudad Lineal, 99 %).
- Límite, si insiste: no hay todavía diversificación ni soluciones Pareto; el orden es solo por % de encaje (D-215, punto 10).
- Estado: hecho en la API (CORE-003) y en producción desde el 11 nov (buscador de B, PR #10, encendido por C en el PR #11). Con `fit-0.6` (12 nov: trabajo en minutos de transporte, D-220, y alquiler de contratos nuevos, D-228), `POST /api/v1/search` con el caso de la Castellana da 27 de 199 zonas, con Latina, Moratalaz, Ciudad Lineal y Puente de Vallecas empatadas al 98 %.

**19. El alquiler solo está publicado para municipios grandes. ¿Qué hacéis en el resto?**
Así es: la Comunidad publica el alquiler de 37 municipios, los de más de 20.000 habitantes con contratos suficientes, y el de los códigos postales de Madrid capital. En el resto, la condición de presupuesto sale «sin dato», se dice y nunca se da por buena. En los distritos de Madrid hacemos la media de sus códigos postales, ponderada por dónde están los colegios, centros de salud y centros sociales, y lo declaramos como aproximación: sale 14,5 €/m², y la Comunidad publica 15,1 para todo Madrid.
- Evidencia: D-214 (puntos 3 y 4) · `data/catalog/features/alquiler_m2_mensual.yaml` v2 · `evidence/gate-04/2026-11-11/phase-core006-f1.txt` (14,46 frente a 15,10) · `CLAUDE.md` §14 (UNKNOWN nunca equivale a PASS).

**20. Vuestro alquiler estimado parece bajo. ¿Es real?**
Es una estimación y lo decimos en cada resultado: el precio por metro de la Comunidad, corregido con lo que cuestan de más los contratos firmados en 2024 según la Agencia Tributaria, por los metros del hogar. Sigue sin ser el precio de un anuncio, y los m² son construidos, del Catastro, así que el piso real es algo menor que el que suponemos (77 m² para 4 personas, la vivienda mediana de ese hogar en el Censo 2021). Por eso la tarjeta dice «un anuncio de hoy puede pedir más».
- Evidencia: D-214 (puntos 2 y 3) · D-228 (contratos nuevos) · pregunta 41 · ficha del portal CM (https://datos.comunidad.madrid/dataset/1934259, campo «Fuente»: «Estadística de Viviendas Declaradas en el Impuesto sobre la Renta de las Personas Físicas. Agencia Estatal de Administración Tributaria») · INE, tabla 59524 (https://www.ine.es/jaxi/Tabla.htm?tpx=59524&L=0) · `limitations` de `alquiler_m2_mensual.yaml`.
- Si preguntan por qué no usamos anuncios: no hay una fuente oficial y abierta de precios de oferta, y no hacemos scraping (pregunta 35).

**21. ¿Tenéis en cuenta lo que se tarda en llegar al trabajo?**
Sí: los minutos de puerta a puerta en transporte público para llegar a las 9:00, con los horarios publicados de las seis redes del Consorcio, desde cada sección censal hasta las 379 estaciones y el centro de cada zona. En el caso de ejemplo, Fuencarral-El Pardo queda a 29 minutos de la Castellana y Ciudad Lineal a 33. Son horarios programados de un día laborable, no tiempos reales, y donde el horario publicado tiene huecos lo decimos.
- Evidencia: D-220 · `packages/domain/src/hi_domain/access/transit.py` · `services/features/src/hi_features/commute.py` · `evidence/gate-03/2026-11-12/commute-matrix.md` · `evidence/gate-04/2026-11-12/golden-search-commute.txt`.
- Límite, si insiste: el GTFS interurbano no trae expediciones de las líneas 720 a 726, y desde 45–50 zonas (Sierra Norte, sureste) no se llega al centro a las 9:00; ahí no hay dato, nunca 0. El paseo hasta la parada va en línea recta con un 30 % de rodeo (D-220 §3 y §6).
- Estado: hecho y en producción desde el 12 nov (despliegue de `28a0f2f`, `evidence/gate-06/2026-11-12-deploy/deploy-17-pub001.md`): el caso de ejemplo da «29 min en transporte público hasta Paseo de la Castellana (Azca), llegando a las 9:00» en Fuencarral-El Pardo.

**22. ¿Cómo medís «a 10 minutos andando»? ¿A qué velocidad?**
Por las calles de verdad, no en línea recta, a 4 km/h: el mismo paso que el estudio «El Madrid de los 15 minutos» del Ayuntamiento. En cada fila damos los minutos en los que llega la mitad de las calles de la zona; si una zona no tiene calles en el mapa, sale «sin datos», nunca cero. Lo comprobamos con 15 casos de lugares conocidos: por ejemplo, La Acebeda no tiene farmacia y la más cercana queda a más de hora y media andando.
- Evidencia: D-210 · D-211 · `data/catalog/features/min_a_pie_*.yaml` y `pct_calle_*.yaml` · `scripts/check_walk_golden.py` y `evidence/gate-03/2026-11-11/phase-core005-f5.txt` (La Acebeda: farmacia a 109,7 min, D-211) · estudio del Ayuntamiento: https://geoportal.madrid.es/fsdescargas/IDEAM_WBGEOPORTAL/GEOPORTAL/Jornada/2022/SALA5_1130_PROXIMIDAD_POR_CALCULODEREDES.pdf («Velocidad de desplazamiento estimada en 4 Km/h»).
- Estado: hecho a 4 km/h, decisión de Mariano del 11 nov (CORE-005 Fase 5, `ad2129a`, D-211, Gate 3 PASS). En la API, con GAP-001 F1 (`2d05d78`), y en producción. Por ejemplo, Puente de Vallecas: la escuela infantil más cercana, a 6 min desde la mitad de sus calles (`min_a_pie_escuela_infantil` = 6,258, `GET /api/v1/gaps/distrito/2807913`, 12 nov). El % de calle a 10 minutos también está calculado (`pct_calle_*.yaml`), pero no se enseña.

---

## Ricardo Curto · Universidad de Oviedo (calidad, licencias y cita de fuentes)

**23. ¿Qué datasets del portal usáis exactamente y con qué licencia?**
27 datasets con ficha en el Portal de Datos Abiertos de la Comunidad de Madrid, cada uno con su enlace, licencia, qué alimenta y su informe de calidad. La lista se genera desde el catálogo, no se escribe a mano.
- Evidencia: `pitch/datasets_cm.md` · `pitch/build_datasets_cm.py` · `GET /api/v1/datasets?cm_only=true` (27 en producción desde la noche del 12 nov; el formulario se envió ese mismo día con 26).
- Si insiste en cuáles se ven: 25 alimentan la lista o el buscador (el 27.º, el valor tasado de la vivienda, da el precio de compra en 28 municipios, D-227); los 2 de camas (12 nov) dan el total de la región: ya los sirve la API (85 hospitales y 3,0 camas por 1.000 habitantes, sincronizado y verificado por A); B los enseña en la nota del hospital en su próximo PR (**pendiente de B**). Si no llega al freeze del 23 nov, se cuentan 25 y no 27 (decisión de datamad-10). De esos 25, los 3 de accesibilidad de las estaciones (12 nov, D-223) se usan con «sin escaleras», en producción desde el 12 nov.

**24. Los GTFS son del Consorcio. ¿Por qué los contáis como datos de la Comunidad?**
Porque el propio portal de la Comunidad los publica con su ficha y su licencia. Aun así, los separamos en la lista y damos también la descarga original del CRTM, para que se vea claro.
- Evidencia: D-196 · `pitch/datasets_cm.md` §2 (6 fichas con licencia «CRTM Licencia de datos abiertos (LDA)» en el portal CM).

**25. ¿Por qué usáis datos del Ministerio de Sanidad si el concurso es de datos de la Comunidad?**
Porque el portal de la Comunidad solo publica las camas de toda la región (85 hospitales y 20.776 camas instaladas en 2023), no las de cada hospital. El Catálogo Nacional de Hospitales sí las da y permite reutilizarlas citando la fuente y la fecha; lo usamos solo para poner nombre y camas a los hospitales del registro de la Comunidad, que sigue siendo la fuente de cada lugar, su tipo y su ubicación. Cruzamos 80 de los 85, 79 por su dirección postal y el Ramón y Cajal a mano con la web oficial del hospital, sin ningún desacuerdo entre público y privado.
- Evidencia: D-217 §4 · D-218 §1–4 · `evidence/gate-01/2026-11-12/hospitales-cnh.md` · `pitch/datasets_cm.md` §3 (licencia: aviso legal del Ministerio, Ley 37/2007).
- Límite, si preguntan por un hospital sin nombre: 5 de los 85 no se cruzan y salen como «Hospital general (Municipio)», sin camas. El Ramón y Cajal era uno: el catálogo lo pone en la calle de Ayala y no en la carretera de Colmenar. Lo emparejamos a mano con la web oficial del hospital, y el fichero de correcciones guarda la fuente de cada cambio. Hoy sale con sus 886 camas (D-218 §10; `data/catalog/corrections/places.yaml`; en producción, 12 nov).

**26. ¿Las camas cuentan para decir qué falta?**
No. A un hospital no se va andando a elegir, y medir las camas alcanzables exigiría el viaje en coche o en transporte público, que aún no calculamos. Lo que sí damos es el nombre y las camas de cada hospital, por ejemplo La Paz, con 966 camas instaladas, en Fuencarral-El Pardo, y en la fila de centros de salud los minutos a pie hasta el hospital general más cercano, como pista de dónde quedan las urgencias.
- Evidencia: D-217 §5 (`min_a_pie_hospital`; ninguna fuente abierta marca las urgencias 24 h) · D-218 §6–7 · producción, 12 nov: `GET /api/v1/places?category=health&admin_unit_id=ES.28.DIS.2807908&subcategory=Hospital general` («Hospital Universitario La Paz», `capacity` 966 «camas instaladas», `dependency: publica`; en el mismo distrito, «Hospital Universitario Ramon y Cajal», 886, y «Clínica Cemtro», 100).
- Estado: hecho en la API y en la web («Todos los centros» de cada zona; comprobado a mano por C en producción, PR #15). Las camas son las instaladas a 31 de diciembre de 2024, no las que funcionan un día concreto.

**27. ¿Qué control de calidad pasa un dataset antes de entrar?**
Claves únicas, que cada municipio exista en la geografía oficial, errores de lectura, ratio de registros en cuarentena y faltantes marcados como faltantes, no como cero. Los registros dudosos van a cuarentena, no se borran, y cada versión guarda la huella del fichero original.
- Evidencia: `evidence/gate-01/*/<dataset>/quality_report.json` · `lineage.json` (sha256 y URL) · `row_counts.json` (`quarantined`).

**28. ¿Encontrasteis errores en los datos del portal?**
Sí, y los tratamos sin ocultarlos. Comparamos 10 zonas a mano con la fuente oficial y encontramos centros sin coordenadas o en el municipio equivocado: 40 se han colocado con el geocodificador oficial del IGN, solo si la dirección cuadra, y los que no van a cuarentena, nunca al sitio equivocado. También sacamos del mapa 1.001 «centros polivalentes», casi todos clínicas privadas, que no son atención primaria ni servicios para mayores.
- Evidencia: `pitch/revision_10_zonas.md` (D1–D7) · D-216 §1 y §3 · D-218 §10 · `evidence/gate-01/2026-11-12/audit-places.md` · `evidence/gate-01/2026-11-12/correcciones.md` · `evidence/gate-01/2026-11-12/cm_centros_educativos/row_counts.json` (40 en cuarentena) · `notes` de `data/catalog/datasets/cm_secciones_censales.yaml` (geometría inválida reparada).
- Límite: los 4 centros de salud «S/N» de Madrid y Alcalá ya están colocados con el número de portal del catálogo del Ministerio (D-218 §10). Quedan sin poder colocar 3, porque ninguna fuente oficial da su ubicación: el consultorio de Villar del Olmo, el de Buitrago y el colegio de Navalafuente. Hoy cuentan como si no estuvieran, y A propone enseñar SIN DATOS.

**29. ¿Los datos están al día?**
Cada fuente se recarga según su propia frecuencia de publicación, y en los GTFS el control de calidad avisa si el horario está caducado. Por ejemplo, el GTFS de metro venció el 27 de mayo de 2026 y sigue siendo el último publicado: lo usamos y el control de calidad lo marca.
- Evidencia: control `feed_current` en `evidence/gate-01/2026-11-10/crtm_gtfs_metro/quality_report.json` · D-196.

**30. ¿Cómo citáis las fuentes en la propia aplicación?**
Cada fila de la lista y cada resultado llevan los datasets de los que salen, con el enlace a su ficha, la versión y la licencia. Además, la web muestra la atribución que pide cada licencia, incluido «Powered by CRTM».
- Evidencia: campo `datasets` de la API (`data/fixtures/contracts/zone_gap_list.mostoles.fixture.json`) · `attribution_text` en `data/catalog/sources/*.yaml`.
- Estado: hecho en producción: pie con Comunidad de Madrid, Ayuntamiento, «Powered by CRTM» y OpenStreetMap (`evidence/map-004/2026-11-11/prod_c4_madrid_que_falta_desktop.png`).

---

## Generales (cualquier miembro)

**31. ¿Qué hicisteis durante la competición y qué ya existía?**
El trabajo previo está identificado con el tag `pre-datamad` (22 oct): la geografía, los 10 primeros datasets y el mapa base. Desde el 7 nov hemos añadido el transporte del CRTM, 7 datasets más de la Comunidad, la lista de lo que falta con sus 6 filas, la red peatonal, la capacidad a pie, la web, el buscador y el despliegue.
- Evidencia: `README.md` («Trabajo previo a DATAMAD») · tag `pre-datamad` = `cf39459` · D-174 · `board/BOARD.md` (07 — DONE).
- Estado: hecho. La lista, la web y el buscador están en producción; el buscador, desde el 11 nov (`evidence/gate-06/2026-11-11-deploy/deploy-12-buscador.md`, PR #11).

**32. ¿Habéis usado IA?**
Sí, como asistente de programación, que las bases permiten (§7), y nosotros respondemos de todo el código y los resultados. El producto no usa IA para calcular nada: todas las cifras salen de reglas deterministas, versionadas y con tests.
- Evidencia: `docs/09_datamad/24_bases_oficiales_2026.md` §7 · `CLAUDE.md` §3 (IA).

**33. ¿Qué pasa con la privacidad?**
Nunca tratamos datos de personas: solo agregados por zona. Además, no mostramos equipamientos que expondrían a personas vulnerables, quitamos teléfonos, emails y NIF que publicaba la fuente, y la base de la demo no se puede leer desde fuera de la API.
- Evidencia: D-186 · D-198 · D-197 · control `no_contact_or_tax_ids` en los `quality_report.json` de puntos.

**34. ¿De dónde sale «lo que falta» si no tenéis usuarios?**
Hoy, de datos oficiales: población, hogares y equipamientos, comparados con los demás municipios del mismo tipo. El siguiente paso es sumar lo que la gente declare que necesita, anónimo y agregado por zona, y no lo simulamos en la demo.
- Evidencia: D-194 · `docs/09_datamad/25_plan_competicion.md` §8.

**35. ¿Por qué no usáis datos de los portales inmobiliarios?**
Porque no hacemos scraping: sus condiciones no lo permiten y las bases exigen respetar licencias. Además, enseñan la oferta, y lo que nosotros medimos es la necesidad.
- Evidencia: `CLAUDE.md` §15 · D-175 y D-185 (Google Maps y Gosom descartados) · bases §6.

**36. ¿Incluís seguridad? Es delicado.**
No la puntuamos, y es una decisión. El dato oficial que evaluamos, los hechos conocidos de infracciones penales por cada 1.000 habitantes, cuenta dónde se denuncia o dónde actúa la policía, no dónde se vive: en 2024, Humanes de Madrid daba 116,2 y Madrid 58,6, frente a 47,9 de referencia, y ordenar zonas así señalaría municipios por la actividad que reciben. Además, solo cubre 36 de las 199 zonas y ninguno de los distritos de Madrid.
- Evidencia: D-224 · D-226 · `evidence/gate-01/2026-11-12/seguridad-evaluacion.md` y `seguridad-fuentes.md` · D-204 y D-205 (nunca nacionalidad ni etiquetas como «peligroso»).
- Si insiste: en los 21 distritos de Madrid sí damos contexto, que no puntúa ni ordena. Es cómo valoran los vecinos la seguridad de su barrio, de 0 a 10, según la Encuesta de calidad de vida de 2025 del Ayuntamiento, con unas 400 personas por distrito; la media de Madrid es 6,4 de noche y 7,8 de día (D-226 §1). Las actuaciones de la Policía Municipal miden la actividad policial, no el riesgo de vivir allí. Los atropellos, sin saber cuánta gente camina por cada calle, señalan los barrios con más vida. Ninguno de los dos puntúa (D-226 §2–3). Enseñar la tasa de criminalidad como contexto en esos 36 municipios sigue abierto (D-224 §3).
- Estado: decidido (D-224 y D-226). La prioridad «Seguridad» no puntúa. La percepción vecinal está en la API; en la web, **pendiente de B**.

**37. ¿Sirve para alguien que no puede subir escaleras?**
Sí, si lo marca: «Sin escaleras» puntúa los minutos andando hasta la estación de metro, Metro Ligero o Cercanías que el Consorcio da como totalmente accesible, y nunca se deduce ni se etiqueta a nadie. Es una aproximación declarada: no mide autobuses, aceras, portales ni ascensores, y la tarjeta lo dice cuando no hay ninguna estación así a un paseo. En Madrid capital va de 6,8 minutos en Chamberí a 25,5 en Usera.
- Evidencia: D-223 · `evidence/gate-01/2026-11-12/estaciones-accesibles.md` · las 3 topologías del CRTM en el portal CM (`pitch/datasets_cm.md`, 24 a 26) · `evidence/gate-04/2026-11-12/golden-search-sin-escaleras.txt`.
- Si insiste en el grado: el CRTM no publica qué significa cada grado. Leemos T como accesibilidad total porque las 57 estaciones de Metro Ligero son T y la Comunidad dice que toda esa red es accesible; P y N no cuentan (D-223 §3). El `wheelchair_boarding` del GTFS no se usa porque no sigue el estándar (D-223 §4).
- Estado: hecho y en producción desde el 12 nov (`fit-0.4`, despliegue de `2761696`: `evidence/gate-06/2026-11-12-deploy/deploy-18-pub002.md`).

**38. ¿Funciona fuera de la Comunidad de Madrid?**
La arquitectura sí: añadir un dataset es añadir un YAML de pipeline, y la geografía se basa en códigos INE. Lo que haría falta en otra región es su portal de datos con equivalentes.
- Evidencia: `data/catalog/pipelines/` · `README.md` (Quickstart).

**39. ¿Es accesible para personas mayores?**
Está pensada para ellas: español llano, texto base de 17 px, botones de 44 px y contraste AA verificado también sobre el cristal. El estado de cada fila nunca depende solo del color: siempre va con texto e icono.
- Evidencia: `DISENO_VIDA_FACIL.md` · `apps/web/src/lib/__tests__/tokens.test.ts` · axe WCAG 2.2 AA en producción sin fallos (`prod-buscador-check.json`, PR #11).
- Estado: hecho. axe AA da 0 fallos en producción (11 nov): en escritorio, en la portada, los resultados, la tarjeta de zona y la compra; en el móvil, en los resultados y la tarjeta.

**40. ¿Por qué «Vida Fácil»?**
Porque es corto, en español y fácil de recordar para cualquiera, también para personas mayores. Comprobamos que no choca con ninguna marca del sector de la vivienda.
- Evidencia: D-199 · consulta de TMview (OEPM + EUIPO) del 11 nov en el PR #3.

---

## Las cinco preguntas difíciles (jurado simulado del 12 nov)

**41. Sale 1.107 € al mes por 77 m² en Fuencarral-El Pardo, y Salamanca entra con 1.500 €. ¿Eso es real?**
Era la media de todos los contratos declarados a Hacienda, también los antiguos, y se quedaba corta. Ahora multiplicamos el precio por metro de la Comunidad por cuánto más cuestan, en cada zona, los contratos firmados en 2024 según la Agencia Tributaria. Fuencarral-El Pardo pasa a unos 1.276 € y Salamanca a unos 1.797 €, así que con 1.500 € ya no entra, y el caso de ejemplo baja de 33 a 27 zonas.
- Evidencia: D-214 (puntos 2 y 3) · D-228, opción A, que eligió Mariano el 12 nov · producción, 12 nov (`fit-0.6`): Fuencarral-El Pardo «Alquiler ≈ 1.276 €/mes por 77 m² (16,6 €/m², contratos firmados en 2024; un anuncio de hoy puede pedir más)» y Salamanca ≈ 1.797 €/mes (23,3 €/m²), que no cumple el presupuesto · Agencia Tributaria, «Estadística de viviendas declaradas en IRPF», ejercicio 2024, «contratos de arrendamiento formalizados en el ejercicio» · `evidence/gate-01/2026-11-12/alquiler-contratos-nuevos/`. Factor por zona: entre 1,05 y 1,26 (Madrid, 1,20).
- Si preguntan por comprar: el precio es el valor tasado medio de la vivienda libre de cada municipio, que publica la Comunidad. No es el de un anuncio, y en los distritos de Madrid sale sin datos (D-227). Con el caso de ejemplo y 300.000 € para comprar, encajan 15 de 199 zonas: la 1.ª es Leganés, con un 95 % y «Comprar ≈ 221.000 € por 77 m²» (producción, 12 nov, `fit-0.5`).
- Si preguntan por el índice de la Comunidad (1934428): solo dice cuánto varían los precios, no cuánto más cuesta un contrato nuevo, y es un único valor para toda la región (D-228 §2).
- Estado: en producción desde el 12 nov (`fit-0.6`). Con 150 € más al mes, el caso de ejemplo gana 3 zonas («¿Y si cambias algo?»), así que el presupuesto ya cuenta.

**42. Una zona sale con un 98 % de encaje (hasta la noche del 12 nov, Fuencarral-El Pardo con un 100 %), pero en «Qué falta» tiene filas en JUSTO. ¿Cómo puede ser?**
Porque son dos preguntas distintas. El % dice cuánto se parece la zona a lo que pidió esta familia: en Latina, colegio a 6 minutos, parada a 2, centro de salud a 10 y 39 minutos hasta el trabajo. «Qué falta» compara la zona con los demás municipios urbanos repartiendo cada servicio entre toda la gente que lo usa: ahí Latina va justa en escuelas infantiles y centros de salud, sin llegar a faltar, y la tarjeta lo dice en una línea bajo el %.
- Evidencia: producción, 12 nov: `POST /api/v1/search` con el caso de ejemplo (`fit-0.6`) y `GET /api/v1/gaps/distrito/2807910`. Latina: escuela infantil 0,95 y centro de salud 0,99, JUSTO; colegio, mayores y farmacia, CUBIERTO; vivienda, SIN DATOS. Fuencarral-El Pardo (`/gaps/distrito/2807908`, 97 %): escuela infantil 0,98, colegio 0,76 y centro de salud 0,76, todas JUSTO.
- Si insiste en el colegio a 0,76: está por debajo del 80 %, pero la diferencia puede ser casual con esa población, y FALTA exige que no lo sea (pregunta 11).

**43. ¿Quién lo ha usado?**
**[Pendiente de Mariano: la prueba con 3–5 personas y un técnico municipal. Va así: «Lo probaron [N] personas que buscan casa y [un técnico municipal]; [cifra, por ejemplo cuántas encontraron una zona en menos de 2 minutos]. Una dijo: "[cita]".»]** Además, comprobamos a mano 10 zonas contra las fuentes oficiales, y eso destapó errores del propio registro que ya están corregidos, como cuatro centros de salud sin número de portal y un hospital sin nombre.
- Evidencia: `pitch/pruebas_usuarios/` (kit y plantilla de resultados) · `pitch/revision_10_zonas.md` · D-216 y D-218 §10.
- Si la prueba no se ha hecho: «Todavía no con usuarios reales: lo hemos validado contra las fuentes oficiales, y es lo siguiente».

**44. ¿Qué es original? El Ayuntamiento ya hizo «El Madrid de los 15 minutos», y el 2SFCA es de 2003.**
El método de repartir la capacidad entre quienes la comparten no es nuestro, y lo citamos: lo nuevo es lo que hacemos con él. El estudio del Ayuntamiento de 2022 da a cada portal de Madrid capital un índice según haya o no cada servicio a 15 minutos. Nosotros cubrimos los 179 municipios, contamos cuánta gente comparte cada servicio, comparamos cada zona con las de su tipo con una prueba estadística y sumamos el tiempo en transporte público con los horarios del Consorcio, que ese estudio dejaba para el futuro; y lo juntamos con un buscador para personas, abierto y con la fuente de cada cifra.
- Evidencia: el estudio, Jornadas de Geodatos 2022 (https://geoportal.madrid.es/fsdescargas/IDEAM_WBGEOPORTAL/GEOPORTAL/Jornada/2022/SALA5_1130_PROXIMIDAD_POR_CALCULODEREDES.pdf):
  - «Objetivo del proyecto»: «desde cada portal»;
  - «Creación de un índice normalizado»: «Existencia o no del equipamiento/servicio»;
  - «Mejora del modelo y posibilidades futuras»: «Población por portal» e «Incorporar los datos General Transit Feed Specification».
- Más evidencia: D-217 (Luo y Wang, 2003; Talbot et al., 2000) · D-213 (comparación por tipo y prueba de Poisson) · D-220 (transporte).
- Si insiste: del estudio tomamos la velocidad de 4 km/h, para que los minutos se puedan comparar (D-211).

**45. ¿Quién lo mantiene cuando acabe el concurso?**
Mariano, y está pensado para que baste una persona. Los datos se recargan con un comando, cada conjunto pasa un control de calidad antes de entrar y una prueba revisa la web pública cada mañana. Al año son unos 2–3 días para la estadística anual y medio día por trimestre para los horarios del transporte; el código es abierto y cada decisión está escrita, así que otra persona puede retomarlo.
- Evidencia: `pitch/modelo_negocio.md` («Mantenimiento con una sola persona», estimación de D) · `.github/workflows/smoke-demo.yml` · `evidence/gate-01/` · `docs/00_index/01_decisions_log.md` · `LICENSE` (Apache-2.0).

## Dos más, con las cifras de impacto (12 nov)

**46. ¿Cómo sabéis que en una zona «falta» y no es casualidad?**
Porque FALTA exige dos cosas: tener menos del 80 % de lo que tienen los municipios parecidos, y que esa diferencia no se explique por azar con una prueba exacta de Poisson. En Puente de Vallecas, con 9.433 niños de 0 a 4 años, una diferencia así saldría por azar menos de 1 vez de cada 100. Por eso Centro, con una proporción parecida pero menos niños, sale JUSTO y no FALTA (pregunta 15).
- Evidencia: D-213 (punto 2: regla de los cuatro quintos e intervalo exacto de Poisson de Garwood, bilateral al 95 %, que equivale a unilateral al 2,5 %) · D-217 · D-229 §3 (`p_value` de cada zona en `GET /api/v1/gaps/impact`) · `evidence/gate-04/2026-11-12/impact-cifras.txt`: p = 0,001 en Puente de Vallecas, 0,016 en Carabanchel y 0,011 en Villaverde.
- Si insiste en los pueblos pequeños: un pueblo con muy pocos casos esperados se compara junto con sus vecinos parecidos (D-217 §6). Si ni así llega, sale «zona pequeña para comparar», nunca FALTA (pregunta 14).
- Si insiste en las comparaciones múltiples: no corregimos por ellas. Con 199 zonas por fila, alguna FALTA podría salir por azar, así que damos la probabilidad de cada una para que se pueda juzgar. Todas las de la lista de impacto están por debajo de 0,02.

**47. ¿A cuánta gente afecta lo que falta?**
En toda la región:
- escuelas infantiles: 25.551 niños de 0 a 4 años, el 9,8 %;
- farmacias: 667.172 personas, el 9,4 %;
- centros de mayores: 54.581 personas de 65 años o más, el 4,1 %;
- vivienda grande: 99.483 hogares de 4 o más personas, el 14,8 %.

En colegios y centros de salud no hay ninguna zona con una falta clara. Las zonas salen ordenadas por la gente afectada, y esa es la lista de dónde invertir primero.
- Evidencia: D-229 (`impact-0.1`) · `GET /api/v1/gaps/impact` · `evidence/gate-04/2026-11-12/impact-cifras.txt` (datos del 12 nov). La gente afectada es la población que ya usa cada fila: el censo de la Comunidad y, en los distritos, el padrón. No se estima nada.
- Detalle, si lo piden:
  - escuelas infantiles: Puente de Vallecas (9.433), Carabanchel (9.150) y Villaverde (6.968);
  - farmacias: Getafe, Torrejón de Ardoz, Parla, Rivas-Vaciamadrid y Valdemoro;
  - mayores: 6 municipios, con Torrejón de Ardoz y Pozuelo de Alarcón a la cabeza;
  - vivienda: 25 municipios, con Fuenlabrada, Leganés y Alcorcón a la cabeza.
- Estado: en producción desde el 12 nov (`GET /api/v1/gaps/impact`, comprobado: 25.551 de 260.310 niños de 0 a 4 años, en 3 zonas). El ranking «dónde invertir primero» aún no se ve en la web (**pendiente de B**): si lo piden, se enseña la ruta.
