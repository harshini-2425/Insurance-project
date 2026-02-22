import requests
import sys

BASE_URL = "http://localhost:8000"

print("\n==== SYSTEM VERIFICATION ====\n")

# 1. Admin can login
print("[1/5] Testing admin login...")
resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "elchuritejaharshini@gmail.com", "password": "958181630"})
if resp.status_code == 200:
    admin_data = resp.json()
    admin_token = admin_data.get("access_token")
    is_admin = admin_data.get("user", {}).get("is_admin")
    print(f"[PASS] Admin login (is_admin={is_admin})")
else:
    print(f"[FAIL] Admin login ({resp.status_code})")
    admin_token = None

# 2. Admin can access admin endpoints
if admin_token:
    print("\n[2/5] Testing admin endpoint access...")
    resp = requests.get(f"{BASE_URL}/admin/users", params={"token": admin_token})
    if resp.status_code == 200:
        print(f"[PASS] Admin endpoint")
    else:
        print(f"[FAIL] Admin endpoint ({resp.status_code})")

# 3. Notifications endpoint exists
print("\n[3/5] Testing notification endpoint...")
try:
    # Try to get notifications (will fail without token, but endpoint should exist)
    resp = requests.get(f"{BASE_URL}/api/user/notifications", params={"token": "invalid"})
    if resp.status_code in [401, 403]:  # Expected auth error
        print("[PASS] Notification endpoint exists")
    else:
        print(f"[INFO] Notification response: {resp.status_code}")
except Exception as e:
    print(f"[FAIL] Notification endpoint ({e})")

# 4. Frontend is running
print("\n[4/5] Testing frontend...")
try:
    resp = requests.get("http://localhost:5173")
    if resp.status_code == 200:
        print("[PASS] Frontend server")
    else:
        print(f"[INFO] Frontend: {resp.status_code}")
except:
    print("[FAIL] Frontend server (not reachable)")

# 5. Backend health check
print("\n[5/5] Testing backend health...")
resp = requests.get(f"{BASE_URL}/health")
if resp.status_code == 200:
    data = resp.json()
    db_status = data.get("db_status")
    print(f"[PASS] Backend health (DB: {db_status})")
else:
    print(f"[FAIL] Backend health")

print("\n==== VERIFICATION COMPLETE ====\n")
