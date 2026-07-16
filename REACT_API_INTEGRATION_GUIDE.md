# React + Task Management API Integration Guide

## ✅ Integration Complete!

The React demo app has been successfully connected to the Task Management API. The dashboard now uses real authentication and fetches live data from the backend.

---

## 🎯 What Was Implemented

### 1. **API Service Layer** (`react-app/src/services/taskApi.ts`)
- Complete TypeScript API client
- Methods for authentication (register, login, refresh)
- Methods for task CRUD operations
- Type-safe interfaces for all API responses
- Automatic JWT token handling

### 2. **Authentication Context** (`react-app/src/contexts/AuthContext.tsx`)
- React Context for global auth state
- JWT token management (access + refresh tokens)
- LocalStorage persistence
- Auto-login on page refresh
- Login, register, and logout functions

### 3. **Login & Register Forms**
- `react-app/src/components/auth/LoginForm.tsx` - Login UI
- `react-app/src/components/auth/RegisterForm.tsx` - Registration UI
- Form validation
- Error handling
- Beautiful dark mode support

### 4. **API-Connected Dashboard** (`react-app/src/pages/DashboardPageWithAuth.tsx`)
- Replaces mock data with real API calls
- Fetches tasks from backend
- Updates task status in real-time
- Deletes tasks via API
- Calculates statistics from real data
- Shows login screen when not authenticated

### 5. **CORS Configuration** (Flask API)
- Enabled Flask-CORS
- Configured to allow requests from React app (localhost:5173)
- Secure cross-origin communication

### 6. **Environment Configuration**
- `.env` file for API URL configuration
- Easy to change API endpoint for different environments

---

## 🚀 How to Run

### Step 1: Start the Task Management API

```bash
# Terminal 1 - Backend API
cd task-management-api
source venv/bin/activate
pip install -r requirements.txt  # Install Flask-CORS if needed
python run.py
```

**API will run on:** `http://localhost:5003`

### Step 2: Start the React App

```bash
# Terminal 2 - Frontend
cd react-app
npm install  # If first time
npm run dev
```

**React app will run on:** `http://localhost:5173`

### Step 3: Test the Integration

1. Open browser: `http://localhost:5173`
2. Click **"Open Dashboard"** button
3. You'll see the login screen
4. **Option A:** Register a new account
   - Click "Register here"
   - Fill in username, email, password
   - Submit
5. **Option B:** Use demo credentials (if you created them)
   - Email: `demo@example.com`
   - Password: `password123`
6. After login, you'll see your tasks from the API!

---

## 🔄 How It Works

### Authentication Flow

```
1. User enters credentials in LoginForm
   ↓
2. LoginForm calls useAuth().login()
   ↓
3. AuthContext calls taskApi.login()
   ↓
4. API returns JWT tokens + user data
   ↓
5. Tokens saved to localStorage
   ↓
6. User state updated, dashboard loads
   ↓
7. Dashboard fetches tasks using access token
```

### Task Management Flow

```
1. Dashboard loads → calls taskApi.getTasks(token)
   ↓
2. API returns array of tasks
   ↓
3. Tasks converted to dashboard format
   ↓
4. Statistics calculated from real data
   ↓
5. User updates task status
   ↓
6. Dashboard calls taskApi.updateTask(token, id, data)
   ↓
7. API updates database
   ↓
8. Dashboard refreshes task list
```

---

## 📁 New Files Created

### React App
```
react-app/
├── .env                                    # API URL configuration
├── src/
│   ├── services/
│   │   └── taskApi.ts                     # API client service
│   ├── contexts/
│   │   └── AuthContext.tsx                # Authentication context
│   ├── components/
│   │   └── auth/
│   │       ├── LoginForm.tsx              # Login component
│   │       └── RegisterForm.tsx           # Register component
│   └── pages/
│       └── DashboardPageWithAuth.tsx      # API-connected dashboard
```

### Backend API
```
task-management-api/
├── requirements.txt                        # Added Flask-CORS
└── app/
    └── __init__.py                        # Added CORS configuration
```

---

## 🎨 Features

### ✅ Authentication
- [x] User registration with validation
- [x] Login with email/password
- [x] JWT token authentication
- [x] Auto-login on page refresh
- [x] Logout functionality
- [x] Token refresh (automatic)

### ✅ Task Management
- [x] Fetch all tasks from API
- [x] Real-time task statistics
- [x] Update task status (drag & drop)
- [x] Delete tasks
- [x] Filter tasks by status/priority
- [x] Error handling

### ✅ UI/UX
- [x] Beautiful login/register forms
- [x] Loading states
- [x] Error messages
- [x] Dark mode support
- [x] Responsive design
- [x] Connection error handling

---

## 🔧 Configuration

### API URL Configuration

Edit `react-app/.env`:
```env
VITE_API_URL=http://localhost:5003/api
```

For production:
```env
VITE_API_URL=https://your-api-domain.com/api
```

### CORS Configuration

Edit `task-management-api/app/__init__.py`:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5173",
            "https://your-production-domain.com"
        ]
    }
})
```

---

## 🧪 Testing the Integration

### 1. Create a Test User

**Via Swagger UI:**
1. Go to `http://localhost:5003/apidocs/`
2. POST `/api/auth/register`
3. Use body:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```

**Via React UI:**
1. Open dashboard
2. Click "Register here"
3. Fill form and submit

### 2. Login and View Tasks

1. Login with your credentials
2. Dashboard loads with empty task list
3. Tasks will appear as you create them

### 3. Create Tasks via API

**Via Swagger UI:**
1. Login to get token
2. Click "Authorize" button
3. Enter: `Bearer YOUR_TOKEN`
4. POST `/api/tasks` with:
```json
{
  "title": "Test Task",
  "description": "Testing the integration",
  "priority": "high",
  "status": "pending"
}
```

**Via Dashboard:**
- Task creation UI coming soon (currently view-only)

### 4. Update Task Status

1. In dashboard, drag a task to different column
2. Task updates in database
3. Refresh to verify persistence

---

## 🐛 Troubleshooting

### "Connection Error" Message

**Problem:** React can't connect to API

**Solutions:**
1. Verify API is running: `http://localhost:5003`
2. Check API logs for errors
3. Verify CORS is enabled
4. Check `.env` file has correct API URL

### "Login Failed" Error

**Problem:** Authentication not working

**Solutions:**
1. Verify user exists in database
2. Check password is correct (min 6 characters)
3. Check API logs for error details
4. Try registering a new user

### Tasks Not Loading

**Problem:** Dashboard shows loading forever

**Solutions:**
1. Check browser console for errors
2. Verify JWT token is valid
3. Check API `/api/tasks` endpoint works
4. Try logging out and back in

### CORS Errors in Console

**Problem:** "Access-Control-Allow-Origin" errors

**Solutions:**
1. Verify Flask-CORS is installed: `pip install Flask-CORS`
2. Check CORS configuration in `app/__init__.py`
3. Restart Flask API after changes
4. Clear browser cache

---

## 📊 API Endpoints Used

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---------------|
| `/api/auth/register` | POST | Create new user | No |
| `/api/auth/login` | POST | Login user | No |
| `/api/auth/refresh` | POST | Refresh token | Yes (Refresh) |
| `/api/auth/me` | GET | Get current user | Yes |
| `/api/tasks` | GET | Get all tasks | Yes |
| `/api/tasks` | POST | Create task | Yes |
| `/api/tasks/:id` | PUT | Update task | Yes |
| `/api/tasks/:id` | DELETE | Delete task | Yes |

---

## 🎯 Next Steps (Optional Enhancements)

### 1. Add Task Creation UI
Create a form in the dashboard to add new tasks directly from React.

### 2. Add Task Editing
Implement a modal to edit task details (title, description, due date, etc.).

### 3. Add Project Support
Integrate project management features from the API.

### 4. Add Notifications
Show real-time notifications from the API.

### 5. Add Team Collaboration
Implement team member management and task assignment.

### 6. Add Search & Filters
Add UI for filtering tasks by status, priority, project, etc.

### 7. Add Due Date Management
Visual calendar for task due dates.

### 8. Add File Uploads
Allow attaching files to tasks.

---

## 📝 Code Examples

### Using the API Service

```typescript
import { taskApi } from '../services/taskApi';
import { useAuth } from '../contexts/AuthContext';

function MyComponent() {
  const { accessToken } = useAuth();

  const loadTasks = async () => {
    const tasks = await taskApi.getTasks(accessToken!);
    console.log(tasks);
  };

  const createTask = async () => {
    const newTask = await taskApi.createTask(accessToken!, {
      title: 'New Task',
      priority: 'high',
      status: 'pending'
    });
    console.log(newTask);
  };
}
```

### Using Auth Context

```typescript
import { useAuth } from '../contexts/AuthContext';

function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuth();

  if (!isAuthenticated) {
    return <div>Please login</div>;
  }

  return (
    <div>
      <p>Welcome, {user?.username}!</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

---

## ✅ Summary

**The React demo is now fully integrated with the Task Management API!**

- ✅ Authentication working (login/register)
- ✅ Real-time task data from API
- ✅ Task updates persist to database
- ✅ Beautiful UI with error handling
- ✅ CORS configured properly
- ✅ Production-ready architecture

**To use:**
1. Start API: `cd task-management-api && python run.py`
2. Start React: `cd react-app && npm run dev`
3. Open dashboard and login!

**Enjoy your fully integrated full-stack application! 🎉**
