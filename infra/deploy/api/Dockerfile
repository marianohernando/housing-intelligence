# Public demo API image (OPS-001). Build context: repository root.
#   docker build -f infra/deploy/api/Dockerfile -t vida-facil-api .
# Runtime env: DATABASE_URL, CORS_ORIGINS, PORT (default 8080). See infra/deploy/README.md.

FROM python:3.12-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.11.4 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv
WORKDIR /src
# Every workspace member must be present for uv to read the lockfile; only hi-api's closure
# (hi-contracts, hi-db, hi-domain and their dependencies) is installed.
COPY pyproject.toml uv.lock ./
COPY apps/api apps/api
COPY packages/contracts packages/contracts
COPY packages/db packages/db
COPY packages/domain packages/domain
COPY services/features services/features
COPY services/ingestion services/ingestion
RUN uv sync --frozen --no-dev --package hi-api --no-editable

FROM python:3.12-slim
RUN useradd --system --uid 10001 --no-create-home api
COPY --from=build /opt/venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PORT=8080
USER api
EXPOSE 8080
# Only the platform proxy reaches the container, so its forwarded headers are trusted.
CMD ["sh", "-c", "exec uvicorn hi_api.main:app --host 0.0.0.0 --port \"$PORT\" --proxy-headers --forwarded-allow-ips '*'"]
