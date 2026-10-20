# Hard & Soft Constraint Engine

## Hard constraints
- alquiler máximo absoluto
- mínimo de dormitorios
- ascensor obligatorio
- commute máximo
- tenure obligatorio
- step-free verificado

## Preferencias
- imprescindible
- importante
- me gustaría
- indiferente
- evitar

## Semántica
- Imprescindible: hard si es verificable.
- Importante: peso alto.
- Me gustaría: peso moderado.
- Indiferente: peso cero/mínimo.
- Evitar: penalización fuerte; puede convertirse en constraint si el usuario lo confirma.

## Estado
- PASS
- FAIL
- UNKNOWN

UNKNOWN nunca equivale a PASS.
