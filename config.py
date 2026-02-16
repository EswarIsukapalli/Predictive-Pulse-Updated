import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration - use PostgreSQL on production, SQLite locally
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Fix for SQLAlchemy 1.4+ compatibility with PostgreSQL
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///predictive_pulse.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = 86400 * 7  # 7 days

