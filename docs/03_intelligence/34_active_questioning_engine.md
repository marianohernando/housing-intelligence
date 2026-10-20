# Active Questioning Engine

## Objetivo
Preguntar menos y mejor.

## Problema
Un onboarding con 30 preguntas reduce conversión.

## Estrategia
1. generar ranking provisional;
2. detectar variables desconocidas;
3. estimar cuánto podría cambiar el ranking cada variable;
4. preguntar por la de mayor impacto;
5. repetir solo si aporta suficiente información.

## Ejemplo
Si saber si el usuario tiene coche cambia completamente 7 de las 10 zonas:
> “Una cosa más: ¿tienes coche habitualmente?”

Si saber si prefiere bares o restaurantes apenas cambia resultados:
no preguntar todavía.

## Implementación MVP
Heurísticas + sensitivity analysis.

## Evolución
Expected Information Gain / uncertainty reduction.

## Límite
No usar active questioning para forzar recogida de datos sensibles.
