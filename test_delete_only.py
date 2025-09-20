#!/usr/bin/env python3
"""
Test only the delete functionality
"""

import requests

def test_delete_functionality():
    """Test template deletion"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 Testing Delete Template Functionality")
    print("=" * 50)
    
    # Login
    login_data = {"username": "templateuser", "password": "password123"}
    response = requests.post(f"{base_url}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return False
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Get templates
    response = requests.get(f"{base_url}/signature/templates", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get templates: {response.status_code}")
        return False
    
    templates = response.json()["templates"]
    print(f"✅ Found {len(templates)} templates")
    
    if len(templates) == 0:
        print("ℹ️ No templates to delete")
        return True
    
    # Try to delete first template
    template_id = templates[0]['id']
    print(f"🗑️ Attempting to delete template ID: {template_id}")
    
    response = requests.delete(f"{base_url}/signature/templates/{template_id}", headers=headers)
    print(f"Delete response status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Template deleted successfully")
        
        # Verify deletion
        response = requests.get(f"{base_url}/signature/templates", headers=headers)
        if response.status_code == 200:
            remaining_templates = response.json()["templates"]
            remaining_ids = [t['id'] for t in remaining_templates]
            if template_id not in remaining_ids:
                print("✅ Template successfully removed from database")
                return True
            else:
                print("❌ Template still exists in database")
                return False
        else:
            print("❌ Failed to verify deletion")
            return False
    else:
        print(f"❌ Delete failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    success = test_delete_functionality()
    if success:
        print("\n🎉 Delete functionality is working correctly!")
    else:
        print("\n❌ Delete functionality has issues.")
