"""
Test script to run the server locally and verify fixes work
"""
import os
import sys

# Set environment to use local database
os.environ['FLASK_ENV'] = 'development'
os.environ['DATABASE_URL'] = 'sqlite:///instance/agribot.db'

# Import after setting env
from app.main import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("Testing AgriBot Locally")
    print("=" * 60)
    print("\nServer will start on: http://localhost:5000")
    print("\nTest URLs:")
    print("  - Analytics: http://localhost:5000/analytics.html")
    print("  - API Test: http://localhost:5000/api/auth/admin/analytics/overview")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)

    app.run(debug=True, port=5000, host='localhost')
