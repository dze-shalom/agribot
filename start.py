"""
Startup script for AgriBot application
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import create_app

if __name__ == '__main__':
    # Create the Flask application
    app = create_app()

    # Run the development server
    print("=" * 60)
    print("AgriBot Server Starting...")
    print("=" * 60)
    print(f"Server running at: http://localhost:5000")
    print(f"Login page: http://localhost:5000/login.html")
    print(f"Health check: http://localhost:5000/health")
    print("=" * 60)
    print("Press CTRL+C to stop the server")
    print("=" * 60)

    try:
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"\nServer error: {e}")
        import traceback
        traceback.print_exc()