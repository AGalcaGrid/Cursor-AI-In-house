# 🐳 Docker Setup for All APIs

This document describes how to run all backend APIs using Docker Compose.

## 📦 Services Included

| Service | Port | Description | Health Check |
|---------|------|-------------|--------------|
| **Blog API** | 5000 | Blog posts and comments | http://localhost:5000/health |
| **Customer Support API** | 5001 | Customer support tickets | http://localhost:5001/api/health |
| **Support Ticket API** | 5002 | Advanced ticket management | http://localhost:5002/api/health |
| **Task Management API** | 5003 | Task and project management | http://localhost:5003/api/auth/health |
| **Redis** | 6379 | Shared cache and message broker | - |
| **Celery Worker** | - | Background tasks for Task API | - |
| **Celery Beat** | - | Scheduled tasks for Task API | - |

## 🚀 Quick Start

### 1. Start All Services

```bash
./docker-start-all.sh
```

This script will:
- ✅ Check Docker installation
- ✅ Create `.env` file if needed
- ✅ Stop existing containers
- ✅ Build Docker images
- ✅ Start all services
- ✅ Display service status and access URLs

### 2. Verify Services

```bash
# Check all services are running
docker compose ps

# Check specific service logs
docker compose logs -f blog-api
docker compose logs -f customer-support-api
docker compose logs -f support-ticket-api
docker compose logs -f task-management-api
```

### 3. Test API Endpoints

```bash
# Blog API
curl http://localhost:5000/health

# Customer Support API
curl http://localhost:5001/api/health

# Support Ticket API
curl http://localhost:5002/api/health

# Task Management API
curl http://localhost:5003/api/auth/health
```

## 📋 Manual Commands

### Start Services
```bash
# Start all services
docker compose up -d

# Start specific service
docker compose up -d blog-api

# Start with build
docker compose up -d --build
```

### Stop Services
```bash
# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# Stop specific service
docker compose stop blog-api
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f task-management-api

# Last 50 lines
docker compose logs --tail=50 blog-api
```

### Restart Services
```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart customer-support-api
```

### Execute Commands in Container
```bash
# Access bash shell
docker compose exec blog-api bash

# Run Python shell
docker compose exec task-management-api python

# Run database migrations
docker compose exec task-management-api flask db upgrade

# Run tests
docker compose exec task-management-api bash -c "PYTHONPATH=/app pytest -v"
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Network (app-network)             │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Blog API    │  │ Customer     │  │  Support     │     │
│  │  Port: 5000  │  │ Support API  │  │  Ticket API  │     │
│  │              │  │  Port: 5001  │  │  Port: 5002  │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                  │              │
│         └─────────────────┼──────────────────┘              │
│                           │                                 │
│                    ┌──────▼───────┐                         │
│                    │    Redis     │                         │
│                    │  Port: 6379  │                         │
│                    └──────┬───────┘                         │
│                           │                                 │
│         ┌─────────────────┼─────────────────┐              │
│         │                 │                 │              │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐    │
│  │ Task Mgmt    │  │   Celery     │  │   Celery     │    │
│  │    API       │  │   Worker     │  │    Beat      │    │
│  │  Port: 5003  │  │              │  │              │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 📂 File Structure

```
CoursorProject/
├── docker-compose.yml           # Main Docker Compose configuration
├── Dockerfile.python-api        # Shared Dockerfile for all APIs
├── docker-start-all.sh          # Startup script
├── .env                         # Environment variables
│
├── blog-api/
│   ├── app/
│   ├── requirements.txt
│   └── run.py
│
├── customer-support-api/
│   ├── app/
│   ├── requirements.txt
│   └── run.py
│
├── support-ticket-api/
│   ├── app/
│   ├── requirements.txt
│   └── run.py
│
└── task-management-api/
    ├── app/
    ├── requirements.txt
    ├── run.py
    └── celery_worker.py
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# Email Configuration (for Task Management API)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Add other variables as needed
```

### Port Configuration

Each API runs on a different port:
- **5000**: Blog API
- **5001**: Customer Support API
- **5002**: Support Ticket API
- **5003**: Task Management API
- **6379**: Redis

To change ports, edit `docker-compose.yml`:
```yaml
ports:
  - "NEW_PORT:CONTAINER_PORT"
```

## 🗄️ Database Management

Each API uses its own SQLite database stored in Docker volumes:

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect coursorproject_blog_instance

# Backup database
docker compose exec blog-api cp /app/instance/blog.db /app/backup.db

# Remove all volumes (⚠️ deletes all data)
docker compose down -v
```

## 🧪 Testing

### Run Tests for Task Management API

```bash
# Run all tests
docker compose exec task-management-api bash -c "PYTHONPATH=/app pytest -v"

# Run with coverage
docker compose exec task-management-api bash -c "PYTHONPATH=/app pytest --cov=app --cov-report=term-missing"

# Run specific test file
docker compose exec task-management-api bash -c "PYTHONPATH=/app pytest tests/test_tasks.py -v"
```

## 🔍 Monitoring

### Check Service Health

```bash
# Check all services
docker compose ps

# Check Redis
docker compose exec redis redis-cli ping

# Check Celery worker
docker compose exec celery-worker celery -A celery_worker.celery inspect active

# Monitor Redis operations
docker compose exec redis redis-cli MONITOR
```

### View Resource Usage

```bash
# All containers
docker stats

# Specific container
docker stats task-management-api
```

## 🐛 Troubleshooting

### Services Not Starting

```bash
# Check logs
docker compose logs

# Rebuild images
docker compose build --no-cache

# Remove all containers and volumes
docker compose down -v
docker compose up -d --build
```

### Port Already in Use

```bash
# Find process using port
lsof -i :5000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Database Issues

```bash
# Reset database
docker compose down -v
docker compose up -d

# Access database directly
docker compose exec blog-api sqlite3 /app/instance/blog.db
```

### Redis Connection Issues

```bash
# Check Redis is running
docker compose ps redis

# Test Redis connection
docker compose exec redis redis-cli ping

# Restart Redis
docker compose restart redis
```

## 📊 API Documentation

### Swagger/OpenAPI

- **Task Management API**: http://localhost:5003/apidocs

### Example API Calls

#### Blog API (Port 5000)
```bash
# Get all posts
curl http://localhost:5000/api/posts

# Create post (requires auth)
curl -X POST http://localhost:5000/api/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"title":"Test Post","content":"Content here"}'
```

#### Customer Support API (Port 5001)
```bash
# Register user
curl -X POST http://localhost:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","password":"Test123!"}'

# Login
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

#### Support Ticket API (Port 5002)
```bash
# Get tickets
curl http://localhost:5002/api/tickets \
  -H "Authorization: Bearer <token>"

# Create ticket
curl -X POST http://localhost:5002/api/tickets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"title":"Issue","description":"Description","priority":"high"}'
```

#### Task Management API (Port 5003)
```bash
# Register
curl -X POST http://localhost:5003/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","password":"Test123!","role":"user"}'

# Get tasks
curl http://localhost:5003/api/tasks \
  -H "Authorization: Bearer <token>"
```

## 🚀 Production Deployment

### Recommendations

1. **Use PostgreSQL** instead of SQLite
2. **Set up Redis persistence**
3. **Use environment-specific configs**
4. **Enable HTTPS/SSL**
5. **Set up monitoring** (Prometheus, Grafana)
6. **Configure logging** (ELK stack)
7. **Use Docker secrets** for sensitive data
8. **Set resource limits**

### Example Production Config

```yaml
services:
  blog-api:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
      restart_policy:
        condition: on-failure
        max_attempts: 3
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Docker Best Practices](https://flask.palletsprojects.com/en/2.3.x/deploying/docker/)
- [Redis Docker Guide](https://redis.io/docs/getting-started/install-stack/docker/)

## ✅ Verification Checklist

- [ ] Docker and Docker Compose installed
- [ ] `.env` file created
- [ ] All services started: `docker compose ps`
- [ ] Health checks passing
- [ ] APIs responding to requests
- [ ] Redis accessible
- [ ] Celery worker running (for Task API)
- [ ] Logs showing no errors

## 🎯 Next Steps

1. **Test each API** with the example curl commands
2. **Set up your frontend** to connect to these APIs
3. **Configure email** for Task Management API notifications
4. **Run tests** to ensure everything works
5. **Monitor logs** for any issues

---

**Happy coding!** 🚀

For issues or questions, check the troubleshooting section or review individual API documentation.
