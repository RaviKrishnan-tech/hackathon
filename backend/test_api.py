#!/usr/bin/env python3
"""
Test the resume API endpoint
"""

import requests
import json

def test_resume_api():
    """Test the resume API endpoint"""
    
    print("🔍 Testing Resume API Endpoint")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"📄 Response: {response.json()}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return
    
    # Test 2: Resume endpoint (without file)
    print("\n2. Testing resume endpoint (should fail without file)...")
    try:
        response = requests.post("http://localhost:8000/resume/process")
        print(f"📄 Status: {response.status_code}")
        if response.status_code == 422:  # Validation error for missing file
            print("✅ Resume endpoint correctly rejects request without file")
        else:
            print(f"⚠️ Unexpected response: {response.text}")
    except Exception as e:
        print(f"❌ Resume endpoint error: {e}")
    
    print("\n✅ API tests completed!")
    print("\n📝 To test with a real resume:")
    print("1. Create a PDF with technical skills")
    print("2. Upload it through the frontend")
    print("3. Check the console for detailed logs")

if __name__ == "__main__":
    test_resume_api() 