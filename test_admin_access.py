#!/usr/bin/env python3
"""
Test the login endpoint to verify admin access is properly restricted
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Test credentials
test_cases = [
    {
        "name": "Admin User",
        "email": "elchuritejaharshini@gmail.com",
        "password": "958181630",
        "expect_admin": True
    },
    {
        "name": "Regular User",
        "email": "test@example.com",
        "password": "password123",
        "expect_admin": False
    },
    {
        "name": "Raj (Previously Admin)",
        "email": "Raj@gmail.com",
        "password": "raj123",
        "expect_admin": False
    }
]

print("=" * 80)
print("TESTING LOGIN ENDPOINT - ADMIN ACCESS VERIFICATION")
print("=" * 80)

for test_case in test_cases:
    print(f"\n{'-' * 80}")
    print(f"Test: {test_case['name']}")
    print(f"Email: {test_case['email']}")
    print(f"Expected Admin: {test_case['expect_admin']}")
    print(f"{'-' * 80}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": test_case["email"],
                "password": test_case["password"]
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            user = data.get("user", {})
            is_admin = user.get("is_admin", False)
            role = user.get("role", "unknown")
            
            print(f"✓ Login successful")
            print(f"  - User ID: {data.get('user_id')}")
            print(f"  - Email: {user.get('email')}")
            print(f"  - is_admin: {is_admin}")
            print(f"  - role: {role}")
            
            # Check if admin status matches expectation
            if is_admin == test_case["expect_admin"]:
                print(f"✓ PASS: Admin status is correct")
            else:
                print(f"✗ FAIL: Admin status mismatch!")
                print(f"  Expected: {test_case['expect_admin']}, Got: {is_admin}")
        
        elif response.status_code == 401:
            print(f"✗ Login failed: Invalid credentials")
            print(f"  Response: {response.json()}")
        else:
            print(f"✗ Unexpected response: {response.status_code}")
            print(f"  Response: {response.text}")
    
    except Exception as e:
        print(f"✗ Error during test: {e}")

print(f"\n{'=' * 80}")
print("Testing complete")
print("=" * 80)
