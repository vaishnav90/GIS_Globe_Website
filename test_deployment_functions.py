#!/usr/bin/env python3
"""
Test script to verify cloud storage functions work correctly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cloud_storage import cloud_storage

def test_cloud_storage_functions():
    """Test various cloud storage functions."""
    print("Testing cloud storage functions...")
    
    # Test team members
    print("\n=== Testing Team Members ===")
    team_members = cloud_storage.get_all_team_members()
    print(f"Found {len(team_members)} team members")
    for member in team_members:
        print(f"  - {member.get('name', 'Unknown')} (ID: {member.get('id', 'No ID')})")
    
    # Test projects
    print("\n=== Testing Projects ===")
    projects = cloud_storage.get_all_projects()
    print(f"Found {len(projects)} projects")
    for project in projects:
        print(f"  - {project.get('title', 'Unknown')} (ID: {project.get('id', 'No ID')})")
        print(f"    Image URL: {project.get('image_url', 'None')}")
    
    # Test gallery items
    print("\n=== Testing Gallery Items ===")
    gallery_items = cloud_storage.get_all_gallery_items()
    print(f"Found {len(gallery_items)} gallery items")
    for item in gallery_items:
        print(f"  - {item.get('title', 'Unknown')} (ID: {item.get('id', 'No ID')})")
    
    # Test file operations
    print("\n=== Testing File Operations ===")
    test_data = {"test": "data", "timestamp": "2025-07-27"}
    test_path = "test/test_file.json"
    
    try:
        # Test save
        print("Testing save operation...")
        cloud_storage._save_json(test_path, test_data)
        print("✓ Save operation successful")
        
        # Test load
        print("Testing load operation...")
        loaded_data = cloud_storage._load_json(test_path)
        if loaded_data == test_data:
            print("✓ Load operation successful")
        else:
            print("✗ Load operation failed - data mismatch")
        
        # Test delete
        print("Testing delete operation...")
        delete_result = cloud_storage._delete_file(test_path)
        if delete_result:
            print("✓ Delete operation successful")
        else:
            print("✗ Delete operation failed")
            
    except Exception as e:
        print(f"✗ File operation test failed: {str(e)}")

if __name__ == "__main__":
    test_cloud_storage_functions() 