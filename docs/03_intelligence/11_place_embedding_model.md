# Madrid Place Embedding Model

## Objetivo
Crear una representación matemática compacta de cada zona.

## Input
Features territoriales normalizadas:
- vivienda;
- demografía;
- servicios;
- movilidad;
- ambiente;
- economía;
- urbanismo.

## Modelo MVP
Autoencoder simple.

### Input
~200–400 features.

### Bottleneck
64–128 dimensiones.

### Output
`place_embedding`.

## Entrenamiento
- normalizar;
- controlar missingness;
- separar train/validation;
- reconstrucción;
- analizar estabilidad.

## Uso
- nearest neighbors;
- zonas similares;
- clustering;
- anomaly detection;
- feature for downstream models.

## No usar directamente como
- explicación al usuario;
- precio;
- score definitivo.

## Explainability
Cuando se diga:
> “Zona B es similar a Zona A”

mostrar atributos que más contribuyen a la similitud usando una explicación aparte.
