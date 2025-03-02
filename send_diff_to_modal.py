import requests
import json

# API endpoint
api_url = "https://jlawman--pr-validator-api-validate.modal.run"

# Read test files
with open("test_diff.txt", "r") as f:
    test_diff = f.read()

with open("test_instructions.txt", "r") as f:
    test_instructions = f.read()

# Prepare payload
payload = {
    "diff": test_diff,
    "instructions": test_instructions
}

# Send request
response = requests.post(api_url, json=payload)

# Print result
print(f"Status code: {response.status_code}")
print(json.dumps(response.json(), indent=2))