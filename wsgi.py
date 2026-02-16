"""
WSGI entry point for production deployment (Render, Heroku, etc.)
"""
import os
from app import app, db

# Create all database tables on startup
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()
