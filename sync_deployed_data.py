#!/usr/bin/env python3
"""
Script to force sync deployed data with local data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cloud_storage import cloud_storage

def sync_deployed_data():
    """Force sync deployed data with local data."""
    print("🔄 Force Syncing Deployed Data...")
    
    # Get all team members from local environment
    print("\n=== Local Team Members ===")
    all_members = cloud_storage.get_all_team_members()
    print(f"Total team members: {len(all_members)}")
    
    for member in all_members:
        print(f"  - {member.get('name', 'Unknown')} (ID: {member.get('id', 'No ID')}) - Updated: {member.get('updated_at', 'No updated_at')}")
    
    # Force update each team member to ensure consistency
    print("\n=== Force Updating All Team Members ===")
    for member in all_members:
        member_id = member['id']
        print(f"\nUpdating {member['name']} (ID: {member_id})...")
        
        # Force update with current data
        updated = cloud_storage.update_team_member(
            member_id=member_id,
            name=member['name'],
            title=member['title'],
            description=member['description'],
            linkedin_url=member.get('linkedin_url', ''),
            member_type=member.get('member_type', 'board'),
            year=member.get('year', '')
        )
        
        if updated:
            print(f"✅ Successfully updated {member['name']}")
            print(f"   New updated_at: {updated.get('updated_at', 'No updated_at')}")
        else:
            print(f"❌ Failed to update {member['name']}")
    
    # Verify the sync
    print("\n=== Verifying Sync ===")
    verify_members = cloud_storage.get_all_team_members()
    print(f"Total team members after sync: {len(verify_members)}")
    
    for member in verify_members:
        print(f"  - {member.get('name', 'Unknown')} (ID: {member.get('id', 'No ID')}) - Updated: {member.get('updated_at', 'No updated_at')}")
    
    print("\n🎉 Sync Complete!")

if __name__ == "__main__":
    sync_deployed_data() 