# ADR: Clean Architecture Patterns

**Date:** 2025-07-26

## Status
Accepted

## Context

As Cyclo Veda evolved from a simple boilerplate to a full-featured application, we needed a scalable architecture that would:
- Support long-term maintainability and resumability
- Enable clear separation of concerns
- Facilitate testing and mocking
- Allow independent evolution of frontend and backend
- Support multiple developers working simultaneously
- Follow industry best practices for modern web applications

The initial implementation had business logic mixed with routing, making testing difficult and violating single responsibility principles.

## Decision

We adopted clean architecture patterns for both frontend and backend, establishing clear boundaries and responsibilities:

### Backend Architecture (FastAPI)

#### Layer Structure
```
app/
├── auth/
│   └── dependencies.py      # Auth middleware & dependencies
├── models/
│   ├── user.py             # Pydantic models (data structures)
│   └── token.py            # Token models
├── routers/
│   ├── auth.py             # API endpoints (presentation layer)
│   └── health.py           # Health check endpoints
├── services/
│   └── auth_service.py     # Business logic (service layer)
└── utils/                  # Shared utilities
```

#### Responsibilities

**Models Layer** (`app/models/`)
- Define data structures using Pydantic
- Validation rules and constraints
- Type safety and serialization
- No business logic

**Services Layer** (`app/services/`)
- Business logic implementation
- Data transformation and processing
- External service integration
- Independent of HTTP/routing concerns

**Routers Layer** (`app/routers/`)
- HTTP endpoint definitions
- Request/response handling
- Input validation (delegated to Pydantic)
- Calls service layer for business logic

**Auth Layer** (`app/auth/`)
- Authentication middleware
- Dependency injection for auth
- Token validation
- User context management

### Frontend Architecture (React + TypeScript)

#### Component Structure
```
src/
├── components/
│   ├── auth/               # Authentication components
│   │   ├── Login.tsx
│   │   ├── ProtectedRoute.tsx
│   │   └── PublicRoute.tsx
│   └── layout/             # Layout components
│       └── Dashboard.tsx
├── hooks/
│   └── useAuth.ts          # Custom React hooks
├── services/
│   └── authService.ts      # API communication layer
├── types/
│   └── auth.ts             # TypeScript type definitions
├── constants/
│   └── index.ts            # Application constants
└── utils/
    ├── index.ts            # Utility functions
    └── errorHandler.ts     # Error handling
```

#### Responsibilities

**Components** (`src/components/`)
- UI rendering and user interaction
- Local state management
- Event handling
- Delegate business logic to hooks/services

**Hooks** (`src/hooks/`)
- Reusable stateful logic
- Component lifecycle management
- State management (auth, data fetching)
- Bridge between components and services

**Services** (`src/services/`)
- API communication
- HTTP request/response handling
- Data transformation for API
- No UI logic

**Types** (`src/types/`)
- TypeScript interfaces and types
- Shared type definitions
- API contract definitions

**Constants** (`src/constants/`)
- Configuration values
- API endpoints
- Route paths
- UI constants

**Utils** (`src/utils/`)
- Pure utility functions
- Error handling
- Validation helpers
- No side effects

### Development Tooling

**Backend**
- **Black**: Code formatting (88 char line length)
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Static type checking
- **pytest**: Testing framework

**Frontend**
- **Prettier**: Code formatting
- **ESLint**: Linting with TypeScript support
- **TypeScript**: Static type checking (strict mode)
- **Vite**: Build tooling

## Benefits

### Maintainability
- Clear file organization makes code easy to find
- Single responsibility principle reduces complexity
- Changes isolated to specific layers
- Easy to understand for new developers

### Testability
- Service layer can be tested independently
- Easy to mock dependencies
- Clear boundaries enable unit testing
- Integration tests focus on layer interactions

### Scalability
- New features follow established patterns
- Easy to add new routers/services/components
- Horizontal scaling through separation of concerns
- Multiple developers can work without conflicts

### Type Safety
- Pydantic models validate backend data
- TypeScript ensures frontend type correctness
- Shared contracts between layers
- Compile-time error detection

### Code Quality
- Automated formatting ensures consistency
- Linting catches common errors
- Type checking prevents runtime errors
- Testing framework validates correctness

## Tradeoffs

### Advantages
- Clear separation of concerns
- Highly testable and maintainable
- Scalable architecture for growth
- Industry-standard patterns
- Strong type safety

### Disadvantages
- More files and folders to navigate
- Initial learning curve for team
- Potential over-engineering for simple features
- More boilerplate code

## Alternatives Considered

1. **Monolithic Structure**
   - Rejected: Doesn't scale, hard to test, tight coupling

2. **MVC Pattern**
   - Rejected: Less clear separation, controllers often become bloated

3. **Microservices**
   - Rejected: Overkill for current scale, adds deployment complexity

4. **Feature-based Structure**
   - Considered: Good for large apps, but layer-based is clearer for current size

## Implementation Details

### Dependency Flow

**Backend**
```
Router → Service → Model
  ↓        ↓
Auth    External
Deps    Services
```

**Frontend**
```
Component → Hook → Service → API
    ↓        ↓
  Types   Utils
```

### Example: Authentication Flow

**Backend**
1. Router (`auth.py`) receives login request
2. Validates input using Pydantic model (`UserLogin`)
3. Calls service layer (`auth_service.authenticate_user()`)
4. Service validates credentials and generates token
5. Router returns token in response

**Frontend**
1. Component (`Login.tsx`) handles form submission
2. Calls hook (`useAuth.login()`)
3. Hook calls service (`authService.login()`)
4. Service makes API request
5. Hook updates auth state
6. Component re-renders with new state

### Code Organization Principles

1. **Single Responsibility**: Each file has one clear purpose
2. **Dependency Inversion**: Depend on abstractions, not implementations
3. **Open/Closed**: Open for extension, closed for modification
4. **Interface Segregation**: Small, focused interfaces
5. **DRY (Don't Repeat Yourself)**: Shared logic in utils/services

## Consequences

### Positive
- Codebase is highly maintainable and resumable
- New features follow clear patterns
- Testing is straightforward and comprehensive
- Onboarding new developers is easier
- Code reviews focus on business logic, not structure

### Negative
- More files to navigate initially
- Requires discipline to maintain patterns
- Simple changes may touch multiple files
- Learning curve for clean architecture concepts

### Neutral
- Team must agree on and follow patterns
- Documentation becomes critical
- Code reviews enforce architectural decisions

## Future Enhancements

- Repository pattern for data access (when database is added)
- Domain-driven design for complex business logic
- Event-driven architecture for async operations
- GraphQL layer for flexible API queries
- Shared type definitions between frontend/backend

## Related Decisions

- [2025-07-26 Pytest Testing Framework](2025-07-26-pytest-testing-framework.md) - Test structure mirrors architecture
- [2025-08-18 JWT Authentication](2025-08-18-jwt-authentication.md) - Implemented using service layer
- [2025-09-20 Docker Containerization](2025-09-20-docker-containerization.md) - Deployment strategy

## References

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [React Component Patterns](https://reactpatterns.com/)

This architectural decision establishes a solid foundation for long-term development, ensuring the Cyclo Veda codebase remains maintainable, testable, and scalable as it grows.
