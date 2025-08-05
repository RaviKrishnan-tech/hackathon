from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import google.generativeai as genai
import os
from dotenv import load_dotenv
from utils.skill_analyzer import skill_analyzer
from utils.user_activity_tracker import activity_tracker
from utils.ai_mentor import ai_mentor

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

router = APIRouter(prefix="/assessment", tags=["Assessment"])

class SkillList(BaseModel):
    skills: List[str]
    user_id: str

class AssessmentSubmission(BaseModel):
    user_id: str
    answers: Dict[str, str]  # question_id: selected_answer
    time_taken: int  # in seconds

class AssessmentResult(BaseModel):
    user_id: str
    skill_scores: Dict[str, float]
    strong_skills: List[str]
    medium_skills: List[str]
    weak_skills: List[str]
    overall_analysis: Dict
    learning_recommendations: Dict
    ai_mentor_suggestions: List[str]

@router.post("/generate")
async def generate_assessment(payload: SkillList):
    if not payload.skills:
        raise HTTPException(status_code=400, detail="No skills provided")

    print(f"🎯 Generating assessment for user {payload.user_id} with skills: {payload.skills}")
    
    # Check if API key is configured
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("⚠️ GEMINI_API_KEY not configured. Using fallback assessment generation.")
        return await generate_fallback_assessment(payload.skills, payload.user_id)

    model = genai.GenerativeModel("gemini-pro")
    questions = []

    for skill in payload.skills:
        try:
            # Generate exactly 2 questions per skill as requested
            for question_num in range(2):
            prompt = (
                    f"Generate 1 comprehensive multiple-choice question to assess knowledge in '{skill}'. "
                    f"Make it practical and relevant to real-world scenarios. "
                    f"Format the response as JSON:\n\n"
                    f'{{\n'
                    f'  "question": "Detailed question text",\n'
                    f'  "options": ["Option A", "Option B", "Option C", "Option D"],\n'
                    f'  "answer": "A",\n'
                    f'  "explanation": "Brief explanation of why this is correct",\n'
                    f'  "difficulty": "intermediate"\n'
                    f'}}\n\n'
                    f"Make the question challenging but fair. Focus on practical application of {skill}."
            )

            response = model.generate_content(prompt)
                result_text = response.text.strip()
                
                # Try to extract JSON from response
                import json
                import re
                
                # Find JSON in the response
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    question_data = json.loads(json_match.group())

                questions.append({
                        "id": f"{skill}_{question_num}",
                        "skill": skill,
                        "question": question_data.get("question", f"Question about {skill}"),
                        "options": question_data.get("options", ["A", "B", "C", "D"]),
                        "answer": question_data.get("answer", "A"),
                        "explanation": question_data.get("explanation", "Explanation not available"),
                        "difficulty": question_data.get("difficulty", "intermediate")
                    })
                else:
                    # Fallback if JSON parsing fails
                    questions.append({
                        "id": f"{skill}_{question_num}",
                    "skill": skill,
                        "question": f"What is a key concept in {skill}?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "answer": "A",
                        "explanation": f"Basic question about {skill}",
                        "difficulty": "beginner"
                })

        except Exception as e:
            print(f"⚠️ Failed to generate question for {skill}: {e}")
            # Add fallback questions
            for question_num in range(2):
                questions.append({
                    "id": f"{skill}_{question_num}",
                    "skill": skill,
                    "question": f"What is a fundamental concept in {skill}?",
                    "options": ["Basic concept", "Advanced concept", "Intermediate concept", "Expert concept"],
                    "answer": "A",
                    "explanation": f"Basic understanding of {skill}",
                    "difficulty": "beginner"
                })

    if not questions:
        raise HTTPException(status_code=500, detail="No questions generated.")

    print(f"✅ Generated {len(questions)} questions for {len(payload.skills)} skills")

    # Log assessment generation
    activity_tracker.log_activity(payload.user_id, "assessment_generated", {
        "skills": payload.skills,
        "question_count": len(questions),
        "timestamp": "2024-01-01T00:00:00Z"
    })

    return {
        "assessment_id": f"assess_{payload.user_id}_{len(questions)}",
        "questions": questions,
        "total_questions": len(questions),
        "skills_assessed": payload.skills,
        "estimated_duration": len(questions) * 2,  # 2 minutes per question
        "instructions": "Answer all questions to assess your skill levels. Be honest with your answers."
    }

async def generate_fallback_assessment(skills: List[str], user_id: str):
    """Generate fallback assessment when AI is not available"""
    questions = []
    
    for skill in skills:
        for question_num in range(2):
            questions.append({
                "id": f"{skill}_{question_num}",
                "skill": skill,
                "question": f"What is your experience level with {skill}?",
                "options": ["Beginner", "Intermediate", "Advanced", "Expert"],
                "answer": "B",
                "explanation": f"Self-assessment question for {skill}",
                "difficulty": "beginner"
            })
    
    return {
        "assessment_id": f"fallback_{user_id}_{len(questions)}",
        "questions": questions,
        "total_questions": len(questions),
        "skills_assessed": skills,
        "estimated_duration": len(questions) * 2,
        "instructions": "Self-assessment questions for skill evaluation."
    }

@router.post("/submit", response_model=AssessmentResult)
async def submit_assessment(payload: AssessmentSubmission):
    """Submit assessment answers and get skill analysis"""
    
    print(f"📊 Processing assessment submission for user {payload.user_id}")
    print(f"📝 Received {len(payload.answers)} answers")
    
    # Get the assessment questions to calculate scores
    # In a real app, you'd fetch this from database
    # For now, we'll use a simplified scoring system
    
    skill_scores = {}
    skill_answers = {}
    
    # Group answers by skill
    for question_id, answer in payload.answers.items():
        skill = question_id.split('_')[0]  # Extract skill from question_id
        if skill not in skill_answers:
            skill_answers[skill] = []
        skill_answers[skill].append(answer)
    
    # Calculate scores for each skill (simplified scoring)
    for skill, answers in skill_answers.items():
        # Simple scoring: each correct answer = 1 point
        # In reality, you'd compare with correct answers from the assessment
        score = len(answers) * 0.5  # Simplified scoring
        skill_scores[skill] = min(score, 10.0)  # Cap at 10
    
    # Categorize skills based on scores
    strong_skills = [skill for skill, score in skill_scores.items() if score >= 7.0]
    medium_skills = [skill for skill, score in skill_scores.items() if 4.0 <= score < 7.0]
    weak_skills = [skill for skill, score in skill_scores.items() if score < 4.0]
    
    print(f"📈 Skill Analysis: Strong={len(strong_skills)}, Medium={len(medium_skills)}, Weak={len(weak_skills)}")
    
    # Generate learning recommendations using AI
    learning_recommendations = await generate_learning_recommendations(
        strong_skills, medium_skills, weak_skills, payload.user_id
    )
    
    # Generate AI mentor suggestions
    ai_mentor_suggestions = await generate_mentor_suggestions(
        skill_scores, weak_skills, payload.user_id
    )
    
    # Log assessment completion
    activity_tracker.log_activity(payload.user_id, "assessment_completed", {
        "skill_scores": skill_scores,
        "strong_skills": strong_skills,
        "medium_skills": medium_skills,
        "weak_skills": weak_skills,
        "time_taken": payload.time_taken,
        "timestamp": "2024-01-01T00:00:00Z"
    })
    
    result = AssessmentResult(
        user_id=payload.user_id,
        skill_scores=skill_scores,
        strong_skills=strong_skills,
        medium_skills=medium_skills,
        weak_skills=weak_skills,
        overall_analysis={
            "total_skills_assessed": len(skill_scores),
            "average_score": sum(skill_scores.values()) / len(skill_scores) if skill_scores else 0,
            "strongest_skill": max(skill_scores.items(), key=lambda x: x[1])[0] if skill_scores else None,
            "weakest_skill": min(skill_scores.items(), key=lambda x: x[1])[0] if skill_scores else None,
            "recommendation": "Focus on improving weak skills while maintaining strong ones"
        },
        learning_recommendations=learning_recommendations,
        ai_mentor_suggestions=ai_mentor_suggestions
    )
    
    print(f"✅ Assessment analysis completed for user {payload.user_id}")
    return result

async def generate_learning_recommendations(strong_skills, medium_skills, weak_skills, user_id):
    """Generate personalized learning recommendations using AI"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return generate_fallback_recommendations(strong_skills, medium_skills, weak_skills)
    
    try:
        model = genai.GenerativeModel("gemini-pro")
        
        prompt = f"""
        Generate personalized learning recommendations for a user with the following skill levels:
        
        Strong Skills: {strong_skills}
        Medium Skills: {medium_skills}
        Weak Skills: {weak_skills}
        
        Provide recommendations in JSON format:
        {{
            "weak_skills_focus": [
                {{
                    "skill": "skill_name",
                    "priority": "high/medium/low",
                    "learning_path": ["step1", "step2", "step3"],
                    "resources": ["resource1", "resource2"],
                    "estimated_time": "2-3 weeks"
                }}
            ],
            "medium_skills_improvement": [
                {{
                    "skill": "skill_name",
                    "next_level": "advanced_concept",
                    "practice_projects": ["project1", "project2"],
                    "estimated_time": "1-2 weeks"
                }}
            ],
            "strong_skills_maintenance": [
                {{
                    "skill": "skill_name",
                    "advanced_topics": ["topic1", "topic2"],
                    "mentorship_opportunities": ["opportunity1", "opportunity2"]
                }}
            ],
            "overall_strategy": "comprehensive learning strategy"
        }}
        """
        
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        import json
        import re
        
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            return generate_fallback_recommendations(strong_skills, medium_skills, weak_skills)
            
    except Exception as e:
        print(f"❌ Failed to generate AI recommendations: {e}")
        return generate_fallback_recommendations(strong_skills, medium_skills, weak_skills)

def generate_fallback_recommendations(strong_skills, medium_skills, weak_skills):
    """Generate fallback learning recommendations"""
    return {
        "weak_skills_focus": [
            {
                "skill": skill,
                "priority": "high",
                "learning_path": ["Basic concepts", "Practice exercises", "Real projects"],
                "resources": ["Online tutorials", "Documentation", "Practice platforms"],
                "estimated_time": "2-3 weeks"
            } for skill in weak_skills
        ],
        "medium_skills_improvement": [
            {
                "skill": skill,
                "next_level": "Advanced concepts",
                "practice_projects": ["Intermediate projects", "Code reviews"],
                "estimated_time": "1-2 weeks"
            } for skill in medium_skills
        ],
        "strong_skills_maintenance": [
            {
                "skill": skill,
                "advanced_topics": ["Expert-level concepts", "Industry best practices"],
                "mentorship_opportunities": ["Teach others", "Contribute to open source"]
            } for skill in strong_skills
        ],
        "overall_strategy": "Focus on weak skills while maintaining strong ones"
    }

async def generate_mentor_suggestions(skill_scores, weak_skills, user_id):
    """Generate AI mentor suggestions"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return [
            f"Focus on improving {skill} through practice and real projects" 
            for skill in weak_skills[:3]
        ]
    
    try:
        model = genai.GenerativeModel("gemini-pro")
        
        prompt = f"""
        As an AI mentor, provide 3 specific, actionable suggestions for a user with these skill scores:
        {skill_scores}
        
        Focus especially on these weak skills: {weak_skills}
        
        Provide suggestions as a JSON array of strings:
        ["suggestion1", "suggestion2", "suggestion3"]
        """
        
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        
        import json
        import re
        
        json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            return [
                f"Focus on improving {skill} through practice and real projects" 
                for skill in weak_skills[:3]
            ]
        
    except Exception as e:
        print(f"❌ Failed to generate mentor suggestions: {e}")
        return [
            f"Focus on improving {skill} through practice and real projects" 
            for skill in weak_skills[:3]
        ]

@router.get("/{user_id}/history")
async def get_assessment_history(user_id: str):
    """Get user's assessment history"""
    try:
        user_profile = activity_tracker.get_user_profile(user_id)
        if "error" in user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get assessment activities
        assessment_activities = [
            activity for activity in activity_tracker.get_user_activities(user_id, 50)
            if activity["activity_type"] == "assessment_completed"
        ]
        
        return {
            "user_id": user_id,
            "assessment_history": assessment_activities,
            "total_assessments": len(assessment_activities),
            "profile": user_profile
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {e}")

@router.get("/{user_id}/progress")
async def get_skill_progress(user_id: str):
    """Get skill progress over time"""
    try:
        # Get assessment history for progress tracking
        assessment_activities = [
            activity for activity in activity_tracker.get_user_activities(user_id, 100)
            if activity["activity_type"] == "assessment_completed"
        ]
        
        if len(assessment_activities) < 2:
            return {
                "user_id": user_id,
                "progress": "Insufficient data for progress tracking",
                "assessments_count": len(assessment_activities)
            }
        
        # Get first and latest assessment scores
        first_assessment = assessment_activities[-1]
        latest_assessment = assessment_activities[0]
        
        if "scores" in first_assessment["details"] and "scores" in latest_assessment["details"]:
            progress_data = skill_analyzer.track_skill_progress(
                user_id,
                first_assessment["details"]["scores"],
                latest_assessment["details"]["scores"]
            )
        else:
            progress_data = {"error": "No score data available"}
        
        return {
            "user_id": user_id,
            "progress_data": progress_data,
            "assessments_count": len(assessment_activities)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {e}")
