# ADR: Docker Containerization with Traefik Reverse Proxy

**Date:** 2025-09-20

## Status
Accepted

## Context

The Cyclo Veda project needs a standardized, reproducible deployment strategy that:
- Simplifies local development setup
- Provides production-ready infrastructure
- Enables easy scaling and service discovery
- Maintains security best practices
- Supports multiple developers working on the project

The current setup requires manual installation of Node.js, Python, and configuration of multiple services, making onboarding difficult for new developers.

## Decision

We will implement a complete Docker containerization strategy with:

1. **Docker Containers**: Separate containers for frontend and backend
2. **Traefik Reverse Proxy**: Modern reverse proxy for routing and load balancing  
3. **Custom Hostnames**: Local development using `cycloveda.local` and `api.cycloveda.local`
4. **Multi-stage Builds**: Optimized production-ready container images
5. **Security Hardening**: Non-root users, security headers, health checks

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Traefik      │    │   Frontend      │    │   Backend       │
│   (Reverse     │◄──►│   (React +      │◄──►│   (FastAPI)     │
│    Proxy)      │    │    Nginx)       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
   Port 80/443            cycloveda.local      api.cycloveda.local
```

## Implementation Details

### Frontend Container
- **Base Image**: Node.js 18 Alpine (multi-stage)
- **Production**: Nginx Alpine with security headers
- **Port**: 3000 (internal)
- **Hostname**: cycloveda.local
- **Features**: Gzip compression, SPA routing, static asset caching

### Backend Container  
- **Base Image**: Python 3.13 Slim (matches local development)
- **Port**: 8000 (internal)
- **Hostname**: api.cycloveda.local
- **Features**: Dedicated health endpoints, curl-based health checks, non-root user, clean router architecture

### Traefik Configuration
- **Version**: v3.0
- **Features**: 
  - Automatic service discovery via Docker labels
  - HTTP/HTTPS routing
  - Health checks and load balancing  
  - Dashboard for monitoring
  - Ready for Let's Encrypt SSL certificates

### Security Measures
- Non-root users in all containers
- Security headers in Nginx
- CORS properly configured
- Resource isolation via custom Docker network
- Health checks for all services

## Benefits

1. **Developer Experience**: Single command setup (`docker-compose up`)
2. **Consistency**: Identical environments across development/production
3. **Scalability**: Easy to add new services and scale existing ones
4. **Security**: Hardened containers with security best practices
5. **Monitoring**: Built-in health checks and Traefik dashboard
6. **Production Ready**: SSL/HTTPS ready, optimized builds

## Tradeoffs

### Advantages
- Simplified onboarding and development setup
- Production-parity environments
- Built-in service discovery and load balancing
- Easy horizontal scaling capabilities
- Comprehensive monitoring and logging

### Disadvantages  
- Additional complexity for simple changes
- Docker learning curve for team members
- Resource overhead of running multiple containers
- Debugging can be more complex in containerized environment

## Alternatives Considered

1. **Manual Setup**: Continue with manual installation of dependencies
   - Rejected: Inconsistent environments, difficult onboarding

2. **Docker without Reverse Proxy**: Simple container setup
   - Rejected: Lacks production readiness, no load balancing

3. **Kubernetes**: Full orchestration platform
   - Rejected: Overkill for current project size, adds unnecessary complexity

4. **Other Reverse Proxies** (nginx-proxy, HAProxy):
   - Rejected: Traefik provides better Docker integration and modern features

## Implementation Plan

1. ✅ Create Dockerfiles for frontend and backend
2. ✅ Configure docker-compose.yml with Traefik
3. ✅ Set up local hostname configuration (manual approach)
4. ✅ Update CORS configuration for new hostnames
5. ✅ Create comprehensive documentation
6. ✅ Update project README and changelog
7. ✅ Implement dedicated health endpoints with proper architecture
8. ✅ Configure build-time environment variables for frontend API URLs
9. ✅ Fix TypeScript compilation in Docker builds
10. ✅ Fix Content Security Policy to allow API connections

## Future Enhancements

- SSL/TLS certificates with Let's Encrypt for production
- Container resource limits and reservations
- Monitoring stack integration (Prometheus, Grafana)
- Database containerization when needed
- CI/CD pipeline integration
- Multi-environment configuration (dev, staging, prod)

## Consequences

- All developers will need Docker installed
- Local development now uses custom hostnames
- Deployment strategy shifts to container-based
- Infrastructure as Code approach adopted
- Foundation set for microservices architecture if needed

This decision establishes a robust, scalable infrastructure foundation that will support the project's growth while maintaining developer productivity and operational excellence.

## Post-Implementation Fixes

### Content Security Policy (CSP) Issue
**Issue**: Frontend login page unable to connect to API due to CSP blocking cross-domain requests.
**Root Cause**: Nginx CSP header only allowed `default-src 'self'` without explicit `connect-src` directive.
**Solution**: Added `connect-src 'self' http://api.cycloveda.local;` to CSP header in `frontend/nginx.conf`.
**Files Modified**: `frontend/nginx.conf` line 37

### CORS Headers Issue  
**Issue**: Browser blocking API requests due to missing `Access-Control-Allow-Headers` in preflight responses.
**Root Cause**: Traefik reverse proxy CORS middleware was missing `accesscontrolallowheaders` configuration, overriding FastAPI CORS.
**Solution**: Added `accesscontrolallowheaders` directive to Traefik CORS middleware and removed FastAPI CORS middleware to avoid conflicts.
**Architectural Decision**: CORS is handled at the Traefik level for centralized control and better performance.
**Files Modified**: 
- `docker-compose.yml` Traefik CORS configuration (line 54)
- `backend/main.py` removed FastAPI CORS middleware
