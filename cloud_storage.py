#!/usr/bin/env python3
"""
Cloud Storage Manager for National 4-H GIS Leadership Team Website
Handles all data storage using Google Cloud Storage buckets
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from google.cloud import storage
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class CloudStorageManager:
    def __init__(self, bucket_name: str = None):
        """Initialize cloud storage manager."""
        self.bucket_name = bucket_name or os.environ.get('STORAGE_BUCKET', 'national-4h-gis-team-data')
        
        # Initialize storage client with authentication
        try:
            # For local development, use service account key if available
            if os.path.exists('service-account-key.json'):
                self.client = storage.Client.from_service_account_json('service-account-key.json')
            else:
                # For production (App Engine), use default credentials
                self.client = storage.Client()
            
            self.bucket = self.client.bucket(self.bucket_name)
            
            # Ensure bucket exists
            if not self.bucket.exists():
                self.bucket.create()
                print(f"Created bucket: {self.bucket_name}")
                
        except Exception as e:
            print(f"Error initializing cloud storage: {e}")
            print("Make sure you have:")
            print("1. Google Cloud SDK installed and authenticated")
            print("2. Service account key file (service-account-key.json) for local development")
            print("3. Proper permissions for the storage bucket")
            raise
    
    def _get_blob(self, path: str):
        """Get a blob from the bucket."""
        return self.bucket.blob(path)
    
    def _save_json(self, path: str, data: Dict):
        """Save JSON data to cloud storage."""
        blob = self._get_blob(path)
        blob.upload_from_string(
            json.dumps(data, default=str),
            content_type='application/json'
        )
    
    def _load_json(self, path: str) -> Optional[Dict]:
        """Load JSON data from cloud storage."""
        try:
            blob = self._get_blob(path)
            if blob.exists():
                return json.loads(blob.download_as_text())
            else:
                print(f"File {path} does not exist")
                return None
        except Exception as e:
            print(f"Error loading JSON from {path}: {str(e)}")
            return None
    
    def _list_files(self, prefix: str) -> List[str]:
        """List files with a specific prefix."""
        blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)
        return [blob.name for blob in blobs]
    
    def _delete_file(self, path: str):
        """Delete a file from cloud storage."""
        try:
            blob = self._get_blob(path)
            if blob.exists():
                blob.delete()
                return True
            else:
                print(f"File {path} does not exist")
                return False
        except Exception as e:
            print(f"Error deleting file {path}: {str(e)}")
            return False
    
    # User Management
    def create_user(self, username: str, email: str, password: str, first_name: str = None, last_name: str = None) -> Dict:
        """Create a new user."""
        user_id = str(uuid.uuid4())
        user_data = {
            'id': user_id,
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'first_name': first_name,
            'last_name': last_name,
            'created_at': datetime.utcnow().isoformat(),
            'last_login': None,
            'is_active': True
        }
        
        # Check if username or email already exists
        if self.get_user_by_username(username):
            raise ValueError('Username already exists')
        if self.get_user_by_email(email):
            raise ValueError('Email already exists')
        
        self._save_json(f'users/{user_id}.json', user_data)
        return user_data
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        return self._load_json(f'users/{user_id}.json')
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username."""
        users = self._list_files('users/')
        for user_file in users:
            user_data = self._load_json(user_file)
            if user_data and user_data.get('username') == username:
                return user_data
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        users = self._list_files('users/')
        for user_file in users:
            user_data = self._load_json(user_file)
            if user_data and user_data.get('email') == email:
                return user_data
        return None
    
    def update_user_login(self, user_id: str):
        """Update user's last login time."""
        user_data = self.get_user_by_id(user_id)
        if user_data:
            user_data['last_login'] = datetime.utcnow().isoformat()
            self._save_json(f'users/{user_id}.json', user_data)
    
    def get_all_users(self) -> List[Dict]:
        """Get all users."""
        users = []
        user_files = self._list_files('users/')
        for user_file in user_files:
            user_data = self._load_json(user_file)
            if user_data:
                users.append(user_data)
        return users
    
    # Project Management
    def create_project(self, title: str, creator_name: str, description: str, project_link: str, project_type: str, 
                      tags: str, image_url: str, created_by: str) -> Dict:
        """Create a new project."""
        project_id = str(uuid.uuid4())
        project_data = {
            'id': project_id,
            'title': title,
            'creator_name': creator_name,
            'description': description,
            'project_link': project_link,
            'project_type': project_type,
            'tags': tags,
            'image_url': image_url,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'created_by': created_by,
            'is_active': True
        }
        
        self._save_json(f'projects/{project_id}.json', project_data)
        return project_data
    
    def get_project_by_id(self, project_id: str) -> Optional[Dict]:
        """Get project by ID."""
        return self._load_json(f'projects/{project_id}.json')
    
    def get_all_projects(self) -> List[Dict]:
        """Get all active projects."""
        projects = []
        project_files = self._list_files('projects/')
        print(f"Found {len(project_files)} project files: {project_files}")
        
        for project_file in project_files:
            project_data = self._load_json(project_file)
            if project_data and project_data.get('is_active', True):
                print(f"Loaded project from {project_file}: {project_data.get('title', 'Unknown')} - Image: {project_data.get('image_url', 'None')}")
                projects.append(project_data)
            else:
                print(f"Failed to load project from {project_file}")
        
        print(f"Total projects loaded: {len(projects)}")
        return sorted(projects, key=lambda x: x['created_at'], reverse=True)
    
    def update_project(self, project_id: str, **kwargs) -> Optional[Dict]:
        """Update a project."""
        print(f"Updating project {project_id} with kwargs: {kwargs}")
        
        project_data = self.get_project_by_id(project_id)
        if not project_data:
            print(f"Project {project_id} not found")
            return None
        
        print(f"Original project data: {project_data}")
        
        # Update fields
        for key, value in kwargs.items():
            if value is not None:
                project_data[key] = value
                print(f"Updated {key}: {value}")
        
        project_data['updated_at'] = datetime.utcnow().isoformat()
        
        print(f"Final project data: {project_data}")
        
        try:
            self._save_json(f'projects/{project_id}.json', project_data)
            print(f"Successfully saved project {project_id}")
            return project_data
        except Exception as e:
            print(f"Error saving project {project_id}: {str(e)}")
            return None
    
    def delete_project(self, project_id: str):
        """Hard delete a project."""
        try:
            # Delete the file from cloud storage
            delete_result = self._delete_file(f'projects/{project_id}.json')
            if delete_result:
                print(f"Successfully deleted project file: {project_id}")
                return True
            else:
                print(f"Failed to delete project file: {project_id}")
                return False
        except Exception as e:
            print(f"Error deleting project {project_id}: {str(e)}")
            return False
    
    # Gallery Management
    def create_gallery_item(self, title: str, description: str, image_url: str, created_by: str) -> Dict:
        """Create a new gallery item."""
        item_id = str(uuid.uuid4())
        item_data = {
            'id': item_id,
            'title': title,
            'description': description,
            'image_url': image_url,
            'created_at': datetime.utcnow().isoformat(),
            'created_by': created_by,
            'is_active': True
        }
        
        self._save_json(f'gallery/{item_id}.json', item_data)
        return item_data
    
    def get_gallery_item_by_id(self, item_id: str) -> Optional[Dict]:
        """Get gallery item by ID."""
        return self._load_json(f'gallery/{item_id}.json')
    
    def get_all_gallery_items(self) -> List[Dict]:
        """Get all active gallery items."""
        items = []
        item_files = self._list_files('gallery/')
        for item_file in item_files:
            item_data = self._load_json(item_file)
            if item_data and item_data.get('is_active', True):
                items.append(item_data)
        return sorted(items, key=lambda x: x['created_at'], reverse=True)
    
    def delete_gallery_item(self, item_id: str):
        """Hard delete a gallery item."""
        try:
            # Delete the file from cloud storage
            delete_result = self._delete_file(f'gallery/{item_id}.json')
            if delete_result:
                print(f"Successfully deleted gallery item file: {item_id}")
                return True
            else:
                print(f"Failed to delete gallery item file: {item_id}")
                return False
        except Exception as e:
            print(f"Error deleting gallery item {item_id}: {str(e)}")
            return False
    
    def update_gallery_item(self, item_id: str, **kwargs) -> Optional[Dict]:
        """Update a gallery item."""
        item_data = self.get_gallery_item_by_id(item_id)
        if item_data:
            # Update provided fields
            for key, value in kwargs.items():
                if key in ['title', 'description', 'image_url']:
                    item_data[key] = value
            
            # Update timestamp
            item_data['updated_at'] = datetime.utcnow().isoformat()
            
            self._save_json(f'gallery/{item_id}.json', item_data)
            return item_data
        return None
    
    # Contact Message Management
    def create_contact_message(self, name: str, email: str, subject: str, message: str, user_id: str = None) -> Dict:
        """Create a new contact message."""
        message_id = str(uuid.uuid4())
        message_data = {
            'id': message_id,
            'name': name,
            'email': email,
            'subject': subject,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id
        }
        
        self._save_json(f'contact_messages/{message_id}.json', message_data)
        return message_data
    
    def get_all_contact_messages(self) -> List[Dict]:
        """Get all contact messages."""
        messages = []
        message_files = self._list_files('contact_messages/')
        for message_file in message_files:
            message_data = self._load_json(message_file)
            if message_data:
                messages.append(message_data)
        return sorted(messages, key=lambda x: x['timestamp'], reverse=True)
    
    # File Upload Management
    def upload_file(self, file_data, filename: str, folder: str = 'uploads') -> str:
        """Upload a file to cloud storage and return the URL."""
        try:
            # Create unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            file_path = f"{folder}/{unique_filename}"
            
            print(f"Uploading file: {filename} to path: {file_path}")
            
            # Upload file
            blob = self._get_blob(file_path)
            blob.upload_from_file(file_data)
            
            print(f"File uploaded successfully to blob: {blob.name}")
            
            # Make public and return URL
            blob.make_public()
            public_url = blob.public_url
            
            print(f"File made public. URL: {public_url}")
            return public_url
            
        except Exception as e:
            print(f"Error uploading file {filename}: {str(e)}")
            return None
    
    # Authentication
    def authenticate_user(self, username_or_email: str, password: str) -> Optional[Dict]:
        """Authenticate a user."""
        # Try username first
        user = self.get_user_by_username(username_or_email)
        if not user:
            # Try email
            user = self.get_user_by_email(username_or_email)
        
        if user and check_password_hash(user['password_hash'], password):
            if user.get('is_active', True):
                self.update_user_login(user['id'])
                return user
        return None

    # Team Member Management
    def create_team_member(self, name: str, title: str, description: str, linkedin_url: str = None, 
                          member_type: str = 'board', year: str = None, created_by: str = None) -> Dict:
        """Create a new team member."""
        member_id = str(uuid.uuid4())
        member_data = {
            'id': member_id,
            'name': name,
            'title': title,
            'description': description,
            'linkedin_url': linkedin_url,
            'member_type': member_type,  # 'board' or 'alumni'
            'year': year,
            'created_by': created_by,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        self._save_json(f'team_members/{member_id}.json', member_data)
        return member_data
    
    def get_team_member(self, member_id: str) -> Optional[Dict]:
        """Get team member by ID."""
        file_path = f'team_members/{member_id}.json'
        print(f"Loading team member from: {file_path}")
        member_data = self._load_json(file_path)
        if member_data:
            print(f"Loaded team member: {member_data.get('name', 'Unknown')} with updated_at: {member_data.get('updated_at', 'No updated_at')}")
        else:
            print(f"No team member data found at: {file_path}")
        return member_data
    
    def get_all_team_members(self) -> List[Dict]:
        """Get all team members."""
        team_members = []
        files = self._list_files('team_members/')
        print(f"Found {len(files)} team member files: {files}")
        
        for file_path in files:
            if file_path.endswith('.json'):
                member_data = self._load_json(file_path)
                if member_data:
                    print(f"Loaded team member from {file_path}: {member_data.get('name', 'Unknown')}")
                    team_members.append(member_data)
                else:
                    print(f"Failed to load team member from {file_path}")
        
        print(f"Total team members loaded: {len(team_members)}")
        # Sort by member type (board first) and then by name
        team_members.sort(key=lambda x: (x.get('member_type', 'board') != 'board', x.get('name', '')))
        return team_members
    
    def update_team_member(self, member_id: str, **kwargs) -> Optional[Dict]:
        """Update a team member."""
        print(f"Updating team member {member_id} with kwargs: {kwargs}")
        
        member_data = self.get_team_member(member_id)
        if not member_data:
            print(f"Team member {member_id} not found")
            return None
        
        print(f"Original member data: {member_data}")
        
        # Update fields
        for key, value in kwargs.items():
            if value is not None:
                member_data[key] = value
                print(f"Updated {key}: {value}")
        
        member_data['updated_at'] = datetime.utcnow().isoformat()
        
        print(f"Final member data: {member_data}")
        
        try:
            self._save_json(f'team_members/{member_id}.json', member_data)
            print(f"Successfully saved team member {member_id}")
            return member_data
        except Exception as e:
            print(f"Error saving team member {member_id}: {str(e)}")
            return None
    
    def delete_team_member(self, member_id: str):
        """Delete a team member."""
        try:
            # Delete the file from cloud storage
            delete_result = self._delete_file(f'team_members/{member_id}.json')
            if delete_result:
                print(f"Successfully deleted team member file: {member_id}")
                return True
            else:
                print(f"Failed to delete team member file: {member_id}")
                return False
        except Exception as e:
            print(f"Error deleting team member {member_id}: {str(e)}")
            return False

# Global instance
cloud_storage = CloudStorageManager() 