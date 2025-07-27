# Contributing to Cyclo Veda Backend

Thank you for contributing to Cyclo Veda! This guide will help you get started with development, testing, and maintaining code quality.

## 🚀 Development Setup

### Prerequisites
- Python 3.9+ (3.13+ recommended)
- Git
- Virtual environment tool (venv, conda, etc.)

### Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Verify installation
python -m pytest --version
black --version
```

### Environment Configuration

Create a `.env` file in the backend directory:

```env
# Required
SECRET_KEY=your-development-secret-key

# Optional (defaults provided)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENV=development
DEBUG=True
```

## 🧪 Testing Guidelines

### Test Structure

Our tests follow a clear structure mirroring the application:

```
tests/
├── unit/                    # Unit tests (isolated components)
│   ├── test_services/       # Business logic tests
│   └── test_models/         # Data model tests
├── integration/             # Integration tests (full workflows)
│   └── test_api/           # API endpoint tests
├── conftest.py             # Shared fixtures and configuration
└── README.md               # Testing documentation
```

### Running Tests

```bash
# Run all tests with coverage
python -m pytest

# Run specific test categories
python -m pytest -m unit           # Unit tests only
python -m pytest -m integration    # Integration tests only
python -m pytest -m auth          # Authentication tests only

# Run specific test files
python -m pytest tests/unit/test_services/test_auth_service.py

# Run with verbose output
python -m pytest -v

# Generate coverage reports
python -m pytest --cov-report=html    # HTML report in htmlcov/
python -m pytest --cov-report=term    # Terminal report
```

### Writing Tests

#### Unit Tests
- Test individual functions/methods in isolation
- Use mocks for external dependencies
- Focus on business logic and edge cases

```python
def test_password_hashing():
    """Test password hashing creates valid hash"""
    password = "test_password"
    hashed = AuthService.get_password_hash(password)
    
    assert hashed != password
    assert AuthService.verify_password(password, hashed)
```

#### Integration Tests
- Test complete workflows and API endpoints
- Use the test client for HTTP requests
- Test authentication flows end-to-end

```python
def test_login_success(client):
    """Test successful login returns token"""
    response = client.post("/api/auth/login", json={
        "email": "admin@cycloveda.com",
        "password": "password"
    })
    
    assert response.status_code == 200
    assert "access_token" in response.json()
```

### Test Fixtures

Use shared fixtures from `conftest.py`:

- `client`: FastAPI test client
- `mock_user`: Sample user data
- `auth_token`: Valid JWT token for testing
- `auth_headers`: Authorization headers

## 📝 Code Standards

### Code Formatting

We use automated code formatting tools:

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .

# Type checking
mypy app/
```

### Code Style Guidelines

1. **Follow PEP 8** - Python style guide
2. **Use type hints** - All functions should have type annotations
3. **Write docstrings** - Document all public functions and classes
4. **Keep functions small** - Single responsibility principle
5. **Use meaningful names** - Self-documenting code

#### Example Function

```python
def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate a user with email and password.
    
    Args:
        email: The user's email address
        password: The user's plaintext password
        
    Returns:
        Optional[User]: User object if authentication successful, None otherwise
    """
    user = get_user(email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
```

### Project Structure Guidelines

#### Adding New Features

1. **Models** (`app/models/`) - Pydantic data models
2. **Services** (`app/services/`) - Business logic
3. **Routers** (`app/routers/`) - API endpoints
4. **Auth** (`app/auth/`) - Authentication middleware

#### File Organization

```python
# app/services/new_service.py
from typing import Optional
from app.models.user import User

class NewService:
    """Service for handling new feature logic."""
    
    @staticmethod
    def process_data(data: dict) -> Optional[dict]:
        """Process incoming data."""
        # Implementation here
        pass
```

## 🔄 Development Workflow

### 1. Branch Strategy

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Create bugfix branch
git checkout -b bugfix/issue-description
```

### 2. Development Process

1. **Write tests first** (TDD approach recommended)
2. **Implement feature** with proper error handling
3. **Run tests** to ensure everything passes
4. **Format code** with black and isort
5. **Check types** with mypy
6. **Update documentation** if needed

### 3. Pre-commit Checklist

```bash
# Run all quality checks
black .                    # Format code
isort .                    # Sort imports
flake8 .                   # Lint code
mypy app/                  # Type checking
python -m pytest          # Run tests
```

### 4. Commit Guidelines

Use conventional commit messages:

```
feat: add user profile endpoint
fix: resolve JWT token expiration issue
test: add integration tests for auth flow
docs: update API documentation
refactor: simplify password validation logic
```

## 🐛 Debugging

### Common Issues

1. **Import Errors**: Ensure you installed in editable mode: `pip install -e ".[dev]"`
2. **Test Failures**: Check that `.env` file exists with required variables
3. **Type Errors**: Run `mypy app/` to identify type issues

### Debugging Tools

```bash
# Run server in debug mode
python main.py

# Debug specific test
python -m pytest tests/path/to/test.py::test_function -v -s

# Use Python debugger
import pdb; pdb.set_trace()  # Add to code for breakpoint
```

## 📚 Additional Resources

### Dependencies

- **FastAPI**: Web framework - [Documentation](https://fastapi.tiangolo.com/)
- **pytest**: Testing framework - [Documentation](https://docs.pytest.org/)
- **Pydantic**: Data validation - [Documentation](https://docs.pydantic.dev/)
- **python-jose**: JWT handling - [Documentation](https://python-jose.readthedocs.io/)

### Project-Specific Docs

- `tests/README.md` - Detailed testing documentation
- `pyproject.toml` - Project configuration and dependencies
- API documentation available at `/docs` when server is running

## 🤝 Getting Help

- **Issues**: Create GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub discussions for questions
- **Code Review**: All PRs require review before merging

## 📋 Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes with tests
4. **Ensure** all checks pass
5. **Submit** a pull request with clear description
6. **Address** review feedback
7. **Merge** after approval

Thank you for contributing to Cyclo Veda! 🎉
