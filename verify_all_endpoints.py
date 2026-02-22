#!/usr/bin/env python
"""
Quick verification script to test all endpoints and document upload functionality.
Run this to verify:
1. Backend is running
2. Database is connected
3. Can fetch claims
4. Can upload documents
5. Can view claim details with documents
"""

import sys
import json
import requests
from pathlib import Path

BASE_URL = "http://localhost:8000"

# Test token (replace with valid token if needed)
TEST_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMywiZXhwIjoxNzcyMTg5ODk2fQ.XFZALJqRpjTk56XfsYG2RnoYxnCHq50fPvtzMu96nj8"

def test_health():
    """Test if backend is running"""
    print("\n" + "="*70)
    print("TEST 1: Backend Health Check")
    print("="*70)
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code == 200:
            print("✅ PASS: Backend is running")
            print(f"   Response: {r.json()}")
            return True
        else:
            print(f"❌ FAIL: Backend returned {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Cannot connect to backend: {e}")
        return False

def test_database():
    """Test database connection"""
    print("\n" + "="*70)
    print("TEST 2: Database Connection & Schema")
    print("="*70)
    try:
        r = requests.post(f"{BASE_URL}/debug/verify-database", timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == "READY":
                print("✅ PASS: Database is ready")
                print(f"   Connection: {data.get('connection')}")
                print(f"   Table exists: {data.get('table_exists')}")
                print(f"   Schema correct: {data.get('schema_correct')}")
                return True
            else:
                print(f"❌ FAIL: Database not ready: {data}")
                return False
        else:
            print(f"❌ FAIL: Database check returned {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Cannot check database: {e}")
        return False

def test_claims_list():
    """Test fetching claims list"""
    print("\n" + "="*70)
    print("TEST 3: Fetch Claims List")
    print("="*70)
    try:
        r = requests.get(f"{BASE_URL}/claims?token={TEST_TOKEN}", timeout=5)
        if r.status_code == 200:
            data = r.json()
            num_claims = len(data.get("claims", []))
            print(f"✅ PASS: Fetched {num_claims} claims")
            if num_claims > 0:
                print(f"   First claim: {data['claims'][0]['id']} - {data['claims'][0].get('claim_number', 'N/A')}")
                return num_claims, data['claims'][0]['id']
            return num_claims, None
        else:
            print(f"❌ FAIL: Claims list returned {r.status_code}")
            return 0, None
    except Exception as e:
        print(f"❌ FAIL: Cannot fetch claims: {e}")
        return 0, None

def test_claim_detail(claim_id):
    """Test fetching claim details - THIS WAS THE BROKEN ENDPOINT"""
    print("\n" + "="*70)
    print(f"TEST 4: Fetch Claim Details (Claim #{claim_id}) - PREVIOUSLY BROKEN")
    print("="*70)
    try:
        r = requests.get(f"{BASE_URL}/claims/{claim_id}?token={TEST_TOKEN}", timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"✅ PASS: Claim details loaded (status code: 200)")
            print(f"   Claim number: {data.get('claim_number')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Documents count: {data.get('documents_count', 0)}")
            print(f"   Has policy info: {bool(data.get('policy'))}")
            return True, data.get('documents_count', 0)
        elif r.status_code == 500:
            print(f"❌ FAIL: Got 500 error (ENDPOINT IS STILL BROKEN)")
            print(f"   Response: {r.text[:200]}")
            return False, 0
        else:
            print(f"❌ FAIL: Got {r.status_code} error")
            print(f"   Response: {r.text[:200]}")
            return False, 0
    except Exception as e:
        print(f"❌ FAIL: Cannot fetch claim details: {e}")
        return False, 0

def test_document_upload(claim_id):
    """Test uploading a document"""
    print("\n" + "="*70)
    print(f"TEST 5: Upload Document to Claim #{claim_id}")
    print("="*70)
    try:
        # Create test PDF file with proper MIME type
        test_file = Path("test_document.pdf")
        # Write minimal PDF content
        test_file.write_bytes(b"%PDF-1.4\n%test\n")
        
        files = {'file': ('test_document.pdf', open(test_file, 'rb'), 'application/pdf')}
        params = {'token': TEST_TOKEN, 'doc_type': 'test_document'}
        
        r = requests.post(
            f"{BASE_URL}/claims/{claim_id}/documents",
            files=files,
            params=params,
            timeout=5
        )
        
        files['file'][1].close()
        test_file.unlink()  # Delete test file
        
        if r.status_code == 200:
            data = r.json()
            print(f"✅ PASS: Document uploaded successfully")
            print(f"   Document ID: {data.get('id')}")
            print(f"   File size: {data.get('file_size_bytes')} bytes")
            print(f"   Status: {data.get('message')}")
            return True, data.get('id')
        else:
            print(f"❌ FAIL: Upload returned {r.status_code}")
            print(f"   Response: {r.text[:200]}")
            return False, None
    except Exception as e:
        print(f"❌ FAIL: Cannot upload document: {e}")
        return False, None

def test_document_in_claim(claim_id):
    """Test that uploaded document appears in claim details"""
    print("\n" + "="*70)
    print(f"TEST 6: Verify Document Appears in Claim Details")
    print("="*70)
    try:
        r = requests.get(f"{BASE_URL}/claims/{claim_id}?token={TEST_TOKEN}", timeout=5)
        if r.status_code == 200:
            data = r.json()
            doc_count = data.get('documents_count', 0)
            docs = data.get('documents', [])
            if doc_count > 0:
                print(f"✅ PASS: Found {doc_count} document(s) in claim")
                for doc in docs:
                    print(f"   - {doc.get('file_name')} ({doc.get('file_type')})")
                return True
            else:
                print(f"⚠️  WARNING: No documents found in claim")
                return False
        else:
            print(f"❌ FAIL: Could not fetch claim: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: Cannot verify document: {e}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*10 + "COMPREHENSIVE ENDPOINT VERIFICATION TEST" + " "*18 + "║")
    print("╚" + "="*68 + "╝")
    
    results = {}
    
    # Test 1: Health
    results['health'] = test_health()
    if not results['health']:
        print("\n❌ CRITICAL: Backend is not running. Start it with:")
        print("   cd c:\\newproject")
        print("   .venv\\Scripts\\python -m uvicorn backend.main:app --reload")
        return
    
    # Test 2: Database
    results['database'] = test_database()
    if not results['database']:
        print("\n❌ CRITICAL: Database connection failed.")
        return
    
    # Test 3: Claims list
    num_claims, first_claim_id = test_claims_list()
    results['claims_list'] = num_claims > 0
    
    if not first_claim_id:
        print("\n⚠️  No claims found. Creating test data or using existing claims...")
        first_claim_id = 1
    
    # Test 4: Claim detail (THE PREVIOUSLY BROKEN ENDPOINT)
    claim_loaded, doc_count_before = test_claim_detail(first_claim_id)
    results['claim_detail'] = claim_loaded
    
    # Test 5: Document upload
    upload_success, doc_id = test_document_upload(first_claim_id)
    results['upload'] = upload_success
    
    # Test 6: Document in claim
    if upload_success:
        results['document_in_claim'] = test_document_in_claim(first_claim_id)
    else:
        results['document_in_claim'] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    print()
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Backend and database are working correctly.")
        print("\nYou can now:")
        print("1. Open http://localhost:5175 in your browser")
        print("2. Login to your account")
        print("3. Go to Claims page and test uploading documents")
        print("4. Click on claims to view details (no more 500 errors!)")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        if not results['claim_detail']:
            print("\n>>> ENDPOINT FIX STATUS: GET /claims/{id} endpoint is still returning errors")
            print("    Check backend console for error details")
            print("    Restart backend: .venv\\Scripts\\python -m uvicorn backend.main:app --reload")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
