# Feature Selection & Redundancy

## Problema
500 features pueden codificar el mismo concepto repetidas veces.

Ejemplo:
- renta media;
- precio vivienda;
- nivel socioeconómico;
- consumo;
podrían estar altamente correlacionadas.

## Pipeline
1. domain review;
2. missingness filter;
3. variance;
4. correlation analysis;
5. multicollinearity;
6. stability over time;
7. model importance;
8. permutation/SHAP where appropriate;
9. business interpretability;
10. fairness review.

## Regla
Una feature no se mantiene porque “suba el accuracy” si introduce leakage o proxy sensible injustificado.

## Feature sets
Versionar:
`feature_set_residential_fit_v1`
`feature_set_place_model_v1`
etc.
