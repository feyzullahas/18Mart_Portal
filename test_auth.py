#!/usr/bin/env python3
"""
Test script to verify authentication flow
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth():
    print("🔐 Testing Authentication Flow...")
    
    # Test login
    print("\n1. Testing login...")
    login_data = {
        "email": "test@example.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data["access_token"]
            print("✅ Login successful!")
            
            # Test courses endpoint with token
            print("\n2. Testing courses endpoint...")
            headers = {"Authorization": f"Bearer {token}"}
            courses_response = requests.get(f"{BASE_URL}/courses/", headers=headers)
            print(f"Courses Status: {courses_response.status_code}")
            
            if courses_response.status_code == 200:
                print("✅ Courses endpoint working!")
                courses = courses_response.json()
                print(f"Found {len(courses)} courses")
            else:
                print(f"❌ Courses endpoint failed: {courses_response.text}")
                
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_auth()
