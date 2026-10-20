# Data Acquisition Rules for Claude Code

## Orden obligatorio
1. official download/API/feed;
2. open structured source;
3. licensed partner/API;
4. web extraction permitted by terms;
5. scraping only after explicit source review.

## No hacer
- scrapear una fuente solo porque sea más fácil que usar su API;
- automatizar bypasses de controles;
- ignorar robots/terms/licensing review;
- guardar contenido de terceros sin base clara;
- convertir una fuente inestable en dependencia crítica.

## Para cada fuente web
Crear:
- source review;
- terms status;
- robots status when relevant;
- legal/licensing notes;
- allowed fields;
- storage policy;
- refresh policy;
- fallback.

## Idealista
Estado inicial:
`PERMISSION_REQUIRED_FOR_MASS_SCRAPING`.

No implementar crawler masivo hasta resolver acceso.

## Catastro/CRTM
Usar servicios oficiales antes que scraping.
