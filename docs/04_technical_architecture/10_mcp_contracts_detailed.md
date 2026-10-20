# MCP Contracts Detallados

## Principio
Tools pequeñas y semánticas.

No crear:
`run_sql(query)`

Sí:
`find_best_areas(profile, constraints)`

## Tool example: `find_best_areas`

### Input
```json
{
  "profile_id": "uuid",
  "max_results": 5,
  "hard_constraints": {},
  "scenario_overrides": {}
}
```

### Output
```json
{
  "areas": [
    {
      "area_id": "...",
      "fit_score": 91,
      "confidence": 0.90,
      "reason_codes": []
    }
  ],
  "methodology_version": "..."
}
```

## Tool example: `analyze_plot`
Input:
- parcel ID or geometry;
- target product optional.

Output:
- legal/known use context;
- demographic context;
- demand;
- supply;
- gap;
- product suggestions;
- confidence;
- source references.

## Recursos MCP
- methodology;
- metric definitions;
- dataset catalog;
- source registry.

## Seguridad
PRO tools requieren auth y scope.
