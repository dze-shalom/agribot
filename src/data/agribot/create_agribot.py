#!/usr/bin/env python3
"""
AgriBot Project Structure Generator
Creates the exact project structure for the sophisticated agricultural chatbot
"""

import os
import sys
from pathlib import Path

class AgriBotProjectGenerator:
    def __init__(self, project_name="agribot"):
        self.project_name = project_name
        self.base_path = Path(project_name)
        
        # Define the exact project structure as specified
        self.directories = [
            "config",
            "app",
            "app/routes", 
            "core",
            "knowledge",
            "nlp",
            "services",
            "services/weather",
            "services/agricultural_data",
            "services/cache",
            "database",
            "database/models",
            "database/migrations",
            "database/seeders",
            "database/repositories",
            "utils",
            "tests",
            "tests/unit",
            "tests/integration", 
            "tests/fixtures",
            "static",
            "static/css",
            "static/js", 
            "static/images",
            "templates",
            "deployment"
        ]
        
        # Define files to create in each directory
        self.files = {
            # Root level files
            "root": [
                "README.md",
                "requirements.txt", 
                ".env.example",
                ".gitignore",
                "run.py"
            ],
            # Config directory
            "config": [
                "__init__.py",
                "settings.py",
                "logging.py"
            ],
            # App directory
            "app": [
                "__init__.py",
                "main.py"
            ],
            "app/routes": [
                "__init__.py",
                "chat.py",
                "api.py", 
                "admin.py"
            ],
            # Core directory
            "core": [
                "__init__.py",
                "agribot_engine.py",
                "conversation_manager.py",
                "response_builder.py"
            ],
            # Knowledge directory
            "knowledge": [
                "__init__.py",
                "agricultural_knowledge.py",
                "crop_database.py",
                "regional_expertise.py"
            ],
            # NLP directory
            "nlp": [
                "__init__.py", 
                "intent_classifier.py",
                "entity_extractor.py",
                "sentiment_analyzer.py",
                "text_processor.py"
            ],
            # Services directory
            "services": [
                "__init__.py",
                "data_coordinator.py"
            ],
            "services/weather": [
                "__init__.py",
                "openweather_client.py",
                "weather_analyzer.py"
            ],
            "services/agricultural_data": [
                "__init__.py",
                "fao_client.py",
                "nasa_client.py"
            ],
            "services/cache": [
                "__init__.py",
                "redis_cache.py"
            ],
            # Database directory
            "database": [
                "__init__.py"
            ],
            "database/models": [
                "__init__.py",
                "user.py",
                "conversation.py", 
                "analytics.py",
                "geographic.py"
            ],
            "database/seeders": [
                "__init__.py",
                "initial_data.py"
            ],
            "database/repositories": [
                "__init__.py",
                "user_repository.py",
                "conversation_repository.py",
                "analytics_repository.py"
            ],
            # Utils directory
            "utils": [
                "__init__.py",
                "decorators.py",
                "validators.py", 
                "exceptions.py",
                "helpers.py"
            ],
            # Tests directory
            "tests": [
                "__init__.py"
            ],
            "tests/unit": [
                "__init__.py",
                "test_nlp.py",
                "test_services.py",
                "test_knowledge.py"
            ],
            "tests/integration": [
                "__init__.py",
                "test_api.py",
                "test_database.py"
            ],
            "tests/fixtures": [
                "__init__.py",
                "test_data.py"
            ],
            # Deployment directory
            "deployment": [
                "Dockerfile",
                "docker-compose.yml",
                "requirements-prod.txt"
            ]
        }

    def create_project(self):
        """Create the complete AgriBot project structure"""
        print(f"🌱 Creating AgriBot project structure: '{self.project_name}/'")
        
        # Create base project directory
        self.base_path.mkdir(exist_ok=True)
        print(f"📁 Created base directory: {self.project_name}/")
        
        # Create all directories
        for directory in self.directories:
            dir_path = self.base_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created: {directory}/")
        
        # Create root level files
        for file_name in self.files["root"]:
            content = self.get_file_content("root", file_name)
            self.create_file("", file_name, content)
        
        # Create files in each directory
        for directory, file_list in self.files.items():
            if directory != "root":
                for file_name in file_list:
                    content = self.get_file_content(directory, file_name)
                    self.create_file(directory, file_name, content)
        
        self.print_success_message()

    def create_file(self, directory, file_name, content):
        """Create a single file with content"""
        if directory:
            file_path = self.base_path / directory / file_name
            display_path = f"{directory}/{file_name}"
        else:
            file_path = self.base_path / file_name
            display_path = file_name
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📄 Created: {display_path}")

    def get_file_content(self, directory, file_name):
        """Get content for specific files"""
        templates = {
            ("root", "README.md"): '''# AgriBot - Advanced Agricultural AI Assistant for Cameroon

A sophisticated conversational AI system providing agricultural guidance across all 10 regions of Cameroon.

## Features

- **Multi-service Data Integration**: OpenWeatherMap, FAO, NASA POWER APIs
- **Advanced NLP**: Intent classification, entity extraction, sentiment analysis
- **Comprehensive Knowledge Base**: Diseases, fertilizers, planting procedures, pest control
- **Context-aware Conversations**: Maintains conversation history and context
- **Regional Expertise**: Specialized advice for all Cameroon regions
- **Analytics Dashboard**: Conversation insights and user feedback systems
- **Production Ready**: Scalable architecture with caching and database persistence

## Quick Start

```bash
# 1. Set up environment
cp .env.example .env
# Edit .env with your API keys

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python run.py
```

## Project Architecture

```
agribot/
├── core/           # Conversation engine and logic
├── knowledge/      # Agricultural domain expertise  
├── nlp/           # Natural language processing
├── services/      # External API integrations
├── database/      # Data persistence and analytics
└── utils/         # Utility functions and helpers
```

## Supported Crops

Maize, cassava, plantain, cocoa, coffee, oil palm, rice, beans, pepper, tomatoes, yam, groundnuts, cotton, millet, sorghum, and 30+ other crops grown in Cameroon.

## Supported Regions

All 10 regions with climate-specific advice: Centre, Littoral, West, Northwest, Southwest, East, North, Far North, Adamawa, South.

## API Documentation

- `/api/chat` - Conversational interface
- `/api/weather/{region}` - Weather data  
- `/api/crops/{crop}/diseases` - Disease information
- `/api/analytics` - Usage analytics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - See LICENSE file for details
''',

            ("root", "requirements.txt"): '''# Core Framework
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Migrate==4.0.5

# External APIs
requests==2.31.0
urllib3==2.0.4

# Environment Management  
python-dotenv==1.0.0

# Caching
redis==5.0.0

# Database
SQLAlchemy==2.0.19
psycopg2-binary==2.9.7

# Testing
pytest==7.4.2
pytest-flask==1.2.1
pytest-cov==4.1.0

# Production Server
gunicorn==21.2.0

# Development Tools
black==23.7.0
flake8==6.0.0
isort==5.12.0

# Utilities
click==8.1.7
python-dateutil==2.8.2
''',

            ("root", ".env.example"): '''# API Keys - Get from respective services
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Flask Configuration
FLASK_SECRET_KEY=your-very-secure-secret-key-here
FLASK_ENV=development
FLASK_APP=app.main:create_app

# Database Configuration
DATABASE_URL=sqlite:///agribot.db
# For production use PostgreSQL:
# DATABASE_URL=postgresql://username:password@localhost/agribot

# Redis Cache (Optional)
REDIS_URL=redis://localhost:6379/0
CACHE_ENABLED=true
CACHE_TIMEOUT=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/agribot.log

# External APIs Configuration
API_TIMEOUT=30
MAX_RETRIES=3
RATE_LIMIT=100

# Feature Flags
ENABLE_ANALYTICS=true
ENABLE_FEEDBACK=true
ENABLE_ADMIN_PANEL=true
''',

            ("root", ".gitignore"): '''# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Database
*.db
*.sqlite3
migrations/versions/*

# Logs
*.log
logs/

# Cache
.cache/
redis-dump.rdb

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
static/uploads/
temp/
''',

            ("root", "run.py"): '''#!/usr/bin/env python3
"""
AgriBot Application Entry Point
Run this file to start the development server
"""

from app.main import create_app
import os

if __name__ == '__main__':
    # Create Flask application
    app = create_app()
    
    # Get configuration from environment
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("🌱 Starting AgriBot Agricultural Assistant")
    print(f"📡 Server: http://{host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print("🚀 Ready to help farmers!")
    
    # Run the application
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug
    )
''',

            # Config files
            ("config", "__init__.py"): '''"""
Configuration package for AgriBot
"""
''',

            ("config", "settings.py"): '''"""
Environment-based configuration management for AgriBot
"""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    url: str = os.getenv('DATABASE_URL', 'sqlite:///agribot.db')
    track_modifications: bool = False
    echo: bool = os.getenv('FLASK_ENV') == 'development'
    pool_size: int = 10
    max_overflow: int = 20

@dataclass
class APIConfig:
    """External API configuration"""
    openweather_key: Optional[str] = os.getenv('OPENWEATHER_API_KEY')
    fao_base_url: str = "https://fenixservices.fao.org/faostat/api/v1/en"
    nasa_base_url: str = "https://power.larc.nasa.gov/api/temporal"
    timeout: int = int(os.getenv('API_TIMEOUT', '30'))
    max_retries: int = int(os.getenv('MAX_RETRIES', '3'))
    rate_limit: int = int(os.getenv('RATE_LIMIT', '100'))

@dataclass
class CacheConfig:
    """Redis cache configuration"""
    url: str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    enabled: bool = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    default_timeout: int = int(os.getenv('CACHE_TIMEOUT', '3600'))
    key_prefix: str = 'agribot:'

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = os.getenv('LOG_LEVEL', 'INFO')
    file: str = os.getenv('LOG_FILE', 'logs/agribot.log')
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

@dataclass
class AppConfig:
    """Main application configuration"""
    secret_key: str = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')
    debug: bool = os.getenv('FLASK_ENV') == 'development'
    testing: bool = False
    
    # Feature flags
    enable_analytics: bool = os.getenv('ENABLE_ANALYTICS', 'true').lower() == 'true'
    enable_feedback: bool = os.getenv('ENABLE_FEEDBACK', 'true').lower() == 'true'
    enable_admin: bool = os.getenv('ENABLE_ADMIN_PANEL', 'true').lower() == 'true'
    
    # Component configurations
    database: DatabaseConfig = DatabaseConfig()
    apis: APIConfig = APIConfig()
    cache: CacheConfig = CacheConfig()
    logging: LoggingConfig = LoggingConfig()
    
    def validate(self):
        """Validate critical configuration values"""
        errors = []
        
        if not self.apis.openweather_key:
            errors.append("OPENWEATHER_API_KEY environment variable is required")
        
        if (self.secret_key == 'dev-key-change-in-production' and 
            not self.debug):
            errors.append("FLASK_SECRET_KEY must be set for production")
        
        if errors:
            raise ValueError("Configuration errors: " + "; ".join(errors))

class DevelopmentConfig(AppConfig):
    """Development environment configuration"""
    debug: bool = True

class TestingConfig(AppConfig):
    """Testing environment configuration"""
    testing: bool = True
    database: DatabaseConfig = DatabaseConfig(url='sqlite:///:memory:')
    cache: CacheConfig = CacheConfig(enabled=False)

class ProductionConfig(AppConfig):
    """Production environment configuration"""
    debug: bool = False
    database: DatabaseConfig = DatabaseConfig(
        url=os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/agribot')
    )

# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': AppConfig
}

def get_config(config_name: str = None) -> AppConfig:
    """Get configuration based on environment"""
    if not config_name:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    config_class = config_map.get(config_name, AppConfig)
    config = config_class()
    config.validate()
    
    return config
''',

            ("config", "logging.py"): '''"""
Logging configuration for AgriBot
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from config.settings import LoggingConfig

def setup_logging(app, config: LoggingConfig = None):
    """Configure application logging"""
    if not config:
        config = LoggingConfig()
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(config.file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Set up file handler for production
    if not app.debug and not app.testing:
        file_handler = RotatingFileHandler(
            config.file,
            maxBytes=config.max_bytes,
            backupCount=config.backup_count
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        # Set log level
        log_level = getattr(logging, config.level.upper(), logging.INFO)
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(log_level)
        
        app.logger.info('AgriBot application startup')
    
    # Console handler for development
    if app.debug:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s'
        ))
        app.logger.addHandler(console_handler)
        app.logger.setLevel(logging.DEBUG)
    
    # Log important configuration
    app.logger.info(f'AgriBot configured with log level: {config.level}')
    if not app.debug:
        app.logger.info(f'Logs will be written to: {config.file}')
''',

            # Default __init__.py content
            ("app", "__init__.py"): '''"""
Flask application package for AgriBot
"""
''',
            
            # All other __init__.py files get minimal content
        }
        
        # For __init__.py files not explicitly defined, return minimal content
        if file_name == "__init__.py" and (directory, file_name) not in templates:
            return f'"""\n{directory.replace("/", " ").title()} package for AgriBot\n"""\n'
        
        # For other files not yet templated, return placeholder
        key = (directory, file_name)
        if key in templates:
            return templates[key]
        else:
            return f'"""\n{file_name} - AgriBot {directory} module\nTODO: Implement this module\n"""\n'

    def print_success_message(self):
        """Print success message with next steps"""
        print("\n" + "="*60)
        print("🎉 AgriBot project structure created successfully!")
        print("="*60)
        print(f"\n📂 Project location: ./{self.project_name}/")
        print(f"📋 Files created: {self.count_files()} files in {len(self.directories)} directories")
        
        print("\n🚀 Next Steps:")
        print(f"1. cd {self.project_name}")
        print("2. cp .env.example .env")
        print("3. Edit .env with your API keys")
        print("4. pip install -r requirements.txt")
        print("5. python run.py")
        
        print("\n📖 Key Files to Review:")
        print("• config/settings.py - Configuration management")
        print("• app/main.py - Application factory")
        print("• core/agribot_engine.py - Main conversation engine")
        print("• knowledge/agricultural_knowledge.py - Domain expertise")
        
        print("\n🔗 API Keys Needed:")
        print("• OpenWeatherMap API key (required)")
        print("• Optional: Redis for caching")
        
        print("\n💡 The structure is ready for your existing code migration!")

    def count_files(self):
        """Count total files that will be created"""
        total = len(self.files["root"])
        for directory, file_list in self.files.items():
            if directory != "root":
                total += len(file_list)
        return total

def main():
    """Main function to generate project"""
    import sys
    
    # Get project name from command line or use default
    project_name = sys.argv[1] if len(sys.argv) > 1 else "agribot"
    
    # Validate project name
    if not project_name.replace("_", "").replace("-", "").isalnum():
        print("❌ Error: Project name must contain only letters, numbers, hyphens, and underscores")
        sys.exit(1)
    
    # Check if directory already exists
    if os.path.exists(project_name):
        response = input(f"⚠️  Directory '{project_name}' already exists. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            sys.exit(0)
    
    # Generate project
    try:
        generator = AgriBotProjectGenerator(project_name)
        generator.create_project()
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()