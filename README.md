# PR Validator

A Modal application that validates Pull Request diffs against given instructions using Claude AI.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
pip install pytest pytest-mock
```

2. Set up your environment variables in `.env` file:
```
ANTHROPIC_API_KEY=your_api_key_here
```

3. Deploy to Modal:
```bash
modal deploy modal_infra.py
```

## Testing

Run the tests with:
```bash
pytest -v
```

Or run individual test files:
```bash
pytest -v test_modal_infra.py
pytest -v test_api_validate.py
```

## Local Testing

For local testing without Modal deployment, you can create test files:

1. Create a `test_diff.txt` file with a sample PR diff
2. Create a `test_instructions.txt` file with sample PR instructions
3. Run:
```bash
python modal_infra.py
```

## API Usage

The API endpoint accepts POST requests with the following JSON body:
```json
{
  "diff": "PR diff content",
  "instructions": "PR instructions"
}
```

It returns a JSON response with:
```json
{
  "valid": true|false,
  "comment": "Validation comment with verdict"
}
``` 