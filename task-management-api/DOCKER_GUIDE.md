# 🐳 Docker Deployment Guide

## Overview
This guide explains how to run the Task Management API with all its dependencies (Redis, Celery) using Docker and Docker Compose.

---

## 📦 What's Included

The Docker setup includes **4 services**:

1. **Redis** - Cache and message broker
2. **Flask API** - Main application server
3. **Celery Worker** - Background task processor
4. **Celery Beat** - Scheduled task scheduler

---

## 🚀 Quick Start

### Prerequisites
- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (included with Docker Desktop)

### 1. Clone and Navigate
```bash
cd task-management-api
```

### 2. Configure Environment (Optional)
```bash
# Copy example env file
cp .env.example .env

# Edit .env if you want to configure email
nano .env
```

### 3. Start All Services
```bash
docker-compose up -d
```

### 4. Verify Services
```bash
# Check all services are running
docker-compose ps

# Check logs
docker-compose logs -f
```

### 5. Access the API
```bash
# API is available at
http://localhost:5003

# Health check
curl http://localhost:5003/api/auth/health

# Swagger docs
http://localhost:5003/apidocs
```

---

## 📋 Docker Compose Services

### Service Overview
```yaml
services:
  redis:        # Port 6379
  api:          # Port 5003
  celery-worker # No exposed port
  celery-beat   # No exposed port
```

### Service Details

**1. Redis**
- **Image**: `redis:7-alpine`
- **Port**: `6379`
- **Purpose**: Cache and message broker
- **Data**: Persisted in `redis_data` volume
- **Health Check**: `redis-cli ping`

**2. Flask API**
- **Build**: From `Dockerfile`
- **Port**: `5003`
- **Purpose**: Main REST API
- **Health Check**: `curl http://localhost:5003/api/auth/health`
- **Depends On**: Redis

**3. Celery Worker**
- **Build**: From `Dockerfile`
- **Purpose**: Process background tasks
- **Depends On**: Redis, API
- **Tasks**: Email, reports, etc.

**4. Celery Beat**
- **Build**: From `Dockerfile`
- **Purpose**: Schedule periodic tasks
- **Depends On**: Redis, API
- **Tasks**: Reminders, cleanup

---

## 🔧 Docker Commands

### Start Services
```bash
# Start all services in background
docker-compose up -d

# Start specific service
docker-compose up -d api

# Start with logs visible
docker-compose up
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop specific service
docker-compose stop api
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f celery-worker
docker-compose logs -f redis

# Last 100 lines
docker-compose logs --tail=100 api
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart api
docker-compose restart celery-worker
```

### Rebuild
```bash
# Rebuild all images
docker-compose build

# Rebuild specific service
docker-compose build api

# Rebuild and start
docker-compose up -d --build
```

---

## 🔍 Service Status

### Check Running Services
```bash
docker-compose ps
```

Expected output:
```
NAME                      STATUS    PORTS
task-api-redis           Up        0.0.0.0:6379->6379/tcp
task-api-flask           Up        0.0.0.0:5003->5003/tcp
task-api-celery-worker   Up
task-api-celery-beat     Up
```

### Check Health
```bash
# API health
curl http://localhost:5003/api/auth/health

# Redis health
docker-compose exec redis redis-cli ping

# Celery worker status
docker-compose exec celery-worker celery -A celery_worker.celery inspect active
```

---

## 🗄️ Database Management

### Access Database
```bash
# Enter API container
docker-compose exec api bash

# Inside container
ls instance/  # Check database file
python
>>> from app import db, create_app
>>> app = create_app()
>>> with app.app_context():
...     # Run database commands
```

### Run Migrations
```bash
# Inside API container
docker-compose exec api flask db upgrade

# Or during build
docker-compose exec api python -c "from app import db, create_app; app = create_app(); app.app_context().push(); db.create_all()"
```

### Backup Database
```bash
# Copy database file from container
docker cp task-api-flask:/app/instance/dev.db ./backup.db
```

---

## 📊 Monitoring

### Redis Monitoring
```bash
# Enter Redis container
docker-compose exec redis redis-cli

# Inside Redis CLI
PING                    # Check connection
INFO memory             # Memory usage
KEYS *                  # List all keys
MONITOR                 # Watch commands in real-time
```

### Celery Monitoring
```bash
# Active tasks
docker-compose exec celery-worker celery -A celery_worker.celery inspect active

# Registered tasks
docker-compose exec celery-worker celery -A celery_worker.celery inspect registered

# Worker stats
docker-compose exec celery-worker celery -A celery_worker.celery inspect stats
```

### Container Stats
```bash
# Resource usage
docker stats

# Specific container
docker stats task-api-flask
```

---

## 🔧 Configuration

### Environment Variables

**Flask API:**
```bash
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=sqlite:///instance/dev.db
REDIS_HOST=redis
REDIS_PORT=6379
CELERY_BROKER_URL=redis://redis:6379/0
```

**Email (Optional):**
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Modify docker-compose.yml
```yaml
services:
  api:
    environment:
      - FLASK_ENV=production  # Change to production
      - FLASK_DEBUG=0         # Disable debug
```

---

## 🧪 Testing with Docker

### Run Tests
```bash
# Run tests inside container
docker-compose exec api pytest

# Run with coverage
docker-compose exec api pytest --cov=app --cov-report=term-missing

# Run specific test
docker-compose exec api pytest tests/test_tasks.py
```

### Interactive Shell
```bash
# Python shell
docker-compose exec api python

# Flask shell
docker-compose exec api flask shell

# Bash shell
docker-compose exec api bash
```

---

## 🐛 Troubleshooting

### Service Won't Start

**Check logs:**
```bash
docker-compose logs api
docker-compose logs redis
```

**Common issues:**
- Port already in use: Change port in `docker-compose.yml`
- Redis not ready: Wait for health check to pass
- Permission issues: Check file permissions

### Redis Connection Failed

```bash
# Check Redis is running
docker-compose ps redis

# Test connection
docker-compose exec api python -c "import redis; r = redis.Redis(host='redis', port=6379); print(r.ping())"
```

### Celery Tasks Not Running

```bash
# Check worker logs
docker-compose logs celery-worker

# Verify worker is connected
docker-compose exec celery-worker celery -A celery_worker.celery inspect ping

# Check task queue
docker-compose exec redis redis-cli LLEN celery
```

### Database Issues

```bash
# Recreate database
docker-compose exec api python -c "from app import db, create_app; app = create_app(); app.app_context().push(); db.drop_all(); db.create_all()"

# Check database file
docker-compose exec api ls -la instance/
```

### Container Keeps Restarting

```bash
# Check exit code
docker-compose ps

# View full logs
docker-compose logs --tail=200 api

# Check health
docker inspect task-api-flask | grep -A 10 Health
```

---

## 🔄 Development Workflow

### Code Changes
```bash
# Code changes are auto-reloaded (volume mounted)
# Just edit files locally, Flask will reload

# If you change requirements.txt:
docker-compose down
docker-compose build
docker-compose up -d
```

### Add New Dependencies
```bash
# 1. Add to requirements.txt
echo "new-package==1.0.0" >> requirements.txt

# 2. Rebuild
docker-compose build api celery-worker celery-beat

# 3. Restart
docker-compose up -d
```

### Database Migrations
```bash
# Create migration
docker-compose exec api flask db migrate -m "Add new field"

# Apply migration
docker-compose exec api flask db upgrade
```

---

## 🚀 Production Deployment

### Production Configuration

**1. Update docker-compose.yml:**
```yaml
services:
  api:
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=0
      - SECRET_KEY=${SECRET_KEY}  # Use env var
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
```

**2. Use PostgreSQL:**
```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: taskmanagement
      POSTGRES_USER: taskuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    environment:
      - DATABASE_URL=postgresql://taskuser:${DB_PASSWORD}@postgres:5432/taskmanagement
    depends_on:
      - postgres
```

**3. Use Production Server:**
```dockerfile
# In Dockerfile, change CMD to:
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5003", "run:app"]
```

**4. Add to requirements.txt:**
```
gunicorn==21.2.0
psycopg2-binary==2.9.9
```

### Security Checklist
- ✅ Change all default secrets
- ✅ Use environment variables for sensitive data
- ✅ Disable debug mode
- ✅ Use HTTPS/TLS
- ✅ Set up proper logging
- ✅ Configure firewall rules
- ✅ Regular backups
- ✅ Monitor resource usage

---

## 📊 Performance Tuning

### Scale Celery Workers
```yaml
services:
  celery-worker:
    deploy:
      replicas: 3  # Run 3 worker instances
```

Or manually:
```bash
docker-compose up -d --scale celery-worker=3
```

### Redis Persistence
```yaml
services:
  redis:
    command: redis-server --appendonly yes --save 60 1000
```

### Resource Limits
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

---

## 🔐 Security

### Network Isolation
```yaml
networks:
  task-network:
    driver: bridge
    internal: true  # Isolate from external access
```

### Read-Only Filesystem
```yaml
services:
  api:
    read_only: true
    tmpfs:
      - /tmp
      - /app/instance
```

### Non-Root User
```dockerfile
# Add to Dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

---

## 📝 Useful Commands Reference

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose down

# View logs
docker-compose logs -f [service]

# Restart service
docker-compose restart [service]

# Rebuild and restart
docker-compose up -d --build

# Execute command in container
docker-compose exec [service] [command]

# Scale service
docker-compose up -d --scale celery-worker=3

# Remove everything including volumes
docker-compose down -v

# Check resource usage
docker stats

# Clean up unused resources
docker system prune -a
```

---

## ✅ Verification Checklist

After starting with Docker:

- ✅ All 4 services running: `docker-compose ps`
- ✅ API accessible: `curl http://localhost:5003/api/auth/health`
- ✅ Redis responding: `docker-compose exec redis redis-cli ping`
- ✅ Celery worker active: `docker-compose logs celery-worker`
- ✅ No errors in logs: `docker-compose logs`
- ✅ Can create user: Test `/api/auth/register`
- ✅ Can login: Test `/api/auth/login`
- ✅ Can create task: Test `/api/tasks`
- ✅ Background tasks work: Check Celery logs

---

## 🎉 Summary

**Docker Setup Includes:**
- ✅ Complete containerized environment
- ✅ Redis for caching and message queue
- ✅ Celery for background tasks
- ✅ Auto-restart on failure
- ✅ Health checks
- ✅ Volume persistence
- ✅ Network isolation
- ✅ Easy scaling

**One Command to Rule Them All:**
```bash
docker-compose up -d
```

**Your API is now running at:** `http://localhost:5003` 🚀
