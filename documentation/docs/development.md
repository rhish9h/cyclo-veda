# Development Guide

## Prerequisites

### Backend
- Python 3.13+
- pip with pyproject.toml (setuptools backend)
- PostgreSQL (via Docker in dev, or a local PostgreSQL instance)

### Frontend
- Node.js 18+
- npm or yarn

## Getting Started

### Docker Development (Recommended)

The project uses Docker Compose for development with PostgreSQL, Traefik reverse proxy, and proper service ordering.

**Prerequisites:**
- Docker Desktop (or Docker Engine with Docker Compose)
- Local hostname setup (optional, for nicer URLs)

**Quick Start:**
```bash
# Copy environment files
cp .env.example .env
cp backend/.env.example backend/.env

# Start all services (seeding happens automatically)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

**Access the application:**
- Frontend: http://cycloveda.local (or http://localhost:5173 if running locally)
- Backend API: http://api.cycloveda.local
- Traefik Dashboard: http://localhost:8080

**Development credentials:**
- Email: `admin@cycloveda.com` | Password: `password`
- Email: `user@example.com` | Password: `password`

**Service architecture:**
The Docker Compose setup follows best practices with proper service ordering:
1. **postgres** - PostgreSQL database with health checks
2. **migrate** - Alembic schema migrations (runs once, exits)
3. **seed** - Development data seeding (runs automatically after migrations, idempotent)
4. **backend** - FastAPI application (depends on migrations and seed completing)
5. **traefik** - Reverse proxy with automatic service discovery

**Seeding:**
The seed service runs automatically on `docker compose up` and uses find-or-create logic, so it's idempotent (safe to run multiple times). Users are only created if they don't already exist.

### Local Development (Backend)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/cyclo-veda.git
   cd cyclo-veda/backend
   ```

2. **Install dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Environment variables**
   Create a `.env` file in the backend directory:
   ```env
   # JWT Settings
   SECRET_KEY=your-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # Database (PostgreSQL for development)
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/cyclo_veda_dev
   ```

4. **Run migrations**
   ```bash
   alembic upgrade head
   ```

5. **Seed development users**
   ```bash
   python scripts/seed_dev_users.py
   ```

6. **Start the server**
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Environment variables**
   Create a `.env` file in the frontend directory:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

## Testing

### Unit Tests (no DB required)

Unit tests run automatically as part of the Docker build. The `test` stage in `backend/Dockerfile` runs `pytest tests/unit` — if any test fails, the build fails. The `runtime` stage inherits from `deps` (not `test`), so a prod build does **not** run tests.

Run locally:

```bash
# All unit tests
pytest tests/unit --override-ini="addopts=" -p no:cov -q

# Specific file
pytest tests/unit/test_services/test_strava_service.py -p no:cov -q

# With coverage (local only — requires pytest-cov)
pytest tests/unit --cov=app --cov-report=term-missing
```

### Integration Tests (requires PostgreSQL)

Integration tests use a real ephemeral PostgreSQL database. Run via Docker Compose:

```bash
docker compose -f docker-compose.test.yml up --build \
  --exit-code-from test-runner \
  --renew-anon-volumes \
  --remove-orphans
```

- Migrations (`alembic upgrade head`) run automatically inside the `test-runner` container before pytest.
- Only outbound HTTP calls to Strava are mocked; all DB, encryption, and routing is exercised for real.
- Exit code mirrors pytest: `0` = all pass, non-zero = failure.

### Frontend Tests
```bash
# Unit tests
npm test

# E2E tests (if configured)
npm run test:e2e
```

## Code Style

### Backend
- Follow PEP 8
- Use type hints
- Maximum line length: 88 characters
- Use Black for code formatting

### Frontend
- Use Prettier for code formatting
- Follow the project's ESLint rules
- Use TypeScript types

## Git Workflow

1. Create a new branch for your feature
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Run tests and linters
   ```bash
   # Backend
   black .
   isort .
   mypy .
   pytest
   
   # Frontend
   npm run format
   npm run lint
   npm test
   ```

4. Commit your changes with a descriptive message
   ```bash
   git commit -m "feat: add user authentication"
   ```

5. Push your branch and create a pull request

## Debugging

### Backend
- Use `print()` statements or Python's `logging`
- VS Code debugger is pre-configured
- Check server logs for errors

### Frontend
- Use browser's developer tools
- React DevTools extension for React debugging
- Check console for errors and warnings

## Deployment

### Backend
1. Set up a production database (PostgreSQL recommended)
2. Configure environment variables
3. Use a production WSGI server (e.g., Gunicorn with Uvicorn workers)
4. Set up a reverse proxy (Nginx/Apache)
5. Configure SSL/TLS

### Frontend
1. Build for production:
   ```bash
   npm run build
   ```
2. Serve the `dist` directory using a web server (Nginx recommended)
3. Configure SSL/TLS

## Monitoring
(To be implemented)
- Set up logging
- Configure monitoring tools
- Set up alerts for critical errors
