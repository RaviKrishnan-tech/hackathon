#!/usr/bin/env python3
"""
Test script for resume parsing functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_key():
    """Test if Gemini API key is configured"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("📝 Please create a .env file with your Gemini API key:")
        print("   GEMINI_API_KEY=your_actual_api_key_here")
        return False
    elif api_key == "your_gemini_api_key_here":
        print("❌ GEMINI_API_KEY is set to placeholder value")
        print("📝 Please replace 'your_gemini_api_key_here' with your actual API key")
        return False
    else:
        print("✅ GEMINI_API_KEY is configured")
        return True

def test_imports():
    """Test if all required packages are installed"""
    try:
        import google.generativeai as genai
        print("✅ google.generativeai imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import google.generativeai: {e}")
        print("📝 Install with: pip install google-generativeai")
        return False
    
    try:
        from PyPDF2 import PdfReader
        print("✅ PyPDF2 imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PyPDF2: {e}")
        print("📝 Install with: pip install PyPDF2")
        return False
    
    try:
        from utils.enhanced_resume_parser import resume_parser
        print("✅ EnhancedResumeParser imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import EnhancedResumeParser: {e}")
        return False
    
    return True

def test_gemini_connection():
    """Test Gemini AI connection"""
    try:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            print("⚠️ Skipping Gemini connection test - no valid API key")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-pro")
        
        # Simple test prompt
        response = model.generate_content("Say 'Hello, Gemini!'")
        print("✅ Gemini AI connection successful")
        print(f"📄 Test response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Gemini AI connection failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 Testing Resume Parser Configuration")
    print("=" * 50)
    
    # Test 1: Environment variables
    print("\n1. Testing environment variables...")
    api_key_ok = test_api_key()
    
    # Test 2: Package imports
    print("\n2. Testing package imports...")
    imports_ok = test_imports()
    
    # Test 3: Gemini connection (only if API key is valid)
    print("\n3. Testing Gemini AI connection...")
    if api_key_ok:
        gemini_ok = test_gemini_connection()
    else:
        gemini_ok = False
        print("⚠️ Skipped - no valid API key")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   API Key: {'✅' if api_key_ok else '❌'}")
    print(f"   Imports: {'✅' if imports_ok else '❌'}")
    print(f"   Gemini: {'✅' if gemini_ok else '❌'}")
    
    if not api_key_ok:
        print("\n🔧 To fix the API key issue:")
        print("1. Get your API key from: https://makersuite.google.com/app/apikey")
        print("2. Create a .env file in the backend directory")
        print("3. Add: GEMINI_API_KEY=your_actual_api_key_here")
        print("4. Restart the backend server")
    
    if not imports_ok:
        print("\n🔧 To fix import issues:")
        print("Run: pip install -r requirements.txt")
    
    if api_key_ok and imports_ok and not gemini_ok:
        print("\n🔧 Gemini connection failed. Check your API key and internet connection.")

if __name__ == "__main__":
    main() 