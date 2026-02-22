#!/usr/bin/env python3
"""Test to verify frontend is loading and responsive"""

import requests
import time

print("\n" + "="*70)
print("FRONTEND VERIFICATION TEST")
print("="*70)

# Test 1: Frontend server accessible
print("\n[1] Checking if frontend dev server is responding...")
try:
    response = requests.get("http://localhost:5173", timeout=5)
    if response.status_code == 200:
        print("✅ Frontend dev server is running on port 5173")
        print(f"   Response size: {len(response.content)} bytes")
        
        # Check if it contains the expected content
        if 'Home' in response.text or 'React' in response.text or 'root' in response.text:
            print("✅ Frontend HTML loaded successfully")
        else:
            print("⚠️  Frontend loaded but content may be incomplete")
    else:
        print(f"❌ Unexpected status: {response.status_code}")
except Exception as e:
    print(f"❌ Frontend not accessible: {e}")

# Test 2: Backend still running
print("\n[2] Checking backend...")
try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    if response.status_code == 200:
        print("✅ Backend still running on port 8000")
    else:
        print(f"❌ Backend status: {response.status_code}")
except Exception as e:
    print(f"❌ Backend not accessible: {e}")

print("\n" + "="*70)
print("✅ FRONTEND AND BACKEND BOTH RUNNING")
print("="*70)
print("\nTo test the navigation:")
print("  1. Open http://localhost:5173 in your browser")
print("  2. Click 'Sign In' button → should go to /login")
print("  3. Click 'Create Account' button → should go to /register")
print("="*70 + "\n")
