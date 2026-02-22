#!/usr/bin/env python3
"""
Quick test script for Admin Portal endpoints
Tests JWT token generation and admin endpoints
"""

import sys
import json
import requests
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
ADMIN_EMAIL = "elchuritejaharshini@gmail.com"
ADMIN_PASSWORD = "958181630"

def colored(text, color):
    """Add color to terminal output"""
    colors = {
        'green': '\033[92m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'end': '\033[0m'
    }
    return f"{colors.get(color, '')}{text}{colors['end']}"

def test_backend_health():
    """Test if backend is running"""
    print(f"\n{colored('Testing Backend Connection...', 'blue')}")
    try:
        response = requests.get(f"{BACKEND_URL}/docs", timeout=2)
        if response.status_code == 200:
            print(colored("✓ Backend is running", "green"))
            return True
    except:
        pass
    
    print(colored("✗ Backend is not running on http://localhost:8000", "red"))
    print("  Please start the backend with: python -m uvicorn backend.main:app --reload")
    return False

def test_admin_login():
    """Test admin login and get JWT token"""
    print(f"\n{colored('Testing Admin Login...', 'blue')}")
    
    try:
        payload = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        response = requests.post(
            f"{BACKEND_URL}/api/login",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            user = data.get('user')
            
            print(colored(f"✓ Login successful", "green"))
            print(f"  User ID: {user.get('id')}")
            print(f"  Email: {user.get('email')}")
            print(f"  Role: {user.get('role')}")
            print(f"  Is Admin: {user.get('is_admin')}")
            print(f"  Token: {token[:20]}...")
            
            return token, user
        else:
            print(colored(f"✗ Login failed: {response.status_code}", "red"))
            print(f"  Response: {response.text}")
            return None, None
            
    except Exception as e:
        print(colored(f"✗ Login error: {str(e)}", "red"))
        return None, None

def test_admin_verify_role(token):
    """Test admin role verification"""
    print(f"\n{colored('Testing Role Verification...', 'blue')}")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/admin/verify-role",
            params={"token": token},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            is_admin = data.get('is_admin')
            role = data.get('role')
            
            print(colored(f"✓ Role verification successful", "green"))
            print(f"  Is Admin: {is_admin}")
            print(f"  Role: {role}")
            
            return is_admin
        else:
            print(colored(f"✗ Role verification failed: {response.status_code}", "red"))
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(colored(f"✗ Role verification error: {str(e)}", "red"))
        return False

def test_dashboard_stats(token):
    """Test dashboard statistics endpoint"""
    print(f"\n{colored('Testing Dashboard Statistics...', 'blue')}")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/admin/dashboard-stats",
            params={"token": token},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            
            print(colored(f"✓ Dashboard stats retrieved", "green"))
            print(f"  Total Users: {data.get('total_users', 0)}")
            print(f"  Total Admins: {data.get('total_admins', 0)}")
            print(f"  Total Policies: {data.get('total_policies', 0)}")
            print(f"  Total Claims: {data.get('total_claims', 0)}")
            print(f"  Total Documents: {data.get('total_documents', 0)}")
            print(f"  Active Claims: {data.get('active_claims', 0)}")
            
            return True
        else:
            print(colored(f"✗ Dashboard stats failed: {response.status_code}", "red"))
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(colored(f"✗ Dashboard stats error: {str(e)}", "red"))
        return False

def test_users_list(token):
    """Test users list endpoint"""
    print(f"\n{colored('Testing Users List...', 'blue')}")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/admin/users",
            params={"token": token, "skip": 0, "limit": 5},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            users = data.get('users', [])
            
            print(colored(f"✓ Users list retrieved", "green"))
            print(f"  Total Count: {data.get('total_count', 0)}")
            print(f"  Returned: {len(users)} users")
            
            if users:
                print(f"  First user: {users[0].get('name')} ({users[0].get('email')})")
            
            return True
        else:
            print(colored(f"✗ Users list failed: {response.status_code}", "red"))
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(colored(f"✗ Users list error: {str(e)}", "red"))
        return False

def test_documents_list(token):
    """Test documents list endpoint"""
    print(f"\n{colored('Testing Documents List...', 'blue')}")
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/admin/claim-documents-list",
            params={"token": token, "skip": 0, "limit": 5},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            docs = data.get('documents', [])
            
            print(colored(f"✓ Documents list retrieved", "green"))
            print(f"  Total Count: {data.get('total_count', 0)}")
            print(f"  Returned: {len(docs)} documents")
            
            if docs:
                doc = docs[0]
                print(f"  First document: {doc.get('file_name')} ({doc.get('file_type')})")
            
            return True
        else:
            print(colored(f"✗ Documents list failed: {response.status_code}", "red"))
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(colored(f"✗ Documents list error: {str(e)}", "red"))
        return False

def main():
    """Run all tests"""
    print(f"\n{'='*60}")
    print(colored("ADMIN PORTAL TEST SUITE", "blue"))
    print(f"{'='*60}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Admin Email: {ADMIN_EMAIL}")
    
    # Test backend health
    if not test_backend_health():
        print(f"\n{colored('Stopping tests - backend not running', 'red')}")
        return False
    
    # Test admin login
    token, user = test_admin_login()
    if not token:
        print(f"\n{colored('Stopping tests - admin login failed', 'red')}")
        return False
    
    # Test admin endpoints
    tests_passed = 0
    tests_total = 0
    
    tests = [
        ("Role Verification", test_admin_verify_role, token),
        ("Dashboard Statistics", test_dashboard_stats, token),
        ("Users List", test_users_list, token),
        ("Documents List", test_documents_list, token),
    ]
    
    for test_name, test_func, *args in tests:
        tests_total += 1
        if test_func(*args):
            tests_passed += 1
    
    # Summary
    print(f"\n{'='*60}")
    print(colored("TEST SUMMARY", "blue"))
    print(f"{'='*60}")
    print(f"Tests Passed: {colored(str(tests_passed), 'green')} / {tests_total}")
    
    if tests_passed == tests_total:
        print(colored("\n✓ All tests passed! Admin portal is working correctly.", "green"))
        print("\nNext steps:")
        print("1. Open http://localhost:5175/login in your browser")
        print(f"2. Login with:")
        print(f"   Email: {ADMIN_EMAIL}")
        print(f"   Password: {ADMIN_PASSWORD}")
        print("3. You should be redirected to /admin/dashboard")
        return True
    else:
        print(colored(f"\n✗ {tests_total - tests_passed} test(s) failed.", "red"))
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
