# Arquitectura Técnica Global

## Stack recomendado
- Frontend: Next.js / React.
- Backend: FastAPI / Python.
- DB: PostgreSQL.
- GIS: PostGIS.
- Vector: pgvector.
- Cache: Redis.
- Map: MapLibre + deck.gl.
- Routing: OpenTripPlanner + OSRM/Valhalla.
- ML: scikit-learn / LightGBM / PyTorch según necesidad.
- Infra inicial: Docker Compose.
- CI: GitHub Actions.

## Monolito modular
Evitar microservicios al principio.

## Servicios lógicos
- ProfileService;
- AreaService;
- HousingService;
- MobilityService;
- AffordabilityService;
- RecommendationService;
- SupportService;
- DemandService;
- SupplyService;
- ParcelService;
- MapService;
- ModelService.
