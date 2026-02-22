"""
Complete test to verify Home page fixes
Tests:
1. Home page accessibility without redirect
2. Button navigation functionality
3. Proper token validation
"""

import requests
import json
import time

print("\n" + "="*70)
print("HOME PAGE FIX VERIFICATION TEST")
print("="*70 + "\n")

# Test 1: Check backend is running
print("1. Checking backend health...")
try:
    response = requests.get('http://localhost:8000/health')
    if response.status_code == 200:
        print("   ✅ Backend running on port 8000")
    else:
        print(f"   ⚠️  Backend responded with status {response.status_code}")
except Exception as e:
    print(f"   ❌ Backend not responding: {e}")
    print("   Please ensure backend is running with: python -m uvicorn backend.main:app --reload")

# Test 2: Check frontend is running
print("\n2. Checking frontend dev server...")
try:
    response = requests.get('http://localhost:5173/')
    if response.status_code == 200:
        print("   ✅ Frontend running on port 5173")
    else:
        print(f"   ⚠️  Frontend responded with status {response.status_code}")
except Exception as e:
    print(f"   ❌ Frontend not responding: {e}")
    print("   Please ensure frontend is running with: npm run dev (in frontend-react folder)")

# Test 3: Check /user/me endpoint exists
print("\n3. Checking /user/me endpoint (for token validation)...")
try:
    # Without token (should fail or return 401)
    response = requests.get('http://localhost:8000/user/me')
    print(f"   Response status: {response.status_code}")
    if response.status_code in [401, 403]:
        print("   ✅ Endpoint exists and requires authentication (correct!)")
    else:
        print(f"   ⚠️  Unexpected response: {response.status_code}")
except Exception as e:
    print(f"   ❌ Endpoint check failed: {e}")

# Test 4: Check Home.jsx was updated
print("\n4. Checking Home.jsx token validation code...")
try:
    with open(r'c:\newproject\frontend-react\src\pages\Home.jsx', 'r', encoding='utf-8') as f:
        content = f.read()
        checks = [
            ('Backend validation call', 'http://localhost:8000/user/me'),
            ('Authorization header', 'Authorization'),
            ('Token validation', 'validateAndRedirect'),
            ('Button Get Started', 'Get Started'),
            ('Button Sign In', 'Sign In'),
            ('Button Create Account', 'Create Account Now'),
            ('Navigate function calls', 'navigate(\'/login\''),
        ]
        
        for check_name, check_string in checks:
            if check_string in content:
                print(f"   ✅ {check_name}")
            else:
                print(f"   ❌ {check_name} - NOT FOUND")
                
except Exception as e:
    print(f"   ❌ Could not read Home.jsx: {e}")

# Test 5: Check if Login and Register pages exist
print("\n5. Checking routing pages...")
try:
    login_exists = False
    register_exists = False
    
    try:
        with open(r'c:\newproject\frontend-react\src\pages\Login.jsx', 'r', encoding='utf-8') as f:
            login_exists = True
            print("   ✅ Login.jsx exists")
    except:
        print("   ❌ Login.jsx NOT found")
    
    try:
        with open(r'c:\newproject\frontend-react\src\pages\Register.jsx', 'r', encoding='utf-8') as f:
            register_exists = True
            print("   ✅ Register.jsx exists")
    except:
        print("   ❌ Register.jsx NOT found")
        
except Exception as e:
    print(f"   ❌ Error checking pages: {e}")

print("\n" + "="*70)
print("NEXT STEPS TO TEST THE FIX:")
print("="*70)
print("""
1. Open http://localhost:5173/ in your browser

2. IMPORTANT: Clear browser storage first
   - Press F12 to open DevTools
   - Go to "Application" tab
   - Expand "Local Storage"
   - Click "http://localhost:5173"
   - Delete all entries
   - Close DevTools

3. Refresh the page (Ctrl+R or F5)
   EXPECTED RESULT: Should see the HOME page with blue buttons
   DO NOT: Should NOT redirect to dashboard

4. Verify console output
   - Press F12 again to open DevTools
   - Go to "Console" tab
   - Should see: "[Home] No valid token/user, showing home page"
   
5. Test button navigation
   - Click "Sign In" button
   - Expected URL change: localhost:5173/login
   
   - Go back to home page (click browser back or navigate to /)
   - Click "Get Started" button
   - Expected URL change: localhost:5173/register
   
   - Go back to home page
   - Click "Create Account Now" button
   - Expected URL change: localhost:5173/register

6. If buttons DON'T work:
   - Check browser console for red ERROR messages
   - Report any errors to the agent
   
7. Testing backend validation (optional)
   - Login with a real account
   - Refresh the page
   - Should be redirected to /dashboard (because token is valid)
   - This confirms the token validation is working

""")
print("="*70 + "\n")
