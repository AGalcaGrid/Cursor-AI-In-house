# E-Commerce API - Docker Setup Complete ✅

## Status: Ready to Run in Docker

The e-commerce API has been successfully added to the Docker setup!

---

## 🚀 Quick Start

### Start All Services (Including E-Commerce API)

```bash
# From project root
./docker-start-all.sh
```

Or manually:

```bash
docker compose up -d
```

### Start Only E-Commerce API

```bash
docker compose up -d ecommerce-api
```

---

## 📡 Service Endpoints

Once running, the e-commerce API will be available at:

**Base URL:** `http://localhost:5004`

### API Endpoints

**Authentication:**
- POST `http://localhost:5004/api/auth/register`
- POST `http://localhost:5004/api/auth/login`
- GET `http://localhost:5004/api/auth/me`

**Products:**
- GET `http://localhost:5004/api/products`
- GET `http://localhost:5004/api/products/{id}`
- POST `http://localhost:5004/api/products`

**Cart:**
- GET `http://localhost:5004/api/cart`
- POST `http://localhost:5004/api/cart/items`
- PUT `http://localhost:5004/api/cart/items/{product_id}`
- DELETE `http://localhost:5004/api/cart/items/{product_id}`

**Checkout:**
- POST `http://localhost:5004/api/checkout/create-payment-intent`
- POST `http://localhost:5004/api/checkout/complete`

**Orders:**
- GET `http://localhost:5004/api/orders`
- GET `http://localhost:5004/api/orders/{id}`

**Discounts:**
- POST `http://localhost:5004/api/discounts/validate`

---

## 🐳 Docker Configuration

### Container Details

| Property | Value |
|----------|-------|
| **Container Name** | `ecommerce-api` |
| **Port** | `5004` |
| **Network** | `app-network` |
| **Volume** | `ecommerce_instance` |
| **Dependencies** | `redis` |

### Environment Variables

```yaml
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=jwt-secret-key-change-in-production
DATABASE_URL=sqlite:///instance/ecommerce.db
REDIS_URL=redis://redis:6379/0
STRIPE_SECRET_KEY=sk_test_mock_key
SENDGRID_API_KEY=mock_sendgrid_key
CORS_ORIGINS=http://localhost:3000
```

---

## 🔧 Docker Commands

### View Logs

```bash
# All services
docker compose logs -f

# E-commerce API only
docker compose logs -f ecommerce-api

# Last 100 lines
docker compose logs --tail=100 ecommerce-api
```

### Restart Service

```bash
docker compose restart ecommerce-api
```

### Stop Service

```bash
docker compose stop ecommerce-api
```

### Rebuild After Code Changes

```bash
docker compose up -d --build ecommerce-api
```

### Access Container Shell

```bash
docker exec -it ecommerce-api /bin/bash
```

---

## 🧪 Testing in Docker

### Run Tests Inside Container

```bash
# Access container
docker exec -it ecommerce-api /bin/bash

# Inside container
pytest -v
pytest --cov=app
```

### Run Tests from Host

```bash
docker exec ecommerce-api pytest -v
```

---

## 📊 All Services Running

After running `./docker-start-all.sh`, you'll have:

| Service | Port | URL |
|---------|------|-----|
| React App | 3000 | http://localhost:3000 |
| Blog API | 5000 | http://localhost:5000 |
| Customer Support API | 5001 | http://localhost:5001 |
| Support Ticket API | 5002 | http://localhost:5002 |
| Task Management API | 5003 | http://localhost:5003 |
| **E-Commerce API** | **5004** | **http://localhost:5004** |
| Redis | 6379 | localhost:6379 |

---

## 🗄️ Database

The e-commerce API uses SQLite in development:
- **Location:** `ecommerce-api/instance/ecommerce.db`
- **Volume:** Persisted in Docker volume `ecommerce_instance`
- **Access:** Database persists even when container is stopped

### View Database

```bash
# Access container
docker exec -it ecommerce-api /bin/bash

# Inside container
sqlite3 instance/ecommerce.db

# SQLite commands
.tables
.schema products
SELECT * FROM products;
.quit
```

---

## 🔄 Development Workflow

### Code Changes

The container has live reload enabled via volume mounting:

1. Edit code in `ecommerce-api/` on your host
2. Changes are automatically reflected in container
3. Flask auto-reloads on code changes

### Add Dependencies

```bash
# Edit requirements.txt
vim ecommerce-api/requirements.txt

# Rebuild container
docker compose up -d --build ecommerce-api
```

---

## 🌐 CORS Configuration

The API is configured to accept requests from:
- `http://localhost:3000` (React app)
- `http://localhost:5173` (Vite dev server)

To add more origins, update `CORS_ORIGINS` in docker-compose.yml.

---

## 🔐 Security Notes

### Development Mode
- Using mock Stripe keys
- Using mock SendGrid keys
- Debug mode enabled
- SQLite database (not for production)

### Production Deployment
Update these in docker-compose.yml:
- `SECRET_KEY` - Use strong random key
- `JWT_SECRET_KEY` - Use strong random key
- `STRIPE_SECRET_KEY` - Real Stripe key
- `SENDGRID_API_KEY` - Real SendGrid key
- `DATABASE_URL` - PostgreSQL connection string

---

## 📝 Sample API Calls

### Register User

```bash
curl -X POST http://localhost:5004/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Get Products

```bash
curl http://localhost:5004/api/products
```

### Add to Cart (with JWT token)

```bash
curl -X POST http://localhost:5004/api/cart/items \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs ecommerce-api

# Check if port 5004 is in use
lsof -i :5004

# Rebuild from scratch
docker compose down
docker compose build --no-cache ecommerce-api
docker compose up -d ecommerce-api
```

### Database Issues

```bash
# Remove database volume and recreate
docker compose down -v
docker compose up -d ecommerce-api
```

### Permission Issues

```bash
# Fix permissions on instance directory
chmod -R 755 ecommerce-api/instance
```

---

## ✅ Verification

### Check if Running

```bash
# Check container status
docker compose ps ecommerce-api

# Test API endpoint
curl http://localhost:5004/api/products

# Expected: {"status":"success","data":{"products":[],...}}
```

### Health Check

```bash
curl http://localhost:5004/api/products
```

If you get a JSON response, the API is running correctly! ✅

---

## 🎉 Summary

✅ **E-Commerce API added to Docker**
✅ **Running on port 5004**
✅ **Integrated with existing services**
✅ **Connected to shared Redis**
✅ **Database persisted in volume**
✅ **Live reload enabled**
✅ **Ready for development**

**Start everything with:** `./docker-start-all.sh`
