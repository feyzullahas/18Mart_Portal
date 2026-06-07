import requests
import json

BASE = "http://localhost:8000"

# 1. Login
login_resp = requests.post(f"{BASE}/auth/login", json={
    "email": "test@test.com",
    "password": "test123"
})
print("Login status:", login_resp.status_code)
if login_resp.status_code != 200:
    print("Login failed:", login_resp.text)
    # Try to create user first
    reg = requests.post(f"{BASE}/auth/register", json={
        "email": "test@test.com",
        "password": "test123",
        "full_name": "Test User"
    })
    print("Register:", reg.status_code, reg.text[:200])
    login_resp = requests.post(f"{BASE}/auth/login", json={
        "email": "test@test.com",
        "password": "test123"
    })
    print("Login retry:", login_resp.status_code)

token = login_resp.json().get("access_token", "")
print("Token:", token[:30] + "..." if token else "NO TOKEN")

# 2. GET ratings
get_resp = requests.get(
    f"{BASE}/meal-ratings/kyk_kahvalti/2026-06-07",
    headers={"Authorization": f"Bearer {token}"}
)
print("\nGET status:", get_resp.status_code)
print("GET body:", get_resp.text)

# 3. POST rating
post_resp = requests.post(
    f"{BASE}/meal-ratings/",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    json={"cafeteria": "kyk_kahvalti", "date": "2026-06-07", "rating": 4}
)
print("\nPOST status:", post_resp.status_code)
print("POST body:", post_resp.text)
