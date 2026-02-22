import requests

# Register the test user
response = requests.post(
    'http://localhost:8000/auth/register',
    json={
        'name': 'Test User',
        'email': 'testuser@example.com',
        'password': 'password123',
        'dob': '1990-01-01'
    }
)

print(f'Register status: {response.status_code}')
if response.status_code != 200:
    print(f'Response: {response.text[:300]}')
else:
    print('Test user registered')

# Now try to login
response = requests.post(
    'http://localhost:8000/auth/login',
    json={
        'email': 'testuser@example.com',
        'password': 'password123'
    }
)
print(f'Login status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Login successful - User ID: {data.get("user_id")}')
else:
    print(f'Login failed: {response.text[:300]}')
