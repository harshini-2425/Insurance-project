"""Test script to verify Home page redirect fix"""

import subprocess
import time
import requests
import json

print("\n" + "="*60)
print("HOME PAGE REDIRECT FIX TEST")
print("="*60)

print("\n1. Clear browser localStorage and refresh page...")
print("   → Run this in browser console:")
print("   → localStorage.clear(); location.reload();")
print()

print("2. Check if /user/profile endpoint exists on backend...")
try:
    response = requests.get('http://localhost:8000/user/profile')
    print(f"   Response status: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ❌ Backend not running on port 8000")
except Exception as e:
    print(f"   Error: {e}")

print("\n3. List available backend endpoints...")
print("   Checking main.py for available routes...")
try:
    with open(r'c:\newproject\backend\main.py', 'r', encoding='utf-8') as f:
        content = f.read()
        # Find all @app.get or @app.post routes
        import re
        routes = re.findall(r'@app\.\w+\("([^"]+)"', content)
        print(f"\n   Found {len(set(routes))} unique routes:")
        for route in sorted(set(routes)):
            if 'user' in route.lower() or 'profile' in route.lower() or 'me' in route.lower() or route == '/':
                print(f"      {route}")
except Exception as e:
    print(f"   Error reading main.py: {e}")

print("\n4. Test steps to verify fix:")
print("   ✓ Open DevTools (F12)")
print("   ✓ Go to Application → Local Storage")
print("   ✓ Clear all localStorage entries")
print("   ✓ Refresh page (Ctrl+R)")
print("   ✓ Should see HOME page, NOT dashboard redirect")
print("   ✓ Check console for: '[Home] No valid token/user'")
print("\n5. Test button navigation:")
print("   ✓ Click 'Sign In' button")
print("   ✓ Should navigate to /login")
print("   ✓ Click 'Get Started' button")
print("   ✓ Should navigate to /register")
print(f"   ✓ No red errors in console")

print("\n" + "="*60)
print("To complete the test:")
print("1. Open http://localhost:5173/")
print("2. Clear localStorage in DevTools")
print("3. Refresh the page")
print("4. Report what you see")
print("="*60 + "\n")
