"""
Input Validators
Location: agribot/utils/validators.py

Validation functions for user input and API parameters.
"""

import re
from typing import Dict, Any, List

def validate_chat_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate chat input data"""
    result = {'valid': True, 'error': None}
    
    # Check if message exists and is not empty
    message = data.get('message', '').strip()
    if not message:
        result['valid'] = False
        result['error'] = 'Message cannot be empty'
        return result
    
    # Check message length
    if len(message) > 2000:
        result['valid'] = False
        result['error'] = 'Message too long (maximum 2000 characters)'
        return result
    
    # Validate user_name if provided
    user_name = data.get('user_name', '')
    if user_name and len(user_name) > 100:
        result['valid'] = False
        result['error'] = 'User name too long (maximum 100 characters)'
        return result
    
    # Validate user_region if provided
    user_region = data.get('user_region', '')
    if user_region and not validate_region(user_region):
        result['valid'] = False
        result['error'] = f'Invalid region: {user_region}'
        return result
    
    return result

def validate_region(region: str) -> bool:
    """Validate if region is supported"""
    supported_regions = [
        'centre', 'littoral', 'west', 'northwest', 'southwest',
        'east', 'north', 'far_north', 'adamawa', 'south'
    ]
    
    return region.lower().strip() in supported_regions

def validate_crop(crop: str) -> bool:
    """Validate if crop is supported"""
    # This is a simplified validation - in practice would check against knowledge base
    supported_crops = [
        'maize', 'cassava', 'plantain', 'cocoa', 'coffee', 'rice', 'yam',
        'beans', 'groundnuts', 'tomatoes', 'pepper', 'okra', 'onion',
        'banana', 'pineapple', 'mango', 'avocado', 'cotton', 'oil_palm'
    ]
    
    return crop.lower().strip() in supported_crops

def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> bool:
    """Validate password strength"""
    if not password:
        return False
    
    # Minimum 6 characters
    if len(password) < 6:
        return False
    
    # Could add more complex rules here (uppercase, lowercase, numbers, special chars)
    # For now, just checking minimum length
    return True

def validate_phone(phone: str) -> bool:
    """Validate Cameroon phone number"""
    if not phone:
        return True  # Phone is optional
    
    # Remove spaces and common separators
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Cameroon phone pattern: +237XXXXXXXXX or 237XXXXXXXXX or XXXXXXXXX
    # Mobile numbers start with 6, 7, 8, or 9
    patterns = [
        r'^\+237[6789]\d{8}$',  # +237XXXXXXXXX
        r'^237[6789]\d{8}$',    # 237XXXXXXXXX
        r'^[6789]\d{8}$'        # XXXXXXXXX
    ]
    
    return any(re.match(pattern, clean_phone) for pattern in patterns)

def validate_name(name: str) -> bool:
    """Validate user name"""
    if not name or not name.strip():
        return False
    
    # Check length
    if len(name.strip()) < 2 or len(name.strip()) > 100:
        return False
    
    # Allow letters, spaces, hyphens, apostrophes
    pattern = r"^[a-zA-ZÀ-ÿ\s\-']+$"
    return re.match(pattern, name.strip()) is not None

def validate_user_registration(data: Dict[str, Any]) -> Dict[str, str]:
    """Validate user registration data"""
    errors = {}
    
    # Name validation
    name = data.get('name', '').strip()
    if not name:
        errors['name'] = 'Name is required'
    elif not validate_name(name):
        errors['name'] = 'Name must be 2-100 characters and contain only letters, spaces, hyphens, and apostrophes'
    
    # Email validation
    email = data.get('email', '').strip()
    if not email:
        errors['email'] = 'Email is required'
    elif not validate_email(email):
        errors['email'] = 'Please enter a valid email address'
    
    # Password validation
    password = data.get('password', '')
    if not password:
        errors['password'] = 'Password is required'
    elif not validate_password(password):
        errors['password'] = 'Password must be at least 6 characters long'
    
    # Confirm password validation
    confirm_password = data.get('confirm_password', '')
    if password and confirm_password and password != confirm_password:
        errors['confirm_password'] = 'Passwords do not match'
    
    # Phone validation (optional)
    phone = data.get('phone', '')
    if phone and not validate_phone(phone):
        errors['phone'] = 'Please enter a valid Cameroon phone number'
    
    # Region validation
    region = data.get('region', '')
    if not region:
        errors['region'] = 'Region is required'
    elif not validate_region(region):
        errors['region'] = 'Please select a valid region'
    
    # Account type validation
    account_type = data.get('account_type', '')
    if not account_type:
        errors['account_type'] = 'Account type is required'
    elif account_type not in ['user', 'admin']:
        errors['account_type'] = 'Invalid account type'
    
    return errors

def validate_user_login(data: Dict[str, Any]) -> Dict[str, str]:
    """Validate user login data"""
    errors = {}
    
    # Email validation
    email = data.get('email', '').strip()
    if not email:
        errors['email'] = 'Email is required'
    elif not validate_email(email):
        errors['email'] = 'Please enter a valid email address'
    
    # Password validation
    password = data.get('password', '')
    if not password:
        errors['password'] = 'Password is required'
    
    # Account type validation
    account_type = data.get('account_type', '')
    if not account_type:
        errors['account_type'] = 'Account type is required'
    elif account_type not in ['user', 'admin']:
        errors['account_type'] = 'Invalid account type'
    
    return errors

def validate_feedback_data(data: Dict[str, Any]) -> Dict[str, str]:
    """Validate feedback submission data"""
    errors = {}
    
    # Conversation ID validation
    conv_id = data.get('conversation_id')
    if not conv_id:
        errors['conversation_id'] = 'Conversation ID is required'
    elif not isinstance(conv_id, int) or conv_id <= 0:
        errors['conversation_id'] = 'Invalid conversation ID'
    
    # Rating validation
    rating = data.get('rating')
    if rating is not None:
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            errors['rating'] = 'Rating must be between 1 and 5'
    
    # Detailed ratings validation
    detailed_ratings = data.get('detailed_ratings', {})
    if detailed_ratings:
        for key, value in detailed_ratings.items():
            if key in ['accuracy', 'completeness', 'helpfulness', 'relevance']:
                if not isinstance(value, int) or value < 1 or value > 5:
                    errors[f'{key}_rating'] = f'{key.title()} rating must be between 1 and 5'
    
    # Comment validation
    comment = data.get('comment', '')
    if comment and len(comment) > 1000:
        errors['comment'] = 'Comment must be less than 1000 characters'
    
    return errors

def sanitize_text_input(text: str) -> str:
    """Sanitize text input to prevent issues"""
    if not text:
        return ""
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Limit length
    text = text[:2000]
    
    # Strip whitespace
    text = text.strip()
    
    return text

def sanitize_user_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize all user input data"""
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_text_input(value)
        else:
            sanitized[key] = value
    
    return sanitized

def validate_search_params(data: Dict[str, Any]) -> Dict[str, str]:
    """Validate search/filter parameters"""
    errors = {}
    
    # Page validation
    page = data.get('page', 1)
    if not isinstance(page, int) or page < 1:
        errors['page'] = 'Page must be a positive integer'
    
    # Per page validation
    per_page = data.get('per_page', 50)
    if not isinstance(per_page, int) or per_page < 1 or per_page > 100:
        errors['per_page'] = 'Per page must be between 1 and 100'
    
    # Search term validation
    search = data.get('search', '')
    if search and len(search) > 200:
        errors['search'] = 'Search term must be less than 200 characters'
    
    # Region filter validation
    region = data.get('region', '')
    if region and not validate_region(region):
        errors['region'] = 'Invalid region filter'
    
    # Status filter validation
    status = data.get('status', '')
    if status and status not in ['active', 'inactive', 'deleted']:
        errors['status'] = 'Invalid status filter'
    
    return errors

def validate_date_range(start_date: str, end_date: str) -> Dict[str, str]:
    """Validate date range for exports and filtering"""
    errors = {}
    
    if start_date or end_date:
        from datetime import datetime
        
        try:
            if start_date:
                start = datetime.fromisoformat(start_date)
            if end_date:
                end = datetime.fromisoformat(end_date)
                
            if start_date and end_date:
                if start > end:
                    errors['date_range'] = 'Start date must be before end date'
                    
        except ValueError:
            errors['date_format'] = 'Invalid date format. Use YYYY-MM-DD format'
    
    return errors