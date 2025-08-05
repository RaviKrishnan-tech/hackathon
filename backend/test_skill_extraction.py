#!/usr/bin/env python3
"""
Test skill extraction with sample resume content
"""

from utils.enhanced_resume_parser import resume_parser

def test_skill_extraction():
    """Test skill extraction with sample resume content"""
    
    # Read the test resume content
    with open('test_resume_content.txt', 'r', encoding='utf-8') as f:
        resume_text = f.read()
    
    print("🔍 Testing Skill Extraction")
    print("=" * 50)
    print(f"📄 Resume text length: {len(resume_text)} characters")
    print(f"📄 First 200 characters: {resume_text[:200]}...")
    print()
    
    # Test the fallback skill extraction
    result = resume_parser._fallback_skill_extraction(resume_text)
    
    print("📊 Results:")
    print(f"   Skills found: {len(result['extracted_skills'])}")
    print(f"   Skills: {result['extracted_skills']}")
    print()
    
    print("📋 Skill Categories:")
    for category, skills in result['skill_categories'].items():
        if skills:
            print(f"   {category}: {skills}")
    
    print()
    print("✅ Test completed!")

if __name__ == "__main__":
    test_skill_extraction() 