# Remaining External Dependencies

## Purpose
Separar “no está documentado” de “solo puede conocerse al ejecutar”.

## Tipos

### EXTERNAL_RESEARCH
Ejemplo:
- descubrir datasets adicionales;
- condiciones de una API.

### DATA_DEPENDENT
Ejemplo:
- decidir si una feature tiene suficiente cobertura.

### IMPLEMENTATION_CALIBRATION
Ejemplo:
- tamaño de caches;
- threshold de modelo.

### USER_VALIDATION
Ejemplo:
- si las explicaciones se entienden realmente.

### LEGAL_REVIEW
Ejemplo:
- tratamiento final de categorías especiales;
- términos de proveedores.

### COMMERCIAL_VALIDATION
Ejemplo:
- pricing.

## Requirement
Cada dependencia debe tener:
- owner;
- fecha/gate objetivo;
- evidence esperado;
- fallback si no se resuelve.
