# Registro de Decisiones

## D-001 — Producto con tres capas
**Decisión:** PUBLIC + PRO + DATA/API/MCP.

## D-002 — Capa gratuita completa
La mayoría de funcionalidades que ayudan al ciudadano deben permanecer gratis para maximizar utilidad, adopción y aprendizaje agregado.

## D-003 — No vender datos personales
La capa PRO solo utilizará datos agregados/anonimizados y fuentes públicas/propias.

## D-004 — Fuente de verdad
La IA no será la fuente de verdad. La fuente de verdad será la combinación de datos estructurados, reglas, modelos, features y versiones.

## D-005 — GIS
PostgreSQL + PostGIS serán el corazón geoespacial.

## D-006 — Base vectorial
pgvector inicialmente, evitando infraestructura extra hasta que sea necesaria.

## D-007 — Geografía
Usar límites administrativos + H3 como malla analítica común.

## D-008 — JEV
JEV se utilizará para decisiones rápidas, tipadas y probabilísticas: clasificación, routing, control de calidad y reranking.

## D-009 — LLM
Claude Fable 5 se reserva para razonamiento complejo, conversación, informes y fallback; no para cálculos ni clasificaciones masivas.

## D-010 — Mapa
MapLibre + deck.gl como stack principal. Digital twin 3D estilizado, no Google Earth completo.

## D-011 — Madrid 3D
Aprovechar modelo 3D oficial de edificios de Madrid cuando sea viable.

## D-012 — MVP
“MVP” para DATAMAD significa versión reducida geográficamente pero técnicamente avanzada, no demo superficial.


## D-013 — Fase actual: datos antes que código
Antes de iniciar desarrollo fuerte se completará inventario de fuentes, taxonomía, geografía y feature dictionary.

## D-014 — Datos exactos vs conocimiento semántico
Población, precios, distancias y métricas exactas vivirán en PostgreSQL/PostGIS. La base vectorial se reserva para documentación, semántica y embeddings de lugares.

## D-015 — Dataset temporal
Cada fuente tendrá frecuencia de actualización explícita y el producto distinguirá datos estructurales, periódicos y casi tiempo real.

## D-016 — Prioridad de fuentes oficiales
Para DATAMAD se priorizarán fuentes oficiales de Comunidad de Madrid y Ayuntamiento, complementadas con INE, Catastro y transporte.


## D-017 — Enriquecimiento multi-fuente
La plataforma combinará fuentes oficiales, Catastro, OSM/POIs, APIs comerciales opcionales y scraping selectivo.

## D-018 — Source Trust
Cada dato tendrá procedencia, frescura y nivel de confianza. Las fuentes oficiales prevalecen cuando exista conflicto.

## D-019 — Entity Resolution
Se construirá un registro canónico de lugares para deduplicar colegios, hospitales, negocios y otros POIs entre múltiples fuentes.

## D-020 — POI scoring
Los POIs no se puntuarán mediante conteo bruto. Se transformarán en accesibilidad, cobertura, diversidad, redundancia y tiempo de viaje.


## D-021 — Documentación orientada a ejecución
La documentación se considera ahora input directo para Claude Code. Debe incluir contratos, acceptance criteria, tests y reglas de implementación.

## D-022 — CLAUDE.md raíz
El repositorio final incluirá un `CLAUDE.md` como punto de entrada obligatorio para agentes de código.

## D-023 — Source/Dataset/Metric registries
Fuentes, datasets y métricas serán entidades versionadas de primera clase.

## D-024 — No SQL libre desde IA
Ni Claude ni MCP expondrán ejecución SQL arbitraria. Toda consulta de negocio debe pasar por tools/servicios.

## D-025 — Model registry
Todo modelo ML activo deberá tener versión, dataset/feature versions, evals y rollback.


## D-026 — Actualización de datos por frecuencia natural
Cada fuente se actualizará según su frecuencia real. No se forzará una única cadencia global.

## D-027 — Perfil persistente con consentimiento
El usuario podrá guardar perfil completo si crea cuenta y acepta el tratamiento. PII y señales analíticas se separarán técnicamente.

## D-028 — Recomendación híbrida
Residential Fit usará hard constraints + scoring explicable + ML progresivo + reranking cuando corresponda.

## D-029 — Prioridades corregibles
La IA propondrá prioridades/pesos y el usuario podrá corregirlas manualmente.

## D-030 — Mapa 3D estilo SimCity
El producto usará una visualización 3D estilizada, tipo SimCity/Jarvis, basada en geometría real y capas analíticas.

## D-031 — Natural Language GIS
El usuario podrá consultar el mapa en lenguaje natural. La IA traducirá la intención a filtros y tools predefinidos; no generará SQL libre.

## D-032 — Plan intermedio de particulares
Se contempla una capa de pago para particulares con mayor número de consultas/análisis avanzados, manteniendo una capa gratuita útil.

## D-033 — Monetización temprana de consumo
AdSense/SEO se podrá utilizar inicialmente en contenido editorial y páginas informativas, separado del mapa interactivo y sin degradar experiencia.

## D-034 — Confidence explícito
Las estimaciones y datos interpolados deberán mostrar confidence/frescura y no aparentar precisión inexistente.

## D-035 — Enriquecimiento por fases
Fase inicial: oficial + OSM/APIs. Fase posterior: ampliar scraping de forma controlada, legal y versionada cuando aporte cobertura real.

## D-036 — Accesibilidad > conteo POI
Los servicios se medirán por tiempo, cobertura, diversidad, redundancia, horario y accesibilidad real.

## D-037 — Madrid Place Model
Se entrenará un modelo territorial propio con 200–400 features y embeddings por microzona.

## D-038 — Aprendizaje progresivo de comportamiento
Las señales de uso agregadas alimentarán primero analytics y, con suficiente volumen/calidad, entrenamiento del recomendador.

## D-039 — Housing Gap avanzado
PRO deberá recomendar no solo dónde hay gap, sino tipología, tamaño, precio objetivo, target y producto residencial sugerido.

## D-040 — Parcel Intelligence ampliado
PRO analizará zonas, parcelas y proyectos/activos subidos por clientes.

## D-041 — Private Data Enrichment
Clientes PRO podrán conectar datos propios aislados por tenant. Nunca se incorporarán al dataset global sin un acuerdo/base específica.

## D-042 — JEV en desarrollo y producción
JEV se utilizará tanto en preparación de datos como en runtime para clasificación, routing, control de calidad y reranking.

## D-043 — pgvector con dos familias
pgvector almacenará RAG documental y embeddings territoriales. No será fuente de cifras exactas.

## D-044 — MCP PRO avanzado
Objetivo a medio plazo: permitir que agentes creen consultas analíticas y capas de mapa temporales desde lenguaje natural.

## D-045 — Evaluador de vivienda por URL/dirección
PUBLIC podrá analizar una vivienda concreta importando datos de un anuncio cuando sea legal/técnicamente posible.

## D-046 — Reality Check como optimizador
El sistema no solo explicará por qué una búsqueda falla: propondrá la mínima modificación de presupuesto, tiempo, tamaño, municipio, movilidad o tenure para volverla viable.


## D-047 — Datos económicos exactos protegidos + rangos derivados
Ingresos, ahorro y deuda podrán almacenarse con valor exacto protegido para cálculo individual. Analytics y PRO usarán rangos/segmentos derivados.

## D-048 — Separación identidad/perfil
La identidad de usuario se almacenará separada del perfil residencial/económico y se unirá por identificador interno.

## D-049 — Ubicaciones sensibles minimizadas
Lugares de trabajo/familia podrán usarse con precisión suficiente para routing, pero se almacenarán minimizando precisión cuando no sea necesaria o cifrando la ubicación exacta.

## D-050 — Datos sensibles voluntarios
Movilidad reducida, dependencia u otras necesidades sensibles solo podrán introducirse voluntariamente y tendrán protección reforzada. Nunca se inferirán silenciosamente.

## D-051 — Entrenamiento territorial H3 + contexto vecinal
Los modelos territoriales usarán H3/sección censal como base y features de contexto de celdas vecinas.

## D-052 — Jerarquía de datos faltantes
Dato directo → agregación razonable → estimación documentada → desconocido. Cada degradación reduce confidence.

## D-053 — Residential Fit evolutivo
Fase inicial: hard constraints + pesos personalizados y explicables. Fase posterior: ML personalizador/ranker, manteniendo el baseline interpretable.

## D-054 — Primer ML de preferencias
Learning-to-Rank/gradient boosting será la primera familia prevista cuando haya volumen suficiente de feedback.

## D-055 — Price/Rent Model
Usar ML estructurado para precio/alquiler combinado con estadísticas oficiales y siempre con intervalos/confidence.

## D-056 — Madrid Place Model
200–400 features territoriales y embeddings de 64–128 dimensiones como diseño inicial.

## D-057 — Histórico MVP
El MVP utilizará actualidad + aproximadamente 3–5 años cuando exista histórico suficiente. El histórico completo queda para evolución posterior.

## D-058 — Emerging Areas
PRO incluirá detección de zonas emergentes a partir de tendencias de población, renta, vivienda, actividad, transporte y servicios.

## D-059 — Forecasting por horizontes
MVP: forecast operativo 1–3 años. Producto completo: escenarios adicionales 5–10 años claramente etiquetados como escenarios y no predicción exacta.

## D-060 — Confidence por componente
Cada fuente/modelo puede tener confidence propio y el resultado puede ofrecer un confidence agregado.

## D-061 — Feedback estructurado + texto
Motivos de rechazo rápidos más texto opcional.

## D-062 — Entrenamiento controlado
No habrá online learning autónomo. Nuevas versiones se entrenan, evalúan, comparan y activan solo tras superar criterios.

## D-063 — Explicabilidad ultra-simple
Las explicaciones deben ser comprensibles sin interpretar métricas abstractas. Priorizar lenguaje cotidiano, comparaciones concretas y ejemplos tangibles.

## D-064 — PRO no expone atributos sensibles
PRO podrá ver necesidades agregadas como “demanda de vivienda accesible”, nunca perfiles sensibles ni atributos individuales.

## D-065 — Cold Start experto
Datos públicos + reglas expertas + perfiles sintéticos para arrancar antes de tener masa de usuarios.

## D-066 — Simulador PRO avanzado
El producto completo incluirá simulación de proyectos: hogares compatibles, absorción, competencia, servicios, movilidad, sensibilidad de precio y escenarios territoriales.

## D-067 — Madrid-first para DATAMAD
En el MVP DATAMAD los datos del Catálogo de Datos Abiertos de la Comunidad de Madrid serán estructurales y alimentarán funcionalidades centrales. Otras fuentes solo complementan, validan o enriquecen.


## D-068 — Micro-location before neighborhood averages
La plataforma no tratará un barrio como unidad homogénea. El scoring principal se calculará a nivel microzona/H3/sección censal y podrá descender a calle/edificio cuando exista cobertura suficiente.

## D-069 — Housing feature set amplio
El modelo de vivienda intentará incorporar precio, superficie, dormitorios, antigüedad, tipología, ascensor, garaje, eficiencia, accesibilidad, obra nueva/usada, tenencia, densidad y vacancia cuando exista información fiable y legalmente reutilizable.

## D-070 — Accesibilidad peatonal por red
La proximidad a servicios se medirá preferentemente por recorridos y tiempos reales de red, no por radio euclídeo.

## D-071 — Transporte multimodal completo
El modelo de movilidad incorporará Metro, autobuses urbanos/interurbanos, Cercanías, Metro Ligero, tren/ferrocarril y otros modos disponibles, considerando acceso, frecuencia, transbordos y destinos.

## D-072 — Múltiples anchors personales
El perfil podrá contener varios destinos relevantes: trabajo, pareja, colegio, familia, universidad, hospital u otros, cada uno con frecuencia y prioridad.

## D-073 — Medio ambiente personalizado
Ruido, contaminación, calor y verde serán capas territoriales y podrán influir en Residential Fit según preferencias.

## D-074 — Actividad urbana dinámica
La vida de barrio se modelará con diversidad, proximidad, horarios y evolución de aperturas/cierres cuando existan datos.

## D-075 — Seguridad objetiva y metodológicamente prudente
La plataforma podrá incorporar seguridad vial y seguridad ciudadana basada en datos oficiales/agregados. No ocultará diferencias territoriales, pero evitará etiquetas estigmatizantes y falsa precisión.

## D-076 — Educación avanzada
El modelo familiar podrá considerar proximidad, etapa, titularidad, oferta/cobertura y otros datos comparables disponibles, evitando rankings simplistas de “barrios buenos/malos”.

## D-077 — Salud avanzada
El modelo incluirá centros de salud, hospitales, farmacias, tiempos de acceso, tipología de centro, urgencias/especialidades y cobertura cuando existan datos.

## D-078 — Building intelligence best-effort
A nivel edificio se intentará combinar Catastro, geometría, contexto, documentación técnica y estimaciones. Si no existe cobertura suficiente, se degradará a contexto catastral/territorial sin inventar datos.

## D-079 — 15-Minute Living Model
Se construirá un modelo de acceso a necesidades en 5, 10 y 15 minutos, personalizado por perfil y multimodal cuando corresponda.

## D-080 — Car Dependency Model
Se calculará dependencia del coche y el impacto económico/temporal de vivir con o sin vehículo privado.

## D-081 — Total Housing Cost completo
El coste residencial incluirá vivienda, energía, transporte, coche, parking, comunidad, impuestos, mantenimiento y coste temporal cuando los datos lo permitan.

## D-082 — Timeline territorial
El mapa deberá soportar evolución histórica y, posteriormente, forecast/escenarios en una experiencia visual tipo SimCity.

## D-083 — Economic Fabric PRO
PRO analizará tejido empresarial, comercio, oficinas, empleo y actividad económica alrededor de zonas y parcelas.

## D-084 — Emerging Opportunity Model
Se desarrollará un modelo de oportunidad emergente combinando cambios de población, vivienda, negocios, transporte, renta y servicios.

## D-085 — Infrastructure Scenario Engine
DATAMAD puede incluir una versión limitada; el producto completo permitirá simular nuevas estaciones, colegios, hospitales, promociones u otras infraestructuras y recalcular el territorio.

## D-086 — Hybrid Technical RAG
Las consultas técnicas combinarán documentación RAG + datos GIS + métricas estructuradas + modelos, no solo texto.

## D-087 — Similarity Search explicable
La búsqueda “como X pero más barato/verde/conectado” usará Place Embeddings + restricciones del usuario + explicación de similitudes y diferencias.

## D-088 — Objetivo de 300–500 features
El feature universe aspirará a 300–500 variables base/derivadas bien documentadas. El MVP usará un subconjunto estable y probado.


## D-089 — Doble referencia territorial
Los scores podrán compararse contra toda Madrid y contra zonas comparables, evitando interpretaciones engañosas.

## D-090 — Tipologías territoriales híbridas
Se usarán clustering/Place Embeddings para descubrir tipologías de zonas, con interpretación y naming humano.

## D-091 — Movilidad sensible a horario
Cuando existan datos, la accesibilidad tendrá en cuenta horarios reales, frecuencia y franjas temporales.

## D-092 — Pendiente y caminabilidad personalizada
La dificultad peatonal podrá incorporar pendiente/ruta y perfil del usuario cuando haya datos suficientes.

## D-093 — Barreras urbanas explícitas
Además del routing, se modelarán barreras urbanas relevantes como vías rápidas, ferrocarril o cruces complejos.

## D-094 — Capacidad de servicios best-effort
Cuando existan datos fiables, colegios, hospitales y otros servicios incorporarán capacidad/servicios; si no, se degradará a tipología/tamaño.

## D-095 — Presión oferta-demanda en servicios
Cuando exista información suficiente, se calculará saturación/cobertura relativa, no solo oferta bruta.

## D-096 — Submodelos por etapa de vida
El motor común tendrá módulos especializados FamilyFit, SeniorFit, StudentFit, AccessibleLivingFit y otros que puedan surgir.

## D-097 — Preferencias inferidas solo como sugerencia
La IA podrá proponer factores plausibles según contexto, pero pedirá confirmación antes de incorporarlos como preferencia.

## D-098 — Progressive profiling
El onboarding será progresivo y preguntará solo lo necesario para mejorar la recomendación.

## D-099 — Active Questioning
El sistema priorizará preguntas que reduzcan más incertidumbre o cambien materialmente el ranking.

## D-100 — Data Coverage Map
Se construirá una capa de cobertura/calidad de datos por microzona.

## D-101 — Históricos versionados
Se conservarán snapshots/versiones de métricas y datasets relevantes para análisis temporal.

## D-102 — Correcciones de fuentes versionadas
Si una fuente corrige históricos, se conservará trazabilidad y se recalcularán dependencias afectadas.

## D-103 — Lineage completo
PUBLIC verá explicaciones sencillas; PRO/engineering podrá acceder a lineage detallado por métrica/score.

## D-104 — Incertidumbre de precio explicada
Estimaciones de precio/alquiler se expresarán como rangos y con explicación de incertidumbre.

## D-105 — Detección de anomalías multi-capa
Outliers mediante reglas + estadística + JEV para triage/revisión.

## D-106 — Knowledge Graph opcional
No es requisito del MVP. Queda documentado para incluirlo solo si sobra tiempo o las relaciones justifican claramente su coste.

## D-107 — Simulación territorial gradual
DATAMAD puede recalcular un subconjunto de variables ante escenarios. Producto completo aspirará a simulación before/after más completa.

## D-108 — Feature abundance, model restraint
El sistema puede tener 300–500 features disponibles, pero cada modelo usará solo las que aporten señal, estabilidad y explicabilidad.

## D-109 — Map-first onboarding
No habrá formulario tradicional como experiencia principal. El usuario entra al mapa y usa chat, chips y filtros.

## D-110 — Conversational + filter UX
Chat y filtros son interfaces sobre un único `ScenarioState`.

## D-111 — Accessibility needs, not diagnosis labels
No crear rankings rígidos por diagnóstico. Modelar necesidades concretas de accesibilidad, movilidad, estímulo, orientación y servicios.

## D-112 — Accessibility is core
Accesibilidad física, visual, auditiva, cognitiva y sensorial forma parte del Residential Intelligence Engine.

## D-113 — No silent inference of disability
Nunca inferir discapacidad, autismo, salud mental u otra condición sensible del comportamiento.

## D-114 — Sensory/cognitive adaptation
El ranking podrá considerar ruido, intensidad peatonal, complejidad de rutas/transbordos, previsibilidad y accesibilidad cognitiva cuando el usuario lo solicite.

## D-115 — Visual-accessibility routing
Incorporar cuando haya datos: avisadores acústicos, cruces, accesibilidad de aceras, complejidad de intersecciones, transporte accesible, obras/incidencias y ayudas de orientación.

## D-116 — Accessibility confidence
No afirmar que una calle/edificio es accesible si solo existen proxies territoriales.

## D-117 — Multi-stage Residential Fit pipeline
Hard constraints → candidate generation → structured scoring → ML/JEV reranking → diversified top results.

## D-118 — Reality Check on empty result
Una búsqueda sin resultados activa diagnóstico de constraints y alternativas mínimas.

## D-119 — Composite + component scores
Score global para ordenar + subscores por coste, movilidad, servicios, entorno, accesibilidad, vivienda, etc.

## D-120 — Personal fit vs territorial quality
Separar “te encaja a ti” de la referencia/calidad territorial general.

## D-121 — Hybrid weight generation
Pesos por baseline experto + preferencias explícitas + contexto + aprendizaje posterior.

## D-122 — Pareto recommendation
Representar compromisos entre objetivos en conflicto.

## D-123 — Confidence-aware scoring
La fiabilidad del dato afecta la certeza y puede bloquear validación si es crítica.

## D-124 — Spatial continuity controls
Contexto vecinal y suavizado selectivo para evitar saltos artificiales.

## D-125 — Piecewise affordability preference
Curvas por tramos: ideal, cómodo, máximo y exclusión.

## D-126 — Multi-anchor weighted mobility
Anchors ponderados por frecuencia, importancia y tolerancia.

## D-127 — Saturation functions
Servicios y POIs usan rendimientos decrecientes.

## D-128 — Hard vs soft penalty
Solo hard constraints o “evitar” eliminan automáticamente.

## D-129 — Safety moderation
Seguridad con peso moderado, personalización y metodología explícita.

## D-130 — Verified accessibility constraints
Requisitos como ascensor/step-free solo se dan por cumplidos con evidencia suficiente; si no, UNKNOWN.

## D-131 — AreaFit + HomeFit
Mismo motor base, capas específicas para zona y vivienda.

## D-132 — Session adaptation, controlled global learning
La sesión adapta; el modelo global cambia solo tras evaluación.

## D-133 — Result diversity
El top contiene alternativas realmente distintas.

## D-134 — Subjective concept enrichment
Ambiente/tranquilidad/vida de barrio se modelan con señales observables y web enrichment trazable.

## D-135 — Explicit alternative discovery
Las alternativas fuera de constraints se separan visualmente.

## D-136 — Algorithm invariants
Validación con golden profiles, synthetic profiles, casos reales e invariantes lógicos.

## D-137 — Bronze/Silver/Gold + lineage completo
Conservar RAW original, versión normalizada y features finales reproducibles.

## D-138 — Source disagreement is data
No esconder discrepancias entre fuentes; almacenarlas y resolverlas mediante políticas por métrica.

## D-139 — Multi-scale features
Cada microzona puede tener features propias y contextuales a 5/10/15 min y vecindad H3.

## D-140 — Null reason taxonomy
Distinguir missing_source, not_applicable, stale, parse_error, coverage_gap, genuinely_absent y otros estados.

## D-141 — Domain feature stores
Features separadas por vivienda, movilidad, servicios, ambiente, economía, urbanismo, etc., con vistas unificadas para modelos.

## D-142 — 30–50 deeply integrated DATAMAD datasets
El MVP prioriza profundidad, calidad y trazabilidad frente a acumular datasets superficiales.

## D-143 — Graceful domain degradation
Si falta un dominio, el motor reduce confidence y aplica reglas de redistribución; nunca imputa 0 por defecto.

## D-144 — Market listing history subject to lawful access
El histórico de anuncios es objetivo estratégico, pero solo se ingiere mediante permiso, licencia, API/proveedor autorizado o fuente reutilizable.

## D-145 — Catastro via official services
Catastro se ingiere preferentemente mediante INSPIRE WFS/ATOM/WMS y productos oficiales, no scraping de interfaz.

## D-146 — Transport via official open feeds
CRTM/operadores: GTFS/API/open data primero; scraping solo como último recurso y nunca para sustituir feeds oficiales.

## D-147 — Commercial activity history
Aprovechar censos de locales/actividades actuales e históricos para churn, aperturas/cierres, intensidad y evolución.

## D-148 — Machine-readable Feature Dictionary
Cada feature tendrá definición canónica YAML/JSON y documentación Markdown derivada/sincronizada.

## D-149 — Feature quality gate
Una feature no entra a producción sin contrato, tests, lineage, confidence, versionado y utilidad definida.

## D-150 — Mid-market developer first GTM
La punta de lanza comercial será promotora/inmobiliaria mediana por accesibilidad comercial y ciclo de venta razonable.

## D-151 — Sell analysis before full SaaS
Antes de completar PRO, monetizar estudios e informes apoyados por la plataforma.

## D-152 — PRO integrated workspace
PRO combina mapa, chat, análisis, escenarios, exportes e informes.

## D-153 — Dual entry: site-first or thesis-first
Una promotora puede empezar por “tengo esta parcela” o “quiero construir este producto”.

## D-154 — Conversational Opportunity Finder
Permitir búsqueda territorial desde tesis de inversión/producto mediante lenguaje natural.

## D-155 — Residential vertical extensibility
El core debe soportar BTR, senior, student, accessible, family/public housing y otras verticales sin duplicar motor.

## D-156 — Project workspace
Cada activo/proyecto tendrá workspace con documentos, análisis, capas, escenarios y comentarios.

## D-157 — Tenant-isolated private data
CRM/leads/cartera/precios/absorción privados se aíslan por tenant.

## D-158 — Competitive benchmarking
Comparar proyectos con oferta comparable y posicionamiento cuando haya datos suficientes.

## D-159 — Price sensitivity engine
PRO podrá estimar cómo cambia demanda compatible según precio/renta objetivo.

## D-160 — Financial scenarios later
No posicionar el MVP como asesoramiento financiero. Añadir escenarios económicos cuando el cliente introduzca supuestos.

## D-161 — B2G same core
Administraciones usan el mismo motor con objetivos y UX específicos.

## D-162 — Tiered PRO pricing
Profesional individual, Business y Enterprise/B2G.

## D-163 — Consumer PLUS
Plan intermedio para particulares con más consultas, escenarios, alertas y análisis.

## D-164 — Useful FREE
La capa gratuita debe resolver el problema principal sin paywall artificial.

## D-165 — Editorial ad monetization only
Adsense limitado a páginas editoriales/SEO; no contaminar mapa/ranking.

## D-166 — Opt-in contextual monetization
Afiliación contextual separada del ranking y siempre opt-in.

## D-167 — Paid reports ladder
Ofrecer desde análisis rápidos hasta estudios de mayor profundidad/importe.

## D-168 — DATA as product
API/MCP con pricing por uso/volumen/SLA y límites según plan.

## D-169 — Residential Intelligence Infrastructure
La empresa se define como infraestructura de inteligencia residencial, no como portal inmobiliario.

## D-170 — Final-product-first development
Se intentará construir el producto final desde el inicio. DATAMAD no tendrá una arquitectura MVP separada.

## D-171 — Controlled scope cuts
Si falta tiempo, se desactivan capabilities mediante flags/fallbacks, manteniendo arquitectura final.

## D-172 — Capability tiering
Toda funcionalidad se clasifica por criticidad/valor/riesgo para ordenar implementación y posibles recortes.

## D-173 — No throwaway hackathon code
Evitar mocks/arquitecturas temporales que haya que desechar salvo prototipos estrictamente de investigación.


## D-174 — Trabajo previo permitido por las bases (2026-10-20)
Las bases oficiales DATAMAD 2026 (§6 "Proyectos preexistentes") permiten usar código, componentes e investigación previos si se identifican, siempre que la propuesta evolucione de forma sustancial entre el 7 y el 26 de noviembre. Se cierra `DATAMAD-PREWORK-01`. Se creará el tag git `pre-datamad` el 6 de noviembre y se declarará el trabajo previo en README y slides. Fuente: `09_datamad/24_bases_oficiales_2026.md`.

## D-175 — Google Maps / Gosom fuera del proyecto DATAMAD (2026-10-20)
`google_maps_scraped` queda `REJECTED`: los términos de Google prohíben la extracción automatizada y las bases (§6.3, §6.7, §16) excluyen datos obtenidos ilícitamente. POIs desde Ayuntamiento, Comunidad de Madrid y OpenStreetMap. Pendiente de Mariano: confirmar o permitir un benchmark privado fuera del repo. Ver `07_privacy_legal/source_reviews/google_maps_gosom.md`.

## D-176 — Entornos de base de datos (2026-10-20)
Docker local (Postgres 17 + PostGIS 3.6 + pgvector 0.8) para desarrollo, tests y CI. Proyecto Supabase free dedicado (`ilvbivfnqvfqslbbiuts`) como entorno remoto/demo, accesible por el MCP de proyecto `supabase-datamad`. Sin h3-pg en Supabase: H3 se calcula siempre en Python. El código solo cambia `DATABASE_URL`.

## D-177 — Toolchain (2026-10-20)
Python 3.12 con uv workspace (wheels geo en arm64), ruff, pyright (strict en `packages/contracts`), pytest + hypothesis, gitleaks con regla explícita para tokens `sbp_`. Node 24 con npm workspaces, Next.js 16, TypeScript 5.9 strict, ESLint 9, Vitest 5.

## D-178 — Imagen de base de datos propia (2026-10-20)
`postgis/postgis` no publica arm64. Se extiende `pgvector/pgvector:pg17` con `postgresql-17-postgis-3`. Extensiones en schema `extensions` (convención Supabase). CI construye la misma imagen en el job de integración.

## D-179 — Capa de datos (2026-10-20)
Nuevo paquete `packages/db` (SQLAlchemy 2 + GeoAlchemy2 + psycopg 3 + Alembic). Vocabularios como `text + CHECK` generados desde los `StrEnum` de `hi_contracts`, no como tipos ENUM de Postgres. Geometrías administrativas en EPSG:4326 y EPSG:25830.

## D-180 — Geografía canónica (2026-10-20)
Fuente estructural: `cm_secciones_censales` (portal de la Comunidad de Madrid, seccionado 2019, EPSG:25830). Municipios, distritos censales y los 131 barrios de Madrid capital se derivan por dissolve. Identificadores canónicos `ES.28.{MUN|DIS|BAR|SEC}.<código INE>`. El seccionado 2025 del INE entra como actualización declarada (DATA-008), no como sustituto.

## D-181 — Scorecard y curación (2026-10-20)
El criterio "ingestion difficulty" del doc 38 se almacena como `ingestion_ease` (5 = más fácil) para que todos los criterios tengan la misma dirección. Los borradores del harvester nunca son P0. La promoción a catálogo curado se hace con ficheros de curación versionados en `data/catalog/curation/`.

## D-182 — Candidatos fuera de git (2026-10-20)
`data/catalog/candidates/*.jsonl` (4–14 MB) se regeneran desde Bronze con `make catalog-harvest` y no se versionan. Sí se versionan manifests Bronze, informe, borradores y catálogo curado.

## D-183 — Idempotencia de pipelines (2026-10-20)
Un pipeline se omite solo si coinciden checksum de entrada y `parser_version` con la última versión válida. Mismo Bronze con código nuevo regenera Silver. Una ingesta que falla la calidad nunca sustituye a la última versión válida.

## D-184 — Integración en P0 (2026-10-20)
Trabajo en la rama `claude/sprint-p0` con CI en cada push. La integración en `main` la decide Mariano mediante PR.

## D-185 — Gosom descartado; POIs abiertos como alternativa (2026-10-20)
Mariano confirma el criterio: no usar nada que pueda dar problemas. Google Maps/Gosom queda REJECTED también como investigación dentro del repo. Se registran `overture_places` y `fsq_os_places` (licencias permisivas por registro) para cubrir negocios y servicios. Valoraciones y reseñas quedan fuera de alcance.

## D-186 — Protección de personas vulnerables en equipamientos (2026-10-22)
Del registro de centros de atención social solo se mapean servicios para mayores (residencias, centros de día y hogares/clubes). Pisos tutelados, viviendas comunitarias, albergues, centros de acogida de menores, centros para mujeres maltratadas y residencias para personas con enfermedad mental o discapacidad no entran en el producto aunque la fuente publique su ubicación. Del registro sanitario se excluyen las consultas privadas individuales (minimización). Nunca se guardan teléfonos, correos ni NIF. Reglas en `data/catalog/pipelines/*.yaml` y tests en `tests/data/test_catalog.py`.

## D-187 — Modelo de observaciones y pipelines declarativos (2026-10-22)
Las estadísticas oficiales se guardan como `metric_observation` (valor XOR motivo del vacío, dimensiones canónicas, territorio, periodo, versión de dataset). Cada dataset declara su pipeline en `data/catalog/pipelines/<dataset_id>.yaml` (`cm_stat_table`, `cm_postcode_concept`, `points_csv`); el código implementa cada tipo una vez sobre un orquestador común. Los equipamientos se guardan en `place_master` + `place_source_alias` con id canónico estable (uuid5).

## D-188 — Sincronización con Supabase (2026-10-22)
El entorno remoto se carga copiando tablas validadas desde la base local (`make supabase-sync PROFILE=demo|full`), no re-ejecutando pipelines. Perfil demo 77 MB y completo 276 MB, simulados con un rol sin superusuario. Pendiente solo la contraseña de la base de datos.

## D-189 — Features (2026-10-22)
Las features se calculan con métodos genéricos (`metric_value`, `metric_share`, `metric_weighted_mean`, `places_per_population`, `place_attribute_per_population`) parametrizados en su YAML. Ratios con denominador por debajo del umbral declarado se publican con confidence 0,5. Nacionalidad y sexo no pueden ser features (test que lo impide); se descartó `poblacion_extranjera_pct`.

## D-190 — search_path explícito (2026-10-22)
Migraciones y motor de la aplicación fijan `search_path TO public, extensions` al conectar; una base recién creada sin esa configuración rompía la migración (detectado al aislar el test de migraciones).

## D-191 — Licencia open source (2026-11-10)
Mariano elige Apache-2.0 para el código (`LICENSE`, texto canónico de apache.org) y CC BY 4.0 para la documentación y los metadatos del catálogo (`docs/LICENSE`). Los datos de terceros mantienen su licencia original por fuente. Cierra LEGAL-001.

## D-192 — Replan comprimido de la fase de competición (2026-11-10)
No hubo commits entre el 22 oct y el 10 nov, así que P2 y Sprint 1 quedaron sin hacer y el roadmap del doc 19 ya no cabe (unos 22 días de trabajo para 13 hasta el freeze del 23 nov). Se prioriza lo que más puntúa (datos CM 25 + impacto 25):
- 11–16 nov: PUBLIC core (CRTM GTFS, features por sección/H3, ScenarioState, affordability, Residential Fit baseline, mapa con chips/filtros, explicación y procedencia).
- 17–20 nov: Housing Gap municipal + API/MCP con 3–5 tools + demo desplegada.
- 21–22 nov: cut review. 23 nov: freeze. 24–25 nov: slides §8 y ensayos. 26 nov: entrega antes de las 14:00.
Quedan en CUT/LATER: PRO workspace, parcel analysis, ML/embeddings, timeline, 3D polish y HomeFit por URL. Si el PUBLIC core no está en verde el 16 nov, el Housing Gap pasa a YELLOW.
Hechos del mismo día: tag `pre-datamad` en `08cc526` (último commit anterior al 7 nov) y merge de PR #2 y #3 en `main`; el trabajo de competición sigue en `claude/sprint-1-public`.

## D-193 — Formulario de presentación antes del 20 nov (2026-11-10)
La organización comunicó el 9 nov (correo de madrid.datamad@urjc.es, recibido en la cuenta de inscripción de Mariano) que es imprescindible enviar el formulario de presentación antes del 20 nov para seguir en la selección: hasta 50 preseleccionados y 12 finalistas que presentan el 26 nov. Ajuste sobre D-192:
- Despliegue de la demo (OPS-001) adelantado al 17 nov.
- Repo público y formulario el 18 nov, con el 19 nov como límite real.
- El Housing Gap y las tools MCP pasan al 19–22 nov, sobre la demo ya publicada.
El formulario lo envía Mariano; Claude prepara el resumen y los enlaces.

## D-194 — Alcance de la demo: lista de lo que falta por zona (2026-11-10)
Mariano confirma el enfoque de su documento «Housing Intelligence — la idea» (31 oct):
- El diferenciador es la lista FALTA / JUSTO / CUBIERTO por zona, no el Housing Gap como recomendador de producto residencial.
- La vivienda entra como una fila más de la lista (tamaño de los hogares frente a superficie de las viviendas). El resto de filas: escuela infantil, colegio, centro de salud, mayores y farmacia.
- La clasificación se hace frente a la referencia regional, con confidence y con los proxies declarados.
- Empresas («qué abrir») queda solo en slides y API/MCP.
- Zonas verdes quedan fuera porque solo hay datos de Madrid capital.
- La necesidad declarada por usuarios se presenta como siguiente paso y nunca se simula.
Plan: `09_datamad/25_plan_competicion.md`.

## D-195 — Repo público (2026-11-10)
Mariano aprueba hacer público el repo en cuanto haya algo enseñable, como tarde el 18 nov (formulario). Antes se cumple el checklist del §7 del plan de competición. Ya están en verde secretos (gitleaks), tokens y licencias. Falta que Mariano acepte que el email de autor de los commits y `docs/` (estrategia) quedarán visibles; el historial no se reescribe.

## D-196 — Transporte nivel A: paradas y frecuencias desde los GTFS del CRTM (2026-11-10)
DATA-007. Los 6 GTFS del CRTM (metro, metro ligero, cercanías, EMT, autobuses urbanos e interurbanos) también están publicados en el Portal de Datos Abiertos de la Comunidad de Madrid, así que cuentan como datasets CM. Cada dataset lo enlaza con un recurso `role: cm_portal`.
- Cada parada, o estación cuando el feed declara `parent_station`, se guarda en `place_master` con `category=transport` y `subcategory=<modo>`. El servicio va en `attributes`: salidas al día, salidas por hora en punta, headway en punta de la línea más frecuente, primer y último servicio, líneas y accesibilidad declarada.
- El servicio se mide en un día de referencia: el martes mediano (por número de viajes activos) dentro de la vigencia del propio feed. El resultado depende solo del fichero, no del día en que se ejecuta. El GTFS de metro venció el 27-05-2026 y sigue siendo el último publicado; se usa y la calidad lo avisa (`feed_current`).
- La punta es de 07:00 a 09:00. La última parada de un viaje y las paradas sin subida no cuentan como salidas. Las salidas antes de las 04:00 se leen como servicio de la noche anterior. El headway es por línea y sentido; en cercanías, que no declara `direction_id`, es por línea con ambos sentidos (`headway_basis`).
- Las paradas sin servicio el día de referencia no se publican y se cuentan en la calidad: nunca se guardan como 0.
- `stop_times` solo vive en Bronze/Silver; la base de datos guarda unas 15.000 paradas agregadas.
- Particularidades de los feeds, declaradas y no ocultas: el `frequencies.txt` de EMT solo anota viajes que ya están listados uno a uno (`expand_frequencies: false`). En metro, 25 andenes de transbordo no declaran estación: se unen a la estación que está en el mismo punto y tiene el mismo nombre.
- El tiempo a polos de empleo (nivel B) queda en CORE-009.
