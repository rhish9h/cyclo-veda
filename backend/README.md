# Cyclo Veda Backend

> Modern FastAPI backend with JWT authentication, comprehensive testing, and Docker-ready deployment.

[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116+-green.svg)](https://fastapi.tiangolo.com/)
[![pytest](https://img.shields.io/badge/pytest-8.3+-red.svg)](https://pytest.org/)

## 🚀 Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"  # Development setup
# or
pip install -e ".[test]" # Testing only
# or  
pip install .            # Production only

# Run server
uvicorn main:app --reload
```

**API Available:** http://localhost:8000  
**Interactive Docs:** http://localhost:8000/docs  
**Alternative Docs:** http://localhost:8000/redoc

## 🧪 Testing

```bash
# Run all tests with coverage
python -m pytest

# Run specific test categories
python -m pytest -m unit      # Unit tests only
python -m pytest -m integration # Integration tests only

# Generate coverage report
python -m pytest --cov-report=html
```

## 🔧 Environment Setup

```bash
cp .env.example .env
# Fill in: SECRET_KEY, DATABASE_URL, STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET
```

See `.env.example` for all required variables and descriptions.

## 📁 Project Structure

```
backend/
├── app/
│   ├── auth/             # Authentication dependencies (get_current_user)
│   ├── models/           # SQLAlchemy ORM models (database tables)
│   ├── schemas/          # Pydantic schemas (request/response validation)
│   ├── repositories/     # Database access layer (UserRepository)
│   ├── routers/          # API endpoints (auth, health, strava)
│   ├── services/         # Business logic (AuthService)
│   └── database.py       # SQLAlchemy engine + get_db dependency
├── migrations/           # Alembic migration scripts
│   └── versions/         # Individual migration files
├── tests/
│   ├── unit/             # Unit tests (no live DB required)
│   └── integration/      # Integration tests
├── alembic.ini           # Alembic configuration
├── main.py               # Application entry point
├── pyproject.toml        # Dependencies & configuration
└── README.md             # This file
```

## 🔐 Authentication

JWT Bearer token authentication. Login via `POST /api/auth/login` to receive a token, then pass it as `Authorization: Bearer <token>` on subsequent requests.

Test users are seeded via the `fake_users_db` scaffold — replace with real user registration when implementing the registration endpoint.

## 🐳 Docker

Migrations run automatically via the `migrate` init container before the backend starts:

```bash
# Dev (source-mounted, hot reload)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Run migrations manually if needed
docker exec cyclo-veda-backend-dev alembic upgrade head

# Check current migration
docker exec cyclo-veda-backend-dev alembic current
```

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines, code standards, and testing practices.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
