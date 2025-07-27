"""
Unit Tests Package

This package contains unit tests for individual components of the Cyclo Veda backend.
Unit tests focus on testing individual functions, classes, and methods in isolation.

Structure mirrors the app directory:
- test_services/: Tests for business logic in app/services/
- test_models/: Tests for data models in app/models/
- test_auth/: Tests for authentication components in app/auth/
- test_utils/: Tests for utility functions in app/utils/

Guidelines:
- Each test file should test a single module
- Use mocking to isolate the unit under test
- Test both success and failure scenarios
- Include edge cases and boundary conditions
- Keep tests fast and independent

Run unit tests only: pytest tests/unit/
"""
