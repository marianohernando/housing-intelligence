# Plan de competición DATAMAD 2026 (10 → 26 nov)

Vigente desde el 10 nov 2026. Decisiones: D-192 (replan), D-193 (formulario), D-194 (alcance de la demo), D-195 (repo público). Las cards y su estado viven en `board/BOARD.md`; este documento explica el porqué y lo que espera el jurado.

## 1. Qué presentamos

Propuesta (documento «Housing Intelligence — la idea», 31 oct): **«Qué necesita la gente. Qué le falta a cada barrio.»** Otros servicios enseñan lo que hay; nosotros enseñamos lo que falta.

| Usuario | Pregunta | En la demo |
|---|---|---|
| Personas (gratis) | ¿Dónde vivo mejor con lo que necesito? | **Buscador**: chips (presupuesto, tamaño del hogar, lugar de trabajo, colegio cerca) → ranking de zonas, el porqué en lenguaje cotidiano, **Reality Check** (cuántas zonas aparecen al relajar cada condición) y procedencia de cada dato |
| Ayuntamientos | ¿Qué le falta a cada barrio y dónde invierto primero? | **Lista de lo que falta por zona**: FALTA / JUSTO / CUBIERTO para escuela infantil, colegio, centro de salud, mayores, farmacia y vivienda (tamaño de los hogares frente a superficie de las viviendas) |
| Empresas (pagan) | ¿Qué negocio o vivienda hace falta aquí? | Solo slides + API/MCP (D-194) |

Fuera de la demo (D-194): zonas verdes (solo hay datos de Madrid capital), «qué abrir» calculado para empresas, necesidad declarada por usuarios (se presenta como siguiente paso y **nunca se simula**), PRO workspace, ML, 3D, timeline y HomeFit.

Reglas de honestidad:
- En la demo y en el pitch solo van cifras reales. Los ejemplos del PDF del 31 oct son ilustrativos.
- Los proxies se declaran. Por ejemplo, «centros por población» no es lo mismo que «plazas».
- Si falta un dato, se baja la confidence; nunca se inventa.
- Solo cuenta como «dataset CM» lo publicado en el Portal de Datos Abiertos de la Comunidad. El resto es complementario.

## 2. Fases y lo que espera el jurado

| Fase | Fecha | Qué miran | Mínimo | Mejor resultado realista |
|---|---|---|---|---|
| 1. Formulario → hasta 50 preseleccionados | antes del 20 nov (objetivo 18) | Nombre, resumen ≤100 palabras, enlaces opcionales; idea y potencial | Resumen claro con los datos CM explícitos | Demo desplegada + repo público: la mayoría enviará solo una idea |
| 2. Corte a 12 finalistas | 20–25 nov (fecha sin anunciar) | Probablemente abren los enlaces | Que la demo cargue y no falle | Demo que se entiende sola en 1 minuto, con un caso de ejemplo precargado |
| 3. Final | 26 nov | Slides antes de las 14:00 + 5 min de pitch + 5 de preguntas; criterios §10 | 4 slides de §8 y demo en directo | Historia con datos reales y respuestas preparadas para cada perfil del jurado |

## 3. Criterios → evidencia

| Criterio | Puntos | Qué buscan | Nuestra prueba |
|---|---|---|---|
| Datos CM | 25 | Uso intensivo y efectivo; primer desempate | Pasar de 10 a 14–16 datasets CM; contador en la app y fuente en cada resultado |
| Impacto | 25 | Beneficio social y económico concreto | Un barrio real con su lista de lo que falta y una familia real buscando dónde vivir |
| Originalidad | 20 | Algo que no existe | «Lo que falta» en vez de «lo que hay», Reality Check y MCP para agentes |
| Viabilidad | 15 | Que se sostenga | Demo desplegada, modelo (pagan las empresas), coste casi nulo, privacidad (D-186) |
| Código abierto | 10 | Reproducible | Repo público Apache-2.0, `make` como entrada única, lineage por dato, pipelines declarativos |
| Presentación | 5 | Claridad | Guion de 5 min ensayado y demo en vivo |

## 4. Jurado

Perfiles según las bases. Lo que valoran es una inferencia a partir de su trayectoria pública.

| Miembro | Perfil | Le importará | Respuesta preparada |
|---|---|---|---|
| Alberto Abella | Gaia-X España | Interoperabilidad, APIs, espacios de datos | API versionada + MCP; catálogo machine-readable; datos con fuente y versión |
| Olga Quirós | ASEDIE (sector infomediario) | Negocio y valor de reutilizar datos públicos | Pagan las empresas por análisis agregados y API; gratis para personas |
| Loren Escot | UCM, Estudios Estadísticos | Rigor de los indicadores | Ratio por población frente a la referencia regional, umbrales declarados, confidence en municipios pequeños |
| Ricardo Curto | Universidad de Oviedo (datos abiertos) | Calidad, licencias y cita de fuentes | Datasets enlazados, licencias por fuente, lineage y Quality Gates |

## 5. Calendario y responsables

| Día | Claude (sesión de desarrollo) | Mariano |
|---|---|---|
| 11–12 nov | DATA-007 transporte CRTM + DATA-016 datasets CM nuevos | Contraseña de Supabase en `.env` |
| 12–13 | CORE-005 indicadores por sección/H3 (distancias a pie) | — |
| 13–14 | GAP-001 lista de lo que falta por zona | 15 min: ¿tiene sentido en barrios que conoces? |
| 15–16 | Buscador: ScenarioState, affordability, Residential Fit + Reality Check, mapa, explicación y procedencia | **16 por la noche: probar la demo 20 min → cut review 1** |
| 17 | OPS-001 despliegue con caso precargado; README | Abrir el enlace en el móvil |
| 18 | Repo público (antes si hay algo enseñable) y resumen final | **Enviar el formulario** (19 = margen) |
| 19–22 | Tiempo a polos de empleo, MCP 3–5 tools, más datasets, accesibilidad; **22: cut review 2** | 15 min/día de feedback |
| 23 | Freeze: solo fixes, manifest final de fuentes | — |
| 24 | Slides (estilo del PDF del 31 oct), guion, vídeo de respaldo, snapshot offline | Revisar slides |
| 25 | Banco de preguntas | **5 ensayos cronometrados** |
| 26 | Smoke test | Entrega y presentación |

Regla de recorte: si una card se atasca más de medio día, se recorta al mínimo útil para la demo y se anota en el board.

## 6. Formulario (DATAMAD-FORM-01)

URL: https://forms.gle/NyatKHN95aPxvQro8. Pide nombre, resumen ≤100 palabras, participantes, confirmación de asistencia al 26 nov y enlaces opcionales. Lo envía Mariano.

Nombre: **Housing Intelligence**

Borrador del resumen (revisar el 18 nov con lo que esté hecho y añadir el número real de datasets CM):

> Housing Intelligence convierte los datos abiertos de la Comunidad de Madrid en un mapa de lo que falta. A las personas les recomienda zonas donde vivir según su presupuesto, hogar y lugares de referencia, explica el porqué en lenguaje cotidiano y propone alternativas cuando lo que buscan no existe. A ayuntamientos y empresas les muestra, zona a zona, qué falta, qué está justo y qué está cubierto: escuelas infantiles, colegios, salud, servicios para mayores, farmacias y tipos de vivienda. Cada resultado cita sus datasets oficiales y su nivel de confianza. Código abierto y API para reutilizarlo.

Enlaces: demo (OPS-001) y repo (DATAMAD-PUBLIC-01).

## 7. Repo público (DATAMAD-PUBLIC-01, D-195)

Checklist antes de cambiar la visibilidad:
- [x] gitleaks sobre todo el historial en verde (CI).
- [x] Sin tokens en ficheros versionados: `.mcp.json` solo tiene el project ref y el token llega por variable de entorno.
- [x] `LICENSE` (Apache-2.0), `docs/LICENSE` (CC BY 4.0), README con la declaración del tag `pre-datamad`.
- [ ] Mariano acepta que el email de autor de los commits quedará visible (no se reescribe el historial).
- [ ] Mariano acepta que `docs/` (estrategia de producto y negocio) será visible para otros equipos.

Comando: `gh repo edit marianohernando/housing-intelligence --visibility public --accept-visibility-change-consequences`.

## 8. Slides y pitch

Entrega antes de las 14:00 del 26 nov (§8 de las bases), en este orden:
1. Título, integrantes y descripción breve.
2. Problema y datasets usados con enlaces.
3. Resultados: utilidad, impacto y viabilidad, con enlaces a la demo y al repo.
4. Pantallazo del sistema.

Estilo: el del PDF del 31 oct.

Guion de 5 minutos:
| Tiempo | Contenido |
|---|---|
| 0:00–0:40 | Problema: personas, ayuntamientos y empresas deciden a ciegas |
| 0:40–2:40 | Demo: una familia busca dónde vivir → zonas, el porqué, Reality Check |
| 2:40–3:40 | Un barrio real y su lista de lo que falta |
| 3:40–4:30 | Datos CM usados, código abierto, quién paga |
| 4:30–5:00 | Impacto y cierre |

Banco de preguntas:
- **¿De dónde sale «lo que falta» si no tenéis usuarios?** Hoy, de datos oficiales CM (población por edad, hogares, equipamientos) comparados con la referencia regional. Después se suma lo que declara la gente, anónimo y agregado por zona con un umbral mínimo.
- **¿Cómo decidís que algo «falta»?** Por el ratio por población frente a la mediana regional, con umbrales declarados. En zonas pequeñas la confidence es baja. Es una señal para priorizar, no un veredicto.
- **¿Qué hicisteis durante la competición?** El tag `pre-datamad` (22 oct) marca datos y mapa. Desde el 7 nov: transporte, la lista de lo que falta, el buscador, el despliegue y la API/MCP.
- **¿Privacidad?** Nunca datos personales: solo agregados por zona. Los equipamientos protegidos quedan excluidos (D-186).
- **¿Reproducible?** Licencia Apache-2.0 y `make` como entrada única. Añadir un dataset es añadir un YAML de pipeline.
- **¿Por qué no usar portales inmobiliarios?** Muestran oferta; nosotros, necesidad y encaje. No hacemos scraping (licencias).

## 9. El 26 de noviembre

| Hora | Qué |
|---|---|
| 8:30 | Smoke test de la demo (online y offline), vídeo de respaldo, slides en PDF, portátil cargado |
| Mañana | Subir las slides en cuanto la plataforma abra; **nunca después de las 13:30** |
| 10:30 | Llegada a URJC Vicálvaro |
| 11:00–13:30 | Inauguración y plenarias; confirmar que la subida está hecha |
| 13:30–17:00 | Talleres; probar proyector, HDMI y wifi; último ensayo |
| 17:00–19:00 | Presentaciones |
| 19:00 / 20:00 | Deliberación / premios |

## 10. Riesgos

| Riesgo | Mitigación |
|---|---|
| Calcular rutas de transporte es complejo | Nivel A (acceso a paradas y frecuencia) obligatorio; tiempo a polos de empleo solo si sobra |
| La demo se cae o no hay wifi | Snapshot offline + vídeo de 2 min |
| Límite de 500 MB del plan free de Supabase | Perfil demo de 77 MB (D-188) |
| Prometer más de lo que hay | Solo cifras reales; proxies declarados |
| No entrar entre los 12 | La demo y el repo públicos siguen teniendo valor |

## 11. Cómo trabajamos

- **Sesión de desarrollo.** Es la única que escribe en la carpeta principal del repo, en la rama `claude/sprint-1-public`. Trabaja en modo bucle por card, con gate + evidencia + commit de rutas explícitas + push por fase, y actualiza el board.
- **Otras sesiones.** Coordinación, slides, formulario y visibilidad del repo. Si necesitan escribir, lo hacen en un worktree propio (`git worktree add ../housing-intelligence-coord -b claude/coord claude/sprint-1-public`) y se integran por PR.
- **Mariano.** Decide, mete las credenciales en `.env`, da 15 min de feedback al día, envía el formulario, ensaya y asiste el 26.
