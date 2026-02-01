#generated test file

import requests
import json

BASE_URL = "http://localhost:8000/api"

# ============================================
# SETUP: Register and Login to get token
# ============================================
print("=" * 60)
print("SETUP: Creating test user and getting token")
print("=" * 60)

# Register a test user
register_data = {
    "username": "polluser",
    "email": "polluser@example.com",
    "password": "PollTest123!",
    "password2": "PollTest123!"
}

response = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
if response.status_code == 201:
    print("✅ User registered successfully")
elif response.status_code == 400 and 'username' in response.json():
    print("⚠️  User already exists, proceeding with login...")
else:
    print(f"❌ Registration failed: {response.json()}")

# Login to get tokens
login_data = {
    "username": "polluser",
    "password": "PollTest123!"
}

response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
if response.status_code == 200:
    tokens = response.json()
    access_token = tokens['access']
    print(f"✅ Login successful\n")
else:
    print(f"❌ Login failed: {response.json()}")
    exit()

# Setup headers with token
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# ============================================
# TEST 1: Create a Poll
# ============================================
print("=" * 60)
print("TEST 1: Create a Poll")
print("=" * 60)

poll_data = {
    "title": "What's your favorite Python web framework?",
    "description": "Help us understand developer preferences",
    "options": [
        {"text": "Django", "order_index": 1},
        {"text": "Flask", "order_index": 2},
        {"text": "FastAPI", "order_index": 3}
    ]
}

response = requests.post(f"{BASE_URL}/polls/", json=poll_data, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

if response.status_code == 201:
    poll_id = response.json()['id']
    print(f"✅ Poll created with ID: {poll_id}\n")
else:
    print("❌ Poll creation failed\n")
    exit()

# ============================================
# TEST 2: List All Polls
# ============================================
print("=" * 60)
print("TEST 2: List All Polls")
print("=" * 60)

response = requests.get(f"{BASE_URL}/polls/")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# ============================================
# TEST 3: Get Poll Details
# ============================================
print("=" * 60)
print("TEST 3: Get Poll Details")
print("=" * 60)

response = requests.get(f"{BASE_URL}/polls/{poll_id}/")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# ============================================
# TEST 4: Update Poll (Owner)
# ============================================
print("=" * 60)
print("TEST 4: Update Poll (Owner)")
print("=" * 60)

update_data = {
    "title": "What's your favorite Python web framework? (Updated)",
    "description": "Updated description"
}

response = requests.patch(f"{BASE_URL}/polls/{poll_id}/", json=update_data, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# ============================================
# TEST 5: Try to Update Without Authentication
# ============================================
print("=" * 60)
print("TEST 5: Try to Update Without Authentication (Should Fail)")
print("=" * 60)

response = requests.patch(f"{BASE_URL}/polls/{poll_id}/", json=update_data)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# ============================================
# TEST 6: Create Poll Without Authentication
# ============================================
print("=" * 60)
print("TEST 6: Create Poll Without Authentication (Should Fail)")
print("=" * 60)

poll_data2 = {
    "title": "Another poll",
    "options": [
        {"text": "Option 1", "order_index": 1},
        {"text": "Option 2", "order_index": 2}
    ]
}

response = requests.post(f"{BASE_URL}/polls/", json=poll_data2)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# ============================================
# TEST 7: Create Poll with Less Than 2 Options (Validation)
# ============================================
print("=" * 60)
print("TEST 7: Create Poll with Only 1 Option (Should Fail)")
print("=" * 60)

invalid_poll = {
    "title": "Invalid poll",
    "options": [
        {"text": "Only option", "order_index": 1}
    ]
}

response = requests.post(f"{BASE_URL}/polls/", json=invalid_poll, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# ============================================
# TEST 8: Create Poll with Expiry Date
# ============================================
print("=" * 60)
print("TEST 8: Create Poll with Future Expiry Date")
print("=" * 60)

poll_with_expiry = {
    "title": "Time-limited poll",
    "description": "This poll expires soon",
    "expires_at": "2026-12-31T23:59:59Z",
    "options": [
        {"text": "Yes", "order_index": 1},
        {"text": "No", "order_index": 2}
    ]
}

response = requests.post(f"{BASE_URL}/polls/", json=poll_with_expiry, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# ============================================
# TEST 9: Delete Poll (Owner)
# ============================================
print("=" * 60)
print("TEST 9: Delete Poll (Owner)")
print("=" * 60)

response = requests.delete(f"{BASE_URL}/polls/{poll_id}/", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 204:
    print("✅ Poll deleted successfully\n")
else:
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# ============================================
# TEST 10: Verify Poll is Deleted
# ============================================
print("=" * 60)
print("TEST 10: Try to Get Deleted Poll (Should Fail)")
print("=" * 60)

response = requests.get(f"{BASE_URL}/polls/{poll_id}/")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

print("=" * 60)
print("✅ All Poll API tests completed!")
print("=" * 60)