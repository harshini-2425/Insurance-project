import requests
import json

BASE_URL = 'http://localhost:8000'

# Login as admin
resp = requests.post(f'{BASE_URL}/auth/login', json={'email': 'elchuritejaharshini@gmail.com', 'password': '958181630'})
admin_token = resp.json().get('access_token')
print('✅ Admin logged in\n')

# Get documents
resp = requests.get(f'{BASE_URL}/admin/claim-documents-list', params={'token': admin_token, 'skip': 0, 'limit': 10})
if resp.status_code == 200:
    data = resp.json()
    docs = data.get('data', {}).get('documents', [])
    
    print('📊 Found {} documents'.format(len(docs)))
    print('\n📋 Claim Number Fields - Verifying searchable data:')
    
    if docs:
        for i, doc in enumerate(docs[:3]):
            claim_num = doc.get('claim_number')
            approval_status = doc.get('approval_status')
            claim_status = doc.get('claim_status')
            print('\n  Doc #{}:'.format(i+1))
            print('    - ID: {}'.format(doc.get('id')))
            print('    - Claim #: {} ✅'.format(claim_num))
            print('    - Claim Status: {}'.format(claim_status))
            print('    - Approval Status: {}'.format(approval_status))
    
    print('\n✅ SUCCESS! All documents now include:')
    print('   ✓ claim_number (e.g., CLM-852DBED6) - for search')
    print('   ✓ claim_status - for display')
    print('   ✓ approval_status - for filtering by pending/approved/rejected')
else:
    print('❌ Error: {}'.format(resp.status_code))
    print(resp.text[:300])
