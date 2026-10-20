# 15-Minute Living Model

## Objetivo
Saber qué necesidades reales puede resolver una persona desde una microzona en:
- 5 min;
- 10 min;
- 15 min.

## Categorías
- grocery;
- pharmacy;
- healthcare;
- school;
- childcare;
- park;
- sport;
- public administration;
- culture;
- restaurant;
- daily retail;
- transit.

## Salida base
Por categoría:
- nearest_time;
- count_reachable;
- diversity;
- redundancy;
- opening coverage cuando exista.

## Personalización
### Familia con niños
Más peso:
- school;
- childcare;
- park;
- healthcare.

### Persona mayor
Más peso:
- pharmacy;
- health;
- food;
- accessible transit;
- social centers.

### Estudiante
Más peso:
- campus/transit;
- grocery;
- library;
- leisure.

## Multimodal
El modelo “15 minutos” por defecto será peatonal, pero el sistema puede mostrar:
- 15 min walking;
- 15 min transit;
- 15 min bike.

## UI
Representar como isócrona real, no círculo.
