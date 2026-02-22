#!/usr/bin/env python3
"""
Test Home.jsx button navigation
Verifies that "Sign In" and "Create Account" buttons route correctly
"""

import re

print("=" * 80)
print("TESTING HOME.JSX BUTTON NAVIGATION")
print("=" * 80)

# Read Home.jsx
with open("frontend-react/src/pages/Home.jsx", "r", encoding="utf-8") as f:
    content = f.read()

print("\n[1] Checking Link Import...")
if "import { Link } from 'react-router-dom'" in content:
    print("    ✓ Link is imported from react-router-dom")
else:
    print("    ✗ Link import not found")

print("\n[2] Checking Register Button...")
if '<Link to="/register"' in content and "Get Started" in content:
    print("    ✓ Register button: <Link to=\"/register\"> with text 'Get Started'")
    if "Get Started →" in content:
        print("    ✓ Button text is 'Get Started →'")
else:
    print("    ✗ Register button not found")

print("\n[3] Checking Login Button...")
if '<Link to="/login"' in content and "Sign In" in content:
    print("    ✓ Login button: <Link to=\"/login\"> with text 'Sign In'")
else:
    print("    ✗ Login button not found")

# Check App.jsx routing
print("\n[4] Checking App.jsx Routes...")
with open("frontend-react/src/App.jsx", "r", encoding="utf-8") as f:
    app_content = f.read()

if 'path="/"' in app_content and '<Home />' in app_content:
    print("    ✓ Home route: <Route path=\"/\" element={<Home />} />")
else:
    print("    ✗ Home route not found")

if 'path="/login"' in app_content and '<Login />' in app_content:
    print("    ✓ Login route: <Route path=\"/login\" element={<Login />} />")
else:
    print("    ✗ Login route not found")

if 'path="/register"' in app_content and '<Register />' in app_content:
    print("    ✓ Register route: <Route path=\"/register\" element={<Register />} />")
else:
    print("    ✗ Register route not found")

if 'BrowserRouter' in app_content or 'Router >' in app_content:
    print("    ✓ BrowserRouter is configured")
else:
    print("    ✗ BrowserRouter not found")

print("\n[5] Checking Button Styles...")
if "btnPrimary" in content and "btnSecondary" in content:
    print("    ✓ Button styles are defined")
    if "textDecoration: 'none'" in content:
        print("    ✓ Link text decoration is set to 'none'")
    if "display: 'inline-block'" in content:
        print("    ✓ Button display is set to 'inline-block'")
else:
    print("    ✗ Button styles not found")

print("\n" + "=" * 80)
print("BUTTON NAVIGATION TEST RESULTS")
print("=" * 80)

all_checks = [
    ("Link import", "import { Link } from 'react-router-dom'" in content),
    ("Register button", '<Link to="/register"' in content and "Get Started" in content),
    ("Login button", '<Link to="/login"' in content and "Sign In" in content),
    ("Home route", 'path="/"' in app_content and '<Home />' in app_content),
    ("Login route", 'path="/login"' in app_content and '<Login />' in app_content),
    ("Register route", 'path="/register"' in app_content and '<Register />' in app_content),
    ("Router setup", 'BrowserRouter' in app_content or 'Router >' in app_content),
]

passed = sum(1 for _, result in all_checks if result)
total = len(all_checks)

for check, result in all_checks:
    status = "✓ PASS" if result else "✗ FAIL"
    print(f"{check.ljust(20)} → {status}")

print("\n" + "=" * 80)
if passed == total:
    print(f"✅ ALL TESTS PASSED ({passed}/{total})")
    print("\nThe buttons should work correctly:")
    print("  1. Click 'Sign In' button → Navigate to /login page")
    print("  2. Click 'Create Account Now' button → Navigate to /register page")
else:
    print(f"❌ SOME TESTS FAILED ({passed}/{total})")
    print("\nPlease fix the issues above")

print("=" * 80 + "\n")
