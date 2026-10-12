# syntax=docker/dockerfile:1
FROM public.ecr.aws/awsguru/aws-lambda-adapter:0.9.1@sha256:8d2a4f69f16819d6e3e8cf7e885c8e8ab6b9e21a8603ca7f4d8ae1eb325c4fb1 AS adapter
FROM python:3.12-slim-bookworm@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258 AS common
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 UV_PROJECT_ENVIRONMENT=/opt/venv UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache
RUN --mount=type=secret,id=proxy_ca \
    if [ -f /run/secrets/proxy_ca ]; then export PIP_CERT=/run/secrets/proxy_ca; fi; \
    pip install --no-cache-dir uv==0.13.0 && useradd --uid 10001 --create-home app
WORKDIR /app/services/api
COPY services/api/pyproject.toml services/api/uv.lock ./
RUN --mount=type=secret,id=proxy_ca \
    if [ -f /run/secrets/proxy_ca ]; then export SSL_CERT_FILE=/run/secrets/proxy_ca; fi; \
    uv sync --locked --no-dev --no-install-project
COPY services/api/ ./
COPY contracts/ /app/contracts/
COPY tools/ /app/tools/
COPY examples/ /app/examples/
COPY openspec/changes/production-mobile-platform/fixtures/ /app/openspec/changes/production-mobile-platform/fixtures/
COPY infra/local/ /app/infra/local/
COPY infra/certs/ /app/infra/certs/
COPY scripts/ /app/scripts/
RUN --mount=type=secret,id=proxy_ca \
    if [ -f /run/secrets/proxy_ca ]; then export SSL_CERT_FILE=/run/secrets/proxy_ca; fi; \
    uv sync --locked --no-dev && chown -R 10001:10001 /app /opt/venv && chmod -R a+rX /app /opt/venv
USER 10001
FROM common AS api
COPY --from=adapter /lambda-adapter /opt/extensions/lambda-adapter
ENV AWS_LWA_INVOKE_MODE=response_stream AWS_LWA_PORT=8000 AWS_LWA_READINESS_CHECK_PATH=/health/live AWS_LWA_ASYNC_INIT=true
CMD ["/usr/local/bin/uv","run","--no-sync","uvicorn","otgd.main:app","--host","0.0.0.0","--port","8000","--no-access-log","--limit-concurrency","100","--timeout-graceful-shutdown","100"]
FROM common AS worker
ENTRYPOINT ["/usr/local/bin/uv","run","--no-sync","python","/app/scripts/serverless_runtime.py"]
CMD ["otgd.serverless_worker.sqs_handler"]
