#!/usr/bin/env python3
"""
AgriBot Server Starter
Launches the full AgriBot application with all features
"""

if __name__ == '__main__':
    print("=" * 60)
    print("Starting AgriBot Server...")
    print("=" * 60)
    print()

    from app.main import create_app

    # Create application with all features
    app = create_app()

    print()
    print("=" * 60)
    print("AgriBot Server Ready!")
    print("=" * 60)
    print()
    print("Admin Dashboard: http://localhost:5000/analytics.html")
    print("Chat Interface:  http://localhost:5000/chatbot.html")
    print("Login Page:      http://localhost:5000/login.html")
    print()
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    print()

    # Run server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True  # Auto-reload on code changes
    )
