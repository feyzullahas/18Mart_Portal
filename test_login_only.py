import requests
import json

BASE_URL = 'http://localhost:8000'

# Try login with existing user
login_data = {
    'email': 'testuser@example.com',
    'password': 'test123'
}

print('Testing login with existing user...')
response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
print(f'Login Status: {response.status_code}')
print(f'Login Response: {response.text}')

if response.status_code == 200:
    token_data = response.json()
    print('✅ Login successful!')
    print(f'Token: {token_data["access_token"][:50]}...')
    
    # Test courses endpoint
    print('\nTesting courses endpoint...')
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    courses_response = requests.get(f'{BASE_URL}/courses/', headers=headers)
    print(f'Courses Status: {courses_response.status_code}')
    
    if courses_response.status_code == 200:
        print('✅ Courses endpoint working!')
        courses = courses_response.json()
        print(f'Found {len(courses)} courses')
    else:
        print(f'❌ Courses endpoint failed: {courses_response.text}')
else:
    print(f'❌ Login failed: {response.text}')
