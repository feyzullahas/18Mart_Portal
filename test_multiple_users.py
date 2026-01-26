import requests
import json

BASE_URL = 'http://localhost:8000'

# Try different users
users = [
    {'email': 'test@example.com', 'password': 'test123'},
    {'email': 'frontend_test@example.com', 'password': 'test123'},
    {'email': 'asfeyzullah@gmail.com', 'password': 'test123'},
]

for i, user_data in enumerate(users):
    print(f"\n--- Testing user {i+1}: {user_data['email']} ---")
    
    response = requests.post(f'{BASE_URL}/auth/login', json=user_data)
    print(f'Login Status: {response.status_code}')
    
    if response.status_code == 200:
        token_data = response.json()
        print('✅ Login successful!')
        print(f'Token: {token_data["access_token"][:50]}...')
        
        # Test courses endpoint
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        courses_response = requests.get(f'{BASE_URL}/courses/', headers=headers)
        print(f'Courses Status: {courses_response.status_code}')
        
        if courses_response.status_code == 200:
            print('✅ Courses endpoint working!')
            courses = courses_response.json()
            print(f'Found {len(courses)} courses')
        else:
            print(f'❌ Courses endpoint failed: {courses_response.text}')
        break
    else:
        print(f'❌ Login failed: {response.text}')
