"""
Integration Tests Package

This package contains integration tests for the Cyclo Veda backend.
Integration tests focus on testing the interaction between multiple components
and the behavior of the system as a whole.

Structure:
- test_api/: Tests for API endpoints and HTTP interactions
- test_auth_flow/: Tests for complete authentication workflows
- test_database/: Tests for database operations (when implemented)
- test_external/: Tests for external service integrations (when implemented)

Guidelines:
- Test complete user workflows and scenarios
- Test API endpoints with real HTTP requests
- Test error handling and edge cases
- Use realistic test data
- May be slower than unit tests
- Test component interactions

Run integration tests only: pytest tests/integration/
"""
