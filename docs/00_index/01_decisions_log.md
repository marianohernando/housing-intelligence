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

## D-197 — RLS en todas las tablas públicas, sin políticas (2026-11-11)
OPS-001. Supabase expone el schema `public` a los roles `anon` y `authenticated` a través de su Data API. Su advisor marcó las 14 tablas como críticas (`rls_disabled_in_public`): con la clave pública se podían leer **y modificar** filas.
- El producto no usa esa API: el frontend nunca accede a la base de datos y el backend se conecta como dueño de las tablas.
- La migración 0003 activa RLS en las 14 tablas sin crear ninguna política. Así la Data API no ve filas ni puede escribir. En Supabase, `postgres` tiene BYPASSRLS, y en local el dueño se salta RLS, así que la API, los pipelines y `make supabase-sync` siguen igual.
- Un test de migraciones falla si una tabla nueva de `public` no tiene RLS.
- Comprobado el 11 nov con datos cargados: la Data API devuelve `[]` con la clave publishable. El advisor solo deja el aviso informativo `rls_enabled_no_policy`, que es el estado buscado.
- Si un día se quiere exponer algo por la Data API, se hace con políticas explícitas de solo lectura y por tabla.

## D-198 — Repo público con el historial limpio (2026-11-11)
DATAMAD-PUBLIC-01; completa D-195. Mariano acepta que se vean el email de autor y `docs/`. Antes de publicar apareció un problema: los fixtures de equipamientos del 22 oct llevaban teléfonos, emails de contacto, NIF y titulares, copiados del portal CM. La licencia CC BY no cubre la protección de datos (bases §6.6 y §16).
- El repo original pasa a llamarse `housing-intelligence-archive`, privado y archivado, como prueba de fechas.
- En la misma URL se publica una copia cuyo historial reescrito solo cambia esos 3 ficheros. Se conservan las fechas y el tag `pre-datamad`, que ahora apunta a `cf39459`.
- `scripts/build_places_fixtures.py` redacta los datos de contacto, los NIF y los titulares.
- Evidencia y tabla de SHAs antiguos y nuevos: `evidence/gate-00/2026-11-11/`.

## D-199 — Nombre del producto: «Vida Fácil» (2026-11-11)
Mariano decide llamar al producto **«Vida Fácil»**, con el lema «Encuentra tu sitio en Madrid»: corto, en español y fácil de recordar para personas mayores. El repo sigue siendo `housing-intelligence`, y «Housing Intelligence» puede aparecer como plataforma o equipo en el pie.
- Nombres descartados:
  - «Madrid 360»: es la marca del Ayuntamiento y parecería un producto municipal.
  - «Madrid Mejor»: suena a eslogan político.
  - «Fix360»: está en inglés.
- La línea D comprobó el 11 nov en TMview y en búsqueda web que no choca con ninguna marca del sector vivienda.

## D-200 — Escala: municipios y distritos de Madrid capital (2026-11-11)
La región se muestra por municipios (179) y Madrid capital por sus 21 distritos, para que no sea un único bloque de 3,3 M habitantes. El buscador y la lista de lo que falta funcionan en los dos niveles. La geometría y los nombres de los 21 distritos ya están en `geo_admin_unit` (nivel `distrito`, códigos 2807901–2807921). La población por edad y los hogares por distrito llegan con DATA-012, que va antes de GAP-001.

## D-201 — Mapa y estilo (2026-11-11)
- **Mapa:** 2D en la vista general. Al entrar en una zona, la cámara se inclina y muestra en 3D edificios, parques y puntos clave.
- **Estilo:** modo claro, navy + violeta + tarjetas de cristal, según el brief `DISENO_VIDA_FACIL.md` y sus dos mockups. Las slides siguen este estilo, no el del PDF del 31 oct.

## D-202 — Encaje en % con hechos tangibles (2026-11-11)
El buscador da un **% de encaje** y, debajo, 3–5 hechos tangibles con su nivel de confianza (por ejemplo, «colegio a 6 min andando»). Nunca notas sobre 100 ni barras. Los hechos siempre se pueden trazar a un indicador y a sus datasets.

## D-203 — Presupuesto de alquiler o de compra (2026-11-11)
El presupuesto puede ser de alquiler (€/mes) o de compra (€). La compra va con confianza baja y con la cobertura declarada. Si no hay una fuente oficial abierta y fiable (DATA-021), la compra queda como SIN DATOS y la web lo explica.

## D-204 — Prioridades del buscador (2026-11-11)
«Me importa»: transporte, salud, colegios, zonas verdes, seguridad y «sin escaleras». «Sin escaleras» es una necesidad funcional opcional, nunca una etiqueta de discapacidad (CLAUDE.md §13). La seguridad solo cuenta si la persona la marca como prioridad.

## D-205 — Extras: zonas verdes, accesibilidad física y seguridad (2026-11-11)
- **Fuentes:** el Ayuntamiento de Madrid y OpenStreetMap (ODbL, con atribución). Son datos complementarios: no cuentan como datos CM, pero suman impacto. Sin fotos de zona.
- **Seguridad (DATA-020):**
  - solo datos oficiales agregados (actuaciones de la Policía Municipal por distrito, por cada 1.000 habitantes);
  - nunca nacionalidad ni otras características de personas, por lo que los datos de «delitos» del portal CM quedan descartados;
  - nunca etiquetas como «peligroso»;
  - fuera de Madrid capital, SIN DATOS salvo una fuente oficial equivalente.
- **Accesibilidad física (DATA-019):** instalaciones accesibles del Ayuntamiento y `wheelchair_boarding` del GTFS de metro y cercanías; el resto, SIN DATOS.
- **Zonas verdes (DATA-018):** inventario del Ayuntamiento en Madrid capital y parques de OSM en el resto.

## D-206 — Orden: núcleo antes que extras (2026-11-11)
Para el formulario del 18 nov va primero el núcleo: el buscador, la lista de lo que falta y el 3D de zona. Los extras (D-205) y el precio de compra (DATA-021) entran del 19 al 22 nov, salvo que la línea A vaya adelantada. El trabajo se reparte en cuatro líneas paralelas según `prompts/LINEAS.md`: A (datos, motor, API e integración), B (web), C (despliegue) y D (formulario y pitch).

## D-207 — Contratos PUBLIC v2 (2026-11-11)
Aplica D-200 a D-204 en `packages/contracts/src/hi_contracts/public/`. La v1 (`7541527`) no llegó a usarse.
- **`ScenarioState` v2:**
  - `budget` con tipo alquiler o compra;
  - hogar con adultos, menores y mayores a cargo;
  - las 6 prioridades;
  - `zone_level` desaparece, porque el buscador siempre usa municipios + distritos de Madrid.
- **`SearchResult` v2:**
  - `match_pct` y `facts` (con `topic` para el icono y `confidence`);
  - `gap_highlights` (3 filas de «Qué falta aquí»);
  - `all_zones` para la coropleta;
  - `relaxed_scenario` en cada opción del Reality Check, para aplicarla con un toque.
- **Rutas:**
  - `GET /api/v1/gaps/{level}/{code}` acepta `distrito`;
  - nueva `GET /api/v1/datasets?cm_only=` para el contador y la procedencia;
  - CORS con `POST`.

## D-208 — Rol de solo lectura para la API pública (2026-11-11)
OPS-001; amplía D-197. La API de la demo se conecta a Supabase como `vf_api_ro` (migración 0005, a partir del SQL de la línea C en `infra/deploy/sql/api_readonly_role.sql`).
- **Permisos del rol:**
  - solo lectura por defecto (`default_transaction_read_only`) y por privilegios: solo tiene `SELECT`;
  - sin superusuario, sin `BYPASSRLS` y sin contraseña en el repo. Mariano la pone a mano (`ALTER ROLE vf_api_ro PASSWORD …`) y solo la usa en la `DATABASE_URL` del alojamiento.
- **Políticas:**
  - cada tabla que lee la API tiene una política `vf_api_ro_read` (`FOR SELECT`, solo para ese rol): `dataset_registry`, `dataset_version`, `feature_registry`, `feature_value`, `geo_admin_unit`, `place_master` y `source_registry`;
  - `anon` y `authenticated` siguen sin ninguna política, así que la Data API de Supabase sigue cerrada;
  - el advisor ya no avisará `rls_enabled_no_policy` en esas 7 tablas, y no es un problema.
- **Tests que lo vigilan:**
  - un test unitario falla si la API empieza a leer una tabla que no esté en `API_TABLES`, porque esa tabla se vería vacía en producción;
  - un test de integración comprueba que el rol lee esas tablas, no ve las demás y no puede escribir.
- **Downgrade:** quita permisos y políticas, pero conserva el rol, porque los roles son de todo el servidor.

## D-209 — Población por distrito de Madrid desde el padrón municipal (2026-11-11)
DATA-012; aplica D-200. La CM no publica la población por distrito de Madrid: `cm_distritos_madrid` solo trae superficie y densidad, y sus «Zonas Estadísticas» no son distritos.
- **Fuente:** padrón municipal del Ayuntamiento (`ayto_padron_municipal`, datos.madrid.es, CC BY 4.0). Trae una fila por sección censal y edad, con 4 recuentos (españoles y extranjeros, hombres y mujeres). Se usa el último mes publicado; la carga del 11 nov es del 1 oct 2026.
- **Qué se guarda:** la métrica `poblacion_padron` por distrito, con las **mismas bandas quinquenales que `poblacion_censada` de la CM** más el total. Así, los filtros de edad de las features valen para los dos niveles sin traducción.
  - El padrón es un registro exhaustivo: una edad sin filas en un distrito es 0 personas, y se publica como 0. Una fila que no se puede leer va a cuarentena y nunca cuenta como 0.
  - Solo se guarda la suma de los 4 recuentos. La nacionalidad y el sexo nunca se guardan (D-189, D-205).
- **Comparabilidad:** el total de Madrid en el padrón es un 1,68 % mayor que el del censo anual de la CM (3.535.868 frente a 3.477.497 a 1 ene 2025), por fecha y por método. No se calibra: se publica tal cual y se declara en las features. La calidad compara los dos totales en cada carga y avisa si la diferencia pasa del 5 %, sin bloquear.
- **Calidad bloqueante:** los 21 distritos tienen que estar y resolver en `geo_admin_unit`. Un fichero incompleto no sustituye a la última versión válida.
- **Procedencia:** es un dato complementario, no CM (`is_cm_open_data=false`), y la procedencia de cada fila lo muestra. El test del catálogo que exige que las estadísticas vengan de la CM admite esta excepción explícita y ninguna más.
- **Hogares por distrito** (DATA-012 Fase 3): salen del panel de indicadores de distritos y barrios del Ayuntamiento (`ayto_panel_indicadores_distritos_barrios`, CC BY 4.0, complementario y no CM).
  - Se guardan el total de hogares y el tamaño medio del hogar que publica el Ayuntamiento, a 1 de enero de cada año del panel (2019–2025).
  - Son hogares del padrón (personas inscritas en una misma vivienda), no el hogar del censo 2021 de la CM.
  - En los distritos, `tamano_medio_hogar` toma la media publicada, sin recalcularla. En los municipios sigue la del censo.
  - La fila de vivienda de GAP-001 queda SIN DATOS por distrito mientras no haya superficie de las viviendas por distrito.

## D-210 — Distancia a pie: velocidad, ventanas, destinos y calles de origen (2026-11-11)
CORE-005, Fases 3 y 4. Doce features por sección censal, municipio y distrito, más la referencia regional. Son 6 destinos con dos medidas cada uno:
- la mediana de minutos hasta el más cercano;
- el % de calle a N minutos o menos.

Datos: la red peatonal de OSM (`osm_red_peatonal`, ODbL, complementaria) y los registros de la CM para los destinos.
- **Velocidad: 4,5 km/h (1,25 m/s) para todo el mundo.** Sustituida por D-211: 4 km/h.
  - La guía de la FHWA de EE. UU. recomienda 1,2 m/s para la mayoría de los casos y 1,0 m/s donde más del 20 % son mayores de 65 (https://www.fhwa.dot.gov/publications/research/safety/pedbike/98107/section2.cfm).
  - El estudio «El Madrid de los 15 minutos» del Ayuntamiento usa 4 km/h (https://geoportal.madrid.es/fsdescargas/IDEAM_WBGEOPORTAL/GEOPORTAL/Jornada/2022/SALA5_1130_PROXIMIDAD_POR_CALCULODEREDES.pdf).
  - 4,5 km/h es un paso adulto tranquilo y la parte alta para personas mayores, y se declara en cada feature. A 4 km/h los minutos salen un 12,5 % más altos y a 3,6 km/h, un 25 % más.
  - Una velocidad para movilidad reducida entra con la accesibilidad física, opcional (D-205, del 19 al 22 nov), sin cambiar este cálculo.
- **Ventanas del %:** transporte 5 min (unos 375 m), centro de salud 15 min y el resto 10 min.
- **Destinos** (por subcategoría del registro, en el YAML de cada feature):
  - escuela infantil: pública y privada, de 0 a 3 años;
  - colegio con primaria: público o concertado;
  - centro de salud o consultorio de atención primaria;
  - farmacia;
  - centro de mayores: hogares, clubes y centros de día (las residencias no son destino a pie);
  - cualquier parada de autobús, metro, metro ligero o cercanías, sin mirar la frecuencia, que llega con CORE-009.
- **Origen: las calles donde vive la gente,** aproximadas por el tipo de vía de OSM: residencial, de convivencia, sin clasificar, peatonal y terciaria.
  - Cada nodo pesa la mitad de la longitud de sus tramos y cae en la sección censal que lo contiene. El municipio y el distrito salen del código de la sección.
  - Es un proxy de dónde vive la gente, no la población. Pesa más donde hay más calle, como las urbanizaciones de baja densidad, y por eso la mediana regional (por ejemplo, 3,4 min a una parada) es más alta que la de la sección típica (2,1 min).
- **Cálculo:**
  - Un Dijkstra multiorigen por tipo de destino sobre la componente principal de la red. Cada destino se une a ella por su nodo más cercano, en línea recta.
  - Por zona se calculan la mediana de minutos ponderada por la longitud de calle y el % de esa calle a N minutos o menos. Las dos medidas son coherentes por construcción: la mediana está dentro de la ventana si y solo si lo está la mitad de la calle o más.
- **Sin datos y desconocido, nunca 0:**
  - una zona sin calles de origen en OSM es `SOURCE_NO_COVERAGE`. Pasa en 24 secciones urbanas pequeñas (0,01–0,13 km²), 15 de ellas en Moratalaz y Villa de Vallecas. Ahí las viviendas dan seguramente a vías que OSM no marca como calle de origen (peatonales o de servicio). Una mejora posible: usar en esas secciones cualquier vía transitable como origen, declarándolo;
  - una zona cuyas calles no llegan a ningún destino es `UNKNOWN`.
- **Confianza:** la parte de la calle de la zona que conecta con la red. Si la zona tiene menos de 300 m de calle de origen, 0,5 como máximo.
- **Niveles:** el H3 r9 queda para cuando lo pida la vista 3D de la zona (CORE-005b). Serían unas 300.000 filas más en `feature_value`, que se copia entera a Supabase.
- **Comprobación (Gate 3):**
  - 15 casos golden con límites razonados, por ejemplo: Sol tiene farmacia a 5 min o menos, y La Acebeda no tiene ninguna farmacia en el registro (97,5 min a la más cercana) pero sí consultorio (12,7 min);
  - la coherencia entre mediana y % en las 4.819 zonas con valor de cada destino;
  - la cobertura de las 4.843 zonas.
  - El cálculo completo de las 24 features tarda 29 s y ocupa 0,9 GB de memoria.

## D-211 — Distancia a pie a 4 km/h (2026-11-11)
CORE-005, Fase 5. Sustituye la velocidad de D-210; el resto de D-210 (ventanas, destinos, calles de origen, cálculo, nulos y confianza) no cambia.
- **Velocidad: 4 km/h (1,11 m/s) para todo el mundo**, en lugar de 4,5 km/h. Decisión de Mariano: la demo también se dirige a personas mayores.
  - Fuente: el estudio «El Madrid de los 15 minutos» del Ayuntamiento («Velocidad de desplazamiento estimada en 4 Km/h»), https://geoportal.madrid.es/fsdescargas/IDEAM_WBGEOPORTAL/GEOPORTAL/Jornada/2022/SALA5_1130_PROXIMIDAD_POR_CALCULODEREDES.pdf. Así las cifras se pueden comparar con las del Ayuntamiento.
  - Referencia: 1,11 m/s queda entre los 1,2 m/s que la FHWA de EE. UU. recomienda para la mayoría de los casos y los 1,0 m/s que recomienda donde más del 20 % son mayores de 65 (https://www.fhwa.dot.gov/publications/research/safety/pedbike/98107/section2.cfm). No se afirma que sea la velocidad de las personas mayores: con movilidad reducida los minutos son más, y la feature lo declara.
- **Efecto:** los minutos suben un 12,5 % (×1,125) y las ventanas del % cubren menos calle: 5 min son unos 333 m (antes 375), 10 min unos 667 m y 15 min unos 1.000 m.
- **Versión:** las 12 features a pie pasan a la versión 2 (`feature_version` en cada fila).
- **Comprobación (Gate 3), con el recálculo real:**
  - los 15 casos golden de D-210 cumplen sus límites sin tocarlos. Los más justos: Sol a una parada, 3,1 min (límite 4), y el centro de Madrid a un centro de salud, 6,9 min (límite 10). La Acebeda: farmacia a 109,7 min y consultorio a 14,3 min (límite 20);
  - la coherencia entre mediana y % sigue sin desacuerdos en las 4.819 zonas con valor de cada destino;
  - por ejemplo, Chamartín (distrito 2807905): centro de salud 9,5 min (antes 8,4) y farmacia 2,6 min (antes 2,3). La mediana regional a una parada pasa de 3,4 a 3,8 min y la de la sección típica, de 2,1 a 2,4 min.

## D-212 — Nombres oficiales de municipios y distritos (2026-11-11)
DATA-022 y los nombres con la Ñ rota que pidió B. El CSV de nombres de `cm_secciones_censales` escribe «/» o el byte 0xD0 donde va la Ñ («REDUE/A», «GRIÐON», «PI/UECAR-GANDULLAS») y no lleva tildes («VICALVARO»). No es un problema de encoding: el carácter se perdió en la fuente.
- **Fuente de los nombres publicados:**
  - los 179 municipios, de la tabla estadística de la CM `cm_poblacion_edad_nacionalidad_sexo` (columna `Territorio`, última versión válida): «Griñón», «Redueña», «Álamo (El)»;
  - los 21 distritos de Madrid, del panel de indicadores del Ayuntamiento (`ayto_panel_indicadores_distritos_barrios`): «Vicálvaro». La CM no publica tablas por distrito de Madrid (D-209);
  - los distritos censales del resto de municipios se llaman «<municipio> — distrito censal NN», con el nombre oficial del municipio;
  - los barrios de Madrid siguen con el nombre de `cm_barrios_madrid`, que ya trae la Ñ (a algunos les faltan tildes, como «Las Aguilas»; queda anotado).
- **Cómo:** un paso aparte, `hi-ingest admin-names` (`make admin-names`, y al final de `run-all`), porque la geografía se publica antes que las tablas que traen los nombres. Solo cambia `geo_admin_unit.name`: la geometría y los códigos no se tocan. La ejecución queda en `ingestion_run` con las versiones usadas, y la evidencia guarda cada cambio.
- **Calidad bloqueante:** cada municipio y cada distrito de Madrid tiene un nombre oficial y solo uno, y ningún nombre publicado lleva caracteres fuera de la ortografía española (falla con «/», «Ð» o un byte sin decodificar). Si falla, no se cambia ningún nombre.
- **Presentación:** `display_name` pone delante el artículo que las tablas de la CM escriben detrás: «Álamo (El)» se muestra «El Álamo». La API lo aplica en `/gaps`, `/geo/admin-units` y `/features`.

## D-213 — Lista de lo que falta: referencia por tipo de territorio y cortes con prueba estadística (2026-11-11)
GAP-001, Fase 5. Sustituye los cortes provisionales de `gap-0.1` (ratio frente a la región: FALTA < 0,8 ≤ JUSTO < 1,0 ≤ CUBIERTO). Método `gap-0.2`, en `hi_domain/gaps.py` y `hi_api/services/gap_reference.py`; la API lo publica en `method`. **Aprobada por Mariano el 11 nov** (a través de `datamad-10`): referencia por tipo de municipio, FALTA solo si la diferencia es clara y no se explica por el tamaño, y «poco fiable» en zonas pequeñas. Refina la decisión cerrada «frente a la referencia regional por población»: sigue siendo una tasa de la región por población, pero de las zonas comparables.

**Problemas de `gap-0.1`, medidos con los datos reales del 11 nov:**
- La tasa de casi todas las filas depende del tipo de territorio. Ejemplo: cada pueblo tiene su consultorio, así que los municipios rurales tienen 14,8 veces más centros de atención primaria por habitante que los urbanos. La media regional (0,59 por 10.000) quedaba por encima de cualquier zona urbana: los 21 distritos de Madrid salían FALTA o JUSTO y ninguno CUBIERTO.
- Una zona pequeña salía FALTA por no tener un servicio que, por su tamaño, ni siquiera se espera que tenga. Ejemplo: un pueblo de 500 habitantes sin farmacia, cuando la región tiene 4,2 por cada 10.000.
- Una zona pequeña podía dar cifras extremas. B señaló La Acebeda, con 10.700 viviendas grandes por cada 100 hogares grandes. Faltaba una regla común para los denominadores pequeños.

**Decisión** (igual para las 6 filas, sin ajustar a ninguna zona concreta):
1. **Referencia: los demás municipios del mismo tipo de la Comunidad de Madrid.**
   - **Tipo:** la definición legal de medio rural de la Ley 45/2007, de desarrollo sostenible del medio rural (art. 3.a): menos de 30.000 habitantes y menos de 100 habitantes por km². Con la población del censo de la CM y la superficie de la geografía canónica salen 84 municipios rurales (143.000 habitantes) y 95 urbanos.
   - **Herencia:** un distrito o una sección toma el tipo de su municipio. Los distritos de Madrid son urbanos.
   - **Cálculo:** la tasa de referencia es la suma de los recuentos de los municipios del tipo dividida por la suma de sus poblaciones, **sin el municipio de la propia zona**. Un distrito o una sección dejan fuera su municipio entero. Madrid es la mitad de la población urbana y no puede compararse consigo mismo. Equivale a la estandarización indirecta: los casos esperados de una zona son su población por esa tasa.
   - **Contexto:** la región entera sigue apareciendo en `regional_reference` y en la explicación («… en los demás municipios urbanos de la Comunidad de Madrid, 0,56 (en toda la Comunidad, 0,59)»).
   - **Procedencia:** las filas citan también la población del censo y la geografía, que fijan el tipo.
   - **Justificación:** una prueba de homogeneidad (χ², 1 gl) de la tasa entre rural y urbano, fila por fila. Todas las filas la rechazan al 5 %:

     | Fila | Tasa rural / urbana | χ² | p |
     |---|---|---|---|
     | Escuela infantil | 2,70 | 64,9 | 8·10⁻¹⁶ |
     | Colegio | 1,81 | 16,0 | 6·10⁻⁵ |
     | Centro de salud | 14,82 | 968,8 | 10⁻²¹² |
     | Mayores | 2,86 | 33,2 | 8·10⁻⁹ |
     | Farmacia | 1,27 | 4,3 | 0,039 |
     | Vivienda | 2,52 | 49.523 | < 10⁻³⁰⁰ |

2. **Cortes:**
   - **CUBIERTO:** ratio ≥ 1, es decir, igual o por encima de la referencia.
   - **FALTA:** la falta tiene que ser grande y no deberse al azar del tamaño de la zona. Hacen falta dos condiciones:
     - **material:** ratio < 0,8. Es la regla de los cuatro quintos, que se usa para decidir cuándo una tasa es sustancialmente menor que la de referencia (29 CFR 1607.4(D)). El corte no cambia respecto a `gap-0.1`;
     - **significativa:** el límite superior del intervalo de confianza exacto de Poisson de la zona (Garwood, bilateral al 95 %; equivale a una prueba unilateral al 2,5 %) queda por debajo de los casos esperados. Es el criterio de «peor que la referencia» de los indicadores de salud pública inglesa (Fingertips) y de los gráficos en embudo (Spiegelhalter, 2005).
   - **JUSTO:** el resto de valores conocidos. **SIN DATOS** sigue siendo solo un valor desconocido.
3. **Zonas demasiado pequeñas (respuesta a B):**
   - **Regla:** una zona es «poco fiable» en una fila (`reliable: false`) cuando sus casos esperados son menos de 3,69. Es el límite superior al 95 % de un recuento de cero: por debajo, ni siquiera no tener ninguno sería una falta significativa.
   - El umbral sale de la propia prueba, no de un tope arbitrario, y es el mismo en todas las filas.
   - Una zona poco fiable nunca sale FALTA y conserva su valor. La API la marca; **la web aún no la muestra** (pendiente de B: «poco fiable»).
   - `reliable` es `true` también cuando la prueba no se aplica (fila sin recuentos o de «menos es mejor»).
   - **La Acebeda en vivienda:** espera 4,3 viviendas grandes y tiene unas 107 por cada hogar grande. El dato es fiable y sale CUBIERTO. La cifra de 10.700 es real: la produce un denominador de un hogar. Mejor mostrarla como «más de 10 veces la referencia».
   - La confidence de los features (umbrales de población pequeña) no cambia: mide la calidad del dato, no la prueba.
4. **Recuentos:** las features por población guardan en `inputs.counts` el numerador y el denominador de cada fila (`places_per_population`, `metric_ratio` y `place_attribute_per_population`; la clasificación solo usa los de las filas principales). Los valores no cambian, así que la versión de las features tampoco, pero los recuentos solo existen tras recalcular las features (`make features`) y sincronizar Supabase.
   - **Comparación con la región entera:** si la región no tiene recuentos o el tipo se queda sin casos. Entonces la comparación es con la región entera y decide solo el ratio. Una zona concreta sin recuentos se compara con su tipo, también solo por el ratio.
5. **Límites declarados:**
   - **Modelo de Poisson:** encaja con recuentos de centros sobre una población.
   - **Vivienda** (viviendas grandes sobre hogares grandes) es un cociente de dos recuentos grandes. La prueba casi siempre sale significativa, así que en esa fila decide en la práctica el corte de 0,8. No se modela la sobredispersión.
   - Contar centros no es contar plazas (`proxy_note`).
   - El tipo se asigna por municipio y la superficie sale de la geometría de 2019.
   - Los casos esperados de un distrito usan el padrón (D-209) con una tasa calculada con el censo de la CM.
   - En `metric_ratio`, la región suma también el numerador de los municipios con denominador 0, y las sumas por tipo no lo hacen. El efecto es despreciable.

**Efecto con los datos del 11 nov** (`evidence/gate-04/2026-11-11/phase-gap001-f5.txt`):
- **Por municipio (179):** FALTA pasa de 44, 65, 27, 90 y 94 a 0, 0, 5, 2 y 5 (escuela infantil, colegio, centro de salud, mayores y farmacia). Entre 116 y 161 municipios quedan poco fiables en esas filas. En vivienda, con recuentos grandes, FALTA sube de 8 a 25.
- **Por distrito de Madrid (21):** centro de salud pasa de 18 FALTA y 3 JUSTO a 21 JUSTO; ningún distrito por sí solo tiene una falta significativa. Escuela infantil: 4 FALTA (antes 8). Colegio: 1 FALTA (antes 4).
- **Casos de la demo:**
  - Chamartín (2807905), centro de salud: antes FALTA (0,79 frente a la región); ahora JUSTO (0,47 frente a 0,56 de los demás municipios urbanos, ratio 0,84);
  - Madrid capital: centro de salud FALTA (0,37 frente a 0,56, ratio 0,67, significativa) y colegio JUSTO (0,96);
  - La Acebeda: farmacia JUSTO y poco fiable (0 farmacias para 70 habitantes).
- **Lectura para el pitch:** FALTA pasa a ser una afirmación fuerte y rara: menos del 80 % de lo que tienen las zonas comparables, con datos suficientes para afirmarlo. Por ejemplo, Madrid capital tiene un tercio menos de centros de atención primaria por habitante que el resto de municipios urbanos, aunque ningún distrito por sí solo baste para afirmarlo.

## D-214 — Asequibilidad: m² supuestos por tamaño del hogar, alquiler por distrito y compra sin datos (2026-11-11)
CORE-006. Código en `hi_domain/affordability.py` y en el método `postcode_weighted_mean` de `hi_features`. Responde a la línea D, que pidió qué m² se suponen según el tamaño del hogar. Es una decisión reversible: cambiar la tabla no toca ningún contrato.

1. **Coste estimado.** El alquiler de una zona es su alquiler medio por m² (feature `alquiler_m2_mensual`) multiplicado por los m² que necesita el hogar. La condición de presupuesto es:
   - **PASS** si ese coste es igual o menor que el presupuesto;
   - **FAIL** si lo supera;
   - **UNKNOWN** si la zona no tiene alquiler publicado. Nunca cuenta como PASS.
2. **m² supuestos por tamaño del hogar.** Si la persona no los fija (`min_floor_area_m2`), se toman los de la vivienda mediana de los hogares de su tamaño en la Comunidad de Madrid:
   - **Fuente:** Censo de Población y Viviendas 2021 del INE, tabla 59524 («Viviendas familiares principales convencionales según tamaño del hogar por superficie»), fila de la Comunidad de Madrid. Son 2.532.510 hogares con superficie conocida.
   - **Cálculo:** mediana interpolada dentro de los tramos de superficie del INE. Las personas del hogar son adultos, menores y mayores a cargo.

     | Personas | 1 | 2 | 3 | 4 | 5 o más |
     |---|---|---|---|---|---|
     | m² supuestos | 61 | 68 | 71 | 77 | 77 |

   - **Por qué la mediana del censo:** es lo que ocupa de verdad la mitad de los hogares de ese tamaño en la región, con una fuente oficial. Una norma de habitabilidad daría mínimos legales, no lo habitual. Con 5 o más personas sale 76,7 m², casi lo mismo que con 4: las familias grandes no viven en pisos mucho mayores. Se fija en 77 para que los m² nunca bajen al crecer el hogar (lo comprueba un test).
3. **Límites declarados (el coste es orientativo y tiende a quedarse corto):**
   - **Contratos vigentes:** el alquiler por m² de la CM sale de la Estadística de viviendas declaradas en el IRPF de la Agencia Tributaria. Es la media de los contratos vigentes, no de los anuncios, y un contrato nuevo suele costar más.
   - **m² de distinta base:** los m² de esa estadística son los del Catastro, que solo tiene superficie construida. El INE estima la superficie útil del censo a partir de esa misma superficie construida, con una recta por el origen. Por eso el coste estimado corresponde a un piso algo menor que el mediano. El INE no publica el coeficiente, así que no se corrige.
   - **Qué FAIL es fiable:** como el coste es una cota baja, FAIL es una afirmación fiable. PASS conserva la confidence del dato y la explicación lo dice («media de los contratos vigentes; uno nuevo suele costar más»).
   - **Cobertura:** la fuente municipal solo publica los municipios de más de 20.000 habitantes con contratos suficientes (37 de 179). El resto queda UNKNOWN, nunca 0 ni estimado.
4. **Alquiler por distrito de Madrid** (versión 2 de `alquiler_m2_mensual`). Conecta `cm_alquiler_m2_codigo_postal_madrid`, el dataset CM número 21:
   - **Problema:** la tabla de la CM publica el alquiler por código postal (54 códigos de Madrid capital, 2024), y no hay geometría de códigos postales (DATA-013 está en el backlog).
   - **Proxy:** el alquiler de cada distrito es la media de sus códigos postales, ponderada por cuántos lugares geocodificados del distrito llevan ese código en su dirección: colegios, centros de salud y centros sociales de la CM (2.885 lugares de Madrid). Los lugares aproximan dónde vive la gente; se declara como proxy.
   - **Confidence:** 0,8 como máximo, multiplicada por la parte de ese peso cuyo código tiene alquiler publicado en el último periodo (2024). Los lugares sin código en la dirección no cuentan: la confidence no mide cuántos lugares sostienen la media. En Madrid son entre 51 y 242 por distrito, así que no hace falta un mínimo; si se extiende a otros municipios, habrá que fijarlo.
   - **Restricción:** solo cuentan los lugares del municipio de Madrid, porque la fuente solo publica sus códigos.
   - **Comprobación:** la media de los 21 distritos ponderada por población da 14,46 €/m², frente a los 15,10 publicados para Madrid. La cifra municipal pondera por viviendas alquiladas, que se concentran en el centro.
   - **Ejemplos:** Salamanca 19,8 €/m², Chamartín 18,0, Fuencarral-El Pardo 14,4 y Villaverde 10,8.
   - **Por qué la media y no la mediana ponderada** (como proponía el board): la fuente publica medias, y con 1 a 5 códigos por distrito una mediana saltaría de un código a otro.
5. **Compra.** Aún no hay una fuente oficial abierta y fiable de precio de compra por zona: DATA-021 entra del 19 al 22 nov (D-206). Mientras tanto, con `budget.kind = buy` la condición sale UNKNOWN en todas las zonas, con la explicación «Sin datos: aún no hay una fuente oficial abierta y fiable de precios de compra por zona». El buscador no inventa un precio.
   - **Candidatas para DATA-021:**
     - el valor tasado de vivienda libre del Ministerio de Vivienda (municipios de más de 25.000 habitantes);
     - el valor de referencia del Catastro que publica la CM para las viviendas arrendadas (municipios de más de 20.000 habitantes y códigos postales de Madrid).

## D-215 — Encaje residencial: condiciones, % de encaje y Reality Check (2026-11-11)
CORE-003. Método `fit-0.1`, en `hi_domain/fit.py`, `hi_domain/reality_check.py` y `hi_domain/search.py`, sobre los contratos v2 (D-202, D-207). Responde a la línea D, que pidió cómo se reparten los pesos y cómo se pasa a %. Es reversible: cambiar un peso o una curva solo cambia `methodology_version`.

1. **Zonas.** Los 178 municipios distintos de Madrid y los 21 distritos de Madrid capital (D-200): 199 zonas.
2. **Condiciones** (PASS, FAIL o UNKNOWN; UNKNOWN nunca cuenta como PASS):
   - **Presupuesto (`budget`):** según D-214.
   - **Servicio cerca obligatorio (`near:<servicio>`):** la mediana de los minutos a pie de las calles de la zona (CORE-005, 4 km/h) frente al máximo que pide la persona. Sin dato, UNKNOWN.
   - **Trayecto con límite (`commute:<i>`):** UNKNOWN en todas las zonas hasta que exista el tiempo en transporte público (CORE-009). La explicación da la distancia en línea recta. Si la persona pone un límite de minutos, ninguna zona pasa y el Reality Check propone quitarlo. Por eso, mientras tanto, la web debería enviar el trabajo sin límite (`max_minutes: null`), como preferencia.
3. **Criterios del % de encaje.** Van en este orden:
   1. las prioridades «Me importa», en el orden en que las marca la persona;
   2. cada lugar de trabajo o estudio;
   3. los servicios cerca que marca como deseables y que no están ya entre sus prioridades;
   4. el margen de presupuesto, si es de alquiler.
4. **Pesos por rango (rank sum):** con n criterios, el primero pesa n, el segundo n − 1 y el último 1, y se normalizan para sumar 1. Ejemplo con 5 criterios: 33 %, 27 %, 20 %, 13 % y 7 %. Es el método de pesos por orden más fácil de explicar: lo que marcas primero cuenta más.
5. **Utilidad de cada criterio** (de 0 a 1, curvas lineales con saturación, CLAUDE.md §14):
   - **Servicio a pie** (transporte → parada; salud → centro de salud; colegios → colegio con primaria): vale 1 hasta la ventana de D-210 y baja a 0 en el triple de esa ventana.
     - Ventanas: transporte 5 min, centro de salud 15 y los demás 10. Si la persona fija sus minutos, se usan los suyos.
     - Ejemplo: un colegio a 10 min vale 1, a 20 min vale 0,5 y a 30 min o más vale 0.
   - **Trabajo:** distancia en línea recta desde el centro de la zona. Vale 1 hasta 2 km (unos 30 min a pie) y 0 desde 20 km, que es más o menos el radio del municipio de Madrid más la primera corona. Es un proxy declarado, porque la distancia no es tiempo de trayecto, y lleva confidence 0,5. Es un parámetro de diseño: se sustituye por el tiempo real con CORE-009.
   - **Margen de presupuesto:** vale 1 si el coste es el 75 % del presupuesto o menos, y 0 si lo iguala.
   - **Zonas verdes, seguridad y «sin escaleras»:** aún sin datos (D-205, del 19 al 22 nov). Nunca puntúan como 0: salen como hecho «sin datos» y bajan la confidence.
6. **Paso a %:** media ponderada de las utilidades de los criterios con dato, por 100 y redondeada a la unidad (0,5 hacia arriba). El orden usa el valor sin redondear.
   - La confidence de la zona es la suma de peso × confidence de los criterios con dato, sobre el peso total. Así un criterio sin dato la baja.
   - Sin ningún criterio, una zona que cumple todo encaja al 100 %. Con criterios pero ninguno con dato, el % es desconocido (`null`), nunca 0.
7. **Resultado:**
   - **`results`:** las 10 mejores zonas con todas las condiciones en PASS, ordenadas por % de encaje, confidence y nombre.
   - **`near_misses`:** hasta 5 zonas que fallan exactamente una condición y cumplen las demás.
   - **`all_zones`:** las 199 zonas, para la coropleta.
   - **`facts`:** hasta 5 hechos tangibles por zona (3 o más cuando hay datos). Primero los criterios con dato, por orden de importancia para la persona, sean fortaleza o debilidad; si hay menos de 3, se completan con minutos a pie de contexto; los «sin datos» van al final.
   - **`gap_highlights`:** 3 filas de GAP-001 elegidas por el hogar: escuela infantil si hay menores de 3 años, colegio si hay menores, mayores si hay mayores a cargo, y después centro de salud, farmacia y vivienda.
8. **Reality Check:** para cada condición, cuántas zonas pasarían si solo esa se relajara, con las demás fijas:
   - **presupuesto de alquiler:** +10 %, redondeado hacia arriba a 50 €;
   - **presupuesto de compra:** quitarlo;
   - **servicio cerca:** +5 min, hasta 60; a partir de ahí pasa a ser preferencia;
   - **trayecto:** sin límite.

   `binding_constraint` es la condición que no se cumple (FAIL o UNKNOWN) en más zonas, digan lo que digan las demás. Con un límite de trayecto, que siempre es UNKNOWN, esa es la que gana. Relajar nunca quita zonas (test de propiedades).
9. **Caso demo con los datos del 11 nov** (`scripts/golden_search.py`, `evidence/gate-04/2026-11-11/phase-core003-f2.txt`): pareja con 2 hijos (4 y 8 años), 1.500 €/mes, colegio a 10 min como requisito, prioridades colegios, transporte y salud, y trabajo en la Castellana como preferencia.
   - **Recuento:** 32 de las 199 zonas cumplen todo y 15 quedan desconocidas (sin alquiler publicado o sin minutos a pie).
   - **Primera:** Ciudad Lineal, con un 99 %: colegio a 5 min, parada a 2 min, centro de salud a 11 min, a 3,2 km de Azca y unos 1.075 €/mes por 77 m².
   - **Siguientes:** Tetuán, Hortaleza y Moratalaz (97 %). Chamartín sale octava (95 %), porque sus 1.384 €/mes dejan poco margen.
   - **Reality Check:** la condición que más zonas quita es el colegio a 10 min. Con 5 min más aparecen 17 zonas, y con 150 € más, 1.
   - **Casi:** Salamanca, que falla solo por presupuesto (≈ 1.526 €/mes).
10. **Pendiente:**
   - diversificación y soluciones Pareto (§14): hoy el orden es solo por % de encaje;
   - tiempo de trayecto real (CORE-009);
   - ML/JEV.

## D-216 — Auditoría de equipamientos: clasificación, coordenadas y contrato de `/places` (2026-11-12)
Fase de prueba, T1 (decisión de Mariano del 12 nov: antes de los extras, comprobar que lo que enseña la demo es cierto y completo). Informe: `evidence/gate-01/2026-11-12/audit-places.md` (`scripts/audit_places.py`). Reversible: son filtros del catálogo y una categoría nueva.
1. **«Centro Polivalente» no son servicios para mayores.** Son los 1.001 «centros polivalentes» del registro de centros sanitarios (RD 1277/2003, tipo C.2.90): clínicas privadas de varias especialidades (97 % «Privado No Benéfico»; estética, fisioterapia, odontología…), sin nombre en el registro. Ni son atención primaria ni hospitales, y ninguna feature los usaba, pero llenaban la capa de salud (el 65 % de sus puntos). **Salen del registro de lugares**, con la misma regla de minimización que ya dejaba fuera las consultas privadas. Que fueran 1.001, como los servicios para mayores de DATA-009, era una coincidencia.
   - Efecto colateral: el alquiler por distrito (D-214) ponderaba los códigos postales también con esas clínicas, que se concentran en zonas comerciales. Sin ellas, el proxy se acerca más a donde vive la gente. Salamanca pasa de 19,8 a 19,0 €/m² y Chamartín de 18,0 a 17,9; Villaverde y Fuencarral-El Pardo apenas cambian. En el caso demo (D-215), Salamanca ya cabe en 1.500 €/mes y deja de ser «casi».
2. **Las farmacias son una categoría propia (`pharmacy`).** Eran `health` y salían en cualquier capa de salud. Migración 0006 (la comprobación de categorías admite `pharmacy`; al bajar, vuelven a `health`). Las features de farmacia cambian de categoría, no de valor ni de versión.
3. **Coordenadas que faltan o contradicen la dirección** (propuesta de D, revisión de 10 zonas):
   - **Cuándo:** solo en los registros sin coordenadas, fuera de los límites de Madrid o cuyas coordenadas caen en otro municipio que el declarado (o, en Madrid, en otro distrito que el declarado por el registro de centros educativos).
   - **Cómo:** la dirección del propio registro va al geocodificador oficial CartoCiudad (IGN, CC BY 4.0 scne.es), sin código postal (con él no responde). Solo se acepta un **portal** en el municipio declarado: el número exacto (confidence 0,8) o el portal conocido más cercano a 10 números o menos (0,6; unos 50–100 m). Sin número («S/N»), solo calle o en otro municipio → cuarentena.
   - Coordenadas en otro municipio sin dirección válida → cuarentena (nunca se publican en el sitio equivocado). Un distrito distinto es una prueba más débil: solo se mueve si la dirección cae en el distrito declarado; si no, se conserva y se anota.
   - Las respuestas se guardan en caché (`data/bronze/geocoding/`) y cada lugar lleva `attributes.coordinates` con el origen. Fuente registrada como `ign_cartociudad`.
   - **La calle también tiene que coincidir** (palabras del nombre sin artículos ni tildes): CartoCiudad puede devolver un portal de otra calle del mismo municipio (revisión con `reviewer`).
   - **Resultado:** 40 lugares geocodificados (educación 18, sanidad 4, mayores 13, farmacias 5): 36 que no tenían coordenadas y 4 reubicados. Entre ellos el colegio Humanitas El Cañaveral, dos centros de salud de Madrid, el consultorio de Gargantilla, la farmacia 763 (estaba en Valdemoro) y el CEIP Amorós (estaba en Tetuán). El consultorio CS12766 de Buitrago, con coordenadas en otro municipio, pasa a cuarentena: el geocodificador devuelve otra calle. Siguen en cuarentena 40 de educación, 6 de sanidad y 34 de mayores: «S/N», carreteras por kilómetro o direcciones que el geocodificador no encuentra. De los casos de D quedan sin resolver los centros de salud de Alcalá (2) y Madrid (2), con «S/N»; el consultorio de Villar del Olmo («calle Real 42» lleva a un pueblo de Jaén y se rechaza) y el CEIP de Navalafuente (el portal conocido más cercano es el 16 para el 56).
   - El CEIP Nuria Espert queda en Barajas: la dirección no contradice las coordenadas y la cartografía oficial (secciones del INE) lo pone en Barajas, aunque el registro diga Hortaleza.
4. **`/places` pasa a tener contrato** (`places-1`, `PlacesResponse`): titularidad pública, concertada o privada en los centros educativos, `gap_rows` (las filas de la lista de lo que falta que cuentan ese lugar, con los mismos filtros del Feature Dictionary), `capacity` cuando la fuente la publica por centro (hoy, las plazas autorizadas de mayores) y el origen y la confidence de las coordenadas. Lo pidió B para su T3.
5. **Base de población de Madrid (D6 de la revisión de D):** se mantiene lo declarado en D-209: el municipio con el censo de la CM y los distritos con el padrón (+1,7 %). En los cálculos que mezclan distritos y municipios (D-217) los distritos se escalan al total del censo para no contar dos veces esa diferencia.

## D-217 — La oferta se mide por capacidad y accesibilidad (2SFCA) y los municipios pequeños se comparan con sus vecinos (2026-11-12)
Fase de prueba, T2a y T2b. **Decisión de Mariano (12 nov):** la oferta de servicios se mide por capacidad y accesibilidad, no por número de centros. Método `gap-0.3`, que sustituye a `gap-0.2` en las cinco filas de servicios; vivienda no cambia. Código: `hi_domain/access/fca.py`, `hi_features/fca.py` (método `two_step_fca`), `hi_domain/gaps.py` (`pool_with_neighbours`) y `hi_api/services/gap_reference.py`. Evidencias: `evidence/gate-04/2026-11-12/gap-status-gap03.md` y `evidence/gate-03/2026-11-12/fca-sensitivity.md`. Refina D-213: la referencia sigue siendo la de los municipios del mismo tipo, con los mismos cortes y la misma prueba.

1. **Qué cambia.** Antes cada fila contaba centros por habitante del propio municipio o distrito: una clínica pesaba como La Paz, un consultorio de aldea como un centro de salud grande, y lo que había al otro lado de la frontera de un distrito no contaba. Ahora cada fila mide **la capacidad que la gente tiene al alcance a pie, compartida con quienes compiten por ella**.
2. **Método: 2SFCA** (Luo y Wang, 2003, «Measures of spatial accessibility to health care in a GIS environment», *Environment and Planning B* 30: 865–884).
   - Paso 1, por centro: su capacidad dividida por la gente que vive a 15 minutos a pie o menos.
   - Paso 2, por calle: la suma de esas cuotas de los centros a 15 minutos o menos.
   - Por zona: la media ponderada por población de sus calles, que es igual a la capacidad que le llega dividida por su población. La capacidad se conserva: en la región, el total es la capacidad alcanzable entre la población (test de propiedades).
   - **Captación: 15 minutos a 4 km/h (1 km por la red de calles),** la de «El Madrid de los 15 minutos» del Ayuntamiento, la misma fuente de D-211. Es binaria (dentro o fuera), la versión más fácil de explicar.
   - **Sensibilidad:** con 10 o 20 minutos, el orden de los municipios casi no cambia (Spearman 0,995–0,997; entre el 1 % y el 2 % se mueve más de 20 puestos).
   - **Red y personas:** la red peatonal y las calles de origen de D-210. La población de cada municipio (censo de la CM), y en Madrid la de cada distrito (padrón escalado al total del censo de Madrid, D-216 §5), se reparte entre sus calles en proporción a su longitud. Quien vive a más de 15 minutos de cualquier centro no suma oferta: la fila mide lo que se tiene cerca.
   - Cruza fronteras: un colegio en el límite de dos distritos sirve a los dos.
3. **Capacidad por fila: solo la publicada, nunca estimada por centro.**

   | Fila | Capacidad (S) | Demanda | Feature |
   |---|---|---|---|
   | Colegio | Aulas de primaria públicas y concertadas del municipio (`cm_unidades_escolares`, curso más reciente), repartidas a partes iguales entre sus colegios de esa titularidad: la estadística no las da por centro (confidence 0,8) | 5 a 14 años | `aulas_primaria_a_pie_por_1000_ninos` |
   | Escuela infantil | 1 por escuela: nadie publica plazas por centro | 0 a 4 años | `escuelas_infantiles_a_pie_por_1000_ninos` |
   | Centro de salud | 1 por centro de salud del SERMAS (equipo de atención primaria, 268). Los consultorios locales son puntos de consulta del mismo equipo: cuentan en los minutos a pie, no como capacidad | Total | `centros_salud_a_pie_por_10000_hab` |
   | Mayores | Plazas autorizadas de hogares, clubes y centros de día (registro de la CM) | 65 o más | `plazas_mayores_a_pie_por_100_mayores` |
   | Farmacia | 1 por farmacia (la ley de la CM las planifica por habitantes) | Total | `farmacias_a_pie_por_10000_hab` |

   - Las features anteriores (centros por habitante) siguen como indicadores extra de cada fila.
   - La fila de centro de salud cuenta un subconjunto de los destinos de sus minutos a pie; el invariante del catálogo lo admite solo en esa fila, declarado en el test.
   - Para la prueba de D-213 las features guardan la capacidad en **centros equivalentes** (capacidad entre la capacidad media por centro de la región). El ratio no cambia, y la prueba de Poisson cuenta centros, no aulas ni plazas, que van en bloques.
4. **Lo que no existe en abierto (T2a, comprobado el 12 nov):**
   - población asignada por tarjeta sanitaria y cupos de médicos por centro o por zona básica de salud;
   - camas por hospital en el portal de la CM. «Hospitales y datos asistenciales» y «Dotación de camas» solo traen el total regional: 85 hospitales y 20.776 camas instaladas en 2023, 3,00 por 1.000 habitantes. Se cargan como referencia (`cm_hospitales_datos_asistenciales` y `cm_dotacion_camas`, 11 métricas).
   - El Catálogo Nacional de Hospitales 2025 (Ministerio de Sanidad) sí publica camas por hospital (XLSX, reutilizable con cita), pero no si tiene urgencias. Queda propuesto como fuente complementaria para enseñar «Hospital La Paz · N camas» (siguiente paso, con resolución de entidades frente al registro de la CM).
   - La geometría de las zonas básicas de salud es abierta, pero de 2019 y con el padrón de 2019: no se usa para la capacidad. Solo sirve aquí para fijar el radio de §6.
5. **Hospitales:** no hay 2SFCA a pie, porque un hospital no se elige a 15 minutos andando. La fila de centro de salud gana como extra `min_a_pie_hospital`: los minutos a pie por la red hasta el hospital general más cercano, público o privado (60). Es un proxy de las urgencias 24 h, que ninguna fuente abierta marca, y se declara.
6. **Escala: los municipios pequeños se comparan con sus vecinos.**
   - El 2SFCA no crea información: en centros equivalentes, un pueblo pequeño sigue esperando menos de 3,69 casos y su estado sigue siendo poco fiable (D-213). Eso le pasaba a 140 de 179 municipios en colegios.
   - **Regla:** un municipio poco fiable se compara junto con sus vecinos más cercanos del mismo tipo (rural o urbano), que se añaden por orden de distancia hasta que el grupo espera 3,69 casos. Es el mismo umbral de D-213 y la referencia deja fuera a todo el grupo.
   - **Radio:** solo vecinos a 15 km o menos (entre los puntos interiores de los municipios). Las zonas básicas de salud rurales de la CM tienen un radio equivalente mediano de 7,7 km y una extensión mediana de 22,9 km (capa oficial de 2019, 15 zonas de menos de 100 hab./km²). Así el grupo es el entorno con el que ya se organizan los servicios de esos pueblos, no una comarca entera. Si con ese radio no se llega, el municipio sigue «poco fiable».
   - **Base:** filtros espaciales adaptativos con un mínimo de casos esperados (Talbot et al., 2000, *Statistics in Medicine* 19: 2399–2408).
   - El estado del grupo es el de la zona, con los mismos cortes y la misma prueba. La API lo marca en `comparison_group` (códigos, nombres y ratio del grupo) y lo explica en el texto de la fila. Los distritos de Madrid no se agrupan: casi nunca son pequeños.
7. **Efecto con los datos del 12 nov** (municipios, 179):
   - **Poco fiables:** escuela infantil de 138 a 37, colegio de 140 a 65, centro de salud de 167 a 96, mayores de 160 a 93 y farmacia de 116 a 18.
   - **FALTA:** escuela infantil 0, colegio 0, centro de salud 0, mayores 6 y farmacia 5 (antes 0, 0, 5, 2 y 5).
   - **Casos de la revisión de D:** M1, San Martín de Valdeiglesias, centro de salud: FALTA → CUBIERTO (1,59; poco fiable, sin vecinos suficientes a 15 km). M2: los consultorios ya no cuentan como capacidad. M3, La Acebeda: 0 a pie, poco fiable.
   - **Madrid capital, centro de salud:** FALTA (0,67) → **JUSTO (0,95)**. Al medir lo que se alcanza a pie, y no centros por habitante del propio municipio, Madrid queda cerca de los demás municipios urbanos. **La frase del pitch «Madrid tiene un tercio menos de centros de atención primaria por habitante» deja de valer.**
   - **Chamartín:** centro de salud CUBIERTO (1,17), colegio CUBIERTO (1,12) y mayores JUSTO (0,59).
8. **Contrato:** `GapMethod.version = gap-0.3`, `ComparisonGroup` y `comparison_group` en `GapRow` y `ZoneGapStatus` (opcional, compatible). Los distritos de las features 2SFCA son solo los 21 de Madrid (D-200). Fixtures regenerados con datos reales, con un ejemplo agrupado (`zone_gap_list.el_alamo`) y `places.colegios_chamartin` (`places-1`, D-216). El test de la web `gapMap.test.ts` lee ahora el estado de Centro del fixture en vez de fijarlo (cambio mínimo en `apps/web`, pedido por `datamad-10`).
9. **Límites declarados:**
   - captación binaria, sin decaimiento con la distancia (E2SFCA, Luo y Qi 2009, queda como mejora);
   - la población se coloca por longitud de calle, no por portal;
   - las aulas se reparten a partes iguales dentro de cada municipio y titularidad;
   - en un hogar o club las plazas autorizadas son aforo y en un centro de día, plazas de atención;
   - la distancia de los vecinos se mide en línea recta;
   - la proximidad a pie no es la única forma de acceso: en los pueblos, el coche y el autobús cuentan (CORE-009).

## D-218 — Nombre y camas de los hospitales desde el Catálogo Nacional de Hospitales (2026-11-12)
Petición de Mariano (12 nov): que se vea el tamaño de cada hospital, porque no es lo mismo una clínica que La Paz, y que los hospitales tengan su nombre en vez de «Hospital general (Madrid)». Reversible: es un directorio complementario y campos opcionales en `/places`. Código: `hi_ingestion/pipelines/directory/` (tipo de pipeline `facility_directory`), `hi_ingestion/pipelines/places/directory.py` (cruce) y `hi_domain/facilities.py`. Evidencia: `evidence/gate-01/2026-11-12/hospitales-cnh.md`.
1. **Fuente:** Catálogo Nacional de Hospitales 2025 del Ministerio de Sanidad (actualizado a 31 de diciembre de 2024), hoja «DIRECTORIO DE HOSPITALES», solo la provincia de Madrid (91 hospitales). El aviso legal del Ministerio autoriza la reutilización, también comercial, si no se desnaturaliza la información, se cita la fuente y se menciona la fecha de actualización. Se leen solo nombre, dirección, código postal, clase, dependencia y camas; nunca teléfono ni correo (D-186). Es fuente complementaria: el portal de la CM no publica camas por hospital (D-217 §4) y el registro de centros sanitarios de la CM sigue siendo la fuente de cada lugar, su tipo y su ubicación.
2. **Solo Silver.** El directorio no crea lugares. Tiene su propio Quality Gate (entre 80 y 120 filas en la región, códigos únicos, camas numéricas en al menos el 90 %, sin columnas de contacto) y el pipeline del registro de la CM lo lee en su última versión válida. Ese fichero entra en la suma de comprobación y en el linaje de la carga del registro: una edición nueva del catálogo vuelve a procesar el registro (test).
3. **Cruce (resolución de entidades).** No hay un código común (el registro de la CM usa su número, `CH0001`; el catálogo, `CODCNH`), así que se cruza por dirección postal con tres reglas, de la más fuerte a la más débil, siempre uno a uno:
   - `direccion` (1,0): mismo código postal, misma calle y el número del registro aparece en la dirección del catálogo;
   - `calle` (0,9): mismo código postal y calle, y es el único hospital de esa calle;
   - `codigo_postal` (0,7): el único hospital de la misma clase en ese código postal.

   «Único» se juzga entre todos los hospitales del código postal, también los ya cruzados: un lugar que el catálogo no tiene nunca hereda el que sobra en su código postal. La calle tiene que tener las mismas palabras (sin tipo de vía ni artículos: «Real» no es «Real de Pozuelo»), los puntos kilométricos y los códigos postales no cuentan como número de portal, y un hospital público nunca se cruza con uno privado (veto cuando las dos fuentes lo dicen). Un hospital del catálogo que reclaman dos lugares no va a ninguno, y lo que ya ha tomado una regla fuerte no se ofrece a una débil. Cada cruce se guarda como alias en `place_source_alias` (método y puntuación) y en `attributes.directory` del lugar. Reglas endurecidas tras la revisión con `reviewer` (parser `places-1.3.1`).
4. **Resultado con los datos del 12 nov:** 79 de los 85 hospitales del registro (64 por dirección, 13 por calle y 2 por código postal). Contraste independiente: antes de añadir el veto, los 79 cruces ya coincidían en público o privado (0 discrepancias), y con las reglas endurecidas salen los mismos 79 pares. Los 6 sin cruzar se declaran en el informe: CH0049 (el catálogo pone el Ramón y Cajal en la calle de Ayala, no en la carretera de Colmenar), CH0068, CH0120, CH0121 (Tres Cantos, sin hospital del catálogo en su código postal), CH0122 y CH0123 (el hospital de su código postal ya lo tomó otro registro por dirección). Conservan «Hospital general (Municipio)» y no muestran camas. Corregirlos a mano necesitaría un fichero de correcciones con fuente oficial por registro: es la misma decisión pendiente de Mariano que la de las coordenadas (board).
5. **Nombre:** el del catálogo tal como lo publica (sin corregir tildes: no se desnaturaliza). Se quita la forma jurídica («Clínica La Luz, S.L.» → «Clínica La Luz») y no se usa cuando el catálogo da una empresa o un operador en lugar del centro: un nombre válido dice qué es («hospital», «clínica», «sanatorio», «centro», «complejo», «instituto», «fundación»). Así quedan fuera «Servicio Madrileño de Salud», «HM Hospitales 1989, S.A.», «ID Dalud Móstoles Sa», «Alm Univass S.L.», «Casta Guadarrama» y «Fraternidad Muprespa, Mutua…» (6 lugares, que conservan el nombre genérico pero sí muestran camas). Son nombres de establecimientos, no de personas: ninguna consulta privada ni titular particular entra en el producto (D-186).
6. **Contrato `/places` (aditivo, sigue `places-1`):** en los hospitales cruzados, `capacity` = camas instaladas (`unit: "camas instaladas"`, `dataset_id: ms_catalogo_nacional_hospitales`) con dos campos opcionales nuevos: `dependency` (`publica` o `privada`, del registro de la CM; las mutuas colaboradoras cuentan como privadas porque solo atienden accidentes de trabajo de sus afiliados) y `kind` (el tipo del registro, p. ej. «Hospital general»). Ningún campo existente cambia ni desaparece. Hasta hoy ningún lugar de salud traía `capacity`; en los hospitales la unidad es «camas instaladas» (las del catálogo a 31/12/2024, no las de funcionamiento de un día concreto). Ejemplo: `data/fixtures/contracts/places.hospitales_madrid.fixture.json`.
7. **Lo que no se hace:** las camas no entran en la lista de lo que falta ni en un 2SFCA. Un hospital no se elige a 15 minutos andando (D-217 §5), y medir «camas alcanzables» exigiría una captación en coche o en transporte público que hoy no tenemos (CORE-009). Queda como posible extra con su propio ADR.
8. **Centros de salud y consultorios (fase 2, mismo método):** el registro de la CM no publica su nombre. Se cruzan con el Catálogo de Centros de Atención Primaria del SNS 2026 del Ministerio de Sanidad (actualizado a 31 de diciembre de 2025; 266 centros de salud y 154 consultorios locales del SERMAS en Madrid, todos de gestión pública directa), con las mismas reglas y el veto público/privado. El catálogo da un nombre de lugar («ABRANTES»), que se presenta con el tipo del registro y en mayúsculas normales: «Centro de salud Abrantes», «Consultorio local La Acebeda». Son nombres de centros públicos, nunca de personas (D-186). Lo que va entre paréntesis en la calle del registro («de la Paloma (El Vellón)») vale con y sin paréntesis. **Resultado:** 356 de los 423 centros de salud y consultorios del registro (278 por dirección, 55 por calle y 23 por código postal; 0 discrepancias público/privado). Los 67 sin cruzar (sobre todo, código postal distinto en las dos fuentes o dos registros de la CM en la misma dirección) conservan «Centro de salud (Municipio)». No hay capacidad: el catálogo no publica profesionales ni población asignada por centro (D-217 §4).
9. **Segunda pasada (HOSP-001 F3, notas de C desde producción):** cinco reglas en vez de tres, con el mismo principio (uno a uno, «único» entre todas las entradas, también las ya tomadas). Nuevas: `direccion_municipio` (0,85; mismo municipio, calle y número en otro código postal, porque las dos fuentes discrepan en los bordes de los distritos) y `municipio` (0,6; la única entrada del mismo tipo en el municipio, para pueblos que comparten código postal). Por debajo de la dirección completa (código postal, calle y número) el municipio y el tipo tienen que coincidir: Madarcos y Robregordo comparten código postal y «calle de las Eras», y un consultorio en Palma 54 no es el centro de salud de Palma 51. La dirección completa basta aunque el catálogo archive el centro en el municipio de su área de salud (Aravaca, en Madrid, figura en Pozuelo de Alarcón). Las calles se comparan con abreviaturas («Mª», «Ntra. Sra.»), singular y plural, esquinas, «bulevar», «callejón» y «carrera» como tipo de vía, el número pegado a «Nº» y la sustitución del catálogo de atención primaria, que escribe «CALLE» por cada «CL» y «AVENIDA» por cada «AV» también dentro de las palabras («SAN CALLEAUDIO», «ISLA DE JAVENIDAA»); el nombre publicado nunca se corrige. **Resultado:** centros de salud con nombre de 228 a 255 (genéricos de 44 a 17) y consultorios de 128 a 144 (de 23 a 7); ningún cruce anterior cambia de pareja y se pierden 3, explicados en la evidencia (Las Américas pasa del centro que solo compartía código postal al que tiene su dirección). Hospitales sin cambios: el Ramón y Cajal (CH0049, Fuencarral-El Pardo) sigue sin nombre ni camas porque el catálogo lo sitúa en la calle de Ayala 38 (28001) y el registro en la carretera de Colmenar Viejo, km 9,1; solo lo resolvería el fichero de correcciones con fuente oficial que sigue pendiente de Mariano (§4). El «Hospital especializado · 50 camas» de Chamartín (CH0113) es el de una mutua: el catálogo publica el nombre de la mutua, no el del centro, y por §5 no se usa. Evidencia: `evidence/gate-01/2026-11-12/nombres-segunda-pasada.md` (parser `places-1.5.3`; los directorios guardan el municipio de cada entrada con `directory-1.1.0`).

## D-219 — Conexiones de la API: pool por entorno y pooler de Supabase en modo transacción (2026-11-12)
Incidente del 12 nov (05:00): la vista de zona daba 500 intermitentes con «EMAXCONNSESSION max clients reached in session mode» (`pool_size: 15`). Cada instancia de Vercel abría el pool por defecto de SQLAlchemy (5 + 10) contra el pooler de Supabase en modo sesión (puerto 5432), que admite 15 clientes en total para todo el proyecto: con tres instancias ya no quedaban. Código: `packages/db/src/hi_db/session.py` y `settings.py`. Reversible: tres variables de entorno, con los valores por defecto de siempre.
1. **Pool por entorno (mitigación, `4645326`):** `DB_POOL_SIZE` y `DB_MAX_OVERFLOW` fijan el pool de cada proceso. Por defecto 5 y 10 (los de SQLAlchemy; validados ≥ 1 y ≥ 0). Producción usa 2 y 1.
2. **Modo transacción (arreglo de fondo):** la API pasa al pooler en modo transacción (puerto 6543), el que Supabase recomienda para funciones serverless que abren muchas conexiones cortas. En ese modo una conexión del servidor se presta solo durante una transacción, así que el límite deja de ser de 15 clientes.
3. **Sin prepared statements en ese modo:** el pooler compartido de Supabase no los admite en modo transacción («turn them off», guía de conexión de Supabase). psycopg 3 prepara solo una consulta cuando la ha ejecutado `prepare_threshold` veces en la misma conexión (5 por defecto) y los desactiva con `prepare_threshold=None` (documentación de psycopg 3.1+, «Prepared statements» y `Connection.connect`). `DB_PREPARED_STATEMENTS=false` pasa ese valor a `psycopg.connect()` por `connect_args`, que SQLAlchemy entrega tal cual al `connect()` del driver. Sin la variable, o con `true`, no se pasa nada y psycopg conserva su valor. Un valor que no sea booleano hace fallar el arranque. Comprobado en la base local: 1 prepared statement tras 8 ejecuciones de la misma consulta con el valor por defecto y 0 con `false` (test unitario `tests/unit/test_db_engine_prepared_statements.py`).
4. **Estado de sesión:** en modo transacción un `SET` de sesión no está garantizado entre transacciones. La API no lo necesita: el rol `vf_api_ro` (D-208, migración 0005) ya trae `search_path = public, extensions`, `default_transaction_read_only` y `statement_timeout` a nivel de rol, y cada conexión del servidor los toma al abrirse (comprobado por MCP en `pg_db_role_setting`). El `SET search_path` de `make_engine` queda como redundante y es inofensivo (pone el mismo valor). La API no usa tablas temporales, `LISTEN`, bloqueos consultivos ni cursores de servidor.
5. **Orden del cambio en producción:** primero `DB_PREPARED_STATEMENTS=false` en Vercel y redespliegue (funciona también en el puerto 5432); después Mariano cambia el puerto de `DATABASE_URL` a 6543, se redespliega y se pasa el smoke. Al revés, las consultas repetidas fallarían con «prepared statement … already exists» o «does not exist». El pool se queda en 2 + 1 hasta medirlo en modo transacción.
6. **Solo la API.** Las migraciones y el sync (`SUPABASE_DATABASE_URL`) siguen en el modo sesión: Alembic necesita estado de sesión (`.env.example`).
7. **Alternativas descartadas:**
   - `NullPool` (una conexión nueva por petición): resuelve el límite, pero suma a cada petición la apertura de TLS y el arranque de sesión con el pooler;
   - conexión directa a Postgres: solo IPv6, y Vercel sale por IPv4;
   - pooler dedicado (PgBouncer ≥ 1.21, que sí admite prepared statements): es de pago;
   - activar `prepare_threshold=None` al detectar el puerto 6543 en la URL: comportamiento oculto; se prefiere una variable explícita;
   - dejar solo el pool pequeño en modo sesión: con 2 + 1 caben 5 instancias, y un pico de tráfico (la demo ante el jurado) puede abrir más.
