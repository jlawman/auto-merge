import modal
import re
from anthropic import Anthropic
import json

# Create Modal stub
app = modal.App("pr-validator")


# Define an image with our dependencies
image = modal.Image.debian_slim().pip_install(
    "anthropic>=0.5.0",
    "python-dotenv"
)

@app.function(image=image, secrets=[modal.Secret.from_name("llms")])
def validate_pr(diff, instructions):
    """
    Validate that a PR diff matches the given instructions.
    
    Args:
        diff (str): The PR diff
        instructions (str): The instructions for the PR
        
    Returns:
        dict: A dictionary with validation result
    """
    client = Anthropic()
    
    # Create the prompt for the LLM
    prompt = f"""
    You are an AI PR reviewer that checks if code changes match the requirements.
    
    <instructions>
    {instructions}
    </instructions>
    
    <diff>
    {diff}
    </diff>
    
    Based on the instructions and diff:
    1. Analyze whether the changes in the diff implement the requirements in the instructions.
    2. Provide a brief explanation of your analysis.
    3. End with a final verdict in an XML tag using this format: <verdict>true</verdict> or <verdict>false</verdict>
    
    Your response:
    """
    
    # Call the Anthropic API
    try:
        response = client.messages.create(
            model="claude-3-7-sonnet-latest",
            max_tokens=2000,
            temperature=0,
            system="You are a precise code reviewer that checks if code changes match the instructions. Be thorough but fair in your assessment.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Extract the verdict
        verdict_match = re.search(r'<verdict>(true|false)</verdict>', response.content[0].text, re.IGNORECASE)
        if verdict_match:
            is_valid = verdict_match.group(1).lower() == 'true'
        else:
            is_valid = False
            
        # Clean up the comment
        comment = response.content[0].text.replace('<verdict>true</verdict>', '').replace('<verdict>false</verdict>', '')
        
        # Prepare emojis for the verdict
        verdict_emoji = "✅" if is_valid else "❌"
        verdict_text = "APPROVED" if is_valid else "CHANGES REQUESTED"
        
        return {
            "valid": is_valid,
            "comment": f"## PR Validation Bot: {verdict_emoji} {verdict_text}\n\n{comment.strip()}"
        }
        
    except Exception as e:
        return {
            "valid": False,
            "comment": f"❌ Error during validation: {str(e)}"
        }

@app.function(image=image)
@modal.web_endpoint(method="POST")
def api_validate(diff: str, instructions: str):
    """API endpoint for the validation function"""
    return validate_pr.remote(diff, instructions)

if __name__ == "__main__":
    # For local testing
    with open("test_diff.txt", "r") as f:
        test_diff = f.read()
    
    with open("test_instructions.txt", "r") as f:
        test_instructions = f.read()
    
    result = validate_pr.local(test_diff, test_instructions)
    print(json.dumps(result, indent=2))