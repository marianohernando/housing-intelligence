# Area Typology Clustering

## Objetivo
Descubrir patrones territoriales sin imponer todas las categorías manualmente.

## Inputs
- Place Embeddings;
- features estructurales;
- densidad;
- vivienda;
- movilidad;
- servicios;
- demografía;
- actividad.

## Métodos
- HDBSCAN;
- k-means cuando aporte estabilidad;
- UMAP solo para visualización.

## Salida
Clusters técnicos.

## Interpretación
Cada cluster recibe un nombre humano revisado:
- centro urbano denso;
- residencial familiar;
- suburbano conectado;
- universitario;
- oficina/empleo;
- envejecido;
- mixto;
- emergente.

## Regla
El nombre humano describe el patrón; no debe introducir juicios de valor.
