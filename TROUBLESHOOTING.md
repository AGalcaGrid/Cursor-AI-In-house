# 🔧 Troubleshooting - White Screen Issue

## Quick Fix Steps

### 1. **Check the Correct Port**
The app might be running on a different port. Check your terminal output:
- If it says `Port 5173 is in use, trying another one...`
- Open: **http://localhost:5174** instead

### 2. **Clear Browser Cache**
```
Chrome/Edge: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
Firefox: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
Safari: Cmd+Option+R
```

### 3. **Check Browser Console**
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for red error messages
4. Share the error if you see one

### 4. **Restart Development Server**
```bash
# Stop the server (Ctrl+C)
cd react-app
npm run dev
```

### 5. **Install Missing Dependencies**
```bash
cd react-app
npm install
```

### 6. **Clear Vite Cache**
```bash
cd react-app
rm -rf node_modules/.vite
npm run dev
```

---

## Common Issues

### Issue: "Cannot find module"
**Solution:**
```bash
npm install
```

### Issue: Port already in use
**Solution:**
- Kill the process on port 5173
- Or use the new port shown in terminal (usually 5174)

### Issue: White screen with no errors
**Solution:**
1. Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
2. Open in incognito/private window
3. Check if API is running on port 5003

---

## Verify Setup

### 1. Check React App is Running
```bash
curl http://localhost:5174
# Should return HTML
```

### 2. Check API is Running
```bash
curl http://localhost:5003/api/auth/me
# Should return 401 (unauthorized) - this is correct!
```

### 3. Check CORS
Open browser console and try:
```javascript
fetch('http://localhost:5003/api/auth/me')
  .then(r => console.log(r.status))
```
Should show `401` not CORS error

---

## Still Having Issues?

### Get Detailed Error Info

1. **Open Browser Console** (F12)
2. **Go to Console tab**
3. **Copy any red error messages**
4. **Check Network tab** for failed requests

### Check Files Exist
```bash
cd react-app
ls -la src/contexts/AuthContext.tsx
ls -la src/services/taskApi.ts
ls -la src/pages/DashboardPageWithAuth.tsx
ls -la src/components/auth/LoginForm.tsx
```

All should exist.

---

## Emergency Rollback

If nothing works, use the original dashboard:

**Edit `react-app/src/App.tsx`:**

Change line 365 from:
```tsx
<DashboardPageWithAuth />
```

Back to:
```tsx
<DashboardPage />
```

This will show the demo dashboard without API integration.

---

## Contact Info

If you're still stuck, provide:
1. Browser console errors (screenshot)
2. Terminal output
3. Which port you're accessing (5173 or 5174)
