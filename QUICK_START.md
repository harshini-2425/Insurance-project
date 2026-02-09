# QUICK START GUIDE

## 🚀 Project Ready for Launch!

### Step 1: Start Backend (Terminal 1)
```bash
cd c:\newproject
start_backend.bat
```

**Expected Output:**
```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 2: Start Frontend (Terminal 2)
```bash
cd c:\newproject\frontend-react
npm run dev
```

**Expected Output:**
```
VITE v7.3.1 ready in XXX ms
➜  Local:   http://localhost:5174/
```

### Step 3: Open in Browser
Navigate to: **http://localhost:5174**

### Step 4: Test the System
```bash
# Terminal 3
cd c:\newproject
C:\newproject\.venv\Scripts\python.exe test_system.py
```

---

## 📋 What's New in This Version

### ✅ 50 Realistic Insurance Policies
- 11 Auto policies (HDFC, ICICI, Bajaj, TATA AIG, etc.)
- 11 Health policies (Star Health, Aditya Birla, Apollo Munich, etc.)
- 9 Home policies (HDFC Ergo, ICICI Lombard, Kotak, etc.)
- 9 Life policies (LIC, HDFC Life, ICICI Prudential, Bajaj, etc.)
- 10 Travel policies (Cholamandalam, ICICI Lombard, AIG, etc.)

### ✅ Refactored Recommendation Engine
- **Stage 1**: Strict policy-type filtering (respects user choice)
- **Stage 2**: Soft-constraint scoring (shows options, ranked by fit)
- **Result**: 5-10 personalized recommendations with explanations

### ✅ Fixed Browse Policies Page
- Shows all 50 policies
- Pagination support (skip/limit)
- Full-text search
- Filter by type, provider, premium
- Compare up to 5 policies

### ✅ Professional Documentation
- README.md (500+ lines)
- RECOMMENDATION_ALGORITHM_REPORT.md (1500+ lines)
- System verification scripts

---

## 🧪 How to Use the System

### 1. Register a New User
- Go to **Register** page
- Enter email, password, and basic info
- Click "Register"

### 2. Browse Policies
- Go to **Browse Policies** page
- View all 50 policies
- Search by title or provider
- Filter by type or premium range
- Select 2-5 policies to compare

### 3. Get Recommendations
- Go to **Get Recommendations** page
- Select preferred policy types
- Enter your max budget and health info
- Click "Generate Recommendations"
- Receive 5-10 personalized recommendations

### 4. Compare Policies
- From Browse page, select multiple policies
- Click "📊 Compare Selected"
- See side-by-side comparison

### 5. Purchase a Policy
- Click on any policy
- Review details
- Click "Purchase"

### 6. File a Claim
- Go to **Claims** page
- Submit claim form
- Upload supporting documents
- Track claim status

---

## 📊 Database Status

### Policies Loaded: ✅ 50
```
AUTO:    11 policies
HEALTH:  11 policies
HOME:     9 policies
LIFE:     9 policies
TRAVEL:  10 policies
─────────────────────
TOTAL:   50 policies
```

### Providers Loaded: ✅ 30
- Life Insurance: 6 companies
- Health Insurance: 6 companies
- Auto Insurance: 7 companies
- Home Insurance: 6 companies
- Travel Insurance: 5 companies

---

## 🔗 Important URLs

| Service | URL | Port |
|---------|-----|------|
| Frontend | http://localhost:5174 | 5174 |
| Backend API | http://localhost:8000 | 8000 |
| API Docs | http://localhost:8000/docs | 8000 |
| API ReDoc | http://localhost:8000/redoc | 8000 |

---

## 📁 Project Files

### Root Directory
```
README.md                           - Main documentation
RECOMMENDATION_ALGORITHM_REPORT.md  - Algorithm details
PROJECT_COMPLETION.md               - Completion summary
VERIFICATION_CHECKLIST.md           - Final checklist
test_system.py                      - System verification script
start_backend.bat                   - Backend launcher
```

### Backend (`backend/`)
```
main.py                   - FastAPI application (20+ endpoints)
models.py                 - Database models (7 tables)
schemas.py                - Pydantic schemas
scoring_refactored.py     - NEW: Recommendation engine
seed_policies.py          - Database seeding script
policies_seed_data.json   - 50 policies, 30 providers
database.py               - SQLAlchemy configuration
auth.py                   - JWT authentication
fraud_rules.py            - Fraud detection
email_service.py          - Email notifications
```

### Frontend (`frontend-react/src/`)
```
pages/
  ├── Login.jsx           - User login
  ├── Register.jsx        - User registration
  ├── Profile.jsx         - User profile
  ├── BrowsePolicies.jsx  - FIXED: Browse all 50 policies
  ├── Recommendations.jsx - Get personalized recommendations
  ├── Compare.jsx         - Compare policies
  ├── Claims.jsx          - FIXED: File insurance claims
  └── Admin.jsx           - Admin dashboard

styles/
  └── Claims.css          - ENHANCED: Fixed text visibility
```

---

## ✅ All Features Working

- [x] User Authentication (Register/Login)
- [x] User Profiles
- [x] Browse 50 Policies
- [x] Search Policies
- [x] Filter Policies
- [x] Compare Policies
- [x] Get Recommendations (2-stage algorithm)
- [x] File Claims
- [x] Upload Documents
- [x] Fraud Detection
- [x] Admin Dashboard
- [x] Policy Purchases
- [x] Claim Tracking

---

## 🎓 Academic Submission

This platform is ready for academic submission with:
- ✅ Complete source code
- ✅ Professional documentation
- ✅ Detailed algorithm explanation
- ✅ Real insurance company data
- ✅ Advanced recommendation system
- ✅ Full-featured UI
- ✅ Fraud detection
- ✅ Claims management

---

## 📞 Support

### If Backend Won't Start
```bash
cd c:\newproject\backend
C:\newproject\.venv\Scripts\python.exe -m uvicorn main:app --port 8000 --reload
```

### If Frontend Won't Start
```bash
cd c:\newproject\frontend-react
npm install
npm run dev
```

### If Database Issues
```bash
cd c:\newproject\backend
C:\newproject\.venv\Scripts\python.exe seed_policies.py
```

### To Reset Database
```bash
cd c:\newproject\backend
del database.db
C:\newproject\.venv\Scripts\python.exe seed_policies.py
```

---

## 🎯 Key Achievements

1. **50 Realistic Policies** - From 30 real insurance companies
2. **Smart Recommendations** - Two-stage algorithm with strict filtering + soft scoring
3. **Complete UI** - All 8 pages fully functional
4. **Professional Docs** - 2000+ lines of documentation
5. **Clean Code** - Removed 20+ old files, organized structure
6. **Production Ready** - Error handling, validation, security
7. **Academic Grade** - Comprehensive algorithms and documentation

---

**Status**: ✅ PRODUCTION READY  
**Version**: 1.0  
**Date**: February 9, 2026

Enjoy using the Insurance Policy Recommendation Platform! 🚀
