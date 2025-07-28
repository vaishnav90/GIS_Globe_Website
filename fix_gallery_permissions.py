#!/usr/bin/env python3
"""
Script to fix gallery permissions and recreate sample items.
"""

from main_cloud import app
from cloud_storage import cloud_storage
from datetime import datetime

def fix_gallery_permissions():
    """Fix gallery permissions and recreate sample items."""
    with app.app_context():
        # Get all users
        users = cloud_storage.get_all_users()
        if not users:
            print("No users found in database. Please create a user first.")
            return
        
        # Delete all existing gallery items
        existing_items = cloud_storage.get_all_gallery_items()
        for item in existing_items:
            cloud_storage.delete_gallery_item(item['id'])
        print(f"Deleted {len(existing_items)} existing gallery items.")
        
        # Get the first user to create items with
        user = users[0]
        
        # Sample gallery items data
        sample_items = [
            {
                'title': 'GIS Strategy Session',
                'description': 'Team meeting discussing GIS strategies and project planning',
                'image_url': 'https://i.scdn.co/image/ab67616d0000b273ea7caaff71dea1051d49b2fe',
                'created_at': datetime(2025, 1, 15)
            },
            {
                'title': 'Data Collection',
                'description': 'Field Work - Team members conducting field data collection for GIS projects',
                'image_url': 'https://i.scdn.co/image/ab67616d0000b273dc30583ba717007b00cceb25',
                'created_at': datetime(2025, 1, 20)
            },
            {
                'title': 'GIS Training Workshop',
                'description': 'Technical training session on GIS software and tools',
                'image_url': 'https://i.scdn.co/image/ab67616d0000b27305ac3e026324594a31fad7fb',
                'created_at': datetime(2025, 2, 5)
            },
            {
                'title': 'Project Presentation',
                'description': 'Final project deliverables presentation to stakeholders',
                'image_url': 'https://i.scdn.co/image/ab67616d0000b273c5649add07ed3720be9d5526',
                'created_at': datetime(2025, 2, 10)
            },
            {
                'title': 'Team Building Activities',
                'description': 'Collaborative team building exercises and activities',
                'image_url': 'https://i.scdn.co/image/ab67616d0000b273d9194aa18fa4c9362b47464f',
                'created_at': datetime(2025, 2, 15)
            },
            {
                'title': 'Spatial Data Processing',
                'description': 'GIS analysis and spatial data processing workflow',
                'image_url': 'https://i.scdn.co/image/ab67616d0000b273c7ea04a9b455e3f68ef82550',
                'created_at': datetime(2025, 2, 20)
            }
        ]
        
        # Add sample gallery items with proper user association
        for item_data in sample_items:
            cloud_storage.create_gallery_item(
                title=item_data['title'],
                description=item_data['description'],
                image_url=item_data['image_url'],
                created_by=user['id']
            )
        
        print(f"Successfully added {len(sample_items)} sample gallery items with proper user association!")
        print(f"User ID used: {user['id']}")
        print(f"User email: {user['email']}")

if __name__ == '__main__':
    fix_gallery_permissions() 