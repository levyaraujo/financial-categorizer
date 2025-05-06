# ─────────────────────────────
# Base Image: Minimal Python
# ─────────────────────────────
FROM python:3.12-slim-bullseye AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:/usr/local/bin:$PATH"

WORKDIR /app

# ─────────────────────────────
# Builder Stage: Install deps
# ─────────────────────────────
FROM base AS builder

RUN apt-get update && apt-get install -y curl ca-certificates

ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-cache && uv cache clean

COPY . .

# ─────────────────────────────
# Final Stage: Runtime Image
# ─────────────────────────────
FROM base AS final

COPY --from=builder /app /app

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"


EXPOSE 8080


CMD ["/app/.venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]