# Backend Testing Guide

This directory contains comprehensive tests for the Cyclo Veda backend application using pytest.

## 📁 Directory Structure

```
tests/
├── __init__.py                 # Tests package initialization
├── conftest.py                 # Pytest configuration and shared fixtures
├── README.md                   # This file - testing documentation
├── requirements-test.txt       # Testing dependencies
├── unit/                       # Unit tests (test individual components)
│   ├── __init__.py
│   ├── test_services/          # Tests for app/services/
│   │   ├── __init__.py
│   │   └── test_auth_service.py
│   ├── test_models/            # Tests for app/models/
│   │   ├── __init__.py
│   │   └── test_user.py
│   ├── test_auth/              # Tests for app/auth/ (future)
│   └── test_utils/             # Tests for app/utils/ (future)
└── integration/                # Integration tests (test component interactions)
    ├── __init__.py
    ├── test_api/               # API endpoint tests
    │   ├── __init__.py
    │   └── test_auth.py
    ├── test_auth_flow/         # Complete auth workflows (future)
    └── test_database/          # Database integration tests (future)
```

## 🚀 Quick Start

### 1. Set Up Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r tests/requirements-test.txt
```

### 2. Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app

# Run with HTML coverage report
pytest --cov=app --cov-report=html
```

### 3. Run Specific Test Categories

```bash
# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Run specific test file
pytest tests/unit/test_services/test_auth_service.py

# Run specific test class
pytest tests/unit/test_services/test_auth_service.py::TestPasswordOperations

# Run specific test method
pytest tests/unit/test_services/test_auth_service.py::TestPasswordOperations::test_hash_password_creates_valid_hash
```

## 🧪 Test Categories

### Unit Tests (`tests/unit/`)

Test individual components in isolation:
- **Services**: Business logic testing with mocked dependencies
- **Models**: Pydantic model validation and serialization
- **Auth**: Authentication utilities and dependencies
- **Utils**: Utility functions and helpers

**Characteristics:**
- Fast execution (< 1 second per test)
- No external dependencies
- Use mocking for isolation
- Test both success and failure scenarios

### Integration Tests (`tests/integration/`)

Test component interactions and complete workflows:
- **API**: HTTP endpoint testing with real requests
- **Auth Flow**: Complete authentication workflows
- **Database**: Database operations (when implemented)
- **External**: Third-party service integrations (when implemented)

**Characteristics:**
- Slower execution (may take several seconds)
- Test real component interactions
- Use test database/external services
- Test end-to-end scenarios

## 🔧 Available Fixtures

The `conftest.py` file provides shared fixtures for all tests:

### Basic Fixtures
- `client`: FastAPI test client for HTTP requests
- `auth_service`: Fresh AuthService instance
- `mock_user`: Test user object
- `mock_user_create`: Test user creation data

### Authentication Fixtures
- `valid_token`: Valid JWT token for testing
- `expired_token`: Expired JWT token for error testing
- `authenticated_client`: Test client with auth headers
- `mock_auth_dependency`: Mocked authentication dependency

### Data Fixtures
- `sample_login_data`: Valid login credentials
- `invalid_login_data`: Invalid login credentials for error testing

### Example Usage

```python
def test_login_success(client, sample_login_data):
    """Test successful login"""
    response = client.post("/api/auth/login", json=sample_login_data)
    assert response.status_code == 200

def test_protected_endpoint(authenticated_client):
    """Test protected endpoint access"""
    response = authenticated_client.get("/api/auth/me")
    assert response.status_code == 200
```

## 📊 Test Markers

Use pytest markers to categorize and filter tests:

```python
@pytest.mark.unit
def test_password_hashing():
    """Unit test for password hashing"""
    pass

@pytest.mark.integration
def test_login_endpoint():
    """Integration test for login endpoint"""
    pass

@pytest.mark.slow
def test_heavy_operation():
    """Test that takes a long time"""
    pass
```

Run tests by marker:
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## 🎯 Writing Good Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`
- Use descriptive names: `test_login_success_with_valid_credentials`

### Test Structure (AAA Pattern)
```python
def test_example():
    # Arrange - Set up test data
    user_data = {"email": "test@example.com", "password": "password"}
    
    # Act - Execute the code under test
    result = auth_service.authenticate_user(**user_data)
    
    # Assert - Verify the results
    assert result is not False
    assert result.email == "test@example.com"
```

### Test Coverage Guidelines
- **Unit Tests**: Aim for 90%+ coverage of business logic
- **Integration Tests**: Cover all API endpoints and major workflows
- **Edge Cases**: Test boundary conditions and error scenarios
- **Security**: Test authentication, authorization, and input validation

## 🔍 Debugging Tests

### Running Tests in Debug Mode
```bash
# Run with Python debugger
pytest --pdb

# Run specific test with debugger
pytest --pdb tests/unit/test_services/test_auth_service.py::test_specific_function

# Print output (disable capture)
pytest -s

# Verbose output with details
pytest -vv
```

### Common Issues and Solutions

1. **Import Errors**
   ```bash
   # Ensure you're in the backend directory
   cd /path/to/backend
   
   # Install in development mode
   pip install -e .
   ```

2. **Fixture Not Found**
   - Check `conftest.py` for fixture definitions
   - Ensure fixture is in the correct scope

3. **Authentication Tests Failing**
   - Verify mock users are initialized in `conftest.py`
   - Check token generation uses correct secret key

## 📈 Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: pip install -r requirements.txt -r tests/requirements-test.txt
    - run: pytest --cov=app --cov-report=xml
    - uses: codecov/codecov-action@v3
```

## 🛠️ Development Workflow

### Adding New Tests

1. **For New Features**:
   - Add unit tests for business logic
   - Add integration tests for API endpoints
   - Update fixtures if needed

2. **Test-Driven Development (TDD)**:
   ```bash
   # 1. Write failing test
   pytest tests/unit/test_new_feature.py::test_new_function
   
   # 2. Implement minimum code to pass
   # 3. Refactor and improve
   # 4. Repeat
   ```

3. **Before Committing**:
   ```bash
   # Run all tests
   pytest
   
   # Check coverage
   pytest --cov=app --cov-report=term-missing
   
   # Run linting
   flake8 app/ tests/
   black app/ tests/
   ```

## 🔐 Security Testing

The test suite includes security-focused tests:
- Password handling and hashing
- JWT token validation and expiration
- Input validation and sanitization
- Authentication and authorization flows

### Running Security Tests
```bash
# Run security linting
bandit -r app/

# Check for known vulnerabilities
safety check

# Run auth-specific tests
pytest tests/ -k "auth" -v
```

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pydantic Testing](https://pydantic-docs.helpmanual.io/usage/models/#testing)
- [Python Testing Best Practices](https://realpython.com/python-testing/)

## 🤝 Contributing

When adding new tests:
1. Follow the existing directory structure
2. Use descriptive test names
3. Include both positive and negative test cases
4. Add appropriate fixtures to `conftest.py`
5. Update this README if adding new test categories
6. Ensure all tests pass before submitting PR

---

**Happy Testing! 🎉**
