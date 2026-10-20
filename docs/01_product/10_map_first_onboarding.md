# Map-First Conversational Onboarding

## Inicio
Abrir directamente:
- mapa;
- chat;
- filtros/chips.

No hay formulario obligatorio.

## Prompt
“Cuéntame qué buscas o empieza explorando el mapa.”

## Chips
- Alquilar
- Comprar
- Familia
- Vivo solo/a
- Necesito accesibilidad
- Cerca del trabajo
- Sin coche
- Zona tranquila

## Estado único
Chat, filtros y mapa modifican el mismo `ScenarioState`.

## Filtros
- presupuesto;
- dormitorios;
- transporte;
- servicios;
- accesibilidad;
- entorno;
- anchors.

## Active Questioning
El chat pregunta solo si una variable desconocida cambia materialmente el resultado.

## Confirmación
Panel editable:
“Esto es lo que estoy teniendo en cuenta”.
