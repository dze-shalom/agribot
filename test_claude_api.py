"""
Test Claude API Connection
Quick test to verify your Claude API key is working
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('CLAUDE_API_KEY')

print("=" * 60)
print("Testing Claude API Connection")
print("=" * 60)
print()

if not api_key or api_key == 'your-claude-api-key-here':
    print("[ERROR] Claude API key not found in .env file")
    print("Please add your API key to the .env file")
    sys.exit(1)

print(f"[OK] API Key found: {api_key[:20]}...")
print()

try:
    from anthropic import Anthropic

    print("[OK] Anthropic package imported successfully")
    print()

    # Initialize client
    client = Anthropic(api_key=api_key)
    print("[OK] Claude client initialized")
    print()

    # Test a simple request
    print("Sending test message to Claude...")
    print()

    # Try multiple models to find what's available
    models_to_try = [
        "claude-3-5-sonnet-20241022",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307"
    ]

    message = None
    for model in models_to_try:
        try:
            print(f"Trying model: {model}...")
            message = client.messages.create(
                model=model,
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": "Say 'Hello, AgriBot is ready!' in one sentence."
                    }
                ]
            )
            print(f"Success with model: {model}")
            break
        except Exception as e:
            print(f"Model {model} not available: {str(e)[:50]}")
            continue

    if not message:
        raise Exception("No available Claude models found for your API key")

    response_text = message.content[0].text

    print("=" * 60)
    print("SUCCESS! Claude API is working!")
    print("=" * 60)
    print()
    print(f"Claude's Response: {response_text}")
    print()
    print("=" * 60)
    print("Next Steps:")
    print("1. Your Claude API is properly configured")
    print("2. Ready to integrate with AgriBot chatbot")
    print("3. You'll get much smarter, context-aware responses")
    print("=" * 60)

except Exception as e:
    print("=" * 60)
    print("ERROR: Claude API test failed")
    print("=" * 60)
    print()
    print(f"Error details: {str(e)}")
    print()
    print("Common issues:")
    print("- Invalid API key")
    print("- Network connection problems")
    print("- API key doesn't have credits")
    print()
    sys.exit(1)
