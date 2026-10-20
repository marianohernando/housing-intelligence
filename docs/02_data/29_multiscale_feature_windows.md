# Multi-scale Feature Windows

## Razón
La calle importa, pero también lo que tienes alrededor.

## Ventanas
- microzona propia;
- walking_5m;
- walking_10m;
- walking_15m;
- H3 ring 1;
- H3 ring 2;
- transit_30m cuando aplique.

## Ejemplos
`pharmacy_count_walk_10m`
`green_area_walk_15m`
`jobs_transit_30m`
`nightlife_h3_ring1`

## Método
Cuando sea posible, las ventanas temporales de acceso se calculan por red/isócrona, no por buffer circular.

## ML
No incluir todas las escalas de todas las variables sin feature selection.
