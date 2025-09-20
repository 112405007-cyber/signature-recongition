#!/usr/bin/env python3
"""
Test script to verify the authentication fix
"""

import requests

def test_auth_flow():
    """Test the complete authentication flow"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 Testing Authentication Fix")
    print("=" * 40)
    
    # Test 1: Login with existing user
    print("1️⃣ Testing login with existing user...")
    login_data = {
        "username": "templateuser",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False
    
    # Test 2: Access templates with authentication
    print("\n2️⃣ Testing authenticated template access...")
    try:
        response = requests.get(f"{base_url}/signature/templates", headers=headers)
        if response.status_code == 200:
            templates = response.json()["templates"]
            print(f"✅ Templates accessed successfully: {len(templates)} templates found")
        else:
            print(f"❌ Template access failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Template access failed: {e}")
        return False
    
    # Test 3: Access history with authentication
    print("\n3️⃣ Testing authenticated history access...")
    try:
        response = requests.get(f"{base_url}/signature/history?limit=10", headers=headers)
        if response.status_code == 200:
            history = response.json()["verification_history"]
            print(f"✅ History accessed successfully: {len(history)} records found")
        else:
            print(f"❌ History access failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ History access failed: {e}")
        return False
    
    # Test 4: Test without authentication (should fail)
    print("\n4️⃣ Testing unauthenticated access (should fail)...")
    try:
        response = requests.get(f"{base_url}/signature/templates")
        if response.status_code == 401:
            print("✅ Unauthenticated access correctly rejected")
        else:
            print(f"❌ Unauthenticated access should have failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("🎉 Authentication fix is working correctly!")
    print("\n📋 Summary:")
    print("✅ Login functionality working")
    print("✅ Authenticated API access working")
    print("✅ Unauthenticated access properly blocked")
    print("✅ Templates and history accessible with auth")
    
    print("\n🌐 Frontend Instructions:")
    print("1. Open frontend/index.html in your browser")
    print("2. You'll see a login form")
    print("3. Use credentials: templateuser / password123")
    print("4. After login, 'Analyze Signature' button will work!")
    
    return True

if __name__ == "__main__":
    success = test_auth_flow()
    if success:
        print("\n✅ All tests passed! The 'Analyze Signature' button should now work.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
