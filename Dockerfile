FROM python:3.12-slim-bullseye AS base

WORKDIR /app

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install uv
RUN apt-get update && apt-get install -y curl && \
    pip install uv


# ───────────────────────────────────────────────

FROM base AS builder

WORKDIR /app

COPY pyproject.toml uv.lock .

RUN uv venv

RUN uv pip install .

COPY . .

# ───────────────────────────────────────────────

FROM base AS final

COPY --from=builder /app /app

EXPOSE 8080

CMD ["fastapi", "main:app", "--port", "8080", "--host", "0.0.0.0"]