#!/usr/bin/env python3
"""
Database initialization script for the Flask application.
This script creates all necessary database tables.
"""

from main import app, db
from models import User, ContactMessage

def init_database():
    """Initialize the database with all tables."""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
        
        # Create a test user if no users exist
        if not User.query.first():
            print("Creating a test user...")
            test_user = User(
                username='admin',
                email='admin@example.com',
                first_name='Admin',
                last_name='User'
            )
            test_user.set_password('password123')
            db.session.add(test_user)
            db.session.commit()
            print("Test user created: username='admin', password='password123'")
        else:
            print("Users already exist in the database.")

if __name__ == '__main__':
    init_database() 