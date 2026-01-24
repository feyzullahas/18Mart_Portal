import requests
import json

# Test registration endpoint
url = "http://localhost:8000/auth/register"
data = {
    "email": "test@example.com",
    "password": "test123456"
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        print("✅ Registration successful!")
    else:
        print("❌ Registration failed")
        
except Exception as e:
    print(f"Error: {e}")
    print("Make sure the backend server is running on localhost:8000")
