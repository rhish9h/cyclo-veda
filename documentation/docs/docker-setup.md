# Docker Setup Guide

This guide explains how to run Cyclo Veda using Docker with Traefik reverse proxy.

## Architecture Overview

The Docker setup includes:
- **Frontend**: React app served by Nginx (accessible at `cycloveda.local`)
- **Backend**: FastAPI application (accessible at `api.cycloveda.local`)
- **Traefik**: Reverse proxy handling routing and load balancing
- **Custom Network**: All services communicate through `cyclo-veda-network`

## Prerequisites

- Docker and Docker Compose installed
- Port 80, 443, and 8080 available on your machine
- Admin/sudo access to modify hosts file

## Quick Start

1. **Set up local hostnames** (one-time setup):
   
   **For Mac/Linux:**
   ```bash
   sudo nano /etc/hosts
   ```
   Add these lines:
   ```
   127.0.0.1 cycloveda.local
   127.0.0.1 api.cycloveda.local
   ```
   
   **For Windows:**
   - Open Notepad as Administrator
   - Open `C:\Windows\System32\drivers\etc\hosts`
   - Add the same entries above

2. **Copy environment file**:
   ```bash
   cp .env.example .env
   ```

3. **Build and start all services**:
   ```bash
   docker compose up --build
   ```

4. **Access the application**:
   - Frontend: http://cycloveda.local
   - Backend API: http://api.cycloveda.local
   - Traefik Dashboard: http://localhost:8080

## Services Details

### Traefik (Reverse Proxy)
- **Image**: traefik:v3.0
- **Ports**: 80 (HTTP), 443 (HTTPS), 8080 (Dashboard)
- **Features**: 
  - Automatic service discovery
  - Load balancing
  - Health checks
  - SSL termination (ready for production)

### Backend (FastAPI)
- **Build**: From `./backend/Dockerfile` (Python 3.13-slim)
- **Port**: 8000 (internal)
- **Hostname**: api.cycloveda.local
- **Health Check**: `/health` endpoint with curl
- **Features**:
  - Dedicated health endpoint
  - CORS configured for frontend
  - JWT authentication
  - Non-root user for security

### Frontend (React + Nginx)
- **Build**: From `./frontend/Dockerfile` (multi-stage)
- **Port**: 3000 (internal)
- **Hostname**: cycloveda.local
- **Features**:
  - Optimized production build
  - Gzip compression
  - Security headers
  - SPA routing support

## Development Commands

### Start services in detached mode:
```bash
docker compose up -d
```

### View logs:
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f traefik
```

### Rebuild specific service:
```bash
docker compose build backend
docker compose build frontend
```

### Stop all services:
```bash
docker compose down
```

### Remove all containers and volumes:
```bash
docker compose down -v
```

## Environment Variables

### Backend Variables (.env)
- `SECRET_KEY`: JWT signing key (change in production)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

### Frontend Variables
- `VITE_API_BASE_URL`: Backend API URL (set to `http://api.cycloveda.local`)

## Health Checks

All services include health checks:
- **Backend**: HTTP GET to `/` endpoint
- **Frontend**: HTTP GET to root path
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3

## Security Features

### Production Ready
- Non-root users in containers
- Security headers in Nginx
- CORS properly configured
- Health checks enabled
- Resource limits (can be added)

### SSL/HTTPS (Production)
To enable HTTPS in production, uncomment the SSL sections in `docker-compose.yml` and configure Let's Encrypt:

1. Set your domain in the Traefik command
2. Uncomment certificate resolver configuration
3. Update router labels to use HTTPS

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 80, 443, 8080 are available
2. **Hostname resolution**: Add hostname entries manually to `/etc/hosts` (see Quick Start section)
3. **Build failures**: Check Docker logs and ensure all dependencies are correct

### Debug Commands

```bash
# Check container status
docker compose ps

# Inspect service logs
docker compose logs [service-name]

# Access container shell
docker compose exec backend /bin/bash
docker compose exec frontend /bin/sh

# Check network connectivity
docker network ls
docker network inspect cyclo-veda-network
```

### Performance Monitoring

Access Traefik dashboard at http://localhost:8080 to monitor:
- Service health
- Request metrics
- Load balancing status
- SSL certificate status

## Production Deployment

For production deployment:

1. **Environment**: Update `.env` with production values
2. **SSL**: Configure Let's Encrypt certificates
3. **Secrets**: Use Docker secrets or external secret management
4. **Monitoring**: Add monitoring stack (Prometheus, Grafana)
5. **Backup**: Implement backup strategy for volumes
6. **Security**: Review and harden security settings

## Maintenance

### Updating Services
```bash
# Pull latest images
docker compose pull

# Rebuild and restart
docker compose up --build -d
```

### Cleanup
```bash
# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune
```
