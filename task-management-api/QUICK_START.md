# Task Management API - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Python 3.12+
- pip (Python package manager)

### Step 1: Setup Virtual Environment

```bash
cd task-management-api

# Activate existing virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

### Step 2: Install Dependencies (if needed)

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# The default settings work for development
# Edit .env if you need custom configuration
```

### Step 4: Run the Application

```bash
python run.py
```

**Server will start on:** `http://localhost:5003`

### Step 5: Access Swagger UI

Open your browser and navigate to:
```
http://localhost:5003/apidocs/
```

You'll see the interactive API documentation where you can test all endpoints!

---

## 📝 Quick API Test

### Using Swagger UI (Recommended)

1. Go to `http://localhost:5003/apidocs/`
2. Click on **POST /api/auth/register**
3. Click "Try it out"
4. Enter test data:
   ```json
   {
     "username": "testuser",
     "email": "test@example.com",
     "password": "password123"
   }
   ```
5. Click "Execute"
6. Copy the response

7. Click on **POST /api/auth/login**
8. Enter credentials:
   ```json
   {
     "email": "test@example.com",
     "password": "password123"
   }
   ```
9. Copy the `access_token` from response

10. Click the **Authorize** button at the top
11. Enter: `Bearer YOUR_ACCESS_TOKEN`
12. Now you can test authenticated endpoints!

### Using curl

#### 1. Register User
```bash
curl -X POST http://localhost:5003/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

#### 2. Login
```bash
curl -X POST http://localhost:5003/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Save the access_token from the response!**

#### 3. Create Task (replace YOUR_TOKEN)
```bash
curl -X POST http://localhost:5003/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "My First Task",
    "description": "Testing the API",
    "priority": "high",
    "status": "pending"
  }'
```

#### 4. Get All Tasks
```bash
curl -X GET http://localhost:5003/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎯 Available Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user profile

### Tasks
- `GET /api/tasks` - Get all tasks (with filters)
- `GET /api/tasks/<id>` - Get specific task
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/<id>` - Update task
- `DELETE /api/tasks/<id>` - Delete task

### Projects
- `GET /api/projects` - Get all projects
- `POST /api/projects` - Create new project
- `PUT /api/projects/<id>` - Update project
- `DELETE /api/projects/<id>` - Delete project
- `POST /api/projects/<id>/members` - Add team member
- `DELETE /api/projects/<id>/members/<user_id>` - Remove member

### Notifications
- `GET /api/notifications` - Get user notifications
- `PUT /api/notifications/<id>/read` - Mark as read

---

## 🔍 Query Parameters

### Get Tasks with Filters
```bash
# Filter by status
GET /api/tasks?status=pending

# Filter by priority
GET /api/tasks?priority=high

# Filter by project
GET /api/tasks?project_id=1

# Show only tasks assigned to me
GET /api/tasks?assigned_to_me=true

# Combine filters
GET /api/tasks?status=in_progress&priority=high
```

---

## 📊 Database

The API uses SQLite by default for development:
- Database file: `instance/dev.db`
- Automatically created on first run
- To reset: delete `instance/dev.db` and restart

### Database Migrations

```bash
# Initialize migrations (already done)
flask db init

# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

---

## 🛠️ Development Tips

### View Database
```bash
# Install SQLite browser or use command line
sqlite3 instance/dev.db

# List tables
.tables

# View users
SELECT * FROM users;

# View tasks
SELECT * FROM tasks;
```

### Enable Debug Mode
Already enabled in development config. Check `config.py`:
```python
class DevelopmentConfig(Config):
    DEBUG = True
```

### Check Logs
The application logs all requests and responses. Check console output for:
- Request details
- Response status
- Execution time
- Errors

---

## 🧪 Testing

### Run Tests (if available)
```bash
pytest
```

### Test Coverage
```bash
pytest --cov=app
```

---

## 🚨 Troubleshooting

### Port Already in Use
```bash
# Change port in run.py
app.run(host='0.0.0.0', port=5004)  # Use different port
```

### Module Not Found
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Errors
```bash
# Delete and recreate database
rm instance/dev.db
python run.py  # Will recreate automatically
```

### JWT Token Expired
```bash
# Use refresh token to get new access token
POST /api/auth/refresh
# Or login again
```

---

## 📚 Additional Resources

- **Swagger UI:** http://localhost:5003/apidocs/
- **API Documentation:** See `TASK_MANAGEMENT_API_VERIFICATION.md`
- **Demo Script:** See `DEMO_SCRIPT.md` in project root

---

## 🎉 You're Ready!

The Task Management API is now running and ready to use. Start with Swagger UI for the easiest testing experience, or use curl/Postman for programmatic access.

**Happy coding! 🚀**
