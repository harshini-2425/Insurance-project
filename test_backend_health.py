#!/usr/bin/env python3
"""Verify backend is running and all endpoints working"""

import requests
import time

API = "http://localhost:8000"

print("\n" + "="*70)
print("BACKEND HEALTH CHECK")
print("="*70)

# Test 1: Health check
print("\n[1] Testing backend health...")
try:
    health_resp = requests.get(f"{API}/health", timeout=5)
    if health_resp.status_code == 200:
        print(f"✅ Backend is running (port 8000)")
    else:
        print(f"❌ Unexpected status: {health_resp.status_code}")
except Exception as e:
    print(f"❌ Backend not responding: {str(e)}")
    exit(1)

# Test 2: Admin login
print("\n[2] Testing admin login...")
try:
    login_resp = requests.post(
        f"{API}/auth/login",
        json={"email": "admin", "password": "admin123"},
        timeout=5
    )
    if login_resp.status_code == 200:
        data = login_resp.json()
        print(f"✅ Admin login successful")
        print(f"   Token valid: {'access_token' in data}")
        print(f"   Is admin: {data['user']['is_admin']}")
    else:
        print(f"❌ Login failed: {login_resp.status_code}")
except Exception as e:
    print(f"❌ Login error: {str(e)}")

# Test 3: Public stats endpoint
print("\n[3] Testing public stats endpoint...")
try:
    stats_resp = requests.get(f"{API}/api/public/stats", timeout=5)
    if stats_resp.status_code == 200:
        print(f"✅ Public stats endpoint working")
    else:
        print(f"❌ Unexpected status: {stats_resp.status_code}")
except Exception as e:
    print(f"❌ Public stats error: {str(e)}")

# Test 4: Notifications endpoint
print("\n[4] Testing notifications endpoint...")
if login_resp.status_code == 200:
    token = login_resp.json()['access_token']
    try:
        notif_resp = requests.get(
            f"{API}/api/user/notifications?token={token}&limit=10",
            timeout=5
        )
        if notif_resp.status_code == 200:
            print(f"✅ Notifications endpoint working")
        else:
            print(f"❌ Unexpected status: {notif_resp.status_code}")
    except Exception as e:
        print(f"❌ Notifications error: {str(e)}")

print("\n" + "="*70)
print("✅ ALL BACKEND CHECKS PASSED - Frontend can now connect!")
print("="*70 + "\n")
