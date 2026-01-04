#!/usr/bin/env python3
"""
Simple API test script for Vercel deployment
"""

import requests
import sys

def test_api(base_url):
    """Test basic API endpoints"""
    print(f"🧪 Testing API at: {base_url}")
    
    try:
        # Test root endpoint
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
        
        # Test courses endpoint
        response = requests.get(f"{base_url}/api/courses")
        if response.status_code == 200:
            print("✅ Courses API working")
        else:
            print(f"❌ Courses API failed: {response.status_code}")
            
        print("🎉 Basic tests completed!")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_api.py <base_url>")
        print("Example: python test_api.py https://your-app.vercel.app")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    test_api(base_url)
