# Estrategia de Datos

## Objetivo
Construir una capa normalizada que valga más que las fuentes originales.

## Capas
- Bronze: original.
- Silver: limpio, tipado, geocodificado.
- Gold: features y productos.

## Familias
- vivienda;
- demografía;
- economía;
- empleo;
- educación;
- sanidad;
- servicios sociales;
- transporte;
- medio ambiente;
- urbanismo;
- catastro;
- ayudas;
- parcelas;
- oferta;
- demanda.

## Formato recomendado
Parquet / GeoParquet para almacenamiento intermedio.
PostgreSQL/PostGIS para serving.
