#!/usr/bin/env python3
"""
End-to-end test script for the insurance platform.
Tests: User authentication, claims, documents, admin approval, and notifications.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Test users
TEST_ADMIN_EMAIL = "elchuritejaharshini@gmail.com"
TEST_ADMIN_PWD = "958181630"
TEST_USER_EMAIL = "testuser@example.com"
TEST_USER_PWD = "password123"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_test(status, test_name, details=""):
    symbol = "✅" if status == "PASS" else "❌"
    print(f"{symbol} {test_name}")
    if details:
        print(f"   {details}")

def register_user(email, password, name="Test User", dob="1990-01-01"):
    """Register a new user"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "name": name,
                "email": email,
                "password": password,
                "dob": dob
            }
        )
        if response.status_code == 200:
            data = response.json()
            return True, data.get("access_token"), data.get("user_id")
        else:
            return False, None, None
    except Exception as e:
        return False, None, None

def login_user(email, password):
    """Login user and get token"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": email,
                "password": password
            }
        )
        if response.status_code == 200:
            data = response.json()
            return True, data.get("access_token"), data.get("user_id")
        else:
            return False, None, None
    except Exception as e:
        return False, None, None

def test_authentication():
    """Test user authentication"""
    print_section("1. AUTHENTICATION TESTS")
    
    # Test login
    success, admin_token, admin_id = login_user(TEST_ADMIN_EMAIL, TEST_ADMIN_PWD)
    print_test("PASS" if success else "FAIL", "Admin login", f"Token: {admin_token[:20]}..." if admin_token else "No token")
    
    success, user_token, user_id = login_user(TEST_USER_EMAIL, TEST_USER_PWD)
    print_test("PASS" if success else "FAIL", "Regular user login", f"User ID: {user_id}")
    
    return admin_token, admin_id, user_token, user_id

def test_admin_access(admin_token):
    """Test admin-only endpoints"""
    print_section("2. ADMIN ACCESS TESTS")
    
    # Test admin users list
    try:
        response = requests.get(
            f"{BASE_URL}/admin/users",
            params={"token": admin_token}
        )
        success = response.status_code == 200
        print_test("PASS" if success else "FAIL", "Admin users list access", f"Status: {response.status_code}")
    except Exception as e:
        print_test("FAIL", "Admin users list access", str(e))

def test_user_claims(user_token, user_id):
    """Test user claim creation and retrieval"""
    print_section("3. USER CLAIMS TESTS")
    
    # Get user claims
    try:
        response = requests.get(
            f"{BASE_URL}/api/user/{user_id}/claims",
            params={"token": user_token}
        )
        success = response.status_code == 200
        claim_count = 0
        if success:
            data = response.json()
            claims = data.get("claims", [])
            claim_count = len(claims)
        print_test("PASS" if success else "FAIL", "Get user claims", f"Found {claim_count} claims")
        return claims if success else []
    except Exception as e:
        print_test("FAIL", "Get user claims", str(e))
        return []

def test_admin_documents(admin_token):
    """Test admin document endpoints"""
    print_section("4. ADMIN DOCUMENTS TESTS")
    
    # Get admin claim documents list
    try:
        response = requests.get(
            f"{BASE_URL}/admin/claim-documents-list",
            params={"token": admin_token}
        )
        success = response.status_code == 200
        doc_count = 0
        documents = []
        if success:
            data = response.json()
            documents = data.get("documents", [])
            doc_count = len(documents)
        print_test("PASS" if success else "FAIL", "Admin documents list", f"Found {doc_count} documents")
        return documents[:5] if success else []
    except Exception as e:
        print_test("FAIL", "Admin documents list", str(e))
        return []

def test_notifications(user_token, user_id):
    """Test notification endpoints"""
    print_section("5. NOTIFICATION TESTS")
    
    # Get user notifications
    try:
        response = requests.get(
            f"{BASE_URL}/api/user/notifications",
            params={"token": user_token, "limit": 10}
        )
        success = response.status_code == 200
        notif_count = 0
        if success:
            data = response.json()
            notifications = data.get("notifications", [])
            notif_count = len(notifications)
        print_test("PASS" if success else "FAIL", "Get user notifications", f"Found {notif_count} notifications")
        return notifications if success else []
    except Exception as e:
        print_test("FAIL", "Get user notifications", str(e))
        return []

def test_frontend_endpoints():
    """Test critical frontend endpoints"""
    print_section("6. FRONTEND ENDPOINT TESTS")
    
    # Test policies endpoint (public)
    try:
        response = requests.get(f"{BASE_URL}/policies")
        success = response.status_code == 200
        print_test("PASS" if success else "FAIL", "Public policies endpoint", f"Status: {response.status_code}")
    except Exception as e:
        print_test("FAIL", "Public policies endpoint", str(e))

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  INSURANCE PLATFORM - END-TO-END TEST")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*60)
    
    # Run authentication tests
    admin_token, admin_id, user_token, user_id = test_authentication()
    
    if admin_token and user_token:
        # Run other tests
        test_admin_access(admin_token)
        claims = test_user_claims(user_token, user_id)
        documents = test_admin_documents(admin_token)
        notifications = test_notifications(user_token, user_id)
        test_frontend_endpoints()
        
        print_section("SUMMARY")
        print("✅ Authentication: PASS")
        print(f"⏳ User has {len(claims)} claims")
        print(f"⏳ Admin can see {len(documents)} documents")
        print(f"⏳ User has {len(notifications)} notifications")
    else:
        print("\n❌ Authentication failed - cannot proceed with tests")
    
    print("\n" + "="*60)
    print("  TEST COMPLETED")
    print("="*60 + "\n")
