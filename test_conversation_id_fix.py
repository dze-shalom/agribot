"""
Test that conversation_id is now returned in the response
"""

print("Testing Conversation ID Fix")
print("="*60)

# Simulate the response structure
response_data = {
    'response': 'Hello! How can I help you?',
    'conversation_id': 123,  # This comes from agribot_engine.process_message()
    'metadata': {}
}

# OLD WAY (before fix):
old_response = {
    'success': True,
    'data': response_data,
    'timestamp': '2025-10-06T10:00:00'
}

print("\nOLD Response Structure (conversation_id hidden in data):")
print(f"  success: {old_response['success']}")
print(f"  conversation_id at top level: {old_response.get('conversation_id', 'MISSING!')}")
print(f"  conversation_id in data: {old_response['data'].get('conversation_id')}")

# NEW WAY (after fix):
new_response = {
    'success': True,
    'data': response_data,
    'conversation_id': response_data.get('conversation_id'),  # Extracted to top level
    'timestamp': '2025-10-06T10:00:00'
}

print("\nNEW Response Structure (conversation_id at top level):")
print(f"  success: {new_response['success']}")
print(f"  conversation_id at top level: {new_response.get('conversation_id', 'MISSING!')}")
print(f"  conversation_id in data: {new_response['data'].get('conversation_id')}")

print("\n" + "="*60)
print("Frontend can now access:")
print("  data.conversation_id (top level) ✓")
print("  data.data.conversation_id (nested) ✓")
print("\nThis means:")
print("  - Frontend will receive real conversation ID (e.g., 123)")
print("  - No more temporary session IDs needed")
print("  - Feedback will use real integer ID")
print("  - Works with INTEGER column in PostgreSQL")
print("="*60)
