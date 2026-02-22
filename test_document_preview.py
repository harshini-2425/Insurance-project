#!/usr/bin/env python3
"""
Test script for Document Preview functionality
Tests backend endpoint and document retrieval

Usage:
    cd c:\newproject
    .venv\Scripts\python test_document_preview.py
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "elchuritejaharshini@gmail.com"
ADMIN_PASSWORD = "958181630"

class DocumentPreviewTester:
    def __init__(self):
        self.token = None
        self.admin_id = None
        
    def test_login(self):
        """Test 1: Admin login to get token"""
        print("\n" + "="*60)
        print("TEST 1: Admin Login")
        print("="*60)
        
        try:
            response = requests.post(
                f"{BASE_URL}/login",
                json={
                    "email": ADMIN_EMAIL,
                    "password": ADMIN_PASSWORD
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.admin_id = data.get("user_id")
                print(f"✅ Login successful")
                print(f"   Token: {self.token[:50]}...")
                print(f"   Admin ID: {self.admin_id}")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_list_documents(self):
        """Test 2: List available documents"""
        print("\n" + "="*60)
        print("TEST 2: List Documents")
        print("="*60)
        
        if not self.token:
            print("⚠️  Skipping - no token available")
            return False
        
        try:
            response = requests.get(
                f"{BASE_URL}/admin/claim-documents-list",
                params={
                    "token": self.token,
                    "skip": 0,
                    "limit": 10
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    docs = data.get("data", {}).get("documents", [])
                    total = data.get("data", {}).get("total_count", 0)
                    print(f"✅ Retrieved {len(docs)} documents (Total: {total})")
                    
                    if docs:
                        for doc in docs[:3]:  # Show first 3
                            print(f"\n   ID: {doc.get('id')}")
                            print(f"   Name: {doc.get('file_name')}")
                            print(f"   Type: {doc.get('file_type')}")
                            print(f"   Doc Type: {doc.get('doc_type')}")
                        
                        # Store first doc for preview test
                        self.test_doc_id = docs[0].get('id')
                        return True
                else:
                    print(f"❌ Failed: {data.get('message')}")
                    return False
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_view_document(self):
        """Test 3: View document using new endpoint"""
        print("\n" + "="*60)
        print("TEST 3: View Document (New Endpoint)")
        print("="*60)
        
        if not self.token or not hasattr(self, 'test_doc_id'):
            print("⚠️  Skipping - no token or document available")
            return False
        
        doc_id = self.test_doc_id
        print(f"Testing with document ID: {doc_id}")
        
        try:
            # Test the new view endpoint
            response = requests.get(
                f"{BASE_URL}/admin/documents/{doc_id}/view",
                params={"token": self.token}
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Content-Disposition: {response.headers.get('content-disposition')}")
            print(f"Content Length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                if len(response.content) > 0:
                    print(f"✅ Document retrieved successfully")
                    print(f"   File size: {len(response.content)} bytes")
                    
                    # Check headers
                    if 'inline' in response.headers.get('content-disposition', ''):
                        print(f"✅ Content-Disposition: inline (correct for viewing)")
                    else:
                        print(f"⚠️  Content-Disposition: {response.headers.get('content-disposition')}")
                    
                    # Check MIME type
                    content_type = response.headers.get('content-type', '')
                    if content_type:
                        print(f"✅ MIME Type: {content_type}")
                    else:
                        print(f"⚠️  No MIME type detected")
                    
                    return True
                else:
                    print(f"❌ Empty file content")
                    return False
            else:
                print(f"❌ Request failed: {response.status_code}")
                try:
                    error = response.json()
                    print(f"   Error: {error.get('detail')}")
                except:
                    print(f"   Response: {response.text[:200]}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_download_document(self):
        """Test 4: Compare with download endpoint (existing)"""
        print("\n" + "="*60)
        print("TEST 4: Download Document (Existing Endpoint)")
        print("="*60)
        
        if not self.token or not hasattr(self, 'test_doc_id'):
            print("⚠️  Skipping - no token or document available")
            return False
        
        doc_id = self.test_doc_id
        
        try:
            response = requests.get(
                f"{BASE_URL}/admin/claim-documents/{doc_id}",
                params={"token": self.token}
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Content-Disposition: {response.headers.get('content-disposition')}")
            print(f"Content Length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                if 'attachment' in response.headers.get('content-disposition', ''):
                    print(f"✅ Content-Disposition: attachment (correct for downloading)")
                else:
                    print(f"⚠️  Content-Disposition: {response.headers.get('content-disposition')}")
                
                print(f"✅ Comparison complete")
                return True
            else:
                print(f"❌ Request failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def test_auth_required(self):
        """Test 5: Verify auth is required"""
        print("\n" + "="*60)
        print("TEST 5: Authentication Required")
        print("="*60)
        
        if not hasattr(self, 'test_doc_id'):
            print("⚠️  Skipping - no document available")
            return False
        
        doc_id = self.test_doc_id
        
        try:
            # Try without token
            response = requests.get(
                f"{BASE_URL}/admin/documents/{doc_id}/view",
                params={}
            )
            
            if response.status_code != 200:
                print(f"✅ Request rejected without token (HTTP {response.status_code})")
                return True
            else:
                print(f"❌ Request succeeded without token (security issue!)")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n")
        print("╔" + "="*58 + "╗")
        print("║" + " "*58 + "║")
        print("║" + "   DOCUMENT PREVIEW FUNCTIONALITY TESTS".center(58) + "║")
        print("║" + " "*58 + "║")
        print("╚" + "="*58 + "╝")
        
        results = {
            "Login": self.test_login(),
            "List Documents": self.test_list_documents(),
            "View Document": self.test_view_document(),
            "Download Document": self.test_download_document(),
            "Authentication": self.test_auth_required(),
        }
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status:10} {test_name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed! Document preview is ready.")
            return True
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")
            return False


def main():
    """Main test runner"""
    tester = DocumentPreviewTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
