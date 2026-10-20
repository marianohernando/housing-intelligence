# Multimodal Accessibility Model

## Objetivo
Modelar cómo se mueve realmente una persona, no cuántas estaciones hay cerca.

## Modos
- walk;
- bus;
- Metro;
- Cercanías;
- Metro Ligero;
- interurban bus;
- rail;
- bicycle cuando sea relevante;
- car.

## Inputs
- red viaria;
- GTFS;
- horarios;
- frecuencias;
- paradas;
- transbordos;
- accesibilidad de estaciones cuando exista;
- walking connectors.

## Outputs
- door_to_door_time;
- waiting_time;
- transfers;
- walking_time;
- frequency_quality;
- service_hours;
- reliability proxy cuando exista;
- destination accessibility.

## Personal anchors
Cada anchor:
```json
{
  "type": "work",
  "location": "...",
  "days_per_week": 4,
  "arrival_window": "08:30-09:30",
  "importance": "high"
}
```

## Aggregation
No promediar todos los anchors por igual.
Ponderar por:
- frecuencia;
- importancia;
- rigidez horaria.

## Example
Un usuario puede preferir una zona con Metro algo peor si tiene un autobús directo frecuente a su trabajo.

El modelo debe capturarlo.
