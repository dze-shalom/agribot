"""
AgriBot Application Runner
Starts the Flask application with full authentication and features
"""
from app.main import create_app

# Create the application
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)