# Housing Gap Product Recommender

## Objetivo
Pasar de:
> “hay demanda”

a:
> “qué producto residencial tendría sentido aquí”.

## Inputs
- household demand;
- affordability;
- housing stock;
- supply pipeline;
- dwelling sizes;
- services;
- mobility;
- parcel/buildability context;
- user-demand aggregates;
- price sensitivity.

## Outputs
```json
{
  "dominant_need": "family_rental",
  "recommended_bedrooms": [2,3],
  "recommended_surface_m2": [80,105],
  "target_rent_monthly": [1100,1300],
  "target_households": ["families_3_4"],
  "required_amenities": [],
  "estimated_compatible_households": 4200,
  "gap_score": 89,
  "confidence": 0.82
}
```

## Restricciones
No confundir recomendación de mercado con:
- viabilidad urbanística legal definitiva;
- tasación;
- recomendación de inversión regulada.

## Explainability
Mostrar:
- demanda;
- oferta;
- affordability;
- competencia;
- transporte;
- servicios;
- riesgos.
