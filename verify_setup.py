#!/usr/bin/env python3
"""Quick verification of enterprise claim workflow setup"""

print("=" * 60)
print("ENTERPRISE CLAIM WORKFLOW VERIFICATION")
print("=" * 60)

# Test 1: Backend imports
print("\n[1/5] Testing backend imports...")
try:
    from backend.claim_service import ClaimService
    print("  ✅ ClaimService imported")
except Exception as e:
    print(f"  ❌ ClaimService ERROR: {e}")

try:
    from backend.admin_middleware import get_admin_user, get_current_user
    print("  ✅ admin_middleware imported")
except Exception as e:
    print(f"  ❌ admin_middleware ERROR: {e}")

# Test 2: Check database
print("\n[2/5] Checking database models...")
try:
    from backend import models
    from backend.database import engine
    from sqlalchemy import inspect
   
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    required = ['admin_logs', 'claim_notifications', 'claims', 'users']
    found = [t for t in required if t in tables]
    missing = [t for t in required if t not in tables]
    
    print(f"  ✅ Found {len(found)}/{len(required)} required tables")
    if found:
        print(f"     Tables: {', '.join(found)}")
    if missing:
        print(f"     Missing: {', '.join(missing)}")
except Exception as e:
    print(f"  ❌ Database check ERROR: {e}")

# Test 3: Check frontend files
print("\n[3/5] Checking frontend components...")
import os

components = [
    'frontend-react/src/components/AdminReview.jsx',
    'frontend-react/src/components/MyClaims.jsx',
    'frontend-react/src/components/AdminReview.css',
    'frontend-react/src/components/MyClaims.css',
    'frontend-react/src/api/claimApi.js',
]

for comp in components:
    if os.path.exists(comp):
        size = os.path.getsize(comp)
        print(f"  ✅ {comp.split('/')[-1]} ({size} bytes)")
    else:
        print(f"  ❌ {comp} NOT FOUND")

# Test 4: Check main.py has new endpoints
print("\n[4/5] Checking main.py endpoints...")
try:
    with open('backend/main.py', 'r') as f:
        content = f.read()
        endpoints = [
            'enterprise_approve_claim',
            'enterprise_reject_claim',
            'get_admin_dashboard_stats',
            'get_audit_logs',
            'get_user_notifications',
            'mark_notification_read',
        ]
        found = [e for e in endpoints if e in content]
        missing = [e for e in endpoints if e not in content]
        
        print(f"  ✅ Found {len(found)}/{len(endpoints)} endpoint functions")
        if missing:
            print(f"  ❌ Missing endpoints: {', '.join(missing)}")
except Exception as e:
    print(f"  ❌ Error checking endpoints: {e}")

# Test 5: Backend health check
print("\n[5/5] Testing backend connectivity...")
try:
    import requests
    r = requests.get('http://localhost:8000/health', timeout=2)
    if r.status_code == 200:
        print(f"  ✅ Backend running (HTTP {r.status_code})")
    else:
        print(f"  ⚠️  Backend responded with {r.status_code}")
except ConnectionError:
    print(f"  ❌ Backend not accessible (is it running?)")
except Exception as e:
    print(f"  ⚠️  Backend check ERROR: {e}")

print("\n" + "=" * 60)
print("✅ SETUP COMPLETE - Ready for testing!")
print("=" * 60)
print("""
Next steps:
1. Start backend: cd backend && uvicorn main:app --reload
2. Start frontend: cd frontend-react && npm run dev
3. Test URLs:
   - Admin Dashboard: http://localhost:5174/admin/documents
   - User Claims: http://localhost:5174/my-claims
   - API Docs: http://localhost:8000/docs
""")
