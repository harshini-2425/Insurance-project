#!/usr/bin/env python3
"""System verification script - tests all components"""
import sys
import json
sys.path.insert(0, 'backend')

from backend.database import SessionLocal
from backend.models import Policy, Provider

def test_database():
    """Test database and policies"""
    print("\n" + "="*60)
    print("TEST 1: DATABASE & POLICIES")
    print("="*60)
    
    db = SessionLocal()
    
    # Count policies
    total_policies = db.query(Policy).count()
    print(f"✅ Total Policies in DB: {total_policies}")
    
    if total_policies != 50:
        print(f"❌ ERROR: Expected 50 policies, got {total_policies}")
        return False
    
    # Get policy breakdown
    from sqlalchemy import func
    breakdown = db.query(
        Policy.policy_type, 
        func.count(Policy.id)
    ).group_by(Policy.policy_type).all()
    
    print("\n📊 Policy Type Breakdown:")
    total_check = 0
    for ptype, count in breakdown:
        print(f"   • {ptype}: {count}")
        total_check += count
    
    if total_check != 50:
        print(f"❌ ERROR: Breakdown total {total_check} != 50")
        return False
    
    # Get providers
    total_providers = db.query(Provider).count()
    print(f"\n✅ Total Providers: {total_providers}")
    
    # Sample policies
    print("\n📋 Sample Policies:")
    samples = db.query(Policy).limit(5).all()
    for policy in samples:
        print(f"   • {policy.title} ({policy.policy_type}) - ₹{policy.premium}")
    
    db.close()
    return True

def test_files():
    """Test seed data file"""
    print("\n" + "="*60)
    print("TEST 2: SEED DATA FILE")
    print("="*60)
    
    try:
        with open('backend/policies_seed_data.json', 'r') as f:
            data = json.load(f)
        
        policies_count = len(data.get('policies', []))
        providers_count = len(data.get('providers', []))
        
        print(f"✅ policies_seed_data.json found")
        print(f"   • Policies in JSON: {policies_count}")
        print(f"   • Providers in JSON: {providers_count}")
        
        if policies_count != 50:
            print(f"❌ ERROR: Expected 50 policies in JSON, got {policies_count}")
            return False
            
        if providers_count != 30:
            print(f"❌ ERROR: Expected 30 providers in JSON, got {providers_count}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ ERROR reading seed data: {e}")
        return False

def test_scripts():
    """Test seed script"""
    print("\n" + "="*60)
    print("TEST 3: SEED SCRIPT")
    print("="*60)
    
    try:
        with open('backend/seed_policies.py', 'r') as f:
            content = f.read()
        
        print(f"✅ seed_policies.py found")
        
        # Check for key functions
        if 'def seed_database():' in content:
            print(f"   • seed_database() function exists")
        else:
            print(f"❌ ERROR: seed_database() function not found")
            return False
        
        if 'def load_seed_data(' in content:
            print(f"   • load_seed_data() function exists")
        else:
            print(f"❌ ERROR: load_seed_data() function not found")
            return False
        
        return True
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_endpoints():
    """Test API endpoints"""
    print("\n" + "="*60)
    print("TEST 4: API ENDPOINTS")
    print("="*60)
    
    try:
        import requests
        
        # Test /policies endpoint
        try:
            response = requests.get('http://localhost:8000/policies', timeout=5)
            if response.status_code == 200:
                data = response.json()
                policy_count = len(data.get('policies', []))
                total_count = data.get('total', 0)
                print(f"✅ GET /policies works")
                print(f"   • Total policies: {total_count}")
                print(f"   • Returned in this request: {policy_count}")
                if total_count == 50:
                    print(f"   ✅ All 50 policies accessible via API")
                    return True
                else:
                    print(f"❌ ERROR: API returned {total_count} policies instead of 50")
                    return False
            else:
                print(f"❌ ERROR: /policies returned {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"❌ ERROR: Cannot connect to http://localhost:8000")
            print(f"   Make sure backend server is running: python -m uvicorn backend.main:app --port 8000")
            return False
    except ImportError:
        print(f"⚠️  requests library not available, skipping API test")
        return True

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("SYSTEM VERIFICATION TEST")
    print("="*60)
    
    tests = [
        ("Database & Policies", test_database),
        ("Seed Data File", test_files),
        ("Seed Script", test_scripts),
        ("API Endpoints", test_endpoints),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ EXCEPTION in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_pass = all(result for _, result in results)
    
    print("\n" + "="*60)
    if all_pass:
        print("✅ ALL TESTS PASSED - SYSTEM READY")
    else:
        print("❌ SOME TESTS FAILED - SEE DETAILS ABOVE")
    print("="*60 + "\n")
    
    return all_pass

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
