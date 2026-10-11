FROM python:3.12-slim-bookworm@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 UV_PROJECT_ENVIRONMENT=/opt/venv UV_NO_SYNC=1
RUN pip install --no-cache-dir uv==0.13.0 && useradd --uid 10001 --create-home app
WORKDIR /app/services/api
COPY services/api/pyproject.toml services/api/uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY services/api/ ./
COPY contracts/ /app/contracts/
COPY tools/ /app/tools/
COPY examples/ /app/examples/
COPY openspec/changes/production-mobile-platform/fixtures/ /app/openspec/changes/production-mobile-platform/fixtures/
COPY infra/local/ /app/infra/local/
COPY infra/certs/ /app/infra/certs/
COPY scripts/ /app/scripts/
RUN uv sync --locked --no-dev && chown -R 10001:10001 /app /opt/venv
USER 10001
EXPOSE 8000
CMD ["uv","run","--no-sync","uvicorn","otgd.main:app","--host","0.0.0.0","--port","8000","--no-access-log","--limit-concurrency","100","--timeout-graceful-shutdown","100"]
