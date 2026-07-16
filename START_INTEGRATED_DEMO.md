# 🚀 Quick Start - Integrated Demo

## Start Both Servers

### Terminal 1: Backend API
```bash
cd task-management-api
source venv/bin/activate
pip install Flask-CORS  # Install CORS if needed
python run.py
```
✅ API running on: **http://localhost:5003**

### Terminal 2: Frontend React App
```bash
cd react-app
npm run dev
```
✅ React running on: **http://localhost:5173**

---

## 🎯 Test the Integration

1. **Open React App:** http://localhost:5173
2. **Click:** "Open Dashboard" button
3. **You'll see:** Login screen

### Option A: Register New Account
1. Click "Register here"
2. Enter:
   - Username: `yourname`
   - Email: `you@example.com`
   - Password: `password123` (min 6 chars)
3. Click "Register"
4. You'll be auto-logged in!

### Option B: Create Demo User via API First
```bash
# In a new terminal
curl -X POST http://localhost:5003/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "email": "demo@example.com",
    "password": "password123"
  }'
```

Then login with:
- Email: `demo@example.com`
- Password: `password123`

---

## ✅ What You'll See

1. **After Login:**
   - Dashboard loads
   - Shows your tasks (empty at first)
   - Real-time statistics

2. **Create Tasks via Swagger:**
   - Go to: http://localhost:5003/apidocs/
   - Login to get token
   - Click "Authorize" → Enter `Bearer YOUR_TOKEN`
   - POST `/api/tasks` with:
   ```json
   {
     "title": "My First Task",
     "description": "Testing the integration",
     "priority": "high",
     "status": "pending"
   }
   ```

3. **Refresh Dashboard:**
   - Your new task appears!
   - Drag it to different columns
   - Status updates in real-time
   - Delete tasks with trash icon

---

## 🎉 You're All Set!

The React app is now fully connected to the Task Management API with:
- ✅ Real authentication
- ✅ Live task data
- ✅ Database persistence
- ✅ Beautiful UI

**Enjoy your integrated full-stack app!**
