# Model Serving & Registry

## Registry

Cada modelo:
```yaml
model_id:
model_type:
version:
training_data_version:
feature_set_version:
trained_at:
metrics:
status:
artifact_location:
```

## Estados
- EXPERIMENT
- SHADOW
- ACTIVE
- DEPRECATED
- ROLLED_BACK

## Serving
El backend nunca carga “el último modelo” de manera implícita.
Carga versión marcada `ACTIVE`.

## Shadow
Modelos nuevos pueden producir resultados sin mostrarlos al usuario para comparar.

## Rollback
Debe ser posible cambiar a versión anterior sin redeploy completo.

## Prediction log
Guardar:
- model version;
- input feature version;
- prediction;
- confidence;
- latency.

Evitar guardar datos personales innecesarios.
