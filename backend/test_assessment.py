#!/usr/bin/env python3
"""
Test assessment generation to debug the 422 error
"""

import requests
import json

def test_assessment_generation():
    """Test the assessment generation endpoint"""
    
    print("🧪 Testing Assessment Generation")
    print("=" * 50)
    
    # Test data
    test_payload = {
        "skills": ["python", "javascript", "sql"],
        "user_id": "test_user_123"
    }
    
    print(f"📤 Sending payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/assessment/generate",
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📥 Response Status: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Assessment generated successfully!")
            print(f"📊 Questions generated: {len(result.get('questions', []))}")
            print(f"🎯 Skills assessed: {result.get('skills_assessed', [])}")
            
            # Show first question as example
            if result.get('questions'):
                first_question = result['questions'][0]
                print(f"\n📝 Sample Question:")
                print(f"   Skill: {first_question.get('skill')}")
                print(f"   Question: {first_question.get('question')}")
                print(f"   Options: {first_question.get('options')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Error Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_assessment_submission():
    """Test assessment submission"""
    
    print("\n🧪 Testing Assessment Submission")
    print("=" * 50)
    
    # Test data
    test_payload = {
        "user_id": "test_user_123",
        "answers": {
            "python_0": "A",
            "python_1": "B",
            "javascript_0": "C",
            "javascript_1": "A",
            "sql_0": "B",
            "sql_1": "D"
        },
        "time_taken": 300  # 5 minutes
    }
    
    print(f"📤 Sending submission: {json.dumps(test_payload, indent=2)}")
    
    try:
        response = requests.post(
            "http://localhost:8000/assessment/submit",
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Assessment submitted successfully!")
            print(f"📊 Skill scores: {result.get('skill_scores', {})}")
            print(f"💪 Strong skills: {result.get('strong_skills', [])}")
            print(f"📈 Medium skills: {result.get('medium_skills', [])}")
            print(f"📉 Weak skills: {result.get('weak_skills', [])}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Error Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_assessment_generation()
    test_assessment_submission() 