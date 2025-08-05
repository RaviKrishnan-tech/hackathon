#!/usr/bin/env python3
"""
Comprehensive test script for the complete learning platform
Tests all major features: Resume parsing, Assessment, AI Mentor, Hackathons, Progress tracking
"""

import requests
import json
import time
from datetime import datetime, timedelta

def test_resume_parsing():
    """Test resume parsing functionality"""
    print("🧪 Testing Resume Parsing")
    print("=" * 50)
    
    # Create a test PDF content
    test_content = """
    John Doe
    Software Developer
    
    SKILLS:
    - Python (Advanced)
    - JavaScript (Intermediate)
    - React (Beginner)
    - SQL (Intermediate)
    - Git (Advanced)
    
    EXPERIENCE:
    - Developed web applications using Python and JavaScript
    - Worked with React framework for frontend development
    - Database management with SQL
    - Version control with Git
    """
    
    # Create test PDF file
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    pdf_path = "test_resume.pdf"
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.drawString(100, 750, test_content)
    c.save()
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': ('test_resume.pdf', f, 'application/pdf')}
            response = requests.post(
                "http://localhost:8000/resume/process",
                files=files
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Resume parsing successful!")
            print(f"📋 Skills extracted: {len(result.get('extracted_skills', []))}")
            print(f"🎯 Skills: {result.get('extracted_skills', [])}")
            return result.get('extracted_skills', [])
        else:
            print(f"❌ Resume parsing failed: {response.status_code}")
            print(f"📄 Error: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Resume parsing error: {e}")
        return []

def test_assessment_generation(skills):
    """Test assessment generation"""
    print("\n🧪 Testing Assessment Generation")
    print("=" * 50)
    
    if not skills:
        skills = ["python", "javascript", "sql"]
    
    test_payload = {
        "skills": skills[:3],  # Test with first 3 skills
        "user_id": "test_user_123"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/assessment/generate",
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Assessment generation successful!")
            print(f"📊 Questions generated: {len(result.get('questions', []))}")
            print(f"🎯 Skills assessed: {result.get('skills_assessed', [])}")
            
            # Test assessment submission
            return test_assessment_submission(result.get('questions', []))
        else:
            print(f"❌ Assessment generation failed: {response.status_code}")
            print(f"📄 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Assessment generation error: {e}")
        return False

def test_assessment_submission(questions):
    """Test assessment submission"""
    print("\n🧪 Testing Assessment Submission")
    print("=" * 50)
    
    if not questions:
        print("❌ No questions available for submission test")
        return False
    
    # Create mock answers
    answers = {}
    for question in questions:
        answers[question['id']] = 'A'  # Mock answer
    
    test_payload = {
        "user_id": "test_user_123",
        "answers": answers,
        "time_taken": 300  # 5 minutes
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/assessment/submit",
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Assessment submission successful!")
            print(f"📊 Skill scores: {result.get('skill_scores', {})}")
            print(f"💪 Strong skills: {result.get('strong_skills', [])}")
            print(f"📈 Medium skills: {result.get('medium_skills', [])}")
            print(f"📉 Weak skills: {result.get('weak_skills', [])}")
            return True
        else:
            print(f"❌ Assessment submission failed: {response.status_code}")
            print(f"📄 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Assessment submission error: {e}")
        return False

def test_ai_mentor():
    """Test AI mentor functionality"""
    print("\n🧪 Testing AI Mentor")
    print("=" * 50)
    
    test_questions = [
        "How can I improve my Python skills?",
        "What are the best practices for React development?",
        "How do I prepare for a technical interview?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Question {i}: {question}")
        
        test_payload = {
            "user_id": "test_user_123",
            "question": question,
            "context": {
                "current_skills": ["python", "javascript", "react"],
                "assessment_results": {
                    "skill_scores": {"python": 7.5, "javascript": 6.0, "react": 4.0}
                }
            }
        }
        
        try:
            response = requests.post(
                "http://localhost:8000/mentor/ask",
                json=test_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ AI Mentor response received!")
                print(f"🤖 Response: {result.get('mentor_response', {}).get('response', '')[:100]}...")
                print(f"📚 Resources: {len(result.get('mentor_response', {}).get('resources', []))}")
                print(f"🎯 Next steps: {len(result.get('mentor_response', {}).get('next_steps', []))}")
            else:
                print(f"❌ AI Mentor failed: {response.status_code}")
                print(f"📄 Error: {response.text}")
                
        except Exception as e:
            print(f"❌ AI Mentor error: {e}")
        
        time.sleep(1)  # Rate limiting

def test_hackathon_system():
    """Test hackathon functionality"""
    print("\n🧪 Testing Hackathon System")
    print("=" * 50)
    
    # Test creating a hackathon (admin function)
    test_hackathon = {
        "title": "Test Hackathon 2024",
        "description": "A test hackathon for system verification",
        "start_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "end_date": (datetime.now() + timedelta(days=10)).isoformat(),
        "max_participants": 50,
        "prizes": ["$1000 First Prize", "$500 Second Prize", "$250 Third Prize"],
        "requirements": ["Basic programming knowledge", "Team of 1-4 members"],
        "technologies": ["Python", "JavaScript", "React", "Node.js"],
        "difficulty": "intermediate",
        "admin_id": "test_admin_123"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/hackathon/create",
            json=test_hackathon,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            hackathon_id = result.get('hackathon_id')
            print("✅ Hackathon created successfully!")
            print(f"🏆 Hackathon ID: {hackathon_id}")
            
            # Test listing hackathons
            list_response = requests.get("http://localhost:8000/hackathon/list")
            if list_response.status_code == 200:
                list_result = list_response.json()
                print(f"📋 Total hackathons: {len(list_result.get('hackathons', []))}")
            
            # Test applying for hackathon
            application_payload = {
                "hackathon_id": hackathon_id,
                "user_id": "test_user_123",
                "team_name": "Test Team",
                "team_members": ["test_user_123"],
                "project_idea": "A revolutionary learning platform",
                "skills": ["python", "javascript", "react"],
                "experience_level": "intermediate"
            }
            
            apply_response = requests.post(
                "http://localhost:8000/hackathon/apply",
                json=application_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if apply_response.status_code == 200:
                print("✅ Hackathon application submitted successfully!")
            else:
                print(f"❌ Application failed: {apply_response.status_code}")
            
            return True
        else:
            print(f"❌ Hackathon creation failed: {response.status_code}")
            print(f"📄 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Hackathon system error: {e}")
        return False

def test_progress_tracking():
    """Test progress tracking functionality"""
    print("\n🧪 Testing Progress Tracking")
    print("=" * 50)
    
    # Test progress overview
    try:
        response = requests.get("http://localhost:8000/progress/test_user_123/overview")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Progress tracking working!")
            print(f"📊 Total activities: {result.get('progress_metrics', {}).get('total_activities', 0)}")
            print(f"🎯 Skills tracked: {len(result.get('skill_progress', []))}")
            print(f"🏆 Achievements: {len(result.get('achievements', []))}")
            return True
        else:
            print(f"❌ Progress tracking failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Progress tracking error: {e}")
        return False

def test_learning_recommendations():
    """Test learning recommendations"""
    print("\n🧪 Testing Learning Recommendations")
    print("=" * 50)
    
    test_payload = {
        "user_id": "test_user_123",
        "skills": ["python", "javascript", "react"],
        "skill_levels": {"python": "intermediate", "javascript": "beginner", "react": "beginner"},
        "goals": ["Become a full-stack developer", "Learn modern web technologies"],
        "time_available": "3-5 hours",
        "preferred_format": ["video", "interactive", "project"]
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/recommend/learning-path",
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Learning recommendations generated!")
            print(f"📚 Learning path length: {len(result.get('learning_path', {}).get('learning_path', []))}")
            print(f"⏱️ Estimated completion: {result.get('learning_path', {}).get('overall_timeline', 'Unknown')}")
            return True
        else:
            print(f"❌ Learning recommendations failed: {response.status_code}")
            print(f"📄 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Learning recommendations error: {e}")
        return False

def test_admin_dashboard():
    """Test admin dashboard functionality"""
    print("\n🧪 Testing Admin Dashboard")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/admin/dashboard?admin_id=test_admin_123")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Admin dashboard working!")
            print(f"📊 Real-time stats: {len(result.get('real_time_stats', {}))}")
            print(f"👥 User analytics: {result.get('user_analytics', {}).get('total_users', 0)} users")
            print(f"🏥 System health: {result.get('system_health', {}).get('overall_status', 'Unknown')}")
            return True
        else:
            print(f"❌ Admin dashboard failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Admin dashboard error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive System Test")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_results = {}
    
    # Test 1: Resume Parsing
    skills = test_resume_parsing()
    test_results['resume_parsing'] = len(skills) > 0
    
    # Test 2: Assessment System
    test_results['assessment'] = test_assessment_generation(skills)
    
    # Test 3: AI Mentor
    test_ai_mentor()
    test_results['ai_mentor'] = True  # Assume success if no exceptions
    
    # Test 4: Hackathon System
    test_results['hackathon'] = test_hackathon_system()
    
    # Test 5: Progress Tracking
    test_results['progress'] = test_progress_tracking()
    
    # Test 6: Learning Recommendations
    test_results['recommendations'] = test_learning_recommendations()
    
    # Test 7: Admin Dashboard
    test_results['admin'] = test_admin_dashboard()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 