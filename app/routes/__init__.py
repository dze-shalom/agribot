"""
Routes Package Initialization
Location: agribot/app/routes/__init__.py

Registers all Flask blueprints for the AgriBot application.
"""

from datetime import datetime
import logging

# Import blueprints defensively so missing optional deps don't block startup
logger = logging.getLogger(__name__)

try:
    from .chat import chat_bp
except Exception as e:
    chat_bp = None
    logger.warning(f"Failed to import chat blueprint: {e}")

try:
    from .api import api_bp
except Exception as e:
    api_bp = None
    logger.warning(f"Failed to import api blueprint: {e}")

try:
    from .admin import admin_bp
except Exception as e:
    admin_bp = None
    logger.warning(f"Failed to import admin blueprint: {e}")

try:
    from .sensors import sensors_bp
except Exception as e:
    sensors_bp = None
    logger.warning(f"Failed to import sensors blueprint: {e}")

def register_routes(app):
    """Register all blueprints with the Flask app"""

    # Chat routes
    if chat_bp:
        app.register_blueprint(chat_bp, url_prefix='/chat')
    else:
        logger.info('Chat blueprint not available; skipping registration')

    # API routes
    if api_bp:
        app.register_blueprint(api_bp, url_prefix='/api/v1')
    else:
        logger.info('API blueprint not available; skipping registration')

    # Admin routes (would typically require authentication)
    if admin_bp:
        app.register_blueprint(admin_bp, url_prefix='/admin')
    else:
        logger.info('Admin blueprint not available; skipping registration')

    # Sensor routes (for IoT sensor data interpretation)
    if sensors_bp:
        app.register_blueprint(sensors_bp)
    else:
        logger.info('Sensors blueprint not available; skipping registration')
    
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