# Cyclo Veda Backend

> Modern FastAPI backend with JWT authentication, comprehensive testing, and Docker-ready deployment.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
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

Create `.env` file:

```env
# Required
SECRET_KEY=your-secret-key-change-in-production

# Optional (defaults provided)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── auth/           # Authentication middleware
│   ├── models/         # Pydantic models
│   ├── routers/        # API endpoints
│   └── services/       # Business logic
├── tests/
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── main.py             # Application entry point
├── pyproject.toml      # Dependencies & configuration
└── README.md           # This file
```

## 🔐 Authentication

**Test Credentials:**
- Email: `admin@cycloveda.com` / Password: `password`
- Email: `user@example.com` / Password: `password`

## 🐳 Docker Deployment

```dockerfile
FROM python:3.13-slim
COPY pyproject.toml .
RUN pip install .  # Production dependencies only
```

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines, code standards, and testing practices.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
