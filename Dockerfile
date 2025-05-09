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

# Copy only dependency files first
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .

# ─────────────────────────────
# Final Stage: Runtime Image
# ─────────────────────────────
FROM base AS final

COPY --from=builder /app /app

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Make the startup script executable
RUN chmod +x /app/start.sh

EXPOSE 8000

# Use the startup script instead of directly running fastapi
CMD ["/app/start.sh"]
