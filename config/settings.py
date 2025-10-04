"""
Configuration Management Module
Location: agribot/config/settings.py

Handles environment-based configuration for the AgriBot application.
Provides structured configuration classes for different environments
and validates critical settings on startup.
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    """Database connection and behavior configuration"""
    url: str = os.getenv('DATABASE_URL', 'sqlite:///instance/agribot.db')
    track_modifications: bool = False
    echo: bool = os.getenv('FLASK_ENV') == 'development'
    pool_size: int = 10
    max_overflow: int = 20

@dataclass
class APIConfig:
    """External API services configuration"""
    openweather_key: Optional[str] = os.getenv('OPENWEATHER_API_KEY')
    claude_api_key: Optional[str] = os.getenv('ANTHROPIC_API_KEY')
    fao_base_url: str = "https://fenixservices.fao.org/faostat/api/v1/en"
    nasa_base_url: str = "https://power.larc.nasa.gov/api/temporal"
    timeout: int = int(os.getenv('API_TIMEOUT', '30'))
    max_retries: int = int(os.getenv('MAX_RETRIES', '3'))
    rate_limit: int = int(os.getenv('RATE_LIMIT', '100'))

@dataclass
class CacheConfig:
    """Redis caching configuration"""
    url: str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    enabled: bool = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    default_timeout: int = int(os.getenv('CACHE_TIMEOUT', '3600'))
    key_prefix: str = 'agribot:'

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = os.getenv('LOG_LEVEL', 'INFO')
    file: str = os.getenv('LOG_FILE', 'logs/agribot.log')
    max_bytes: int = int(os.getenv('LOG_MAX_BYTES', str(10 * 1024 * 1024)))  # 10 MB
    backup_count: int = int(os.getenv('LOG_BACKUP_COUNT', '5'))

class AppConfig:
    """Main application configuration with validation"""
    def __init__(self):
        self.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')
        self.debug = os.getenv('FLASK_ENV') == 'development'
        self.testing = False

        # Component configurations
        self.database = DatabaseConfig()
        self.apis = APIConfig()
        self.cache = CacheConfig()
        self.logging = LoggingConfig()
    
    def validate(self):
        """Validate critical configuration values and raise errors for missing keys"""
        errors = []

        if not self.apis.openweather_key:
            errors.append("OPENWEATHER_API_KEY environment variable is required")

        # Claude API key is required for production, optional for development
        if not self.apis.claude_api_key and not self.debug:
            errors.append("ANTHROPIC_API_KEY environment variable is required for production")

        if (self.secret_key == 'dev-key-change-in-production' and not self.debug):
            errors.append("FLASK_SECRET_KEY must be set for production")

        if errors:
            raise ValueError("Configuration errors: " + "; ".join(errors))

class ProductionConfig(AppConfig):
    """Production environment with PostgreSQL and security hardening"""
    def __init__(self):
        super().__init__()
        self.debug = False
        # In production, DATABASE_URL MUST be set - fail fast if not
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            raise ValueError("DATABASE_URL environment variable is required for production")
        self.database = DatabaseConfig(url=db_url)

def get_config(env_name: str = None) -> AppConfig:
    """Factory function to get appropriate configuration based on environment"""
    env = env_name or os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig()
    else:
        return AppConfig()