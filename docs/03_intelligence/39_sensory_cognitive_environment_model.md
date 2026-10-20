# Sensory & Cognitive Environment Model

## Inputs potenciales
- ruido;
- tráfico;
- intensidad peatonal;
- ocio nocturno;
- densidad de POIs;
- intersecciones complejas;
- número de transbordos;
- tiempo de espera;
- variabilidad del trayecto;
- verde;
- calles peatonales;
- obras/incidencias;
- complejidad de estaciones.

## Features
- sensory_noise_exposure;
- nightlife_intensity;
- pedestrian_intensity;
- route_complexity;
- transfer_complexity;
- intersection_complexity;
- green_relief_access;
- predictable_mobility_score.

## Importante
Son features del entorno, no médicas.

## Ejemplo
“Me agobian mucho el ruido y las aglomeraciones.”
→ aumentar peso de low_noise, lower pedestrian intensity, green access y simple transit.

## Limitaciones
Etiquetar cada atributo como observed / proxy / estimated.
