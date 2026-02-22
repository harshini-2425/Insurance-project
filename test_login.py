#!/usr/bin/env python3
"""Quick test script to verify login is working"""

import requests
import json

print("\n" + "="*70)
print("TESTING ADMIN LOGIN")
print("="*70 + "\n")

try:
    print("Sending login request...")
    
    response = requests.post(
        'http://localhost:8000/auth/login',
        json={
            'email': 'elchuritejaharshini@gmail.com',
            'password': '958181630'
        },
        timeout=5
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ LOGIN SUCCESSFUL!\n")
        print(f"Token: {data.get('access_token', '')[:50]}...")
        print(f"User ID: {data.get('user_id')}")
        
        user = data.get('user', {})
        print(f"User Name: {user.get('name')}")
        print(f"User Email: {user.get('email')}")
        print(f"User Role: {user.get('role')}")
        print(f"Is Admin: {user.get('is_admin')}")
        
    else:
        print(f"\n✗ LOGIN FAILED")
        print(f"Response: {response.json()}")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
    
print("\n" + "="*70 + "\n")
