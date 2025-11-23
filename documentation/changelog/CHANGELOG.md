# Changelog

All notable changes to the Cyclo Veda project will be documented in this file.

## [Unreleased]

### Under Development
- Advanced user management features
- Enhanced dashboard functionality
- API documentation improvements

## [0.5.0] - 2025-11-23

### Added
- Complete Settings management system with multi-section interface:
  - Profile information management (name, email, phone)
  - Security settings (password change functionality)
  - App preferences (theme, language, timezone selection)
  - Notification preferences (email, push, marketing toggles)
  - Third-party service connections section
- ConnectionCard component for managing external integrations:
  - Reusable component design for third-party services
  - Connection status display and management
  - Prepared for Strava integration with sync activities toggle
- Enhanced Layout system with improved component architecture:
  - Configurable header/footer display via props
  - Dedicated Header, Footer, and Sidebar subcomponents
  - Flexible layout customization for different page types
- Complete CSS Modules implementation across all components:
  - Full migration from traditional CSS to CSS Modules
  - Scoped styling preventing class name conflicts
  - TypeScript integration with CSS module imports
  - camelCase class naming convention for consistency
- Improved component composition patterns:
  - Better separation of concerns in layout components
  - Reusable component architecture for settings management
  - Enhanced form handling with TypeScript interfaces

### Changed
- Settings page now uses comprehensive state management with typed interfaces
- All styling converted to CSS Modules for better maintainability
- Layout component enhanced with prop-based customization
- Component structure improved with better directory organization

### Infrastructure
- Frontend components now fully utilize CSS Modules architecture
- Settings system ready for backend API integration
- ConnectionCard component prepared for multiple third-party service integrations
- Enhanced Layout system supporting varied page layouts

## [0.4.0] - 2025-09-20

### Added
- Complete Docker containerization with multi-stage builds
- Traefik reverse proxy for service routing and load balancing
- Docker Compose configuration with production-ready setup
- Dedicated `/health` endpoint for proper health monitoring
- Health router: Moved health endpoints from `main.py` to dedicated `app/routers/health.py` for better code organization
- Comprehensive Docker documentation and deployment guide
- Environment configuration with `.env.example`
- Manual hostname setup instructions for Mac and Windows
- Security hardening in Docker containers (non-root users)
- CORS configuration for Docker hostnames
- Content Security Policy (CSP) configuration in Nginx

### Changed
- Backend uses Python 3.9+ compatible Docker image (supports 3.9-3.13)
- Health checks now use curl with dedicated `/health` endpoint instead of Python requests
- Backend CORS origins updated to include Docker hostnames
- Frontend configured to work with containerized backend API
- Removed automated hostname setup script in favor of manual instructions
- Centralized CORS handling at Traefik reverse proxy level for better performance and consistency
- Removed FastAPI CORS middleware to avoid conflicts with Traefik CORS configuration

### Fixed
- Frontend Docker build now installs all dependencies (including devDependencies) needed for TypeScript compilation
- Frontend now correctly uses `api.cycloveda.local` for API calls in Docker environment via build-time configuration
- Content Security Policy to allow API connections from frontend
- CORS headers in Traefik to properly handle preflight requests

### Removed  
- `setup-hosts.sh` script (replaced with manual setup instructions)

### Infrastructure
- Frontend: React app served by Nginx on `cycloveda.local`
- Backend: FastAPI application on `api.cycloveda.local`
- Reverse Proxy: Traefik v3.0 with automatic service discovery
- Network: Custom Docker network for service isolation

## [0.3.0] - 2025-08-18

### Added
- Login interface CSS improvements and visual enhancements
- Enhanced UI/UX with better styling and user experience
- Comprehensive project documentation framework
- ADR (Architectural Decision Records) system
- JWT Authentication ADR
- API reference documentation
- Architecture documentation
- Authentication guide
- Development guide

### Changed
- Refined login page styling for better visual appeal
- Enhanced CSS organization and maintainability
- Improved documentation structure and organization

## [0.2.0] - 2025-07-26

### Added
- Complete React + TypeScript frontend application
- FastAPI backend with clean architecture
- JWT-based authentication system with secure token handling
- Comprehensive pytest testing framework:
  - Unit tests for authentication services and user models
  - Integration tests for API endpoints
  - 98%+ test coverage with coverage reporting
- Case-sensitive email authentication for enhanced security
- Advanced error handling and validation systems
- Production-ready development tooling:
  - Backend: Black, isort, flake8, mypy configuration
  - Frontend: ESLint, Prettier, TypeScript strict mode
- Component-based architecture:
  - Authentication components (Login, ProtectedRoute, PublicRoute)
  - Layout components (Dashboard)
  - Error boundary implementation
- Utility systems:
  - Centralized constants for API endpoints and configuration
  - Storage, validation, and async utility functions
  - Type-safe configuration management

### Changed
- Implemented clean architecture patterns in backend
- Enhanced security with proper password hashing and token validation
- Improved project structure with separation of concerns

### Fixed
- Authentication flow edge cases
- Password hashing compatibility issues
- Token validation security improvements

## [0.1.0] - 2025-07-19

### Added
- Initial project boilerplate and structure
- Basic FastAPI setup
- Initial React application scaffolding
- Git repository initialization
- Basic project configuration

[Unreleased]: https://github.com/rhish9h/cyclo-veda/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/rhish9h/cyclo-veda/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/rhish9h/cyclo-veda/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/rhish9h/cyclo-veda/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/rhish9h/cyclo-veda/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/rhish9h/cyclo-veda/releases/tag/v0.1.0
