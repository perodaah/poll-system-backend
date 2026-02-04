import requests
import json

BASE_URL = "http://localhost:8000/api"

# ============================================
# SETUP: Register, Login, and Create a Poll
# ============================================
print("=" * 60)
print("SETUP: Creating test user and poll")
print("=" * 60)

# Register a test user
register_data = {
    "username": "voter1",
    "email": "voter1@example.com",
    "password": "VoteTest123!",
    "password2": "VoteTest123!"
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
    "username": "voter1",
    "password": "VoteTest123!"
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

# Create a poll for voting tests
poll_data = {
    "title": "Best Programming Language?",
    "description": "Vote for your favorite language",
    "options": [
        {"text": "Python", "order_index": 1},
        {"text": "JavaScript", "order_index": 2},
        {"text": "Go", "order_index": 3},
        {"text": "Rust", "order_index": 4}
    ]
}

response = requests.post(f"{BASE_URL}/polls/", json=poll_data, headers=headers)
if response.status_code == 201:
    poll = response.json()
    poll_id = poll['id']
    python_option_id = poll['options'][0]['id']
    javascript_option_id = poll['options'][1]['id']
    go_option_id = poll['options'][2]['id']
    rust_option_id = poll['options'][3]['id']
    print(f"✅ Poll created with ID: {poll_id}")
    print(f"   Python option ID: {python_option_id}")
    print(f"   JavaScript option ID: {javascript_option_id}")
    print(f"   Go option ID: {go_option_id}")
    print(f"   Rust option ID: {rust_option_id}\n")
else:
    print(f"❌ Poll creation failed: {response.json()}")
    exit()

# ============================================
# TEST 1: Vote on Poll (Authenticated User)
# ============================================
print("=" * 60)
print("TEST 1: Cast Vote as Authenticated User")
print("=" * 60)

vote_data = {
    "option_id": python_option_id
}

response = requests.post(f"{BASE_URL}/polls/{poll_id}/vote/", json=vote_data, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# ============================================
# TEST 2: Try to Vote Again (Should Fail)
# ============================================
print("=" * 60)
print("TEST 2: Try to Vote Again (Should Fail - Duplicate)")
print("=" * 60)

response = requests.post(f"{BASE_URL}/polls/{poll_id}/vote/", json=vote_data, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# ============================================
# TEST 3: Get Poll Results
# ============================================
print("=" * 60)
print("TEST 3: Get Poll Results (After 1 Vote)")
print("=" * 60)

response = requests.get(f"{BASE_URL}/polls/{poll_id}/results/")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# ============================================
# TEST 4: Vote as Anonymous User
# ============================================
print("=" * 60)
print("TEST 4: Cast Vote as Anonymous User (No Auth)")
print("=" * 60)

vote_data_anonymous = {
    "option_id": javascript_option_id
}

response = requests.post(f"{BASE_URL}/polls/{poll_id}/vote/", json=vote_data_anonymous)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# ============================================
# TEST 5: Try to Vote as Anonymous Again
# ============================================
print("=" * 60)
print("TEST 5: Try to Vote as Anonymous Again (Should Fail)")
print("=" * 60)

response = requests.post(f"{BASE_URL}/polls/{poll_id}/vote/", json=vote_data_anonymous)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# ============================================
# TEST 6: Get Updated Results
# ============================================
print("=" * 60)
print("TEST 6: Get Updated Poll Results (After 2 Votes)")
print("=" * 60)

response = requests.get(f"{BASE_URL}/polls/{poll_id}/results/")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# ============================================
# TEST 7: Vote with Invalid Option ID
# ============================================
print("=" * 60)
print("TEST 7: Vote with Invalid Option ID (Should Fail)")
print("=" * 60)

# Create another user to test with
register_data2 = {
    "username": "voter2",
    "email": "voter2@example.com",
    "password": "VoteTest123!",
    "password2": "VoteTest123!"
}
requests.post(f"{BASE_URL}/auth/register/", json=register_data2)

login_data2 = {
    "username": "voter2",
    "password": "VoteTest123!"
}
response = requests.post(f"{BASE_URL}/auth/login/", json=login_data2)
access_token2 = response.json().get('access', '')
headers2 = {"Authorization": f"Bearer {access_token2}"}

invalid_vote = {
    "option_id": 99999  # Non-existent option
}

response = requests.post(f"{BASE_URL}/polls/{poll_id}/vote/", json=invalid_vote, headers=headers2)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# ============================================
# TEST 8: Vote on Inactive Poll
# ============================================
print("=" * 60)
print("TEST 8: Try to Vote on Inactive Poll (Should Fail)")
print("=" * 60)

# Deactivate the poll
deactivate_data = {
    "is_active": False
}
requests.patch(f"{BASE_URL}/polls/{poll_id}/", json=deactivate_data, headers=headers)

vote_on_inactive = {
    "option_id": rust_option_id
}

response = requests.post(f"{BASE_URL}/polls/{poll_id}/vote/", json=vote_on_inactive, headers=headers2)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

# ============================================
# TEST 9: Final Results Check
# ============================================
print("=" * 60)
print("TEST 9: Final Poll Results")
print("=" * 60)

response = requests.get(f"{BASE_URL}/polls/{poll_id}/results/")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

print("=" * 60)
print("✅ All Voting System tests completed!")
print("=" * 60)