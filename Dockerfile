# ══════════════════════════════════════════════════════════════
# Stage 1 — base
#   Shared foundation: Python + system runtime libs.
#   Both builder and runtime inherit from here so package
#   versions are identical in the final image.
# ══════════════════════════════════════════════════════════════
FROM python:3.11-slim AS base

# libpq5   — psycopg runtime (binary wheel still calls into libpq)
# ca-certs — TLS connections to Neon (Postgres over SSL)
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libpq5 \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app


# ══════════════════════════════════════════════════════════════
# Stage 2 — builder
#   Installs uv and resolves / installs all Python dependencies
#   into an isolated .venv.  Nothing from this stage leaks into
#   the runtime image except the finished virtual-environment.
# ══════════════════════════════════════════════════════════════
FROM base AS builder

# Drop uv binary from its official image — zero extra layers
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# psycopg[binary] needs libpq headers only at build time
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Layer-cache: copy manifests before source so a code change
# doesn't re-download packages.
COPY pyproject.toml uv.lock ./

# --frozen          → fail if uv.lock is out of sync
# --no-install-project → install deps only, not the app itself
# --no-dev          → skip dev/test extras
RUN uv sync --frozen --no-install-project --no-dev


# ══════════════════════════════════════════════════════════════
# Stage 3 — runtime
#   Minimal production image.  Inherits system libs from base,
#   copies only the compiled venv and application source.
#   No uv, no build tools, no caches.
# ══════════════════════════════════════════════════════════════
FROM base AS runtime

# Non-root user — least-privilege principle
RUN groupadd --system appgroup \
    && useradd --system --gid appgroup --no-create-home appuser \
    && chown appuser:appgroup /app

# Pull in the resolved virtual-environment from builder
COPY --from=builder /app/.venv /app/.venv

# Application source (ordered by change frequency for cache efficiency)
COPY static/ ./static/
COPY db.py components.py main.py ./

# Activate the venv for all subsequent commands
ENV PATH="/app/.venv/bin:$PATH"

USER appuser

EXPOSE 5001

CMD ["python", "main.py"]
