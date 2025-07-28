#!/usr/bin/env python3
"""
Test script to check project image URLs
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cloud_storage import cloud_storage
import requests

def test_image_urls():
    """Test if project image URLs are accessible."""
    print("Testing project image URLs...")
    
    projects = cloud_storage.get_all_projects()
    print(f"Found {len(projects)} projects")
    
    for project in projects:
        title = project.get('title', 'Unknown')
        image_url = project.get('image_url', '')
        
        print(f"\nProject: {title}")
        print(f"Image URL: {image_url}")
        
        if image_url:
            try:
                response = requests.head(image_url, timeout=10)
                if response.status_code == 200:
                    print(f"✓ Image URL is accessible (Status: {response.status_code})")
                else:
                    print(f"✗ Image URL returned status: {response.status_code}")
            except Exception as e:
                print(f"✗ Error accessing image URL: {str(e)}")
        else:
            print("✗ No image URL provided")

if __name__ == "__main__":
    test_image_urls() 