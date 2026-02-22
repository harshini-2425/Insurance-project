#!/usr/bin/env python3
import requests

BASE_URL = "http://localhost:8000"

print("\n=== Testing Approve/Reject with CORS Fixes ===\n")

# 1. Login
print("[1] Admin login...")
r = requests.post(f"{BASE_URL}/auth/login", json={"email": "elchuritejaharshini@gmail.com", "password": "958181630"})
if r.status_code != 200:
    print(f"   FAILED: {r.status_code}")
    exit(1)

token = r.json().get("access_token")
print(f"   SUCCESS: token={token[:30]}...")

# 2. Get documents
print("\n[2] Get documents...")
r = requests.get(f"{BASE_URL}/admin/claim-documents-list?token={token}")
if r.status_code != 200:
    print(f"   FAILED: {r.status_code}")
    exit(1)

docs = r.json().get("data", {}).get("documents", [])
print(f"   SUCCESS: found {len(docs)} documents")

if not docs:
    print("   No documents available for testing")
    exit(0)

# 3. Test approve
doc_id = docs[0].get("id")
print(f"\n[3] Approve document {doc_id}...")
r = requests.post(
    f"{BASE_URL}/admin/documents/{doc_id}/approve?token={token}",
    headers={"Content-Type": "application/json"}
)
print(f"   Status: {r.status_code}")
if r.status_code != 200:
    print(f"   Response: {r.text[:300]}")
else:
    print(f"   SUCCESS: {r.json()}")

# 4. Test reject (if second doc exists)
if len(docs) > 1:
    doc_id2 = docs[1].get("id")
    print(f"\n[4] Reject document {doc_id2}...")
    r = requests.post(
        f"{BASE_URL}/admin/documents/{doc_id2}/reject?token={token}&reason=test",
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {r.status_code}")
    if r.status_code != 200:
        print(f"   Response: {r.text[:300]}")
    else:
        print(f"   SUCCESS: {r.json()}")

print("\n=== Test Complete ===\n")
