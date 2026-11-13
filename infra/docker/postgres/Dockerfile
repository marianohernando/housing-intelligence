# Postgres 17 + pgvector (official multi-arch image) + PostGIS 3 from PGDG apt.
# postgis/postgis has no arm64 manifest, so we extend pgvector instead.
# PostGIS is pinned: on 12 Nov 2026 PGDG published 3.7.0+dfsg-1.pgdg12+2, which fails to load on
# the 17.11 server of the base image («undefined symbol: heap_datum_check») and broke CI.
# 3.6.4 is the version the local database was built with. Move the pin only after booting the
# image with infra/docker/postgres/initdb (CREATE EXTENSION postgis) on amd64 and arm64.
FROM pgvector/pgvector:pg17
ARG POSTGIS_VERSION=3.6.4+dfsg-2.pgdg12+1
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        "postgresql-17-postgis-3=${POSTGIS_VERSION}" "postgresql-17-postgis-3-scripts=${POSTGIS_VERSION}" \
    && rm -rf /var/lib/apt/lists/*
