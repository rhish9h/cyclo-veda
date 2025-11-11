# ADR: Case-Sensitive Email Authentication

**Date:** 2025-07-26

## Status
Accepted

## Context

During the implementation of the authentication system, we needed to decide how to handle email addresses for user authentication. Email addresses have unique characteristics that affect security, user experience, and data integrity:

### Email Address Standards
- **RFC 5321**: Email local parts (before @) are technically case-sensitive
- **RFC 5322**: Email domain parts (after @) are case-insensitive
- **Real-world practice**: Most email providers treat addresses as case-insensitive
- **User expectations**: Users expect `User@Example.com` and `user@example.com` to be the same

### Security Considerations
- **Account enumeration**: Case-insensitive matching could reveal account existence
- **Duplicate accounts**: Case variations could create multiple accounts for same user
- **Phishing risks**: Similar-looking emails with different cases could confuse users
- **Database uniqueness**: Need to prevent `user@example.com` and `User@Example.com` as separate accounts

### Initial Implementation
The first version used Pydantic's `EmailStr` type for the `UserLogin` model, which automatically normalizes emails to lowercase. This caused issues:
- Users couldn't login with the exact email they registered with
- Inconsistent behavior between registration and login
- Confusion during testing and development

## Decision

We implemented **case-sensitive email authentication** with the following approach:

### Login Model
```python
class UserLogin(BaseModel):
    """Model for user login credentials.
    
    Note: Uses str instead of EmailStr for case-sensitive email authentication.
    """
    email: str = Field(..., example="user@example.com", description="Email address (case-sensitive)")
    password: str = Field(..., example="securePassword123!")
```

### Authentication Service
```python
def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
    """Authenticate user with case-sensitive email matching.
    
    Args:
        email: User's email (case-sensitive)
        password: User's password
        
    Returns:
        UserInDB if authentication successful, None otherwise
    """
    user = self.get_user_by_email(email)  # Exact match
    if not user:
        return None
    if not self.verify_password(password, user.hashed_password):
        return None
    return user
```

### Key Characteristics
1. **Exact matching**: Email must match exactly as stored in database
2. **No normalization**: Preserve email case from user input
3. **Consistent behavior**: Same matching logic for registration and login
4. **Clear documentation**: Explicitly document case-sensitive behavior

## Benefits

### Security
- **Prevents account enumeration**: Attackers can't probe with case variations
- **Explicit behavior**: No hidden normalization that could cause confusion
- **Audit trail**: Exact email preserved in logs and database
- **Consistent validation**: Same rules across all authentication flows

### User Experience
- **Predictable**: Users get exactly what they entered
- **Clear error messages**: Failed login shows exact email that was attempted
- **No surprises**: No hidden transformations of user input
- **Testing clarity**: Test cases use exact email strings

### Development
- **Simpler logic**: No normalization edge cases to handle
- **Easier debugging**: See exact values users entered
- **Clear tests**: Test exact string matching
- **Explicit contracts**: API documentation shows case-sensitive requirement

## Tradeoffs

### Advantages
- Simple implementation with no normalization logic
- Explicit and predictable behavior
- Better security through exact matching
- Easier to test and debug
- Clear API contracts

### Disadvantages
- Users must remember exact case of their email
- Potential UX friction if users enter wrong case
- Doesn't match common email provider behavior
- Could lead to support requests about login failures

### Mitigations for Disadvantages
1. **Clear UI messaging**: Login form shows "Email (case-sensitive)"
2. **Error messages**: Provide helpful feedback on failed login
3. **Future enhancement**: Could add case-insensitive lookup with warning
4. **Documentation**: Clearly document behavior in API docs

## Alternatives Considered

### 1. Case-Insensitive with Lowercase Normalization
```python
email: EmailStr  # Automatically lowercases
```
**Rejected because:**
- Hidden behavior not obvious to users
- Could cause confusion when email doesn't match what user entered
- Pydantic's EmailStr normalization is opaque
- Harder to debug when normalization happens automatically

### 2. Case-Insensitive with Database Collation
```sql
CREATE UNIQUE INDEX idx_email ON users (LOWER(email));
```
**Rejected because:**
- Adds database-specific logic
- Not portable across databases
- Requires migration and index management
- Complexity not justified for current scale

### 3. Store Both Original and Normalized
```python
email: str  # Original case
email_normalized: str  # Lowercase for lookup
```
**Rejected because:**
- Data duplication
- Synchronization complexity
- More storage required
- Over-engineering for current needs

### 4. Case-Insensitive Matching in Code
```python
def get_user_by_email(self, email: str):
    for user in users:
        if user.email.lower() == email.lower():
            return user
```
**Rejected because:**
- Performance issues with large user bases
- Doesn't prevent duplicate accounts with different cases
- Still need database constraints
- Inefficient compared to exact matching

## Implementation Details

### Changes Made
1. **UserLogin model**: Changed `email: EmailStr` to `email: str`
2. **Documentation**: Added comments explaining case-sensitive behavior
3. **Tests**: Updated to use exact email matching
4. **API docs**: OpenAPI schema shows string type for email

### Test Coverage
```python
def test_login_case_sensitive():
    """Test that login is case-sensitive for email."""
    # Register with specific case
    register_user(email="User@Example.com", password="password")
    
    # Login with exact case - should succeed
    assert login(email="User@Example.com", password="password")
    
    # Login with different case - should fail
    assert not login(email="user@example.com", password="password")
```

## Consequences

### Positive
- Clear and predictable authentication behavior
- Simpler codebase without normalization logic
- Better security through exact matching
- Easier testing and debugging
- Explicit API contracts

### Negative
- Users must remember exact email case
- Potential UX friction for some users
- Doesn't match common email provider behavior
- May require user education

### Neutral
- Team must document case-sensitive requirement
- UI should indicate case-sensitive behavior
- Support team should be aware of this design choice

## Future Considerations

### Potential Enhancements
1. **Case-insensitive lookup with warning**: Allow login with any case but warn user
2. **Email verification**: Send verification email to confirm ownership
3. **Account recovery**: Password reset flow could handle case variations
4. **Analytics**: Track how often users fail due to case mismatch
5. **Progressive enhancement**: Start strict, relax if UX issues arise

### Migration Path
If we decide to switch to case-insensitive in the future:
1. Add normalized email field to database
2. Populate normalized field for existing users
3. Update authentication to use normalized field
4. Maintain backward compatibility during transition
5. Update documentation and tests

## Related Decisions

- [2025-08-18 JWT Authentication](2025-08-18-jwt-authentication.md) - Authentication mechanism
- [2025-07-26 Clean Architecture](2025-07-26-clean-architecture-patterns.md) - Service layer handles authentication
- [2025-07-26 Pytest Testing Framework](2025-07-26-pytest-testing-framework.md) - Tests validate case-sensitive behavior

## References

- [RFC 5321 - SMTP](https://tools.ietf.org/html/rfc5321)
- [RFC 5322 - Internet Message Format](https://tools.ietf.org/html/rfc5322)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

This decision prioritizes simplicity, security, and explicit behavior over matching common email provider conventions. The case-sensitive approach provides a solid foundation that can be evolved if user feedback indicates UX issues.
