# =============================================================================
# Stage 1: deps — install production dependencies only
# =============================================================================
FROM python:3.14-slim AS deps

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# =============================================================================
# Stage 2: test — install test deps, copy all code, run unit tests
# Fails the build if any unit test fails. Test deps never reach the runtime image.
# =============================================================================
FROM deps AS test

RUN pip install --no-cache-dir -e ".[test]"

COPY . .

# Load test env vars from .env.test (mounted as build secret or copied below)
# Unit tests mock all DB/external calls — no live services needed at build time.
RUN --mount=type=secret,id=env_test,target=/app/.env \
    pytest tests/unit --override-ini="addopts=" -p no:cov -q

# =============================================================================
# Stage 2.5: dev — development image with debugpy and hot reload
# Inherits from deps, installs dev dependencies, sets up debugging
# =============================================================================
FROM deps AS dev

RUN pip install --no-cache-dir -e ".[dev]"

COPY . .

RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

EXPOSE 8000 5678

# Start with debugpy listener, wait for debugger attachment, then run uvicorn with reload
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================================
# Stage 3: runtime — production image, inherits from deps (not test)
# No test dependencies, no test files in the final image.
# =============================================================================
FROM deps AS runtime

COPY app/ ./app/
COPY migrations/ ./migrations/
COPY scripts/ ./scripts/
COPY alembic.ini ./

RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
