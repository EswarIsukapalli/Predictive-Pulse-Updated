"""
WSGI entry point for production deployment (Render, Heroku, etc.)
"""
import os
import logging
from app import app, db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create all database tables on startup
try:
    logger.info(f"Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')[:50]}...")
    with app.app_context():
        logger.info("Creating database tables...")
        db.create_all()
        logger.info("Database tables created successfully!")
except Exception as e:
    logger.error(f"Error creating database tables: {e}", exc_info=True)
    raise

if __name__ == "__main__":
    app.run()
