"""
Quick console commands for testing
Copy and paste these into browser DevTools Console (F12)
"""

import json

print("\n" + "="*70)
print("BROWSER CONSOLE COMMANDS FOR TESTING")
print("="*70 + "\n")

print("1. CHECK CURRENT LOCALSTORAGE:\n")
print("   localStorage")
print()

print("2. CLEAR ALL LOCALSTORAGE (fixes 'redirects to dashboard' issue):\n")
print("   localStorage.clear(); location.reload();")
print()

print("3. MANUALLY TEST TOKEN VALIDATION ENDPOINT:\n")
print("   fetch('http://localhost:8000/user/me', {")
print("       headers: { 'Authorization': 'Bearer YOUR_TOKEN_HERE' }")
print("   }).then(r => r.json()).then(d => console.log(d))")
print()

print("4. CHECK IF BUTTONS CAN NAVIGATE (from Home.jsx):\n")
print("   // Should work if router is set up correctly")
print("   window.location.href = '/login'")
print()

print("5. DEBUG: Check if useNavigate hook works:\n")
print("   // Search for 'Navigate' in console when button clicked")
print("   // Should see: '[Home] Navigate called successfully'")
print()

print("="*70)
print("\nIMPORTANT:")
print("=" * 70)
print("""
The fix is already applied to Home.jsx. To test it:

1. Open http://localhost:5173/ in browser
2. Press F12 to open DevTools
3. Go to Application → Local Storage → http://localhost:5173
4. Delete all entries (or run: localStorage.clear() in console)
5. Refresh page (F5 or Ctrl+R)
6. Press F12 again and go to Console tab
7. You should see: "[Home] No valid token/user, showing home page"
8. The page should display the HOME page (NOT redirect to dashboard)
9. Click buttons to test navigation

If you still see redirect to dashboard:
- Check if any localStorage entries remain
- Try: localStorage.clear(); location.reload();
- Check console for errors (should be empty/green logs only)
""")
print("="*70 + "\n")
