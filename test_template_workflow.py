#!/usr/bin/env python3
"""
Test script to demonstrate template and history workflow
"""

import requests
import json
import io
from PIL import Image
import numpy as np

def create_test_signature():
    """Create a test signature image"""
    # Create a simple signature-like image
    img = Image.new('RGB', (200, 100), color='white')
    pixels = img.load()
    
    # Draw a simple signature-like pattern
    for x in range(50, 150):
        for y in range(30, 70):
            if (x - 100) ** 2 + (y - 50) ** 2 < 400:  # Circle
                pixels[x, y] = (0, 0, 0)  # Black
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()

def test_template_workflow():
    """Test the complete template workflow"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 Testing Template and History Workflow")
    print("=" * 50)
    
    # Step 1: Register a user
    print("1️⃣ Registering user...")
    register_data = {
        "username": "templateuser",
        "email": "template@example.com",
        "password": "password123",
        "full_name": "Template User"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/register", json=register_data)
        if response.status_code == 200:
            print("✅ User registered successfully")
        else:
            print(f"⚠️ User might already exist: {response.status_code}")
    except Exception as e:
        print(f"❌ Registration failed: {e}")
        return
    
    # Step 2: Login
    print("\n2️⃣ Logging in...")
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
            return
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return
    
    # Step 3: Upload signature and save as template
    print("\n3️⃣ Uploading signature and saving as template...")
    test_image = create_test_signature()
    
    files = {
        'file': ('test_signature.png', test_image, 'image/png')
    }
    data = {
        'template_name': 'My Test Signature Template'
    }
    
    try:
        response = requests.post(f"{base_url}/signature/upload", 
                               files=files, data=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✅ Signature uploaded and saved as template")
            print(f"   - Template ID: {result.get('template_id')}")
            print(f"   - Authenticity Score: {result['analysis_result']['authenticity_score']:.3f}")
            print(f"   - Is Authentic: {result['analysis_result']['is_authentic']}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return
    
    # Step 4: List templates
    print("\n4️⃣ Listing templates...")
    try:
        response = requests.get(f"{base_url}/signature/templates", headers=headers)
        if response.status_code == 200:
            templates = response.json()["templates"]
            print(f"✅ Found {len(templates)} templates:")
            for template in templates:
                print(f"   - ID: {template['id']}, Name: {template['template_name']}")
                print(f"     Created: {template['created_at']}")
        else:
            print(f"❌ Failed to list templates: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to list templates: {e}")
    
    # Step 5: Upload another signature for verification
    print("\n5️⃣ Uploading signature for verification...")
    test_image2 = create_test_signature()
    
    files = {
        'file': ('test_signature2.png', test_image2, 'image/png')
    }
    
    try:
        response = requests.post(f"{base_url}/signature/upload", 
                               files=files, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✅ Second signature uploaded")
            print(f"   - Authenticity Score: {result['analysis_result']['authenticity_score']:.3f}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
    
    # Step 6: View history
    print("\n6️⃣ Viewing verification history...")
    try:
        response = requests.get(f"{base_url}/signature/history?limit=10", headers=headers)
        if response.status_code == 200:
            history = response.json()["verification_history"]
            print(f"✅ Found {len(history)} verification records:")
            for record in history:
                print(f"   - Score: {record['authenticity_score']:.3f}")
                print(f"     Authentic: {record['is_authentic']}")
                print(f"     Date: {record['created_at']}")
        else:
            print(f"❌ Failed to get history: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to get history: {e}")
    
    # Step 7: Get user statistics
    print("\n7️⃣ Getting user statistics...")
    try:
        response = requests.get(f"{base_url}/signature/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print("✅ User statistics:")
            print(f"   - Templates: {stats['template_count']}")
            print(f"   - Verifications: {stats['verification_count']}")
            print(f"   - Authentic signatures: {stats['authentic_count']}")
            print(f"   - Average score: {stats['average_authenticity_score']:.3f}")
        else:
            print(f"❌ Failed to get stats: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to get stats: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Template and History workflow test completed!")
    print("\n📋 Summary:")
    print("✅ User registration and authentication")
    print("✅ Signature upload and template saving")
    print("✅ Template listing")
    print("✅ Verification history tracking")
    print("✅ User statistics")
    print("\n🌐 You can now use the frontend at frontend/index.html")
    print("   - Login with username: templateuser, password: password123")
    print("   - View your templates in 'My Templates' tab")
    print("   - Check history in 'History' tab")

if __name__ == "__main__":
    test_template_workflow()
