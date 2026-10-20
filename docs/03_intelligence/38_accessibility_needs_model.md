# Accessibility Needs Model

## Objetivo
Convertir necesidades explícitas en constraints/features sin usar diagnósticos como atajo.

## Grupos
- mobility;
- visual;
- hearing;
- cognitive;
- sensory.

## Hard constraints vs preferencias
Ejemplos:
- ascensor obligatorio → hard constraint.
- menos ruido → preference.
- estación step-free → hard/strong preference según usuario.

## Regla
No mapear automáticamente `autism -> low_noise=true`.
Preguntar: “¿Te ayuda que la zona sea poco ruidosa o con rutas sencillas?”

## Explicabilidad
Sí:
“Esta zona tiene varios cruces con avisadores acústicos y el trayecto al Metro requiere menos cruces complejos.”

No:
“Esta es la mejor zona para personas ciegas.”

## Missing data
Si falta inventario:
“Tenemos buena información del transporte, pero no suficiente detalle de accesibilidad de todas las aceras.”

## Arquitectura
Submodelo del Residential Intelligence Engine.
