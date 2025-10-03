"""
Routes Package Initialization
Location: agribot/app/routes/__init__.py

Registers all Flask blueprints for the AgriBot application.
"""

from datetime import datetime
from .chat import chat_bp
from .api import api_bp
from .admin import admin_bp
from .sensors import sensors_bp

def register_routes(app):
    """Register all blueprints with the Flask app"""

    # Chat routes
    app.register_blueprint(chat_bp, url_prefix='/chat')

    # API routes
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    # Admin routes (would typically require authentication)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Sensor routes (for IoT sensor data interpretation)
    app.register_blueprint(sensors_bp)
    
    # API info route
    @app.route('/api')
    def api_info():
        return {
            'message': 'AgriBot API Server',
            'version': '1.0.0',
            'status': 'operational',
            'endpoints': {
                'chat': '/chat',
                'api': '/api/v1',
                'admin': '/admin'
            }
        }
    
    @app.route('/health')
    def health():
        """Simple health check endpoint"""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        }