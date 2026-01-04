#!/usr/bin/env python3
"""
Simple bcrypt test script to verify compatibility in different environments
This can be used to test bcrypt functionality before deployment
"""

import os
import sys

def test_bcrypt():
    """Test bcrypt functionality with various configurations"""
    print("🔐 Testing bcrypt compatibility...")
    
    try:
        import bcrypt
        print(f"✅ bcrypt imported successfully (version: {getattr(bcrypt, '__version__', 'unknown')})")
    except ImportError as e:
        print(f"❌ Failed to import bcrypt: {e}")
        return False
    
    # Test 1: Basic password hashing
    try:
        test_password = "test123"
        hashed = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
        print(f"✅ Basic hashing test passed")
        print(f"   Hash length: {len(hashed)} bytes")
    except Exception as e:
        print(f"❌ Basic hashing test failed: {e}")
        return False
    
    # Test 2: Password verification
    try:
        if bcrypt.checkpw(test_password.encode('utf-8'), hashed):
            print("✅ Password verification test passed")
        else:
            print("❌ Password verification test failed")
            return False
    except Exception as e:
        print(f"❌ Password verification test failed: {e}")
        return False
    
    # Test 3: Long password (72 byte limit test)
    try:
        long_password = "a" * 80  # 80 characters, should be truncated to 72 bytes
        long_hashed = bcrypt.hashpw(long_password.encode('utf-8'), bcrypt.gensalt())
        print(f"✅ Long password test passed")
        
        # Test verification with original long password
        if bcrypt.checkpw(long_password.encode('utf-8'), long_hashed):
            print("✅ Long password verification passed")
        else:
            print("❌ Long password verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Long password test failed: {e}")
        print(f"   This might indicate bcrypt version compatibility issues")
        return False
    
    # Test 4: Different salt rounds
    try:
        for rounds in [4, 8, 12]:
            salt = bcrypt.gensalt(rounds=rounds)
            hash_test = bcrypt.hashpw(b"test", salt)
            print(f"✅ Salt rounds {rounds} test passed")
    except Exception as e:
        print(f"❌ Salt rounds test failed: {e}")
        return False
    
    print("🎉 All bcrypt tests passed!")
    return True

def test_environment_info():
    """Print environment information that might affect bcrypt"""
    print("\n🌍 Environment Information:")
    print(f"   Python version: {sys.version}")
    print(f"   Platform: {sys.platform}")
    print(f"   Working directory: {os.getcwd()}")
    
    # Check for environment variables that might affect bcrypt
    vercel_vars = [k for k in os.environ.keys() if 'VERCEL' in k.upper()]
    if vercel_vars:
        print(f"   Vercel environment detected: {vercel_vars[:3]}")  # Show first 3
    
    # Check Python path
    print(f"   Python executable: {sys.executable}")
    
    try:
        import platform
        print(f"   Architecture: {platform.machine()}")
        print(f"   System: {platform.system()} {platform.release()}")
    except:
        pass

if __name__ == "__main__":
    print("🧪 Bcrypt Compatibility Test")
    print("=" * 50)
    
    test_environment_info()
    print("\n" + "=" * 50)
    
    success = test_bcrypt()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed - bcrypt should work properly")
        sys.exit(0)
    else:
        print("❌ Some tests failed - bcrypt might have compatibility issues")
        sys.exit(1)
