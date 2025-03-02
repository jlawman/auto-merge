#!/usr/bin/env python3
import os
import json
import requests
import re

# Extract XML tags from PR body to get instructions
def extract_instructions(body):
    # Look for tags like <instructions>...</instructions>
    match = re.search(r'<instructions>(.*?)</instructions>', body, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        # Fallback to using the entire PR body if no tags
        return body.strip()

def call_validation(diff, instructions):
    """
    Validates PR diff against instructions using Anthropic API directly
    """
    # Get API key from environment
    anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not anthropic_api_key:
        return {
            "valid": False,
            "comment": "❌ Error: ANTHROPIC_API_KEY not set"
        }
    
    # Prepare the API request to Anthropic
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": anthropic_api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # Construct the prompt for validation
    prompt = f"""
You are validating a pull request. Please review the following changes and determine if they match the provided instructions.

Instructions:
{instructions}

Changes (diff):
{diff}

Please respond with:
1. Whether the changes match the instructions (valid: true/false)
2. A brief comment explaining your decision

<comment>
brief comment explaining your decision
</comment>
<verdict>
true/false
</verdict>
"""
    
    payload = {
        "model": "claude-3-7-sonnet-latest",
        "max_tokens": 1000,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        json=payload,
        headers=headers
    )
    
    if response.status_code != 200:
        return {
            "valid": False,
            "comment": f"❌ Error calling validation service: {response.text}"
        }
    
    # Parse Anthropic response 
    llm_response = response.json()
    response_content = llm_response.get("content", [{}])[0].get("text", "")
    
    # Simple heuristic to determine validity - can be improved
    is_valid = "valid: true" in response_content.lower() or "changes match the instructions" in response_content.lower()
    
    return {
        "valid": is_valid,
        "comment": response_content
    }

if __name__ == "__main__":
    # Get PR diff and body from environment variables
    pr_diff = os.environ.get('PR_DIFF', '')
    pr_body = os.environ.get('PR_BODY', '')
    
    # Extract instructions from PR body
    instructions = extract_instructions(pr_body)
    
    # Call validation function
    result = call_validation(pr_diff, instructions)
    
    # Write result to file for the next GitHub Action step
    with open('validation_result.json', 'w') as f:
        json.dump(result, f)
    
    print(f"Validation result: {'Valid' if result['valid'] else 'Invalid'}")