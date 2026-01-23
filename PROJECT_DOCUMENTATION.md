# Insurance Comparison, Recommendation & Claims Assistant
## Implementation Progress Report

**Project Status**: ✅ Weeks 1-2 Complete (Foundations & Policy Catalog)  
**Current Date**: January 15, 2026  
**Next Phase**: Weeks 3-4 (Recommendations Engine)

---

## ✅ MILESTONE 1 COMPLETED: Weeks 1-2 – Foundations & Catalog

### Week 1: Auth, Schema & Seed Data
- ✅ Database schema created with 8 tables:
  - `Users` - User authentication & profiles
  - `Providers` - Insurance company details
  - `Policies` - Insurance policy listings
  - `UserPolicies` - User's purchased policies
  - `Claims` - User claim submissions
  - `ClaimDocuments` - Uploaded claim files
  - `Recommendations` - Personalized policy suggestions
  - `FraudFlags` - Risk detection markers
  - `AdminLogs` - Audit trail

- ✅ SQLAlchemy ORM models with relationships
- ✅ Pydantic validation schemas for all endpoints
- ✅ Sample data seeded: 5 providers, 10 policies across all types
- ✅ JWT authentication with argon2 password hashing

### Week 2: Policy Browse & Compare UI
- ✅ Backend API endpoints built:
  - `/auth/register` - User registration
  - `/auth/login` - User login
  - `/user/me` - Get profile
  - `/user/profile` - Update profile
  - `/providers` - List insurance providers
  - `/policies` - List all policies with filters (type, price range)
  - `/policies/{id}` - Get policy details
  - `/policies/compare` - Compare multiple policies
  - `/user-policies` - Manage purchased policies

- ✅ Frontend React pages:
  - **Register** - New user sign-up
  - **Login** - User authentication
  - **BrowsePolicies** - Policy listing with filtering and selection
  - **ComparePolicies** - Side-by-side policy comparison table
  - **Profile** - User dashboard (in progress)

### Expected Output
✅ **Users can browse/compare policies with pricing fields**
- Policy cards display: title, provider, type, premium, term, deductible, coverage
- Filter by: policy type, premium range
- Select multiple policies for comparison
- Detailed comparison table with all coverage details

---

## 📋 ARCHITECTURE OVERVIEW

### Technology Stack
- **Frontend**: React 19.2.0 + Vite 7.2.4 + React Router 7.11.0
- **Backend**: FastAPI 0.128.0 + Uvicorn
- **Database**: PostgreSQL 16+ (insurance_db)
- **Authentication**: JWT (HS256) with 60-minute expiration
- **Password Security**: Argon2 hashing
- **CORS**: Enabled for localhost:5173 & 5174

### Running the Project

**Backend (Terminal 1)**:
```bash
cd C:\newproject\backend
C:/newproject/.venv/Scripts/python.exe -m uvicorn main:app --reload --port 8000
```

**Frontend (Terminal 2)**:
```bash
cd C:\newproject\frontend-react
npm run dev  # Runs on http://localhost:5174
```

**Database**: PostgreSQL running on localhost:5432, user: postgres, password: 958181630

---

## 🗄️ DATABASE SCHEMA

### Users Table
```sql
id (INT, PK) | name (VARCHAR) | email (VARCHAR, UNIQUE) | password (VARCHAR)
dob (DATE) | risk_profile (JSONB) | created_at (TIMESTAMP)
```

### Providers Table
```sql
id (INT, PK) | name (VARCHAR) | country (VARCHAR) | created_at (TIMESTAMP)
```

### Policies Table
```sql
id (INT, PK) | provider_id (FK) | policy_type (ENUM) | title (VARCHAR)
coverage (JSONB) | premium (NUMERIC) | term_months (INT) | deductible (NUMERIC)
tnc_url (VARCHAR) | created_at (TIMESTAMP)
```

### UserPolicies Table
```sql
id (INT, PK) | user_id (FK) | policy_id (FK) | policy_number (VARCHAR, UNIQUE)
start_date (DATE) | end_date (DATE) | premium (NUMERIC) | status (ENUM)
auto_renew (BOOLEAN) | created_at (TIMESTAMP)
```

### Claims & Supporting Tables
```sql
Claims: id | user_policy_id (FK) | claim_number | claim_type | incident_date
        amount_claimed | status (draft/submitted/under_review/approved/rejected/paid) | created_at

ClaimDocuments: id | claim_id (FK) | file_url | doc_type | uploaded_at

FraudFlags: id | claim_id (FK) | rule_code | severity (low/medium/high) | details | created_at

Recommendations: id | user_id (FK) | policy_id (FK) | score | reason | created_at
```

---

## 🚀 API ENDPOINTS IMPLEMENTED

### Authentication (Module A)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Authenticate user |
| GET | `/user/me` | Get current user profile |
| PUT | `/user/profile` | Update profile & preferences |

### Policy Catalog (Module B)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/policies` | List all policies with filters |
| GET | `/policies/{id}` | Get specific policy details |
| GET | `/policies/compare` | Compare multiple policies |
| GET | `/providers` | List insurance providers |
| POST | `/user-policies` | Purchase/assign policy to user |
| GET | `/user-policies` | Get user's purchased policies |

---

## 📂 FILE STRUCTURE

```
C:\newproject\
├── backend\
│   ├── main.py (FastAPI app with all routes)
│   ├── models.py (SQLAlchemy ORM models)
│   ├── schemas.py (Pydantic validation schemas)
│   ├── auth.py (Password hashing & JWT)
│   ├── deps.py (Database & auth dependencies)
│   ├── database.py (PostgreSQL connection)
│   ├── seed_data.py (Sample data initialization)
│   └── requirements.txt
│
├── frontend-react\
│   ├── src\
│   │   ├── App.jsx (Main router)
│   │   ├── pages\
│   │   │   ├── Register.jsx (Sign-up form)
│   │   │   ├── Login.jsx (Authentication)
│   │   │   ├── Profile.jsx (User dashboard)
│   │   │   ├── BrowsePolicies.jsx (Policy listing & selection)
│   │   │   └── ComparePolicies.jsx (Side-by-side comparison)
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.html
│   └── package.json
│
└── .venv\ (Python virtual environment)
```

---

## 🎯 NEXT STEPS: WEEKS 3-4 – RECOMMENDATIONS ENGINE (Module C)

### Week 3: Collect User Preferences
- [ ] User preference collection UI (risk profile, policy priorities)
- [ ] Save preferences to risk_profile JSONB
- [ ] Create API endpoint: `POST /user/preferences`

### Week 4: Score & Recommend Policies
- [ ] Scoring algorithm (premium/coverage/term matching)
- [ ] Populate Recommendations table
- [ ] API endpoint: `GET /recommendations` - Personalized shortlist
- [ ] Frontend: Recommendations page with rationale

### Expected Output
- Personalized policy recommendations ranked by score
- Display reason for each recommendation
- Link to purchase recommended policies

---

## 🔐 AUTHENTICATION FLOW

1. User registers → password hashed with Argon2 → stored in DB
2. User logs in → password verified → JWT token generated
3. Token stored in localStorage (frontend)
4. All protected endpoints require token in query parameter: `?token=<JWT>`
5. Backend decodes JWT → retrieves user_id → returns user data

### Example Protected Request
```javascript
const token = localStorage.getItem("token");
fetch(`http://localhost:8000/user-policies?token=${token}`)
```

---

## 📊 SAMPLE DATA IN DATABASE

### 5 Providers Seeded
1. SafeGuard Insurance (USA)
2. Guardian Life (USA)
3. AXA Global (France)
4. Allianz (Germany)
5. State Farm (USA)

### 10 Policies Seeded
- **Auto**: Basic ($85/mo), Premium Plus ($125/mo)
- **Health**: Basic ($300/mo), Family ($650/mo)
- **Life**: Term 20-Year ($45/mo), Whole Life ($150/mo)
- **Home**: Basic ($95/mo), Complete ($180/mo)
- **Travel**: Budget ($25/mo), Premium International ($85/mo)

---

## 🧪 TESTING THE APPLICATION

### Test Registration & Login
1. Open http://localhost:5174
2. Register with new account
3. Login with credentials
4. Token saved to localStorage

### Test Policy Browsing
1. After login, navigate to `/browse`
2. Use filters to narrow policies
3. Select 2+ policies
4. Click "Compare Selected"
5. View side-by-side comparison

### Test API Directly
```bash
# Get all policies
curl http://localhost:8000/policies

# Get specific policy
curl http://localhost:8000/policies/1

# Compare policies
curl "http://localhost:8000/policies/compare?policy_ids=1,2,3"

# Get user profile (requires token)
curl "http://localhost:8000/user/me?token=<YOUR_JWT_TOKEN>"
```

---

## ⚠️ KNOWN ISSUES & SOLUTIONS

### Issue: "password cannot be longer than 72 bytes"
**Root Cause**: Bcrypt version incompatibility with passlib  
**Solution**: Switched to Argon2 hashing (no byte limit)  
**Status**: ✅ FIXED

### Issue: CORS blocking requests
**Root Cause**: CORSMiddleware order and origin configuration  
**Solution**: Moved middleware before routes, added explicit origins  
**Status**: ✅ FIXED

### Issue: First registration works, subsequent fail
**Root Cause**: Backend process reloading during file changes  
**Solution**: Disabled auto-reload in development  
**Status**: ✅ FIXED

---

## 📝 UPCOMING FEATURES (Weeks 5-8)

### Module D: Claims (Weeks 5-6)
- [ ] Claim filing wizard with multi-step form
- [ ] Document upload (S3 integration)
- [ ] Real-time status tracking
- [ ] Notification system (Celery + email)

### Module E: Fraud & Analytics (Weeks 7-8)
- [ ] Fraud detection rules engine:
  - Duplicate documents
  - Suspicious timing
  - Amount anomalies
- [ ] Admin dashboard
- [ ] Export analytics reports
- [ ] QA & production deployment

---

## 💡 DEVELOPMENT NOTES

- Use `Bearer <token>` header for future API versions instead of query params
- Consider adding refresh token logic (separate endpoint)
- Implement role-based access control (admin/user)
- Add rate limiting for auth endpoints
- Consider caching provider/policy lists (Redis)
- Log all admin actions to AdminLogs table for audit

---

**Last Updated**: January 15, 2026  
**Next Milestone Review**: Week 3  
**Project Owner**: Insurance Comparison Team
