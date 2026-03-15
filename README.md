# Cyclo Veda 🚴‍♀️

An app to gain more insights from your cycling journey!

## 🚀 Setup

### One-time Setup

```bash
# 1. Add to /etc/hosts (sudo nano /etc/hosts)
127.0.0.1 cycloveda.local
127.0.0.1 api.cycloveda.local

# 2. Copy environment file
cp .env.example .env
```

## 🛠️ Development

```bash
# Start backend & database
docker compose -f docker-compose-dev.yml up -d postgres backend traefik

# Start frontend locally
cd frontend && npm install && npm run dev
```

**Access:** Frontend at http://localhost:5173 | Backend at http://api.cycloveda.local | Dashboard at http://localhost:8080

### Development Commands

```bash
# View backend logs
docker compose -f docker-compose-dev.yml logs -f backend

# Restart backend
docker compose -f docker-compose-dev.yml restart backend

# Stop services
docker compose -f docker-compose-dev.yml down
```

## 🏭 Production

```bash
docker compose up --build
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
- FastAPI (Python 3.13)
- JWT authentication with python-jose
- Password hashing with bcrypt
- Pydantic for data validation
- Dedicated health endpoints

### Infrastructure
- Docker & Docker Compose
- Traefik reverse proxy
- Nginx for frontend serving
- Multi-stage builds for optimization

## 🧪 Test Credentials

For testing the authentication system:
- **Admin**: admin@cycloveda.com / password
- **User**: user@example.com / password

## 📖 Project Structure

```
├── backend/           # FastAPI application (Python 3.13)
│   ├── app/
│   │   ├── routers/  # API endpoints (auth, health)
│   │   ├── models/   # Pydantic data models
│   │   ├── services/ # Business logic layer
│   │   └── auth/     # Authentication utilities
│   └── tests/        # Comprehensive test suite
├── frontend/          # React + TypeScript application
│   ├── src/
│   │   ├── components/ # React components (auth, layout)
│   │   ├── services/   # API service layer
│   │   ├── hooks/      # Custom React hooks
│   │   ├── types/      # TypeScript definitions
│   │   └── constants/  # Application constants
│   └── public/       # Static assets
├── documentation/     # Project documentation
│   ├── adr/          # Architecture Decision Records
│   ├── changelog/    # Change history
│   └── docs/         # Technical documentation
└── docker-compose.yml # Multi-service orchestration
├── docker-compose-dev.yml # Development configuration
```

## 🤝 Contributing

1. Follow the [resumability guidelines](.windsurf/rules/resumability.md)
2. Update documentation for any significant changes
3. Add tests for new functionality
4. Ensure Docker builds work correctly

## 📝 License

MIT License - see LICENSE file for details.
