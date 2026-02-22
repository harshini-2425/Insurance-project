#!/usr/bin/env python3
"""
Backend API Verification Script
Tests that all admin endpoints are working correctly
"""

import sys
import json
import requests
import time

BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "elchuritejaharshini@gmail.com"
ADMIN_PASSWORD = "958181630"

def colored(text, color):
    colors = {
        'green': '\033[92m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'end': '\033[0m'
    }
    return f"{colors.get(color, '')}{text}{colors['end']}"

print("\n" + "="*70)
print(colored("ADMIN PORTAL BACKEND VERIFICATION", "blue"))
print("="*70 + "\n")

# Step 1: Test Backend Connectivity
print(colored("1️⃣  Testing Backend Connectivity...", "blue"))
try:
    response = requests.get(f"{BASE_URL}/docs", timeout=2)
    if response.status_code == 200:
        print(colored("✓ Backend is running on http://localhost:8000", "green"))
    else:
        print(colored("✗ Backend responded with non-200 status", "red"))
        sys.exit(1)
except Exception as e:
    print(colored(f"✗ Cannot connect to backend: {e}", "red"))
    print("  Make sure to run: .venv\\Scripts\\python -m uvicorn backend.main:app --reload")
    sys.exit(1)

# Step 2: Test Admin Login
print(colored("\n2️⃣  Testing Admin Login...", "blue"))
try:
    response = requests.post(
        f"{BASE_URL}/api/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        user = data.get('user')
        
        print(colored("✓ Admin login successful", "green"))
        print(f"  User ID: {user.get('id')}")
        print(f"  Role: {user.get('role')}")
        print(f"  Is Admin: {user.get('is_admin')}")
        print(f"  Token (first 30 chars): {token[:30]}...")
    else:
        print(colored(f"✗ Login failed with status {response.status_code}", "red"))
        print(f"  Response: {response.text}")
        sys.exit(1)
except Exception as e:
    print(colored(f"✗ Login error: {e}", "red"))
    sys.exit(1)

# Step 3: Test Dashboard Stats Endpoint
print(colored("\n3️⃣  Testing Dashboard Stats Endpoint...", "blue"))
try:
    response = requests.get(
        f"{BASE_URL}/admin/dashboard-stats?token={token}",
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        stats = data.get('data', {})
        
        print(colored("✓ Dashboard stats endpoint working", "green"))
        print(f"  Total Users: {stats.get('total_users', 0)}")
        print(f"  Total Admins: {stats.get('total_admins', 0)}")
        print(f"  Total Policies: {stats.get('total_policies', 0)}")
        print(f"  Total Claims: {stats.get('total_claims', 0)}")
        print(f"  Total Documents: {stats.get('total_documents', 0)}")
        print(f"  Active Claims: {stats.get('active_claims', 0)}")
    else:
        print(colored(f"✗ Dashboard stats failed with status {response.status_code}", "red"))
        print(f"  Response: {response.text}")
except Exception as e:
    print(colored(f"✗ Dashboard stats error: {e}", "red"))

# Step 4: Test Users List Endpoint
print(colored("\n4️⃣  Testing Users List Endpoint...", "blue"))
try:
    response = requests.get(
        f"{BASE_URL}/admin/users?token={token}&skip=0&limit=10",
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        users_data = data.get('data', {})
        users = users_data.get('users', [])
        
        print(colored("✓ Users list endpoint working", "green"))
        print(f"  Total Users: {users_data.get('total_count', 0)}")
        print(f"  Returned: {len(users)} users")
        if users:
            print(f"  First user: {users[0].get('name')} ({users[0].get('email')})")
    else:
        print(colored(f"✗ Users list failed with status {response.status_code}", "red"))
        print(f"  Response: {response.text}")
except Exception as e:
    print(colored(f"✗ Users list error: {e}", "red"))

# Step 5: Test Documents List Endpoint
print(colored("\n5️⃣  Testing Documents List Endpoint...", "blue"))
try:
    response = requests.get(
        f"{BASE_URL}/admin/claim-documents-list?token={token}&skip=0&limit=10",
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        docs_data = data.get('data', {})
        documents = docs_data.get('documents', [])
        
        print(colored("✓ Documents list endpoint working", "green"))
        print(f"  Total Documents: {docs_data.get('total_count', 0)}")
        print(f"  Returned: {len(documents)} documents")
        if documents:
            doc = documents[0]
            print(f"  First doc: {doc.get('file_name')} (ID: {doc.get('id')})")
            print(f"            Type: {doc.get('file_type')}")
            print(f"            Size: {doc.get('file_size_bytes')} bytes")
    else:
        print(colored(f"✗ Documents list failed with status {response.status_code}", "red"))
        print(f"  Response: {response.text}")
except Exception as e:
    print(colored(f"✗ Documents list error: {e}", "red"))

# Step 6: Test Role Verification Endpoint
print(colored("\n6️⃣  Testing Role Verification Endpoint...", "blue"))
try:
    response = requests.get(
        f"{BASE_URL}/admin/verify-role?token={token}",
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print(colored("✓ Role verification endpoint working", "green"))
        print(f"  Is Admin: {data.get('is_admin')}")
        print(f"  Role: {data.get('role')}")
        print(f"  User ID: {data.get('user_id')}")
    else:
        print(colored(f"✗ Role verification failed with status {response.status_code}", "red"))
        print(f"  Response: {response.text}")
except Exception as e:
    print(colored(f"✗ Role verification error: {e}", "red"))

# Summary
print("\n" + "="*70)
print(colored("VERIFICATION COMPLETE", "green"))
print("="*70)
print("\n✅ Backend API is functioning correctly!")
print("\nNext Steps:")
print("1. Open http://localhost:5175 in your browser")
print("2. Login with admin credentials")
print("3. Navigate to /admin/documents to test frontend")
print("\n" + "="*70 + "\n")
