> **HISTÓRICO / SUPERADO.** Las preguntas de este documento ya fueron respondidas en rondas posteriores. No usarlo como lista de decisiones abiertas. La fuente vigente es `00_index/01_decisions_log.md` y los documentos `*_decisions.md`.

# Ronda 03 — Data Model, ML Core, Privacidad y Precisión

## Objetivo
Cerrar las decisiones que determinan:
- cómo representamos al usuario;
- qué datos personales almacenamos;
- cómo medimos precisión;
- cómo entrenamos el Madrid Place Model;
- cómo combinamos reglas, ML, JEV y LLM;
- cómo evitamos falsa precisión;
- cómo hacemos que el sistema aprenda.

## Decisiones pendientes
1. Modelo de perfil del usuario.
2. Separación PII / analytics.
3. Nivel de persistencia de datos sensibles.
4. Geografía de entrenamiento.
5. Estrategia de imputación.
6. Modelo base de Residential Fit.
7. Primer modelo ML de ranking.
8. Modelo de precio/alquiler.
9. Place Embedding dimensionality.
10. Historical vs current features.
11. Forecasting.
12. Confidence model.
13. User feedback labels.
14. Online learning.
15. Model explainability.
16. Model governance.
17. Sensitive-feature policy.
18. Fairness controls.
19. Cold start.
20. Simulation / what-if engine.

## Regla
No implementar modelos productivos hasta cerrar esta ronda.
