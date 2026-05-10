---
trigger: model_decision
description: Apply when running, writing, or debugging tests. Covers how unit and integration tests are structured and executed in this project.
---

## Testing

### Unit tests

- Live in `backend/tests/unit/`
- No live DB or external services required — all dependencies are mocked
- Run via Docker build (`test` stage in `backend/Dockerfile` runs them automatically)
- Run locally: `pytest tests/unit --override-ini="addopts=" -p no:cov -q`
- A failing unit test will fail the Docker build — do not bypass this

### Integration tests

- Live in `backend/tests/integration/`
- Require a real PostgreSQL DB — always run via Docker Compose, never plain `pytest`
- Command: `docker compose -f docker-compose.test.yml up --build --exit-code-from test-runner --renew-anon-volumes --remove-orphans`
- Migrations (`alembic upgrade head`) run automatically inside `test-runner` before pytest starts
- Only outbound HTTP to Strava is mocked; DB, encryption, and routing are real

### Key patterns

- Per-test DB isolation: SAVEPOINT rollback (not table truncation)
- Seed data (e.g. the `users` row) is committed at conftest import time via `asyncio.run()` — not via a pytest fixture — to guarantee it exists before any fixture setup
- After writing ORM records in a test, call `db.expire_all()` before making requests that will re-read those records, to avoid SQLAlchemy identity map serving stale in-memory state
- `DATABASE_URL` is captured at module import time in `conftest.py` to survive `reset_environment` clearing `os.environ`
