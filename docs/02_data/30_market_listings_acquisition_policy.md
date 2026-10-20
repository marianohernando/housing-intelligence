# Market Listings Acquisition Policy

## Objetivo
Construir inteligencia de oferta y mercado sin basar el producto en acceso no autorizado.

## Fuentes posibles
1. datasets oficiales de alquiler/compraventa;
2. SERPAVI / fuentes ministeriales;
3. portales con API/licencia/permiso;
4. partners/feeds;
5. datos aportados por clientes;
6. anuncios individuales aportados por el usuario para análisis puntual, dentro de condiciones aplicables.

## Idealista
Objetivo estratégico por riqueza del mercado, pero:
- no asumir derecho a scraping masivo;
- sus términos actuales requieren permiso expreso para robots/scrapers;
- no construir un componente crítico que dependa de scraping no autorizado.

## Si obtenemos permiso/feed
Pipeline:
- listing_id externo;
- snapshot;
- precio;
- m²;
- dormitorios;
- planta;
- ascensor;
- características;
- ubicación permitida;
- first_seen;
- last_seen;
- price_changes;
- removed_at.

## Histórico agregado
Derivar:
- new_listings_rate;
- removal_rate;
- median_asking_price;
- price_change_rate;
- days_visible proxy;
- supply_mix.

## Separar
Precio anunciado ≠ precio de transacción.
Nunca mezclarlos sin etiqueta.
