"""
Custom Exceptions Module

Location: agribot/utils/exceptions.py

Defines application-specific exceptions for better error handling
and debugging throughout the AgriBot system.
"""

class AgriBotException(Exception):
    """Base exception class for all AgriBot-specific errors"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class ConfigurationError(AgriBotException):
    """Raised when there are configuration-related problems"""
    pass

class APIServiceError(AgriBotException):
    """Raised when external API services fail or are unavailable"""
    
    def __init__(self, service_name: str, message: str, status_code: int = None):
        self.service_name = service_name
        self.status_code = status_code
        super().__init__(
            message=f"{service_name} API Error: {message}",
            error_code="API_ERROR",
            details={"service": service_name, "status_code": status_code}
        )

class NLPProcessingError(AgriBotException):
    """Raised when natural language processing fails"""
    pass

class KnowledgeBaseError(AgriBotException):
    """Raised when agricultural knowledge base operations fail"""
    pass

class DatabaseError(AgriBotException):
    """Raised when database operations fail"""
    pass

class ValidationError(AgriBotException):
    """Raised when input validation fails"""
    
    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(
            message=f"Validation error for '{field}': {message}",
            error_code="VALIDATION_ERROR",
            details={"field": field}
        )

class AuthenticationError(AgriBotException):
    """Raised when authentication or authorization fails"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTH_ERROR",
            details={"auth_failure": True}
        )