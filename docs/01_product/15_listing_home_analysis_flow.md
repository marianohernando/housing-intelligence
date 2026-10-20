# Listing / Home Analysis Flow

## Entradas
- URL autorizada;
- dirección;
- referencia catastral;
- datos manuales.

## Pipeline
1. parse / manual input;
2. resolve address/building;
3. extract property facts;
4. mark fact provenance;
5. calculate HomeFit;
6. calculate Total Housing Cost;
7. compare against saved areas/homes;
8. visit checklist;
9. risk/unknown fields.

## Provenance states
- listing_claim;
- official_observed;
- user_input;
- inferred;
- modeled.

## Regla
Una característica declarada en anuncio no se transforma en hecho oficial.

## Security
URL ingestion must follow SSRF/web-fetch policy.
