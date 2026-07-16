# Quick Fix for White Screen

## ✅ Solution 1: Use Correct Port

Your app is running on **PORT 5174**, not 5173!

**Open:** http://localhost:5174

---

## ✅ Solution 2: Hard Refresh

After opening http://localhost:5174:

- **Mac:** Press `Cmd + Shift + R`
- **Windows:** Press `Ctrl + Shift + R`

---

## ✅ Solution 3: Check Browser Console

1. Press `F12` (or right-click → Inspect)
2. Click "Console" tab
3. Look for errors (red text)
4. If you see errors, share them

---

## ✅ Solution 4: Temporarily Disable API Integration

If you just want to see the demo working:

**Edit:** `react-app/src/App.tsx`

**Find line 365:**
```tsx
<DashboardPageWithAuth />
```

**Change to:**
```tsx
<DashboardPage />
```

**Save and refresh browser.**

This will show the original demo dashboard with mock data (no API needed).

---

## ✅ Solution 5: Restart Everything

```bash
# Terminal 1 - Stop and restart React
cd react-app
# Press Ctrl+C to stop
npm run dev

# Terminal 2 - Make sure API is running
cd task-management-api
source venv/bin/activate
python run.py
```

Then open: **http://localhost:5174** (or whatever port is shown)

---

## 🎯 Most Likely Issue

You're accessing **http://localhost:5173** but the app is on **http://localhost:5174**

**Try:** http://localhost:5174
