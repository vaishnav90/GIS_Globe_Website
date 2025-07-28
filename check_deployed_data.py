#!/usr/bin/env python3
"""
Script to check deployed data and identify issues
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cloud_storage import cloud_storage

def check_deployed_data():
    """Check deployed data and identify issues."""
    print("🔍 Checking Deployed Data...")
    
    # Check all team members
    print("\n=== All Team Members ===")
    all_members = cloud_storage.get_all_team_members()
    print(f"Total team members: {len(all_members)}")
    
    for member in all_members:
        print(f"  - {member.get('name', 'Unknown')} (ID: {member.get('id', 'No ID')}) - Updated: {member.get('updated_at', 'No updated_at')}")
    
    # Check specific team member
    print("\n=== Checking Austin Ramsey ===")
    austin_members = [m for m in all_members if m.get('name') == 'Austin Ramsey']
    print(f"Found {len(austin_members)} Austin Ramsey entries:")
    
    for i, member in enumerate(austin_members):
        print(f"  {i+1}. ID: {member.get('id')}")
        print(f"     Updated: {member.get('updated_at', 'No updated_at')}")
        print(f"     Description: {member.get('description', 'No description')[:100]}...")
    
    # Test direct file access
    if austin_members:
        test_id = austin_members[0]['id']
        print(f"\n=== Direct File Access for {test_id} ===")
        
        # Load directly
        direct_load = cloud_storage.get_team_member(test_id)
        if direct_load:
            print(f"Direct load successful:")
            print(f"  Updated: {direct_load.get('updated_at', 'No updated_at')}")
            print(f"  Description: {direct_load.get('description', 'No description')[:100]}...")
        else:
            print("Direct load failed")
        
        # Test update
        print(f"\n=== Testing Update ===")
        test_description = f"{direct_load.get('description', '')} [DEPLOYED TEST]"
        updated = cloud_storage.update_team_member(
            member_id=test_id,
            description=test_description
        )
        
        if updated:
            print(f"Update successful:")
            print(f"  New updated_at: {updated.get('updated_at', 'No updated_at')}")
            print(f"  New description: {updated.get('description', 'No description')[:100]}...")
            
            # Verify the update
            print(f"\n=== Verifying Update ===")
            verify_load = cloud_storage.get_team_member(test_id)
            if verify_load:
                print(f"Verification successful:")
                print(f"  Updated: {verify_load.get('updated_at', 'No updated_at')}")
                print(f"  Description: {verify_load.get('description', 'No description')[:100]}...")
                
                if verify_load.get('updated_at') == updated.get('updated_at'):
                    print("✅ Update verified successfully")
                else:
                    print("❌ Update verification failed - timestamps don't match")
            else:
                print("❌ Verification failed - could not load updated data")
        else:
            print("❌ Update failed")

if __name__ == "__main__":
    check_deployed_data() 