# Service Pressure / Saturation Model

## Objetivo
No asumir que muchos servicios implican suficiente cobertura.

## Ejemplos
- 4 colegios para 10.000 niños puede ser peor que 2 para 1.000.
- un centro de salud puede estar saturado aunque esté cerca.

## Inputs posibles
- capacidad;
- población objetivo;
- plazas;
- matrícula;
- consultas;
- camas;
- cobertura;
- ratios oficiales.

## Niveles de implementación

### Nivel 1
Oferta accesible.

### Nivel 2
Oferta / población objetivo.

### Nivel 3
Capacidad real / demanda estimada.

## MVP
Usar Nivel 2 o 3 solo donde existan datos suficientemente fiables.

## Fallback
Si no existe capacidad:
mostrar acceso, no inventar saturación.
