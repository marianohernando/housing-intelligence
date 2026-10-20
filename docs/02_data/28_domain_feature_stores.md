# Domain Feature Stores

## Tablas lógicas
- housing_features
- market_features
- affordability_features
- demographic_features
- household_features
- mobility_features
- education_features
- health_features
- social_features
- accessibility_features
- poi_features
- environment_features
- safety_features
- economic_features
- urbanism_features
- temporal_features
- pro_intelligence_features

## Key
Normalmente:
- geo_id / h3_id
- period
- feature_version

## Unified model view
Crear vistas/materializaciones:
`model_feature_matrix_<version>`

Los modelos no deben hacer joins improvisados sobre 40 tablas durante serving.
