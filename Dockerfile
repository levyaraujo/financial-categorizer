# ─────────────────────────────
# Base Image: Minimal Python
# ─────────────────────────────
FROM python:3.12-slim-bullseye AS base

# Prevents Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Ensures stdout/stderr is unbuffered (useful for logs)
ENV PYTHONUNBUFFERED=1
ENV PATH="/usr/local/bin:$PATH"

WORKDIR /app

# ─────────────────────────────
# Builder Stage: Install deps
# ─────────────────────────────
FROM base AS builder

# Install build tools & uv
RUN apt-get update && apt-get install -y curl && \
    pip install uv && \
    apt-get purge -y --auto-remove curl && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN uv venv && \
    uv pip install -r pyproject.toml && \
    uv cache clean

COPY . .

# ─────────────────────────────
# Final Stage: Runtime Image
# ─────────────────────────────
FROM base AS final

# Copy only needed files from builder
COPY --from=builder /app /app

EXPOSE 8080

# Start the FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
