#!/usr/bin/env python3
"""
Script to clean up duplicate team members from the database
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cloud_storage import cloud_storage

def cleanup_duplicate_team_members():
    """Remove duplicate team members, keeping only the most recent version of each person."""
    print("Cleaning up duplicate team members...")
    
    # Get all team members
    all_members = cloud_storage.get_all_team_members()
    print(f"Found {len(all_members)} total team members")
    
    # Group by name
    members_by_name = {}
    for member in all_members:
        name = member.get('name', 'Unknown')
        if name not in members_by_name:
            members_by_name[name] = []
        members_by_name[name].append(member)
    
    # Find duplicates and keep the most recent
    duplicates_to_delete = []
    for name, members in members_by_name.items():
        if len(members) > 1:
            print(f"Found {len(members)} duplicates for {name}")
            
            # Sort by updated_at (most recent first)
            members.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            
            # Keep the first (most recent) one, delete the rest
            keep_member = members[0]
            delete_members = members[1:]
            
            print(f"  Keeping: {keep_member.get('id')} (updated: {keep_member.get('updated_at')})")
            for delete_member in delete_members:
                print(f"  Deleting: {delete_member.get('id')} (updated: {delete_member.get('updated_at')})")
                duplicates_to_delete.append(delete_member.get('id'))
    
    # Delete the duplicates
    if duplicates_to_delete:
        print(f"\nDeleting {len(duplicates_to_delete)} duplicate team members...")
        for member_id in duplicates_to_delete:
            try:
                cloud_storage.delete_team_member(member_id)
                print(f"✓ Deleted: {member_id}")
            except Exception as e:
                print(f"✗ Failed to delete {member_id}: {str(e)}")
        
        print(f"\nCleanup complete! Deleted {len(duplicates_to_delete)} duplicate team members.")
    else:
        print("No duplicates found!")

if __name__ == "__main__":
    cleanup_duplicate_team_members() 