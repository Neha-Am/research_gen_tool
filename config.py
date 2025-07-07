"""
Configuration file for the IEEE Conference Paper Generator Flask API
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # API Configuration
    API_TITLE = "IEEE Conference Paper Generator API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "A modular Flask API for generating IEEE conference paper content using Google's Gemini AI"
    
    # Google API Configuration
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    GEMINI_MODEL = "gemini-2.0-flash"
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size
    ALLOWED_EXTENSIONS = {'pdf'}
    UPLOAD_FOLDER = 'uploads'
    
    # PDF Processing Configuration
    MAX_PDF_PAGES = 50
    MAX_TEXT_LENGTH = 50000  # Maximum text length for processing
    
    # Content Generation Configuration
    MAX_TITLE_LENGTH = 200
    MAX_RESEARCH_FIELD_LENGTH = 1000
    MAX_METHODOLOGY_LENGTH = 2000
    MAX_EXPECTED_RESULTS_LENGTH = 2000
    MAX_CUSTOM_PARAMETERS = 20
    MAX_PARAMETER_VALUE_LENGTH = 500
    
    # Cost Estimation Configuration (Gemini 2.0 Flash pricing)
    INPUT_TOKEN_COST_PER_1M = 0.075  # USD per 1M input tokens
    OUTPUT_TOKEN_COST_PER_1M = 0.30  # USD per 1M output tokens
    ESTIMATED_INPUT_TOKENS_PER_CALL = 2000
    ESTIMATED_OUTPUT_TOKENS_PER_CALL = 1000
    
    # API Tracking Configuration
    TRACKER_FILE = 'api_call_tracker.json'
    MAX_CALL_HISTORY = 100  # Keep last 100 calls in history
    
    # Validation Configuration
    MIN_TITLE_LENGTH = 5
    MIN_RESEARCH_FIELD_LENGTH = 10
    MIN_METHODOLOGY_LENGTH = 10
    MIN_EXPECTED_RESULTS_LENGTH = 10
    MIN_AUTHOR_NAME_LENGTH = 2
    MAX_AUTHOR_NAME_LENGTH = 100
    MIN_INSTITUTION_LENGTH = 3
    MAX_INSTITUTION_LENGTH = 200
    
    # Security Configuration
    SUSPICIOUS_PATTERNS = [
        'hack', 'crack', 'illegal', 'unauthorized', 'malware', 'virus',
        'spam', 'phishing', 'fraud', 'scam', 'fake', 'counterfeit'
    ]
    DANGEROUS_CHARS = ['<script>', '</script>', 'javascript:', 'onload=', 'onerror=']
    
    # CORS Configuration
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]
    
    # Rate Limiting Configuration (if implemented)
    RATE_LIMIT_ENABLED = False
    RATE_LIMIT_REQUESTS = 100  # requests per hour
    RATE_LIMIT_WINDOW = timedelta(hours=1)
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    CORS_ORIGINS = ["*"]  # Allow all origins in development

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Add production-specific settings here
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to stderr in production
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    GOOGLE_API_KEY = 'test-api-key'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    config_name = os.environ.get('FLASK_CONFIG') or 'default'
    return config[config_name] 