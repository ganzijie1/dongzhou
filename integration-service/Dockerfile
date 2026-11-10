FROM python:3.12.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1
WORKDIR /build
COPY --from=nexus . /build/NexusKernel
COPY integration-service /build/integration-service
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install /build/NexusKernel \
    && /opt/venv/bin/pip install httpx==0.28.1 \
    && /opt/venv/bin/pip install --no-deps /build/integration-service

FROM python:3.12.12-slim
ENV PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DONGZHOU_ENV=production \
    DONGZHOU_WEB_ROOT=/app/web-game \
    DONGZHOU_DATABASE_PATH=/data/dongzhou-integration.sqlite3
RUN groupadd --system --gid 10001 dongzhou \
    && useradd --system --uid 10001 --gid 10001 --home /app dongzhou \
    && mkdir -p /app/web-game /data \
    && chown -R dongzhou:dongzhou /app /data
COPY --from=builder /opt/venv /opt/venv
COPY web-game /app/web-game
WORKDIR /app
USER 10001:10001
EXPOSE 8765
VOLUME ["/data"]
HEALTHCHECK --interval=15s --timeout=3s --retries=5 CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/health/live', timeout=2)"]
CMD ["uvicorn", "dongzhou_integration.app:app", "--host", "0.0.0.0", "--port", "8765", "--workers", "1", "--proxy-headers"]
