"""
Configuration package for the universal sacred text platform.
"""
import os

class Config:
    """Application configuration."""
    
    # Flask settings
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = FLASK_ENV == 'development'
    
    # CORS settings
    CORS_ORIGINS = [
        'http://localhost:5173', 
        'http://localhost:3000',
        'http://localhost:5001'
    ]
    
    # Data paths
    # Default to local path for development, Docker path if DATA_PATH is set
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DEFAULT_DATA_PATH = os.path.join(PROJECT_ROOT, '..', 'data')  # Go up one level from api/
    DATA_BASE_PATH = os.getenv('DATA_PATH', DEFAULT_DATA_PATH)
    SLOKAS_PATH = os.path.join(DATA_BASE_PATH, 'slokas', 'Slokas')
    
    # Search settings
    DEFAULT_FUZZY_THRESHOLD = 70
    DEFAULT_MIN_RATIO = 0
    MAX_SEARCH_RESULTS = 1000  # Increased for better search results
    
    # Pagination settings
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 50
    STREAM_BATCH_SIZE = 5
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')