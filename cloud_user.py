#!/usr/bin/env python3
"""
Cloud User class for Flask-Login integration
"""

from flask_login import UserMixin
from cloud_storage import cloud_storage

class CloudUser(UserMixin):
    def __init__(self, user_data: dict):
        self.user_data = user_data
        self.id = user_data['id']
        self.username = user_data['username']
        self.email = user_data['email']
        self.first_name = user_data.get('first_name')
        self.last_name = user_data.get('last_name')
        self.created_at = user_data['created_at']
        self.last_login = user_data.get('last_login')
        self._is_active = user_data.get('is_active', True)
    
    def get_id(self):
        return self.id
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return self._is_active
    
    @property
    def is_anonymous(self):
        return False
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.user_data['password_hash'], password)
    
    @staticmethod
    def get(user_id):
        """Get user by ID for Flask-Login."""
        user_data = cloud_storage.get_user_by_id(user_id)
        if user_data:
            return CloudUser(user_data)
        return None
    
    @staticmethod
    def get_by_username(username):
        """Get user by username."""
        user_data = cloud_storage.get_user_by_username(username)
        if user_data:
            return CloudUser(user_data)
        return None
    
    @staticmethod
    def get_by_email(email):
        """Get user by email."""
        user_data = cloud_storage.get_user_by_email(email)
        if user_data:
            return CloudUser(user_data)
        return None
    
    def __repr__(self):
        return f'<CloudUser {self.username}>' 