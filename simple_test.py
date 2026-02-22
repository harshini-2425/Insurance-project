#!/usr/bin/env python3
import requests

BASE_URL = "http://localhost:8000"

# Login
r = requests.post(f"{BASE_URL}/auth/login", json={"email": "elchuritejaharshini@gmail.com", "password": "958181630"})
token = r.json().get("access_token")
print(f"[1] Admin login: {r.status_code}")

# Get documents
r = requests.get(f"{BASE_URL}/admin/claim-documents-list?token={token}")
docs = r.json().get("data", {}).get("documents", [])
print(f"[2] Documents found: {len(docs)}")

if docs:
    doc_id = docs[0].get("id")
    user_id = docs[0].get("user_id") if "user_id" in docs[0] else None
    print(f"[3] Testing with document ID: {doc_id}, User ID: {user_id}")
    
    # Test approve
    r = requests.post(f"{BASE_URL}/admin/documents/{doc_id}/approve?token={token}&comments=test%20approval")
    print(f"[4] Approve response: {r.status_code}")
    if r.status_code != 200:
        print(f"    Error: {r.text[:200]}")
    else:
        print(f"    Result: {r.json()}")
else:
    print("[3] No documents to test")
