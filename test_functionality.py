#!/usr/bin/env python3
"""
Test script to verify signature recognition functionality
"""

import sys
import os
import numpy as np
from PIL import Image
import io

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.signature_analyzer import SignatureAnalyzer
from app.services.image_processor import ImageProcessor
from app.services.feature_extractor import FeatureExtractor

def create_test_signature_image():
    """Create a simple test signature image"""
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

def test_image_processor():
    """Test image processing functionality"""
    print("🔄 Testing Image Processor...")
    
    processor = ImageProcessor()
    test_image_data = create_test_signature_image()
    
    try:
        # Load image
        image = processor.load_image(test_image_data)
        print(f"✅ Image loaded successfully: {image.shape}")
        
        # Preprocess image
        processed_image = processor.preprocess_image(image)
        print(f"✅ Image preprocessed successfully: {processed_image.shape}")
        
        # Get image properties
        properties = processor.get_image_properties(processed_image)
        print(f"✅ Image properties extracted: {len(properties)} properties")
        
        return True
    except Exception as e:
        print(f"❌ Image processor test failed: {e}")
        return False

def test_feature_extractor():
    """Test feature extraction functionality"""
    print("\n🔄 Testing Feature Extractor...")
    
    extractor = FeatureExtractor()
    processor = ImageProcessor()
    test_image_data = create_test_signature_image()
    
    try:
        # Process image
        image = processor.load_image(test_image_data)
        processed_image = processor.preprocess_image(image)
        
        # Extract features
        features = extractor.extract_all_features(processed_image)
        print(f"✅ Features extracted successfully: {len(features)} features")
        
        # Test feature serialization
        features_json = extractor.features_to_json(features)
        restored_features = extractor.features_from_json(features_json)
        print(f"✅ Feature serialization works: {len(restored_features)} features restored")
        
        return True
    except Exception as e:
        print(f"❌ Feature extractor test failed: {e}")
        return False

def test_signature_analyzer():
    """Test signature analysis functionality"""
    print("\n🔄 Testing Signature Analyzer...")
    
    analyzer = SignatureAnalyzer()
    test_image_data = create_test_signature_image()
    
    try:
        # Analyze signature
        result = analyzer.analyze_signature(test_image_data)
        print(f"✅ Signature analysis completed")
        print(f"   - Authenticity Score: {result['authenticity_score']:.3f}")
        print(f"   - Confidence Level: {result['confidence_level']:.3f}")
        print(f"   - Is Authentic: {result['is_authentic']}")
        print(f"   - Processing Time: {result['processing_time']:.3f}s")
        
        return True
    except Exception as e:
        print(f"❌ Signature analyzer test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🔄 Testing API Endpoints...")
    
    import requests
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test root endpoint
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint working: {data['message']}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
        
        # Test API docs endpoint
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("✅ API documentation accessible")
        else:
            print(f"❌ API docs failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Signature Recognition System Functionality")
    print("=" * 60)
    
    tests = [
        ("Image Processor", test_image_processor),
        ("Feature Extractor", test_feature_extractor),
        ("Signature Analyzer", test_signature_analyzer),
        ("API Endpoints", test_api_endpoints)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! The system is functioning correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
