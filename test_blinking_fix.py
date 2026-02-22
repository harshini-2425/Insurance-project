#!/usr/bin/env python3
"""
Verify React Router blinking fix implementations
Tests:
1. Login.jsx uses Navigate component for immediate redirect
2. Register.jsx uses Navigate component for immediate redirect
3. App.jsx has correct routes (lowercase)
4. No async useEffect redirect patterns
5. Synchronous token checks before component render
"""

import re

print("=" * 80)
print("REACT ROUTER BLINKING FIX - VERIFICATION")
print("=" * 80)

all_passed = True

# Test 1: Check Login.jsx
print("\n[1] Checking Login.jsx...")
with open("frontend-react/src/pages/Login.jsx", "r", encoding="utf-8") as f:
    login_content = f.read()

checks = [
    ("Navigate import", "import { useState } from 'react'" in login_content and "Navigate" in login_content),
    ("Sync token check", "if (token) {" in login_content),
    ("Navigate component redirect", "<Navigate to=\"/\" replace />" in login_content),
    ("No useEffect", "useEffect" not in login_content),
    ("handleLogin function", "const handleLogin = async ()" in login_content),
]

for check_name, result in checks:
    status = "✓ PASS" if result else "✗ FAIL"
    print(f"    {check_name.ljust(30)} → {status}")
    if not result:
        all_passed = False

# Test 2: Check Register.jsx
print("\n[2] Checking Register.jsx...")
with open("frontend-react/src/pages/Register.jsx", "r", encoding="utf-8") as f:
    register_content = f.read()

checks = [
    ("Navigate import", "import { useState }" in register_content and "Navigate" in register_content),
    ("Sync token check", "if (token) {" in register_content),
    ("Navigate component redirect", "<Navigate to=\"/\" replace />" in register_content),
    ("No useEffect", "useEffect" not in register_content),
    ("submit function", "const submit = async ()" in register_content),
]

for check_name, result in checks:
    status = "✓ PASS" if result else "✗ FAIL"
    print(f"    {check_name.ljust(30)} → {status}")
    if not result:
        all_passed = False

# Test 3: Check App.jsx routing
print("\n[3] Checking App.jsx routes...")
with open("frontend-react/src/App.jsx", "r", encoding="utf-8") as f:
    app_content = f.read()

checks = [
    ("Home route (lowercase)", 'path="/"' in app_content and '<Home />' in app_content),
    ("Login route (lowercase)", 'path="/login"' in app_content and '<Login />' in app_content),
    ("Register route (lowercase)", 'path="/register"' in app_content and '<Register />' in app_content),
    ("BrowserRouter", "BrowserRouter" in app_content),
    ("Routes component", "<Routes>" in app_content),
]

for check_name, result in checks:
    status = "✓ PASS" if result else "✗ FAIL"
    print(f"    {check_name.ljust(30)} → {status}")
    if not result:
        all_passed = False

# Test 4: Check Home.jsx buttons
print("\n[4] Checking Home.jsx navigation...")
with open("frontend-react/src/pages/Home.jsx", "r", encoding="utf-8") as f:
    home_content = f.read()

checks = [
    ("Link import", "import { Link } from 'react-router-dom'" in home_content),
    ("Sign In button", '<Link to="/login"' in home_content and "Sign In" in home_content),
    ("Create Account button", '<Link to="/register"' in home_content and "Get Started" in home_content),
    ("No useEffect redirect", "navigate('/')" not in home_content or home_content.count("navigate('/')") == 0),
]

for check_name, result in checks:
    status = "✓ PASS" if result else "✗ FAIL"
    print(f"    {check_name.ljust(30)} → {status}")
    if not result:
        all_passed = False

# Test 5: Check for blinking patterns
print("\n[5] Checking for potential blinking patterns...")
blinking_patterns = [
    ("useRef pattern in Login", "useRef" in login_content and "Login" in login_content),
    ("useRef pattern in Register", "useRef" in register_content and "Register" in register_content),
    ("Multiple Navigate components", login_content.count("<Navigate") > 0 and register_content.count("<Navigate") > 0),
]

for check_name, result in blinking_patterns:
    # For these, we want them to be FALSE (not present)
    should_not_exist = not result
    status = "✓ PASS" if should_not_exist else "✗ POSSIBLE ISSUE"
    print(f"    {check_name.ljust(30)} → {status}")
    if not should_not_exist and "useRef" not in check_name:
        all_passed = False

print("\n" + "=" * 80)
print("EXPECTED BEHAVIOR AFTER FIX")
print("=" * 80)
print("""
When user clicks "Sign In" button:
  1. Click Sign In on Home page
  2. Immediate navigation to /login route
  3. Login.jsx component loads
  4. Synchronous token check runs BEFORE render
  5. If no token → Show login form
  6. If token exists → Immediately redirect to "/" WITHOUT showing form
  7. ✓ No blinking, smooth navigation

When user clicks "Create Account Now" button:
  1. Click Create Account on Home page
  2. Immediate navigation to /register route
  3. Register.jsx component loads
  4. Synchronous token check runs BEFORE render
  5. If no token → Show register form
  6. If token exists → Immediately redirect to "/" WITHOUT showing form
  7. ✓ No blinking, smooth navigation

Key Differences from Old Implementation:
  OLD: useEffect → runs AFTER first render → can see form briefly → blinking ❌
  NEW: Synchronous check → runs BEFORE render → form never visible if redirecting ✓
""")

print("=" * 80)
if all_passed:
    print("✅ ALL TESTS PASSED - BLINKING FIX IS PROPERLY IMPLEMENTED")
else:
    print("⚠️  SOME TESTS FAILED - REVIEW THE ISSUES ABOVE")

print("=" * 80 + "\n")
