# 🛡️ Insurance Comparison, Recommendation & Claims Assistant

A full-stack web application for comparing insurance policies, getting personalized recommendations, and managing claims with fraud detection.

## 📊 Project Status

**✅ COMPLETE: Weeks 1-2 (Foundations & Policy Catalog)**
- User authentication (Register/Login)
- Database schema with 8 tables
- Policy browsing and comparison
- Sample data (5 providers, 10 policies)

**🚀 IN PROGRESS: Weeks 3-4 (Recommendations Engine)**

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ with pip
- Node.js 16+ with npm
- PostgreSQL 14+ running locally

### 1. Database Setup
```bash
# Create PostgreSQL database
createdb insurance_db

# Create database user (if needed)
# Connect to PostgreSQL and run:
# CREATE USER postgres WITH PASSWORD '958181630';
# ALTER ROLE postgres CREATEDB;
```

### 2. Backend Setup
```bash
cd c:\newproject\backend

# Create virtual environment (if not exists)
python -m venv ..\.venv

# Activate virtual environment
..\.venv\Scripts\activate  # Windows
# OR
source ../.venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Seed database with sample data
python seed_data.py

# Start server
python -m uvicorn main:app --reload --port 8000
```

Server runs on: **http://localhost:8000**

### 3. Frontend Setup
```bash
cd c:\newproject\frontend-react

# Install dependencies
npm install

# Start development server
npm run dev
```

App runs on: **http://localhost:5174**

---

## 🎯 Features Implemented

### ✅ Authentication (Module A)
- **Register**: Create new user account with email, password, DOB
- **Login**: Authenticate with email/password
- **JWT Tokens**: 60-minute expiration with HS256 algorithm
- **Password Security**: Argon2 hashing (no byte limits)

### ✅ Policy Catalog (Module B)
- **Browse**: View all insurance policies with details
- **Filter**: By policy type, premium range
- **Compare**: Side-by-side comparison of multiple policies
- **Details**: View full coverage information for each policy

### Available Policy Types
- **Auto**: Vehicle insurance
- **Health**: Medical coverage
- **Life**: Term and Whole Life
- **Home**: Property and liability
- **Travel**: Trip and emergency coverage

---

## 📡 API Endpoints

### Authentication
```
POST /auth/register
POST /auth/login
GET /user/me?token=<JWT>
PUT /user/profile?token=<JWT>
```

### Policies
```
GET /policies?policy_type=auto&min_premium=50&max_premium=200
GET /policies/{policy_id}
GET /policies/compare?policy_ids=1,2,3
GET /providers
```

### User Policies
```
POST /user-policies?token=<JWT>
GET /user-policies?token=<JWT>
GET /user-policies/{user_policy_id}?token=<JWT>
```

---

## 🧭 Frontend Pages

| Path | Component | Purpose |
|------|-----------|---------|
| `/` | App | Redirect to /browse |
| `/login` | Login | User authentication |
| `/register` | Register | New user sign-up |
| `/browse` | BrowsePolicies | Policy listing & filtering |
| `/compare` | ComparePolicies | Policy comparison table |
| `/profile` | Profile | User dashboard |

---

## 📁 Project Structure

```
newproject/
├── backend/
│   ├── main.py                 # FastAPI app & routes
│   ├── models.py               # SQLAlchemy ORM models
│   ├── schemas.py              # Pydantic validation schemas
│   ├── auth.py                 # Authentication utilities
│   ├── deps.py                 # FastAPI dependencies
│   ├── database.py             # PostgreSQL connection
│   ├── seed_data.py            # Sample data initialization
│   └── requirements.txt         # Python dependencies
│
├── frontend-react/
│   ├── src/
│   │   ├── App.jsx             # Main router component
│   │   ├── components/
│   │   │   └── Header.jsx      # Navigation header
│   │   ├── pages/
│   │   │   ├── Login.jsx       # Login page
│   │   │   ├── Register.jsx    # Registration page
│   │   │   ├── BrowsePolicies.jsx
│   │   │   ├── ComparePolicies.jsx
│   │   │   └── Profile.jsx
│   │   └── App.css
│   ├── package.json
│   └── index.html
│
└── .venv/                      # Python virtual environment
```

---

## 💾 Database Schema

### Users
```
id (INT, PK) | name | email (UNIQUE) | password | dob | risk_profile (JSON) | created_at
```

### Providers
```
id (INT, PK) | name | country | created_at
```

### Policies
```
id (INT, PK) | provider_id (FK) | policy_type (ENUM) | title | coverage (JSON)
premium (NUMERIC) | term_months (INT) | deductible (NUMERIC) | tnc_url | created_at
```

### User Policies
```
id (INT, PK) | user_id (FK) | policy_id (FK) | policy_number (UNIQUE) | start_date
end_date | premium | status (ENUM) | auto_renew | created_at
```

### Claims, ClaimDocuments, FraudFlags, Recommendations, AdminLogs
*(See full schema in PROJECT_DOCUMENTATION.md)*

---

## 🔐 Authentication Flow

1. **Register**: POST `/auth/register` with name, email, password, dob
   - Returns: JWT token + user_id
   
2. **Login**: POST `/auth/login` with email, password
   - Returns: JWT token
   
3. **Protected Requests**: Add `?token=<JWT>` to query parameters
   - Backend decodes JWT and retrieves user_id
   - Returns 401 if token invalid/expired

4. **Storage**: Token saved in localStorage on client
   - Sent with each request requiring authentication
   - Cleared on logout

---

## 🧪 Testing

### Test User
- Email: `test@example.com`
- Password: `test123`

### Manual API Testing
```bash
# List all policies
curl http://localhost:8000/policies

# Get specific policy
curl http://localhost:8000/policies/1

# Filter policies (auto insurance, $50-150)
curl "http://localhost:8000/policies?policy_type=auto&min_premium=50&max_premium=150"

# Compare policies
curl "http://localhost:8000/policies/compare?policy_ids=1,2,3"

# Get user (requires valid token)
curl "http://localhost:8000/user/me?token=YOUR_JWT_TOKEN"
```

---

## 🛠️ Environment Variables

### Backend (.env or hardcoded)
```
DATABASE_URL=postgresql://postgres:958181630@localhost:5432/insurance_db
SECRET_KEY=SECRET123  # Change in production!
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Frontend (.env.local)
```
VITE_API_URL=http://localhost:8000
```

---

## 📋 Next Steps (Weeks 3-4)

### Recommendations Engine
- [ ] User preference collection form
- [ ] Risk profile scoring algorithm
- [ ] Policy recommendation scoring
- [ ] Recommendations page with rationale
- [ ] Personalized dashboard

### Implementation Plan
1. Create `POST /user/preferences` endpoint
2. Implement scoring algorithm in Python
3. Populate Recommendations table
4. Create Recommendations React page
5. Add "Get Recommendations" button to Browse page

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process using port 8000
taskkill /PID <PID> /F

# Restart backend
python -m uvicorn main:app --reload --port 8000
```

### Database connection error
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Verify credentials and database exists
psql -U postgres -d insurance_db
```

### Frontend can't connect to backend
- Check backend is running on 8000
- Check CORS configuration in `main.py`
- Check browser console for specific errors
- Clear browser cache (Ctrl+Shift+Delete)

### "Module not found" errors
```bash
# Reinstall all dependencies
pip install -r requirements.txt
npm install
```

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/description`
2. Make changes and test locally
3. Commit with clear messages: `git commit -m "feat: description"`
4. Push to branch: `git push origin feature/description`
5. Create pull request

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review `PROJECT_DOCUMENTATION.md` for detailed info
3. Check backend logs: look for "ERROR" messages
4. Check browser console: F12 → Console tab

---

## 📅 Milestone Timeline

| Week | Phase | Status |
|------|-------|--------|
| 1-2 | Foundations & Catalog | ✅ Complete |
| 3-4 | Recommendations | 🚀 In Progress |
| 5-6 | Claims & Documents | ⏳ Planned |
| 7-8 | Fraud & Analytics | ⏳ Planned |

---

## 📚 Architecture Overview

```
┌─────────────────┐
│  React Frontend │
│  (Vite + Route) │
└────────┬────────┘
         │
         ↓ HTTP/REST
┌─────────────────┐
│  FastAPI Server │ ← Authentication (JWT)
│  (Uvicorn)      │ ← Policy Management
└────────┬────────┘
         │
         ↓ SQLAlchemy ORM
┌─────────────────┐
│  PostgreSQL DB  │
│  (8 Tables)     │
└─────────────────┘
```

---

**Created**: January 15, 2026  
**Last Updated**: January 15, 2026  
**Version**: 1.0.0  
**Status**: Alpha
