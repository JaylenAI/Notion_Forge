# ===== 개발용 스테이지 =====
FROM python:3.11-slim AS dev

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache-dir

COPY . .

EXPOSE 9500
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9500", "--reload"]

# ===== 프로덕션 스테이지 =====
FROM python:3.11-slim AS prod

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r notionforge && useradd -r -g notionforge notionforge

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-cache-dir

COPY . .

RUN chown -R notionforge:notionforge /app

USER notionforge

EXPOSE 9500
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9500"]

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:9500/health || exit 1
