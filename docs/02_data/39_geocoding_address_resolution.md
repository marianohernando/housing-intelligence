# Geocoding & Address Resolution

## Objetivo
Resolver dirección → entidad canónica sin depender de strings frágiles.

## Pipeline
1. normalize text;
2. official address match where possible;
3. Catastro address/reference;
4. geocoder fallback;
5. coordinate verification;
6. entity link.

## Confidence
- exact official;
- exact normalized;
- fuzzy high;
- fuzzy low;
- unresolved.

## Regla
Fuzzy-low nunca enlaza automáticamente un edificio para un hard constraint.

## Cache
Geocoding results versioned/cached.

## Privacy
Anchors privados no se envían a terceros sin review/need.
