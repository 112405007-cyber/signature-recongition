#!/usr/bin/env python3
"""
Simple test to debug the verification endpoint
"""

import requests
import json
import io
from PIL import Image

def create_simple_signature():
    """Create a simple signature image"""
    img = Image.new('RGB', (200, 100), color='white')
    pixels = img.load()
    
    # Draw a simple line
    for x in range(50, 150):
        for y in range(50, 52):
            pixels[x, y] = (0, 0, 0)
    
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()

def test_simple_verify():
    """Simple verification test"""
    base_url = "http://localhost:8000/api/v1"
    
    print("🧪 Simple Verification Test")
    print("=" * 40)
    
    # Login
    login_data = {"username": "templateuser", "password": "password123"}
    response = requests.post(f"{base_url}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return False
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Create signature
    signature_data = create_simple_signature()
    print("✅ Signature created")
    
    # Upload as template
    files = {'file': ('test.png', signature_data, 'image/png')}
    data = {'template_name': 'Test Template'}
    
    response = requests.post(f"{base_url}/signature/upload", files=files, data=data, headers=headers)
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    result = response.json()
    template_id = result.get('template_id')
    print(f"✅ Template created (ID: {template_id})")
    
    # Verify against template
    files2 = {'file': ('test2.png', signature_data, 'image/png')}
    data2 = {'template_id': str(template_id)}
    
    print(f"Verifying with template_id: {template_id} (type: {type(template_id)})")
    
    response = requests.post(f"{base_url}/signature/verify", files=files2, data=data2, headers=headers)
    print(f"Response status: {response.status_code}")
    print(f"Response text: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Verification successful")
        print(f"   - Score: {result['analysis_result']['authenticity_score']:.3f}")
        return True
    else:
        print(f"❌ Verification failed: {response.status_code}")
        return False

if __name__ == "__main__":
    test_simple_verify()
