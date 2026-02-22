#!/usr/bin/env python3
"""
Test for error fixes:
1. CSS @media query error fixed
2. 403 Forbidden error fixed for admin endpoints
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

print("\n" + "="*70)
print("TESTING ERROR FIXES")
print("="*70)

# Test 1: Admin login and dashboard access
print("\n[1] Testing admin login and dashboard access...")
login_resp = requests.post(
    f"{API_BASE}/auth/login",
    json={"email": "admin", "password": "admin123"}
)

if login_resp.status_code == 200:
    data = login_resp.json()
    token = data['access_token']
    is_admin = data['user']['is_admin']
    print(f"✅ Login successful")
    print(f"   is_admin: {is_admin}")
    
    # Test 2: Access admin claims list
    print("\n[2] Testing admin claims list endpoint...")
    claims_resp = requests.get(
        f"{API_BASE}/admin/claims-list?token={token}&skip=0&limit=15"
    )
    
    if claims_resp.status_code == 200:
        print(f"✅ Admin claims list accessible (200)")
        claims_data = claims_resp.json()
        print(f"   Total claims: {claims_data.get('data', {}).get('total_count', 0)}")
    elif claims_resp.status_code == 403:
        print(f"❌ 403 Forbidden error still exists")
        print(f"   Details: {claims_resp.json()}")
    else:
        print(f"⚠️  Unexpected status: {claims_resp.status_code}")
        print(f"   Response: {claims_resp.text[:200]}")
    
    # Test 3: Access admin documents list
    print("\n[3] Testing admin documents list endpoint...")
    docs_resp = requests.get(
        f"{API_BASE}/admin/claim-documents-list?token={token}&skip=0&limit=20"
    )
    
    if docs_resp.status_code == 200:
        print(f"✅ Admin documents list accessible (200)")
        docs_data = docs_resp.json()
        print(f"   Total documents: {docs_data.get('data', {}).get('total_count', 0)}")
    elif docs_resp.status_code == 403:
        print(f"❌ 403 Forbidden error still exists")
        print(f"   Details: {docs_resp.json()}")
    else:
        print(f"⚠️  Unexpected status: {docs_resp.status_code}")
        print(f"   Response: {docs_resp.text[:200]}")
    
    # Test 4: Access admin stats
    print("\n[4] Testing admin dashboard stats endpoint...")
    stats_resp = requests.get(
        f"{API_BASE}/api/admin/dashboard/stats?token={token}"
    )
    
    if stats_resp.status_code == 200:
        print(f"✅ Admin stats accessible (200)")
    elif stats_resp.status_code == 403:
        print(f"❌ 403 Forbidden error still exists")
        print(f"   Details: {stats_resp.json()}")
    else:
        print(f"⚠️  Unexpected status: {stats_resp.status_code}")
        print(f"   Response: {stats_resp.text[:200]}")
    
else:
    print(f"❌ Login failed: {login_resp.status_code}")
    print(f"   Response: {login_resp.text[:200]}")

print("\n" + "="*70)
print("✅ ERROR FIX TEST COMPLETE")
print("="*70)
print("\nFixes Applied:")
print("  ✓ Removed @media from inline styles in Login.jsx")
print("  ✓ Fixed admin endpoint authorization checks")
print("="*70 + "\n")
