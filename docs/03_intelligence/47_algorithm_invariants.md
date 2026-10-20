# Algorithm Invariants

Ejemplos:

## Budget monotonicity
Aumentar el presupuesto máximo no debe hacer desaparecer todas las opciones previas solo por ese cambio.

## Accessibility
Si ascensor es obligatorio y el edificio está confirmado sin ascensor → FAIL.

## Commute
Si un anchor se acerca, movilidad no debería empeorar manteniendo lo demás.

## Services
Añadir un servicio relevante cercano no debería empeorar su componente.

## Confidence
Menor cobertura/calidad no puede aumentar certeza.

## Hard constraints
Un FAIL no puede aparecer como válido estándar.

## Alternatives
Los candidatos que rompen constraints solo salen en Alternative Finder / Reality Check.

Implementar como tests/property-based tests cuando tenga sentido.
