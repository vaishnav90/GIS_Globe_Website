#!/usr/bin/env python3
"""
Test script to verify edit functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cloud_storage import cloud_storage

def test_edit_functionality():
    """Test that edit functionality is working."""
    print("Testing edit functionality...")
    
    # Test team member editing
    print("\n=== Testing Team Member Editing ===")
    team_members = cloud_storage.get_all_team_members()
    if team_members:
        test_member = team_members[0]
        member_id = test_member['id']
        original_description = test_member['description']
        
        print(f"Original description: {original_description}")
        
        # Try to update the description
        test_description = f"{original_description} [TEST UPDATE]"
        updated_member = cloud_storage.update_team_member(
            member_id=member_id,
            description=test_description
        )
        
        if updated_member:
            print(f"✓ Successfully updated team member description")
            print(f"New description: {updated_member['description']}")
            
            # Verify the change was saved
            reloaded_member = cloud_storage.get_team_member(member_id)
            if reloaded_member and reloaded_member['description'] == test_description:
                print(f"✓ Change verified in database")
            else:
                print(f"✗ Change not found in database")
        else:
            print(f"✗ Failed to update team member")
    
    # Test project editing
    print("\n=== Testing Project Editing ===")
    projects = cloud_storage.get_all_projects()
    if projects:
        test_project = projects[0]
        project_id = test_project['id']
        original_title = test_project['title']
        
        print(f"Original title: {original_title}")
        
        # Try to update the title
        test_title = f"{original_title} [TEST UPDATE]"
        updated_project = cloud_storage.update_project(
            project_id=project_id,
            title=test_title
        )
        
        if updated_project:
            print(f"✓ Successfully updated project title")
            print(f"New title: {updated_project['title']}")
            
            # Verify the change was saved
            reloaded_project = cloud_storage.get_project_by_id(project_id)
            if reloaded_project and reloaded_project['title'] == test_title:
                print(f"✓ Change verified in database")
            else:
                print(f"✗ Change not found in database")
        else:
            print(f"✗ Failed to update project")

if __name__ == "__main__":
    test_edit_functionality() 