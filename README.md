# Cyclo Veda 🚴‍♀️

An app to gain more insights from your cycling journey!

## 🚀 Setup

### One-time Setup

```bash
# 1. Add to /etc/hosts (sudo nano /etc/hosts)
127.0.0.1 cycloveda.local
127.0.0.1 api.cycloveda.local

# 2. Copy environment files
cp .env.example .env
cp backend/.env.example backend/.env
# Fill in POSTGRES_PASSWORD, SECRET_KEY, DATABASE_URL, and Strava credentials
```

## 🛠️ Development Tools

- **Docker Desktop** - Container management and orchestration
- **Postman** - API testing and documentation  
- **pgAdmin 4** - PostgreSQL database management
- **Modern Web Browser** - Application testing and development

## 🛠️ Development

```bash
# Start backend, database, and run migrations
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Start frontend locally (fastest hot reload)
cd frontend && npm install && npm run dev
```

**Access:** Frontend at http://localhost:5173 | Backend at http://api.cycloveda.local | Traefik dashboard at http://localhost:8080

### Development Commands

```bash
# View backend logs
docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f backend

# Restart backend
docker compose -f docker-compose.yml -f docker-compose.dev.yml restart backend

# Stop all services
docker compose -f docker-compose.yml -f docker-compose.dev.yml down

# Run backend tests (no live DB needed)
cd backend && python -m pytest
```

## 🏭 Production

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

**Access:** Frontend at http://cycloveda.local | Backend at http://api.cycloveda.local

## 🏗️ Architecture

- **Frontend**: React + TypeScript with modern tooling
- **Backend**: FastAPI with JWT authentication
- **Reverse Proxy**: Traefik v2.11 for routing and load balancing
- **Testing**: Comprehensive test suite with pytest
- **Documentation**: ADR framework for architectural decisions

## 📚 Documentation

- [Docker Setup Guide](documentation/docs/docker-setup.md) - Complete containerization setup
- [API Reference](documentation/docs/api-reference.md) - API endpoints documentation
- [Authentication Guide](documentation/docs/authentication.md) - Auth implementation details
- [Architecture Overview](documentation/docs/architecture.md) - System design decisions
- [Changelog](documentation/changelog/CHANGELOG.md) - Project change history

### Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests (coming soon)
cd frontend
npm test
```

## 🔧 Tech Stack

### Frontend
- React 19 + TypeScript
- Vite for build tooling
- React Router for navigation
- Modern CSS with responsive design

### Backend
- FastAPI (Python 3.14)
- JWT authentication with PyJWT
- Password hashing with pwdlib[bcrypt]
- Pydantic v2 for data validation
- SQLAlchemy 2.x ORM + PostgreSQL
- Alembic for database migrations

### Infrastructure
- Docker & Docker Compose
- Traefik reverse proxy
- Nginx for frontend serving
- Multi-stage builds for optimization

## 📖 Project Structure

```
├── backend/                  # FastAPI application (Python 3.14)
│   ├── app/
│   │   ├── auth/             # Authentication dependencies
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── repositories/     # Database access layer
│   │   ├── routers/          # API endpoints (auth, health, strava)
│   │   ├── services/         # Business logic layer
│   │   └── database.py       # DB engine and session factory
│   ├── migrations/           # Alembic migration scripts
│   └── tests/                # Comprehensive test suite
├── frontend/                 # React + TypeScript application
│   ├── src/
│   │   ├── components/       # React components (auth, layout)
│   │   ├── services/         # API service layer
│   │   ├── hooks/            # Custom React hooks
│   │   ├── types/            # TypeScript definitions
│   │   └── constants/        # Application constants
│   └── public/               # Static assets
├── documentation/            # Project documentation
│   ├── adr/                  # Architecture Decision Records
│   ├── changelog/            # Change history
│   └── docs/                 # Technical documentation
├── docker-compose.yml        # Base: shared services (traefik, migrate, backend, postgres)
├── docker-compose.dev.yml    # Dev overrides: source mount, dev CORS, dev container names
└── docker-compose.prod.yml   # Prod overrides: frontend service, read-only docker.sock
```

## 🤝 Contributing

1. Follow the [resumability guidelines](.windsurf/rules/resumability.md)
2. Update documentation for any significant changes
3. Add tests for new functionality
4. Ensure Docker builds work correctly

## 📝 License

MIT License - see LICENSE file for details.
