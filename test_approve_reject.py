import requests
import json

BASE_URL = "http://localhost:8000"

# First, login as admin
print("1. Admin login...")
resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "elchuritejaharshini@gmail.com", "password": "958181630"})
if resp.status_code != 200:
    print(f"Login failed: {resp.text}")
    exit(1)

admin_token = resp.json().get("access_token")
print(f"   Admin token: {admin_token[:30]}...")

# Get documents list
print("\n2. Get documents list...")
resp = requests.get(f"{BASE_URL}/admin/claim-documents-list", params={"token": admin_token})
if resp.status_code != 200:
    print(f"Failed: {resp.status_code} - {resp.text}")
    exit(1)

data = resp.json()
documents = data.get("data", {}).get("documents", [])
print(f"   Found {len(documents)} documents")

if not documents:
    print("   No documents to test with. Creating test data would be needed.")
    exit(0)

# Get first document
doc = documents[0]
doc_id = doc.get("id")
print(f"   Testing with document ID: {doc_id}")

# Test approve
print(f"\n3. Testing APPROVE endpoint...")
resp = requests.post(
    f"{BASE_URL}/admin/documents/{doc_id}/approve",
    params={"token": admin_token, "comments": "Test approval"}
)

if resp.status_code == 200:
    result = resp.json()
    print(f"   SUCCESS: {result.get('message')}")
    print(f"   Status: {result.get('status')}")
else:
    print(f"   FAILED: {resp.status_code}")
    print(f"   Response: {resp.text[:300]}")

print("\n4. Testing REJECT endpoint (different document)...")
if len(documents) > 1:
    doc2 = documents[1]
    doc_id2 = doc2.get("id")
    resp = requests.post(
        f"{BASE_URL}/admin/documents/{doc_id2}/reject",
        params={"token": admin_token, "reason": "Test rejection"}
    )
    
    if resp.status_code == 200:
        result = resp.json()
        print(f"   SUCCESS: {result.get('message')}")
        print(f"   Status: {result.get('status')}")
    else:
        print(f"   FAILED: {resp.status_code}")
        print(f"   Response: {resp.text[:300]}")

print("\n5. Check notifications were created...")
# Login as regular user to check notifications
resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "testuser@example.com", "password": "password123"})
if resp.status_code == 200:
    user_token = resp.json().get("access_token")
    resp = requests.get(f"{BASE_URL}/api/user/notifications", params={"token": user_token, "limit": 10})
    if resp.status_code == 200:
        notifs = resp.json().get("notifications", [])
        print(f"   User has {len(notifs)} notifications")
        for notif in notifs[-2:]:  # Show last 2 notifications
            print(f"     - {notif.get('title')}: {notif.get('message')[:50]}")

print("\nTest complete!")
