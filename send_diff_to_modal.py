import requests
import json

# API endpoint
api_url = "https://jlawman--pr-validator-api-validate.modal.run"

# Read test files
with open("test_diff.txt", "r") as f:
    test_diff = f.read()

with open("test_instructions.txt", "r") as f:
    test_instructions = f.read()

payload = {
    "diff": test_diff,
    "instructions": test_instructions
}

print("Sending diff and instructions to Modal as query parameters")
response1 = requests.post(api_url, params=payload)
print(f"Status code: {response1.status_code}")
try:
    print(json.dumps(response1.json(), indent=2))
except json.JSONDecodeError:
    print("Response isn't valid JSON. Raw response:")
    print(response1.text)

# Print the content length for debugging
print(f"\nDiff length: {len(test_diff)} characters")
print(f"Instructions length: {len(test_instructions)} characters")