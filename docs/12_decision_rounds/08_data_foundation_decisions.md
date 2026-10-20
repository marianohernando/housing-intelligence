# Ronda 08 — Decisiones Cerradas: Data Foundation Operativa

121 C — conservar RAW + datos limpios + features finales + lineage.
122 C — grafo completo Dataset → Metric → Feature → Model → Result.
123 C — conservar discrepancias entre fuentes y aplicar política por métrica; Comunidad de Madrid sigue siendo core DATAMAD.
124 C — features actuales + tendencias + velocidad + estabilidad.
125 C — features multiescala: celda propia + contexto 5/10/15 min y vecindad H3.
126 C — nulls con razón explícita.
127 C — feature stores por dominio + vista unificada para modelos.
128 C — 30–50 datasets muy bien integrados para MVP + catálogo mayor investigado.
129 C — degradación elegante cuando falta un dominio, con redistribución segura de pesos y menor confidence.
130 C — diferenciar “no existe” de “no tenemos datos”.
131 C — histórico agregado de anuncios como objetivo, solo cuando exista base legal/licencia/permiso suficiente.
132 C — Catastro: geometría + atributos públicos + cruce con microzona/edificios/modelos.
133 C — urbanismo: uso, edificabilidad, restricciones, planeamiento y documentación cuando exista.
134 C — comercios: histórico + categoría + churn + horarios + intensidad.
135 C — transporte: estático + horarios + realtime/incidencias cuando exista; fallback a GTFS/estático.
136 C — histórico ambiental para exposición habitual y tendencias.
137 C — feature selection estadística + importancia + estabilidad + lógica de negocio.
138 C — detectar redundancias/correlaciones para evitar triple peso conceptual.
139 C — Feature Dictionary machine-readable + Markdown sincronizado.
140 C — una feature válida exige fuente, fórmula, unidad, geografía, tiempo, null policy, confidence, tests, usos y versión.
