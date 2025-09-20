# Cyclo Veda 🚴‍♀️

An app to gain more insights from your cycling journey!

## 🚀 Quick Start with Docker

The easiest way to run Cyclo Veda is using Docker:

```bash
# 1. Set up local hostnames (one-time setup) - see instructions below

# 2. Copy environment file
cp .env.example .env

# 3. Start all services
docker compose up --build
```

### Setting Up Local Hostnames

You need to add entries to your hosts file to use the custom hostnames:

**For Mac/Linux:**
```bash
sudo nano /etc/hosts
```

Add these lines at the end:
```
127.0.0.1 cycloveda.local
127.0.0.1 api.cycloveda.local
```

**For Windows:**
1. Open Notepad as Administrator
2. Open the file: `C:\Windows\System32\drivers\etc\hosts`
3. Add these lines at the end:
```
127.0.0.1 cycloveda.local
127.0.0.1 api.cycloveda.local
```
4. Save the file

**Access the application:**
- 🌐 Frontend: http://cycloveda.local
- 🔌 Backend API: http://api.cycloveda.local
- 📊 Traefik Dashboard: http://localhost:8080

## 🏗️ Architecture

- **Frontend**: React + TypeScript with modern tooling
- **Backend**: FastAPI with JWT authentication
- **Reverse Proxy**: Traefik v3.0 for routing and load balancing
- **Testing**: Comprehensive test suite with pytest
- **Documentation**: ADR framework for architectural decisions

## 📚 Documentation

- [Docker Setup Guide](documentation/docs/docker-setup.md) - Complete containerization setup
- [API Reference](documentation/docs/api-reference.md) - API endpoints documentation
- [Authentication Guide](documentation/docs/authentication.md) - Auth implementation details
- [Architecture Overview](documentation/docs/architecture.md) - System design decisions
- [Changelog](documentation/changelog/CHANGELOG.md) - Project change history

## 🛠️ Development

### Local Development (without Docker)

**Backend:**
```bash
cd backend
pip install -e ".[dev]"
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

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
```

## 🤝 Contributing

1. Follow the [resumability guidelines](.windsurf/rules/resumability.md)
2. Update documentation for any significant changes
3. Add tests for new functionality
4. Ensure Docker builds work correctly

## 📝 License

MIT License - see LICENSE file for details.
