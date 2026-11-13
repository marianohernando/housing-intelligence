# API, OpenAPI y MCP

## API
Versionada `/api/v1`.

## Endpoints base
- `/areas/{id}`;
- `/recommendations`;
- `/affordability`;
- `/compare`;
- `/housing-gap`;
- `/plots/analyze`;
- `/support`.

## MCP PUBLIC
Implementado en local desde MCP-001 (D-225): `buscar_zonas`, `que_falta`, `explicar_zona`, `encontrar_zona` y `fuentes_de_datos`. Ver `32_mcp_server.md`. La lista de abajo es el objetivo.

- find_best_areas;
- compare_areas;
- calculate_affordability;
- calculate_total_cost;
- find_housing_support;
- get_commute_times;
- explain_score.

## MCP PRO
- analyze_area;
- find_supply_gap;
- find_demand_gap;
- search_investment_areas;
- analyze_plot;
- compare_markets;
- recommend_housing_product;
- forecast_demand;
- find_similar_areas.

## MCP documental
- search_housing_regulation;
- search_urban_planning_docs;
- search_dataset_catalog;
- get_metric_definition;
- get_methodology;
- get_source.
