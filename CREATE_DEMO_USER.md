# 🔧 Create Demo User

## The Issue

The demo credentials shown on the login page don't exist yet in the database. You need to create them first!

---

## ✅ Solution: Register the Demo User

### Option 1: Register via React UI (Easiest)

1. **On the login page**, click **"Register here"**
2. **Fill the form:**
   - Username: `demo`
   - Email: `demo@example.com`
   - Password: `password123`
3. **Click "Register"**
4. ✅ **You'll be auto-logged in!**

Now the demo credentials will work for future logins.

---

### Option 2: Create via API (Alternative)

**Using curl:**
```bash
curl -X POST http://localhost:5003/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo",
    "email": "demo@example.com",
    "password": "password123"
  }'
```

**Using Swagger UI:**
1. Go to: http://localhost:5003/apidocs/
2. Find **POST /api/auth/register**
3. Click "Try it out"
4. Enter:
   ```json
   {
     "username": "demo",
     "email": "demo@example.com",
     "password": "password123"
   }
   ```
5. Click "Execute"

Then go back to the React app and login with those credentials.

---

## 🎯 Quick Fix

**Just click "Register here" on the login page and create the account!**

After registration, you can:
- ✅ Login with those credentials anytime
- ✅ Test logout functionality
- ✅ Create tasks
- ✅ Use the full dashboard

---

## 📝 Note

I should update the login form to remove those demo credentials since they're misleading. Let me fix that now...
