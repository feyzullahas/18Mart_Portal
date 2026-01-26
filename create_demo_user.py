import requests
import json

BASE_URL = 'http://localhost:8000'

# Create a new user with known credentials
new_user = {
    'email': 'demo@18mart.com',
    'password': 'demo123'
}

print('Creating new demo user...')
response = requests.post(f'{BASE_URL}/auth/register', json=new_user)
print(f'Register Status: {response.status_code}')
print(f'Register Response: {response.text}')

if response.status_code == 201:
    print('✅ User registered successfully!')
    
    # Now login
    print('\nTesting login...')
    login_response = requests.post(f'{BASE_URL}/auth/login', json=new_user)
    print(f'Login Status: {login_response.status_code}')
    
    if login_response.status_code == 200:
        token_data = login_response.json()
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
        print(f'❌ Login failed: {login_response.text}')
else:
    print(f'❌ Registration failed: {response.text}')
