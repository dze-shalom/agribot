"""
Main Application Entry Point
Location: agribot/app/main.py

Flask application factory and configuration setup.
"""

from flask import Flask, request, g, render_template, session, redirect, url_for
from flask_cors import CORS
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from config.settings import get_config
from config.logging import setup_logging
from database import init_db
from knowledge.agricultural_knowledge import AgriculturalKnowledgeBase
from nlp import NLPProcessor
from services.data_coordinator import DataCoordinator
from core.agribot_engine import AgriBotEngine
from app.routes import register_routes
from app.routes.auth import auth_bp
from app.routes.chat import chat_bp
from app.routes.api import api_bp
from utils.exceptions import AgriBotException

def create_app(config_name=None):
    """Create and configure Flask application"""
    
    # Create Flask app with correct template directory
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Load configuration
    config = get_config(config_name)
    
    # Configure Flask settings
    app.config.update({
        'SECRET_KEY': config.secret_key,
        'DEBUG': config.debug,
        'TESTING': config.testing,
        'SQLALCHEMY_DATABASE_URI': config.database.url,
        'SQLALCHEMY_TRACK_MODIFICATIONS': config.database.track_modifications,
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'pool_size': config.database.pool_size,
            'max_overflow': config.database.max_overflow
        },
        'SEND_FILE_MAX_AGE_DEFAULT': 0  # Disable caching in debug mode
    })
    
    # Store config object for access throughout app
    app.config_obj = config
    
    # Setup logging
    setup_logging(app, config.logging)
    app.logger.info("AgriBot application starting up")
    
    # Enable CORS for API access
    CORS(app, resources={
        r"/api/*": {"origins": "*"},
        r"/chat/*": {"origins": "*"}
    })
    
    # Initialize database
    init_db(app)
    app.logger.info("Database initialized")
    
    # Initialize AgriBot engine with dependency injection
    app.agribot = create_agribot_engine(config, app.logger)
    app.logger.info("AgriBot engine initialized")
    
    # Store data coordinator for direct API access
    app.data_coordinator = app.agribot.data_coordinator
    
    # Register authentication blueprint first
    app.register_blueprint(auth_bp)

    # Register other routes
    register_routes(app)
    app.logger.info("Routes registered")
    
    # Register main page routes
    register_main_routes(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register request handlers
    register_request_handlers(app)
    
    app.logger.info("AgriBot application fully initialized")
    
    return app

def register_main_routes(app):
    """Register main page routes with authentication"""

    @app.route('/')
    def index():
        """Main landing page with authentication check"""
        if 'user_id' in session:
            # Redirect to appropriate dashboard based on account type
            account_type = session.get('account_type', 'user')
            if account_type == 'admin':
                return redirect('/analytics.html')
            else:
                return redirect('/chatbot.html')

        # Show login page for non-authenticated users
        return redirect('/login.html')

    @app.route('/uploads/plant_images/<path:filename>')
    def serve_plant_image(filename):
        """Serve uploaded plant images"""
        import os
        from flask import send_from_directory

        upload_folder = os.path.join(os.getcwd(), 'uploads', 'plant_images')
        return send_from_directory(upload_folder, filename)
    
    @app.route('/login.html')
    def login_page():
        """Login page"""
        # Redirect if already logged in - go directly to appropriate page
        if 'user_id' in session:
            account_type = session.get('account_type', 'user')
            if account_type == 'admin':
                return redirect('/analytics.html')
            else:
                return redirect('/chatbot.html')

        return render_template('login.html')
    
    @app.route('/chatbot.html')
    def chatbot_page():
        """Chatbot interface for regular users"""
        if 'user_id' not in session:
            return redirect('/login.html')
        
        if session.get('account_type') == 'admin':
            return redirect('/analytics.html')
        
        return render_template('chatbot.html')
    
    @app.route('/analytics.html')
    def analytics_page():
        """Analytics dashboard for admins"""
        if 'user_id' not in session:
            return redirect('/login.html')
        
        if session.get('account_type') != 'admin':
            return redirect('/chatbot.html')
        
        return render_template('analytics.html')
    
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0'
        }

def create_agribot_engine(config, logger):
    """Create AgriBot engine with proper dependency injection"""
    try:
        # Initialize knowledge base
        logger.info("Loading agricultural knowledge base...")
        knowledge_base = AgriculturalKnowledgeBase()
        
        # Initialize NLP processor
        logger.info("Initializing NLP processor...")
        nlp_processor = NLPProcessor()
        
        # Initialize data coordinator with API config
        logger.info("Setting up data coordinator...")
        data_coordinator = DataCoordinator(config.apis)
        
        # Create main engine
        logger.info("Creating AgriBot engine...")
        engine = AgriBotEngine(knowledge_base, nlp_processor, data_coordinator, config)
        
        logger.info("AgriBot engine created successfully")
        return engine
        
    except Exception as e:
        logger.error(f"Failed to create AgriBot engine: {str(e)}")
        raise

def register_error_handlers(app):
    """Register global error handlers"""
    
    @app.errorhandler(AgriBotException)
    def handle_agribot_exception(e):
        """Handle AgriBot-specific exceptions"""
        app.logger.error(f"AgriBot exception: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'error_type': 'agribot_error'
        }, 500
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 errors"""
        return {
            'success': False,
            'error': 'Bad request'
        }, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 errors"""
        return {
            'success': False,
            'error': 'Authentication required'
        }, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 errors"""
        return {
            'success': False,
            'error': 'Access forbidden'
        }, 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        # For HTML requests, redirect to login
        if request.accept_mimetypes.accept_html:
            return redirect('/login.html')
        
        return {
            'success': False,
            'error': 'Endpoint not found'
        }, 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors"""
        return {
            'success': False,
            'error': 'Method not allowed'
        }, 405
    
    @app.errorhandler(422)
    def validation_error(error):
        """Handle validation errors"""
        return {
            'success': False,
            'error': 'Validation failed'
        }, 422
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle rate limiting"""
        return {
            'success': False,
            'error': 'Rate limit exceeded'
        }, 429
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        import traceback
        app.logger.error(f"Internal server error: {str(error)}")
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        if app.debug:
            return {
                'success': False,
                'error': 'Internal server error',
                'details': str(error),
                'traceback': traceback.format_exc()
            }, 500
        return {
            'success': False,
            'error': 'Internal server error'
        }, 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle service unavailable"""
        return {
            'success': False,
            'error': 'Service temporarily unavailable'
        }, 503

def register_request_handlers(app):
    """Register request lifecycle handlers"""
    
    @app.before_request
    def before_request():
        """Process before each request"""
        g.start_time = datetime.now()
        
        # Set user context if logged in
        if 'user_id' in session:
            g.user_id = session['user_id']
            g.account_type = session.get('account_type', 'user')
        else:
            g.user_id = None
            g.account_type = None
        
        # Log request info (excluding sensitive data)
        if not request.endpoint or 'static' not in request.endpoint:
            user_info = f"user:{g.user_id}" if g.user_id else "anonymous"
            app.logger.info(f"Request: {request.method} {request.path} [{user_info}]")
        
        # Security headers for all responses
        g.security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block'
        }
    
    @app.after_request
    def after_request(response):
        """Process after each request"""
        # Add security headers
        if hasattr(g, 'security_headers'):
            for header, value in g.security_headers.items():
                response.headers[header] = value
        
        # Log performance metrics
        if hasattr(g, 'start_time'):
            duration = datetime.now() - g.start_time
            duration_ms = duration.total_seconds() * 1000
            
            # Log response info
            if not request.endpoint or 'static' not in request.endpoint:
                app.logger.info(f"Response: {response.status_code} in {duration_ms:.2f}ms")
                
                # Log slow requests
                if duration_ms > 1000:
                    app.logger.warning(f"Slow request: {request.method} {request.path} took {duration_ms:.2f}ms")
        
        return response
    
    @app.teardown_appcontext
    def close_db(error):
        """Clean up after request"""
        # Database connections are handled by SQLAlchemy
        if error:
            app.logger.error(f"Request teardown error: {str(error)}")

def setup_session_config(app):
    """Configure session management"""
    app.config.update({
        'SESSION_COOKIE_SECURE': not app.debug,  # HTTPS only in production
        'SESSION_COOKIE_HTTPONLY': True,  # Prevent XSS
        'SESSION_COOKIE_SAMESITE': 'Lax',  # CSRF protection
        'PERMANENT_SESSION_LIFETIME': 86400,  # 24 hours
    })

# Create app instance for gunicorn
app = create_app()

# For development server
if __name__ == '__main__':
    # Use the existing app instance
    
    # Additional dev configuration
    if app.debug:
        setup_session_config(app)
        app.logger.info("Development server starting...")
        app.logger.info("Available routes:")
        for rule in app.url_map.iter_rules():
            app.logger.info(f"  {rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]")
    
    app.run(host='0.0.0.0', port=5000, debug=True)