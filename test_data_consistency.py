#!/usr/bin/env python3
"""
Test script to check data consistency and identify issues
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from cloud_storage import cloud_storage

def test_data_consistency():
    """Test data consistency and identify issues."""
    print("🔍 Testing Data Consistency...")
    
    # Test 1: Check for duplicate team member files
    print("\n=== Test 1: Check for Duplicate Files ===")
    all_members = cloud_storage.get_all_team_members()
    
    # Group by name to find duplicates
    members_by_name = {}
    for member in all_members:
        name = member.get('name', 'Unknown')
        if name not in members_by_name:
            members_by_name[name] = []
        members_by_name[name].append(member)
    
    duplicates_found = False
    for name, members in members_by_name.items():
        if len(members) > 1:
            duplicates_found = True
            print(f"❌ Found {len(members)} duplicates for: {name}")
            for i, member in enumerate(members):
                print(f"  {i+1}. ID: {member.get('id')} - Updated: {member.get('updated_at', 'No updated_at')}")
    
    if not duplicates_found:
        print("✅ No duplicate team members found")
    
    # Test 2: Check specific team member data consistency
    print("\n=== Test 2: Data Consistency Check ===")
    if all_members:
        test_member = all_members[0]
        member_id = test_member['id']
        
        print(f"Testing member: {test_member['name']} (ID: {member_id})")
        print(f"Current data updated_at: {test_member.get('updated_at', 'No updated_at')}")
        
        # Load the same member directly
        direct_load = cloud_storage.get_team_member(member_id)
        if direct_load:
            print(f"Direct load updated_at: {direct_load.get('updated_at', 'No updated_at')}")
            
            if direct_load.get('updated_at') == test_member.get('updated_at'):
                print("✅ Data consistency verified")
            else:
                print("❌ Data inconsistency detected!")
                print(f"  All members load: {test_member.get('updated_at')}")
                print(f"  Direct load: {direct_load.get('updated_at')}")
        else:
            print("❌ Could not load member directly")
    
    # Test 3: Check file listing vs actual data
    print("\n=== Test 3: File Listing Check ===")
    files = cloud_storage._list_files('team_members/')
    print(f"Files found: {len(files)}")
    for file_path in files:
        print(f"  - {file_path}")
    
    # Test 4: Verify each file can be loaded
    print("\n=== Test 4: File Loading Verification ===")
    for file_path in files:
        if file_path.endswith('.json'):
            data = cloud_storage._load_json(file_path)
            if data:
                print(f"✅ {file_path}: {data.get('name', 'Unknown')} - {data.get('updated_at', 'No updated_at')}")
            else:
                print(f"❌ {file_path}: Failed to load")

if __name__ == "__main__":
    test_data_consistency() 