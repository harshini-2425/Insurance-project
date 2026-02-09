# 🚀 HOW TO START THE APPLICATION

## IMPORTANT: Follow These Steps in Order

### Step 1: Start Backend (First - Very Important!)
```
Open a NEW Command Prompt or PowerShell
Run: c:\newproject\run_backend.bat

You should see:
    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Step 2: Start Frontend (Second - After backend is running)
```
Open ANOTHER NEW Command Prompt or PowerShell
Run:
    cd c:\newproject\frontend-react
    npm run dev

You should see:
    ➜  Local:   http://localhost:5174/
```

### Step 3: Open Application in Browser
```
Open your browser and go to: http://localhost:5174
```

### Step 4: Register & Login
- Click "Register" to create a new account
- Enter email, password, and basic info
- Click "Login" with your credentials
- You're in! 🎉

---

## ✅ What Should Work Now

- ✅ User Registration (Create new account)
- ✅ User Login (Sign in to account)
- ✅ Browse Policies (View all 50 policies)
- ✅ Search Policies (Search by title/provider)
- ✅ Filter Policies (By type, provider, premium)
- ✅ Compare Policies (Side-by-side comparison)
- ✅ Get Recommendations (Personalized suggestions)
- ✅ Claims Management (File and track claims)
- ✅ Document Upload (Upload claim documents)
- ✅ User Profile (View and edit profile)

---

## 🔧 Troubleshooting

### If you see: "net::ERR_CONNECTION_REFUSED"
**Solution**: The backend is not running!
- Make sure you ran `c:\newproject\run_backend.bat` FIRST
- Check that you see "Uvicorn running on http://127.0.0.1:8000"

### If backend won't start
**Solution**: 
```
1. Kill any existing Python processes:
   taskkill /F /IM python.exe
2. Free port 8000:
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
3. Try again: c:\newproject\run_backend.bat
```

### If frontend won't start
**Solution**:
```
1. Go to: cd c:\newproject\frontend-react
2. Install dependencies: npm install
3. Start: npm run dev
```

### Port Already in Use
**Solution**:
```
taskkill /F /IM python.exe
Start-Sleep 3
Then try: c:\newproject\run_backend.bat
```

---

## 📋 Quick Checklist

Before trying to login/register, verify:

- [ ] Backend is running (c:\newproject\run_backend.bat)
- [ ] You see "Uvicorn running on http://127.0.0.1:8000"
- [ ] Frontend is running (npm run dev in frontend-react)
- [ ] You see "Local:   http://localhost:5174/"
- [ ] Browser can reach http://localhost:5174
- [ ] No errors in browser console (F12)

---

## 🎯 Test URLs

After both servers are running, test these:

- Frontend: http://localhost:5174
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Policies: http://localhost:8000/policies

---

## 📝 Default Test Account

If you want to test without registering:
```
Email: test@example.com
Password: test123
```

(You may need to register first with any valid email/password)

---

## ✅ System Ready When You See

**Backend Terminal:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

**Frontend Terminal:**
```
➜  Local:   http://localhost:5174/
```

**Browser:**
- Shows Login or Register page (no errors)
- Able to click buttons and enter text

---

**You're all set! The application is now working correctly.** 🎉

If you still have issues, make sure:
1. Backend is running FIRST
2. Frontend is running SECOND
3. Wait 5 seconds after starting backend before opening browser
4. Check browser console (F12) for errors
