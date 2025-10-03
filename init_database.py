#!/usr/bin/env python3
"""
Database Initialization Script
Location: agribot/init_database.py

Simple script to initialize the AgriBot database without starting the full application.
Useful for development setup and deployment scripts.
"""

import os
import sys
from flask import Flask
from config.settings import get_config
from database import init_db

def initialize_database():
    """Initialize the AgriBot database"""
    print("Initializing AgriBot database...")

    # Create Flask app
    app = Flask(__name__)

    # Load configuration
    config = get_config()

    # Configure Flask for database
    app.config.update({
        'SQLALCHEMY_DATABASE_URI': config.database.url,
        'SQLALCHEMY_TRACK_MODIFICATIONS': config.database.track_modifications,
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'pool_size': config.database.pool_size,
            'max_overflow': config.database.max_overflow
        }
    })

    # Initialize database
    try:
        db = init_db(app)
        print("[SUCCESS] Database initialized successfully!")
        print(f"   Database URL: {config.database.url}")
        return True
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = initialize_database()
    sys.exit(0 if success else 1)