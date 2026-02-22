#!/usr/bin/env python3
"""Test document search filtering by claim number"""

import requests

API = "http://localhost:8000"

# Admin login
login = requests.post(f"{API}/auth/login", json={"email": "admin", "password": "admin123"})
token = login.json()['access_token']

print("=" * 70)
print("TESTING DOCUMENT SEARCH FILTERING BY CLAIM NUMBER")
print("=" * 70)

# Get all documents (no filter)
print("\n[1] Fetching ALL documents (no claim filter)...")
all_resp = requests.get(f"{API}/admin/claim-documents-list?token={token}&skip=0&limit=100")
all_data = all_resp.json()
all_docs = all_data['data']['documents']
print(f"✓ Total documents without filter: {len(all_docs)}")
if all_docs:
    print(f"  Sample claim numbers: {[d['claim_number'] for d in all_docs[:3]]}")

# Get unique claim numbers
claim_numbers = list(set(d['claim_number'] for d in all_docs))
print(f"\n[2] Found {len(claim_numbers)} unique claim numbers")

if claim_numbers:
    test_claim = claim_numbers[0]
    print(f"\n[3] Testing filter with claim_number: {test_claim}")
    
    # Fetch with claim filter
    filtered_resp = requests.get(
        f"{API}/admin/claim-documents-list?token={token}&skip=0&limit=100&claim_number={test_claim}"
    )
    filtered_data = filtered_resp.json()
    filtered_docs = filtered_data['data']['documents']
    
    print(f"✓ Documents for {test_claim}: {len(filtered_docs)}")
    
    # Verify all returned documents have the correct claim number
    all_match = all(d['claim_number'] == test_claim for d in filtered_docs)
    if all_match:
        print(f"✅ ALL documents have correct claim_number: {test_claim}")
    else:
        print(f"❌ MISMATCH! Some documents have different claim_number:")
        for d in filtered_docs[:3]:
            print(f"   - {d['claim_number']}")

print("\n" + "=" * 70)
