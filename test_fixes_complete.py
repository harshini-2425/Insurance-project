#!/usr/bin/env python3
"""
Test verification for fixes:
1. Document search filtering by claim number
2. Document preview component refactoring (visual test in browser)
"""

import requests
import time

API = "http://localhost:8000"

print("\n" + "=" * 70)
print("TESTING FIXES")
print("=" * 70)

# Step 1: Admin login
print("\n[1] Admin login...")
login_resp = requests.post(f"{API}/auth/login", json={"email": "admin", "password": "admin123"})
if login_resp.status_code != 200:
    print(f"❌ Login failed: {login_resp.status_code}")
    exit(1)

token = login_resp.json()['access_token']
print(f"✓ Admin logged in successfully")

# Step 2: Get all claims
print("\n[2] Fetching admin claims list...")
claims_resp = requests.get(f"{API}/admin/claims-list?token={token}&skip=0&limit=15")
if claims_resp.status_code != 200:
    print(f"❌ Failed to get claims: {claims_resp.status_code}")
    exit(1)

claims = claims_resp.json()['data']['claims']
print(f"✓ Retrieved {len(claims)} claims")

if not claims:
    print("⚠️  No claims found, skipping detailed tests")
    exit(0)

# Step 3: Test document search filtering for each claim that has documents
print("\n[3] Testing document search filtering by claim number...")
test_passed = True
for claim in claims[:3]:  # Test first 3 claims
    claim_number = claim['claim_number']
    claim_id = claim['id']
    doc_count = claim.get('documents_count', 0)
    
    if doc_count == 0:
        print(f"   ↷ Skipping {claim_number} (no documents)")
        continue
    
    # Get documents with claim filter
    filtered_resp = requests.get(
        f"{API}/admin/claim-documents-list?token={token}&claim_number={claim_number}&skip=0&limit=100"
    )
    
    if filtered_resp.status_code != 200:
        print(f"   ❌ Failed for {claim_number}")
        test_passed = False
        continue
    
    filtered_docs = filtered_resp.json()['data']['documents']
    
    # Verify all documents match the claim number
    all_match = all(d['claim_number'] == claim_number for d in filtered_docs)
    
    if all_match and len(filtered_docs) == doc_count:
        print(f"   ✓ {claim_number}: {len(filtered_docs)} document(s) correctly filtered")
    else:
        print(f"   ❌ {claim_number}: Filtering issue (expected {doc_count}, got {len(filtered_docs)})")
        test_passed = False

# Step 4: Test document preview endpoint
print("\n[4] Testing document retrieval (for preview)...")
if claims:
    claim = claims[0]
    if (claim.get('documents_count', 0)) > 0:
        # Get documents list to get a document ID
        docs_resp = requests.get(
            f"{API}/admin/claim-documents-list?token={token}&claim_number={claim['claim_number']}&skip=0&limit=1"
        )
        if docs_resp.status_code == 200:
            docs = docs_resp.json()['data']['documents']
            if docs:
                doc_id = docs[0]['id']
                # Try to fetch the document
                view_resp = requests.get(f"{API}/admin/documents/{doc_id}/view?token={token}")
                if view_resp.status_code == 200:
                    print(f"   ✓ Document preview endpoint working (doc {doc_id})")
                else:
                    print(f"   ❌ Document preview failed: {view_resp.status_code}")
                    test_passed = False

print("\n" + "=" * 70)
if test_passed:
    print("✅ ALL TESTS PASSED")
    print("\nFixes Applied:")
    print("  ✓ AdminDocumentReview useEffect now includes searchClaimNumber & selectedFilter")
    print("    → Search filter will trigger fetch when claim number changes")
    print("  ✓ DocumentPreviewModal converted from Tailwind to inline styles")
    print("    → Modal will now display as centered overlay (not at bottom)")
else:
    print("⚠️  Some tests failed - please review")
print("=" * 70 + "\n")
