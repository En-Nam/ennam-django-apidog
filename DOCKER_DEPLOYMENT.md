# Docker Deployment Guide

## Overview

Using Docker eliminates environment variable management issues and provides a reproducible, isolated environment for running `ennam-django-apidog`.

## Why Docker?

### Problem Solved

**Before Docker:**
```bash
# Manual environment setup required every time
export APIDOG_PROJECT_ID=1133189
export APIDOG_TOKEN=your-token
python manage.py apidog push
# If terminal restarts, must export again ❌
```

**With Docker:**
```bash
# Environment loaded automatically from .env.local
docker-compose up
docker-compose exec django python manage.py apidog push
# Environment persists for container lifetime ✅
```

### Benefits

1. ✅ **No manual environment setup** - `.env.local` loaded automatically
2. ✅ **Consistent across machines** - Same Python, dependencies everywhere
3. ✅ **Isolated environment** - No system pollution
4. ✅ **Easy deployment** - Works on any machine with Docker
5. ✅ **Production-ready** - Use same containers in prod

## Quick Start

### Step 1: Install Docker

- **Windows/Mac**: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: `apt-get install docker.io docker-compose`

### Step 2: Setup .env.local

```bash
cd test_django_project
cat > .env.local << 'EOF'
APIDOG_PROJECT_ID=1133189
APIDOG_TOKEN=your-token
DJANGO_SETTINGS_MODULE=project.settings
EOF
```

### Step 3: Build and Run

```bash
# Build image
docker-compose build

# Start container
docker-compose up

# In new terminal, run commands
docker-compose exec django python manage.py apidog export
docker-compose exec django python manage.py apidog push
```

## Development Workflow

### File Structure

```
test_django_project/
├── Dockerfile              # Container definition
├── docker-compose.yml      # Services configuration
├── requirements.txt        # Python dependencies
├── .env.local             # Credentials (in .gitignore)
├── manage.py
├── project/
│   ├── settings.py        # Uses os.getenv() for config
│   ├── urls.py
│   └── wsgi.py
└── apidog/
    └── openapi_schema_latest.json
```

### Commands

```bash
# Start development server
docker-compose up

# Run management commands
docker-compose exec django python manage.py apidog export
docker-compose exec django python manage.py apidog push
docker-compose exec django python manage.py migrate
docker-compose exec django python manage.py createsuperuser

# Interactive shell
docker-compose exec django bash

# View logs
docker-compose logs -f django

# Stop container
docker-compose down
```

## How Environment Variables Work in Docker

### docker-compose.yml

```yaml
services:
  django:
    env_file:
      - .env.local                # Load from .env.local ✅
    environment:
      - PYTHONUNBUFFERED=1        # Additional env vars
```

### Flow

```
.env.local (file on host)
    ↓
docker-compose.yml env_file directive
    ↓
Container environment variables
    ↓
Django os.getenv() reads values ✅
    ↓
APIDOG_SETTINGS gets credentials ✅
    ↓
apidog command uses real token ✅
```

**Result**: Environment variables persist for entire container lifetime! No re-exporting needed.

## Production Deployment

### Using Docker in Production

For production, use these practices:

#### 1. Use Environment Variables (Not .env.local)

```bash
# Set in container orchestration (Kubernetes, ECS, etc.)
docker run \
  -e APIDOG_PROJECT_ID=1133189 \
  -e APIDOG_TOKEN=your-token \
  -e DJANGO_SETTINGS_MODULE=project.settings \
  your-image:latest
```

#### 2. Use Secrets Management

```yaml
# docker-compose production
services:
  django:
    environment:
      - APIDOG_PROJECT_ID=${APIDOG_PROJECT_ID}
      - APIDOG_TOKEN=${APIDOG_TOKEN}
    # Don't use env_file in production
```

Then provide from secrets:
```bash
export APIDOG_PROJECT_ID=$(aws secretsmanager get-secret-value --secret-id apidog/project-id)
export APIDOG_TOKEN=$(aws secretsmanager get-secret-value --secret-id apidog/token)
docker-compose up
```

#### 3. Use Docker Secrets (Swarm)

```yaml
services:
  django:
    secrets:
      - apidog_token
    environment:
      - APIDOG_TOKEN_FILE=/run/secrets/apidog_token

secrets:
  apidog_token:
    external: true
```

#### 4. Kubernetes

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: django-app
spec:
  containers:
  - name: django
    image: your-image:latest
    env:
    - name: APIDOG_PROJECT_ID
      valueFrom:
        secretKeyRef:
          name: apidog-secrets
          key: project-id
    - name: APIDOG_TOKEN
      valueFrom:
        secretKeyRef:
          name: apidog-secrets
          key: token
```

## Advanced Configuration

### Custom Django Settings for Docker

Create `project/settings_docker.py`:

```python
from .settings import *

# Docker-specific overrides
DEBUG = False
ALLOWED_HOSTS = ['*']

# Database in Docker
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',  # Docker service name
        'PORT': '5432',
    }
}

# APIDOG settings
APIDOG_SETTINGS = {
    'PROJECT_ID': os.getenv('APIDOG_PROJECT_ID'),
    'TOKEN': os.getenv('APIDOG_TOKEN'),
    'OUTPUT_DIR': os.path.join(BASE_DIR, 'apidog'),
}
```

Then in docker-compose.yml:
```yaml
environment:
  - DJANGO_SETTINGS_MODULE=project.settings_docker
```

### Multi-stage Dockerfile for Production

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
RUN useradd -m -u 1000 django && chown -R django:django /app
USER django

EXPOSE 8000
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Docker Compose with Database

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=django_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  django:
    build: .
    command: >
      sh -c "python manage.py migrate &&
             gunicorn project.wsgi:application --bind 0.0.0.0:8000"
    environment:
      - DJANGO_SETTINGS_MODULE=project.settings_docker
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/django_db
      - APIDOG_PROJECT_ID=${APIDOG_PROJECT_ID}
      - APIDOG_TOKEN=${APIDOG_TOKEN}
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - .:/app

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - django

volumes:
  postgres_data:
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs django

# Rebuild image
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Can't connect to APIDOG API

```bash
# Verify env vars are loaded
docker-compose exec django bash
env | grep APIDOG

# Test connection
python -c "import os; print(os.getenv('APIDOG_TOKEN'))"
```

### Volume permissions issues

```bash
# Fix ownership
docker-compose exec django chown -R django:django /app

# Or use explicit user in docker-compose.yml
user: "1000:1000"
```

### Port already in use

```yaml
# Change in docker-compose.yml
ports:
  - "8001:8000"  # Use different host port
```

## Performance Optimization

### Reduce Image Size

```dockerfile
# Use slim or alpine variants
FROM python:3.11-slim

# Multi-stage builds
FROM python:3.11-slim as builder
# ... build steps ...

FROM python:3.11-slim
# ... copy only needed files ...
```

### Build Caching

```dockerfile
# Order matters - change infrequently modified files last
COPY requirements.txt .          # Cache this
RUN pip install -r requirements.txt

COPY . .                         # Copy app (changes frequently)
```

### Resource Limits

```yaml
services:
  django:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

## Comparison: Docker vs Manual Setup

| Aspect | Manual | Docker |
|--------|--------|--------|
| Env vars setup | ❌ Manual export | ✅ Auto from .env.local |
| Persistence | ❌ Lost when terminal closes | ✅ Persists in container |
| Dependency conflicts | ❌ Possible with system libs | ✅ Isolated environment |
| Cross-machine | ❌ May differ | ✅ Exact same |
| Production deployment | ❌ Complex setup | ✅ Just push image |
| Learning curve | ✅ Simple | ⚠️ Medium (worth learning) |

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [12 Factor App](https://12factor.net/)

## Next Steps

1. Install Docker: https://docs.docker.com/get-docker/
2. Read test_django_project/[DOCKER_SETUP.md](./test_django_project/DOCKER_SETUP.md)
3. Build and test: `docker-compose build && docker-compose up`
4. Run commands: `docker-compose exec django python manage.py apidog push`

---

**Last Updated**: December 3, 2025
**Status**: Production-ready
