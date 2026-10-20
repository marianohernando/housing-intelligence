# Postgres 17 + pgvector (official multi-arch image) + PostGIS 3 from PGDG apt.
# postgis/postgis has no arm64 manifest, so we extend pgvector instead.
FROM pgvector/pgvector:pg17
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-17-postgis-3 postgresql-17-postgis-3-scripts \
    && rm -rf /var/lib/apt/lists/*
