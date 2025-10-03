"""
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
