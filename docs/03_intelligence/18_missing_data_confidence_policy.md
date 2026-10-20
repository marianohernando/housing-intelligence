# Missing Data & Confidence Policy

## Jerarquía
1. Observación directa.
2. Valor oficial agregado compatible.
3. Inferencia espacial/temporal razonable.
4. Modelo de estimación.
5. Desconocido.

## Nunca
- rellenar con 0 salvo que 0 sea observación válida;
- ocultar que un dato fue estimado;
- interpolar de municipio a microzona fingiendo precisión real.

## Confidence dimensions
- source_confidence;
- freshness_confidence;
- geographic_confidence;
- model_confidence;
- coverage_confidence.

## Resultado
El score final puede tener un confidence agregado, pero internamente deben mantenerse separados.

## UX
Evitar números abstractos si no aportan.

Ejemplo:
En lugar de:
> confidence 0.71

PUBLIC:
> “Tenemos buenos datos de transporte y servicios, pero el alquiler de esta microzona es una estimación basada en datos del entorno.”

PRO sí puede mostrar el detalle técnico.
