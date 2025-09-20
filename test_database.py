#!/usr/bin/env python3
"""
Test database functionality
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.models.database import engine, Base, get_db
from app.models.signature_model import User, SignatureTemplate, VerificationResult
from sqlalchemy.orm import Session

def test_database_connection():
    """Test database connection and table creation"""
    print("🔄 Testing Database Connection...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Test database session
        db = next(get_db())
        print("✅ Database session created successfully")
        
        # Test basic query
        user_count = db.query(User).count()
        print(f"✅ Database query successful: {user_count} users found")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_user_creation():
    """Test user creation functionality"""
    print("\n🔄 Testing User Creation...")
    
    try:
        from app.routes.auth import get_password_hash
        
        # Test password hashing
        password = "test_password_123"
        hashed_password = get_password_hash(password)
        print("✅ Password hashing works")
        
        # Test database operations
        db = next(get_db())
        
        # Create a test user
        test_user = User(
            username="test_user",
            email="test@example.com",
            hashed_password=hashed_password,
            full_name="Test User"
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"✅ User created successfully: ID {test_user.id}")
        
        # Clean up
        db.delete(test_user)
        db.commit()
        print("✅ Test user cleaned up")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ User creation test failed: {e}")
        return False

def main():
    """Run database tests"""
    print("🧪 Testing Database Functionality")
    print("=" * 40)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("User Creation", test_user_creation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 40)
    print("📊 Database Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 Database functionality is working correctly!")
        return True
    else:
        print("⚠️  Some database tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
