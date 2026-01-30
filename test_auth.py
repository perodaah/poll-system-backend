import requests
import json

BASE_URL = "http://localhost:8000/api"

# Test 1: Register a new user
print("=" * 50)
print("TEST 1: User Registration")
print("=" * 50)

register_data = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!",
    "password2": "TestPass123!"
}

response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# Test 2: Login (get tokens)
print("=" * 50)
print("TEST 2: User Login")
print("=" * 50)

login_data = {
    "username": "testuser",
    "password": "TestPass123!"
}

response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
print(f"Status: {response.status_code}")
tokens = response.json()
print(f"Response: {json.dumps(tokens, indent=2)}\n")

# Save tokens
access_token = tokens.get('access')
refresh_token = tokens.get('refresh')

# Test 3: Access protected endpoint (profile)
print("=" * 50)
print("TEST 3: Get User Profile (Protected)")
print("=" * 50)

headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(f"{BASE_URL}/auth/profile/", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# Test 4: Refresh token
print("=" * 50)
print("TEST 4: Refresh Access Token")
print("=" * 50)

refresh_data = {
    "refresh": refresh_token
}

response = requests.post(f"{BASE_URL}/auth/refresh/", json=refresh_data)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

print("✅ All authentication tests completed!")