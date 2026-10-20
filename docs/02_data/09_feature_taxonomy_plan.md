# Plan para el Diccionario de Features

## Objetivo
Transformar decenas de datasets en un conjunto estable de 200–400 variables comprensibles por código, modelos, JEV, LLM y humanos.

# Familias propuestas
## Vivienda
rent_m2, average_rent, housing_units, average_surface, large_unit_share, transaction_rate.

## Affordability
rent_to_income, estimated_effort, purchase_affordability, target_household_coverage.

## Demografía
population, population_growth, child_share, senior_share, dependency_ratio, household_size.

## Familia
households_3_plus, households_5_plus, family_housing_supply_gap.

## Mayores / dependencia
senior_population, social_centers_access, pharmacy_access, health_access, senior_service_gap.

## Educación
school_density, schools_per_child_population, nearest_school_time, education_access_score.

## Salud
healthcare_facilities, nearest_healthcare_time, pharmacies, health_access_score.

## Movilidad
metro_access, cercanias_access, bus_access, multimodal_score, commute_matrix.

## Medio ambiente
air_quality, green_access, tree_density, noise, heat_risk.

## Economía
disposable_income, employment, business_activity.

## Urbanismo
parcel_availability, buildability, residential_land, housing_pipeline.

## PRO
modeled_demand, compatible_supply, housing_gap, absorption, opportunity, social_impact.

# Ficha obligatoria por feature
- feature_id
- human_name
- description
- category
- unit
- direction
- geographic_resolution
- temporal_resolution
- formula
- source_datasets
- null_strategy
- normalization
- public_use
- pro_use
- models
- limitations
- feature_version

# Regla
Nada de columnas ambiguas como `score_1` o `data_x`.
Cada nombre debe expresar un concepto estable y auditable.
