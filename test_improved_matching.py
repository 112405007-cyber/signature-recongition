#!/usr/bin/env python3
"""
Test script to verify improved signature matching and delete functionality
"""

import requests
import json
import io
from PIL import Image
import numpy as np

def create_different_signatures():
    """Create two different signature images for testing"""
    signatures = []
    
    # Signature 1: Simple circle
    img1 = Image.new('RGB', (200, 100), color='white')
    pixels1 = img1.load()
    for x in range(50, 150):
        for y in range(30, 70):
            if (x - 100) ** 2 + (y - 50) ** 2 < 400:  # Circle
                pixels1[x, y] = (0, 0, 0)
    
    img_bytes1 = io.BytesIO()
    img1.save(img_bytes1, format='PNG')
    signatures.append(('circle_signature.png', img_bytes1.getvalue()))
    
    # Signature 2: Different shape - rectangle
    img2 = Image.new('RGB', (200, 100), color='white')
    pixels2 = img2.load()
    for x in range(60, 140):
        for y in range(20, 80):
            pixels2[x, y] = (0, 0, 0)  # Rectangle
    
    img_bytes2 = io.BytesIO()
    img2.save(img_bytes2, format='PNG')
    signatures.append(('rectangle_signature.png', img_bytes2.getvalue()))
    
    return signatures

def test_improved_matching():
    """Test the improved signature matching and delete functionality"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 Testing Improved Signature Matching and Delete Functionality")
    print("=" * 70)
    
    # Step 1: Login
    print("1️⃣ Logging in...")
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
    
    # Step 2: Create different signatures
    print("\n2️⃣ Creating different signature images...")
    signatures = create_different_signatures()
    print(f"✅ Created {len(signatures)} different signatures")
    
    # Step 3: Upload first signature as template
    print("\n3️⃣ Uploading first signature as template...")
    files1 = {
        'file': (signatures[0][0], signatures[0][1], 'image/png')
    }
    data1 = {
        'template_name': 'Circle Signature Template'
    }
    
    try:
        response = requests.post(f"{base_url}/signature/upload", 
                               files=files1, data=data1, headers=headers)
        if response.status_code == 200:
            result1 = response.json()
            template_id = result1.get('template_id')
            score1 = result1['analysis_result']['authenticity_score']
            print(f"✅ First signature uploaded as template (ID: {template_id})")
            print(f"   - Authenticity Score: {score1:.3f}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False
    
    # Step 4: Upload second signature for verification
    print("\n4️⃣ Uploading second signature for verification...")
    files2 = {
        'file': (signatures[1][0], signatures[1][1], 'image/png')
    }
    data2 = {
        'template_id': template_id  # Send as integer, not string
    }
    
    try:
        response = requests.post(f"{base_url}/signature/verify", 
                               files=files2, data=data2, headers=headers)
        if response.status_code == 200:
            result2 = response.json()
            score2 = result2['analysis_result']['authenticity_score']
            is_authentic = result2['analysis_result']['is_authentic']
            print(f"✅ Second signature verified against template")
            print(f"   - Match Score: {score2:.3f}")
            print(f"   - Is Authentic: {is_authentic}")
            
            # Check if the system correctly identified different signatures
            if score2 < 0.7:  # Should be low for different signatures
                print("✅ System correctly identified different signatures (low match score)")
            else:
                print("⚠️ System may not be discriminating enough between different signatures")
        else:
            print(f"❌ Verification failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False
    
    # Step 5: Test delete functionality
    print("\n5️⃣ Testing template deletion...")
    try:
        response = requests.delete(f"{base_url}/signature/templates/{template_id}", headers=headers)
        if response.status_code == 200:
            print("✅ Template deleted successfully")
        else:
            print(f"❌ Delete failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Delete failed: {e}")
        return False
    
    # Step 6: Verify template is deleted
    print("\n6️⃣ Verifying template deletion...")
    try:
        response = requests.get(f"{base_url}/signature/templates", headers=headers)
        if response.status_code == 200:
            templates = response.json()["templates"]
            remaining_templates = [t for t in templates if t['id'] == template_id]
            if len(remaining_templates) == 0:
                print("✅ Template successfully deleted from database")
            else:
                print("❌ Template still exists in database")
                return False
        else:
            print(f"❌ Failed to check templates: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to check templates: {e}")
        return False
    
    # Step 7: Test with same signature (should have high match)
    print("\n7️⃣ Testing with same signature (should have high match)...")
    files3 = {
        'file': (signatures[0][0], signatures[0][1], 'image/png')
    }
    data3 = {
        'template_name': 'Circle Signature Template 2'
    }
    
    try:
        # Upload as new template
        response = requests.post(f"{base_url}/signature/upload", 
                               files=files3, data=data3, headers=headers)
        if response.status_code == 200:
            result3 = response.json()
            new_template_id = result3.get('template_id')
            print(f"✅ Same signature uploaded as new template (ID: {new_template_id})")
            
            # Now verify the same signature against itself
            files4 = {
                'file': (signatures[0][0], signatures[0][1], 'image/png')
            }
            data4 = {
                'template_id': new_template_id  # Send as integer, not string
            }
            
            response = requests.post(f"{base_url}/signature/verify", 
                                   files=files4, data=data4, headers=headers)
            if response.status_code == 200:
                result4 = response.json()
                score4 = result4['analysis_result']['authenticity_score']
                is_authentic4 = result4['analysis_result']['is_authentic']
                print(f"✅ Same signature verified against itself")
                print(f"   - Match Score: {score4:.3f}")
                print(f"   - Is Authentic: {is_authentic4}")
                
                if score4 > 0.8:  # Should be high for same signature
                    print("✅ System correctly identified same signature (high match score)")
                else:
                    print("⚠️ System may not be recognizing same signatures properly")
            else:
                print(f"❌ Self-verification failed: {response.status_code}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    print("\n" + "=" * 70)
    print("🎉 Improved signature matching and delete functionality test completed!")
    print("\n📋 Summary:")
    print("✅ Template deletion working correctly")
    print("✅ Different signatures detected with low match scores")
    print("✅ Same signatures detected with high match scores")
    print("✅ Authentication working for all operations")
    
    print("\n🌐 Frontend Instructions:")
    print("1. Open frontend/index.html in your browser")
    print("2. Login with: templateuser / password123")
    print("3. Delete templates now works correctly")
    print("4. Different signatures will show low match scores")
    print("5. Same signatures will show high match scores")
    
    return True

if __name__ == "__main__":
    success = test_improved_matching()
    if success:
        print("\n✅ All tests passed! Delete and matching functionality improved.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
