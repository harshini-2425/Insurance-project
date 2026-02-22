#!/usr/bin/env python3
"""
Comprehensive Test Suite for Claim Approval Workflow
Tests the complete workflow of document approvals affecting claim status
"""

import requests
import json
from datetime import date

BASE_URL = "http://localhost:8000"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_success(msg):
    print(f"  ✅ {msg}")

def print_error(msg):
    print(f"  ❌ {msg}")

def print_info(msg):
    print(f"  ℹ️  {msg}")

def test_create_user():
    """Create a test user"""
    print_section("Step 1: Create Test User")
    
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "name": "Test User",
        "email": f"test_{date.today().isoformat()}@example.com",
        "password": "password123",
        "dob": "1990-01-01"
    })
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"User created: {data.get('email')}")
        return data.get('token')
    else:
        print_error(f"Failed to create user: {response.text}")
        return None

def test_get_policies(token):
    """Get available policies"""
    print_section("Step 2: Fetch Available Policies")
    
    response = requests.get(f"{BASE_URL}/policies?token={token}")
    
    if response.status_code == 200:
        data = response.json()
        policies = data.get('policies', [])
        print_success(f"Found {len(policies)} policies")
        if policies:
            print_info(f"Using policy: {policies[0]['title']} (ID: {policies[0]['id']})")
            return policies[0]['id']
    else:
        print_error(f"Failed to fetch policies: {response.text}")
    
    return None

def test_assign_policy(token, policy_id):
    """Assign policy to user"""
    print_section("Step 3: Assign Policy to User")
    
    response = requests.post(f"{BASE_URL}/user-policies", json={
        "policy_id": policy_id
    }, params={"token": token})
    
    if response.status_code in [200, 201]:
        data = response.json()
        user_policy_id = data.get('user_policy_id') or data.get('id')
        print_success(f"Policy assigned: User Policy ID {user_policy_id}")
        return user_policy_id
    else:
        print_error(f"Failed to assign policy: {response.text}")
    
    return None

def test_create_claim(token, user_policy_id):
    """Create a claim"""
    print_section("Step 4: Create Claim")
    
    response = requests.post(f"{BASE_URL}/claims", json={
        "user_policy_id": user_policy_id,
        "claim_type": "auto_accident",
        "incident_date": str(date.today()),
        "amount_claimed": 5000,
        "description": "Test claim for workflow verification"
    }, params={"token": token})
    
    if response.status_code in [200, 201]:
        data = response.json()
        claim_id = data.get('id') or data.get('claim_id')
        claim_number = data.get('claim_number')
        print_success(f"Claim created: {claim_number} (ID: {claim_id})")
        return claim_id, claim_number
    else:
        print_error(f"Failed to create claim: {response.text}")
    
    return None, None

def test_upload_documents(token, claim_id, num_docs=2):
    """Upload multiple documents to claim"""
    print_section(f"Step 5: Upload {num_docs} Test Documents")
    
    doc_ids = []
    doc_types = ["receipt", "medical_report"]
    
    for i in range(num_docs):
        doc_type = doc_types[i % len(doc_types)]
        
        # Create a simple test file
        files = {
            "file": ("test_doc_{}.txt".format(i+1), b"Test document content", "text/plain")
        }
        
        response = requests.post(
            f"{BASE_URL}/claims/{claim_id}/documents?token={token}",
            files=files,
            data={"doc_type": doc_type}
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            doc_id = data.get('id') or data.get('document_id')
            doc_ids.append((doc_id, doc_type))
            print_success(f"Document {i+1} uploaded: {doc_type} (ID: {doc_id})")
        else:
            print_error(f"Failed to upload document: {response.text}")
    
    return doc_ids

def test_submit_claim_for_review(token, claim_id):
    """Submit claim for review"""
    print_section("Step 6: Submit Claim for Review")
    
    response = requests.post(
        f"{BASE_URL}/claims/{claim_id}/submit?token={token}"
    )
    
    if response.status_code == 200:
        print_success("Claim submitted for review")
        return True
    else:
        print_error(f"Failed to submit claim: {response.text}")
    
    return False

def test_admin_login():
    """Admin login"""
    print_section("Step 7: Admin Login")
    
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@example.com",
        "password": "admin_password"
    })
    
    if response.status_code == 200:
        data = response.json()
        admin_token = data.get('token')
        print_success(f"Admin logged in")
        return admin_token
    else:
        print_error(f"Failed to login as admin: {response.text}")
    
    return None

def test_get_pending_documents(admin_token):
    """Get pending documents for admin review"""
    print_section("Step 8: Fetch Pending Documents")
    
    response = requests.get(f"{BASE_URL}/admin/documents?token={admin_token}")
    
    if response.status_code == 200:
        data = response.json()
        documents = data.get('documents', [])
        print_success(f"Found {len(documents)} pending documents")
        return documents
    else:
        print_error(f"Failed to fetch documents: {response.text}")
    
    return []

def test_approve_document(admin_token, doc_id):
    """Approve a document"""
    
    response = requests.post(
        f"{BASE_URL}/admin/documents/{doc_id}/approve?token={admin_token}",
        params={"comments": "Document looks good"}
    )
    
    if response.status_code == 200:
        print_success(f"Document {doc_id} approved")
        return True
    else:
        print_error(f"Failed to approve document: {response.text}")
    
    return False

def test_reject_document(admin_token, doc_id, reason="Document does not meet requirements"):
    """Reject a document"""
    
    response = requests.post(
        f"{BASE_URL}/admin/documents/{doc_id}/reject?token={admin_token}",
        params={"reason": reason}
    )
    
    if response.status_code == 200:
        print_success(f"Document {doc_id} rejected: {reason}")
        return True
    else:
        print_error(f"Failed to reject document: {response.text}")
    
    return False

def test_get_claim_status(token, claim_id):
    """Get claim status"""
    
    response = requests.get(f"{BASE_URL}/claims/{claim_id}?token={token}")
    
    if response.status_code == 200:
        data = response.json()
        claim = data.get('claim') or data
        return {
            "status": claim.get('status'),
            "rejection_reason": claim.get('rejection_reason')
        }
    return None

def test_workflow_all_approved(user_token, admin_token, claim_id):
    """Test: All documents approved → Claim should be APPROVED"""
    print_section("TEST CASE 1: All Documents Approved → Claim Approved")
    
    # Get pending documents
    documents = test_get_pending_documents(admin_token)
    if not documents:
        print_error("No documents found")
        return False
    
    # Approve all documents
    print_info("Approving all documents...")
    for doc in documents[:2]:  # Approve first 2
        test_approve_document(admin_token, doc['id'])
    
    # Check claim status
    claim_status = test_get_claim_status(user_token, claim_id)
    
    if claim_status and claim_status['status'] == 'approved':
        print_success("✅ Claim status is APPROVED (as expected)")
        return True
    else:
        print_error(f"❌ Claim status is {claim_status.get('status') if claim_status else 'unknown'} (expected APPROVED)")
        return False

def test_workflow_one_rejected(user_token, admin_token, claim_id):
    """Test: Any document rejected → Claim should be REJECTED"""
    print_section("TEST CASE 2: One Document Rejected → Claim Rejected")
    
    # Get pending documents
    documents = test_get_pending_documents(admin_token)
    if not documents:
        print_error("No documents found")
        return False
    
    # Reject the first document with a reason
    print_info("Rejecting first document...")
    test_reject_document(admin_token, documents[0]['id'], 
                        "Missing required signature on document")
    
    # Check claim status
    claim_status = test_get_claim_status(user_token, claim_id)
    
    if claim_status and claim_status['status'] == 'rejected':
        print_success("✅ Claim status is REJECTED (as expected)")
        if claim_status.get('rejection_reason'):
            print_info(f"Rejection reason: {claim_status['rejection_reason']}")
        return True
    else:
        print_error(f"❌ Claim status is {claim_status.get('status') if claim_status else 'unknown'} (expected REJECTED)")
        return False

def main():
    """Run complete workflow test"""
    
    print("\n" + "=" * 60)
    print("   CLAIM APPROVAL WORKFLOW - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    # Test Case 1: All Documents Approved
    print("\n📝 TEST CASE 1: All Documents Approved → Claim Approved")
    
    user_token = test_create_user()
    if not user_token:
        print_error("Cannot proceed without user token")
        return
    
    policy_id = test_get_policies(user_token)
    if not policy_id:
        print_error("Cannot proceed without policy")
        return
    
    user_policy_id = test_assign_policy(user_token, policy_id)
    if not user_policy_id:
        print_error("Cannot proceed without user policy")
        return
    
    claim_id, claim_number = test_create_claim(user_token, user_policy_id)
    if not claim_id:
        print_error("Cannot proceed without claim")
        return
    
    doc_ids = test_upload_documents(user_token, claim_id, 2)
    if not doc_ids:
        print_error("Cannot proceed without documents")
        return
    
    if not test_submit_claim_for_review(user_token, claim_id):
        print_error("Cannot proceed without submitted claim")
        return
    
    admin_token = test_admin_login()
    if not admin_token:
        print_error("Cannot proceed without admin token")
        return
    
    # Run test case
    test_case_1_result = test_workflow_all_approved(user_token, admin_token, claim_id)
    
    # Test Case 2: One Document Rejected
    print("\n📝 TEST CASE 2: One Document Rejected → Claim Rejected")
    
    user_token_2 = test_create_user()
    policy_id = test_get_policies(user_token_2)
    user_policy_id = test_assign_policy(user_token_2, policy_id)
    claim_id_2, _ = test_create_claim(user_token_2, user_policy_id)
    doc_ids_2 = test_upload_documents(user_token_2, claim_id_2, 2)
    test_submit_claim_for_review(user_token_2, claim_id_2)
    
    test_case_2_result = test_workflow_one_rejected(user_token_2, admin_token, claim_id_2)
    
    # Summary
    print_section("TEST SUMMARY")
    
    print("\n📊 Results:")
    print(f"  Test Case 1 (All Approved): {'✅ PASSED' if test_case_1_result else '❌ FAILED'}")
    print(f"  Test Case 2 (One Rejected): {'✅ PASSED' if test_case_2_result else '❌ FAILED'}")
    
    if test_case_1_result and test_case_2_result:
        print("\n🎉 ALL TESTS PASSED! Workflow is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")

if __name__ == "__main__":
    main()
