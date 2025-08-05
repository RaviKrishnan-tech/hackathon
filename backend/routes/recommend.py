from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import uuid
from utils.skill_analyzer import skill_analyzer
from utils.ai_mentor import ai_mentor
from utils.user_activity_tracker import activity_tracker
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

router = APIRouter(prefix="/recommend", tags=["Recommendation"])

class RecommendRequest(BaseModel):
    user_id: str
    scores: Dict[str, float]
    learning_goals: List[str] = []
    preferred_learning_style: str = "mixed"  # visual, audio, text, mixed

class LearningModule(BaseModel):
    id: str
    title: str
    skill: str
    level: str
    estimated_hours: int
    learning_objectives: List[str]
    resources: List[str]
    exercises: List[str]
    milestones: List[str]
    difficulty: str
    prerequisites: List[str]

class LearningPathResponse(BaseModel):
    user_id: str
    learning_path: List[LearningModule]
    total_estimated_weeks: int
    focus_areas: List[str]
    success_metrics: List[str]
    ai_mentor_guidance: Dict

@router.post("/learning-path", response_model=LearningPathResponse)
async def generate_learning_path(payload: RecommendRequest):
    """Generate AI-powered personalized learning path"""
    
    if not payload.scores:
        raise HTTPException(status_code=400, detail="Assessment scores are required")
    
    try:
        # Analyze skills to identify gaps
        skill_analysis = skill_analyzer.analyze_skill_strengths(payload.scores)
        
        # Generate learning path using AI
        learning_path_data = skill_analyzer.generate_personalized_learning_path(skill_analysis)
        
        # Enhance learning path with AI mentor guidance
        mentor_guidance = ai_mentor.get_mentor_response(
            payload.user_id,
            f"Generate a detailed learning strategy for skills: {skill_analysis['weak_skills']}. "
            f"Learning goals: {payload.learning_goals}. "
            f"Preferred style: {payload.preferred_learning_style}",
            {
                "recent_assessment_scores": payload.scores,
                "weak_skills": skill_analysis["weak_skills"],
                "learning_goals": payload.learning_goals,
                "learning_style": payload.preferred_learning_style
            }
        )
        
        # Convert to structured learning modules
        learning_modules = []
        for module_data in learning_path_data.get("learning_path", []):
            learning_modules.append(LearningModule(
                id=str(uuid.uuid4()),
                title=module_data.get("skill", "Unknown Skill"),
                skill=module_data.get("skill", "Unknown"),
                level=module_data.get("priority", "medium"),
                estimated_hours=module_data.get("estimated_weeks", 4) * 10,  # Convert weeks to hours
                learning_objectives=module_data.get("learning_objectives", []),
                resources=module_data.get("resources", []),
                exercises=module_data.get("exercises", []),
                milestones=module_data.get("milestones", []),
                difficulty=module_data.get("difficulty", "intermediate"),
                prerequisites=[]
            ))
        
        # Log learning path generation
        activity_tracker.log_activity(payload.user_id, "learning_path_generated", {
            "skills_targeted": skill_analysis["weak_skills"],
            "total_modules": len(learning_modules),
            "estimated_weeks": learning_path_data.get("total_estimated_weeks", 0)
        })
        
        return LearningPathResponse(
            user_id=payload.user_id,
            learning_path=learning_modules,
            total_estimated_weeks=learning_path_data.get("total_estimated_weeks", 0),
            focus_areas=learning_path_data.get("focus_areas", []),
            success_metrics=learning_path_data.get("success_metrics", []),
            ai_mentor_guidance=mentor_guidance
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate learning path: {e}")

@router.post("/modules")
async def generate_learning_modules(payload: RecommendRequest):
    """Generate detailed learning modules for specific skills"""
    
    if not payload.scores:
        raise HTTPException(status_code=400, detail="Assessment scores are required")
    
    try:
        model = genai.GenerativeModel("gemini-pro")
        
        # Identify weak skills that need improvement
        skill_analysis = skill_analyzer.analyze_skill_strengths(payload.scores)
        weak_skills = skill_analysis["weak_skills"]
        
        if not weak_skills:
            return {"modules": [], "message": "No skills identified for improvement"}
        
        modules = []
        
        for skill in weak_skills[:5]:  # Limit to top 5 skills
            try:
                prompt = f"""Create a comprehensive learning module for '{skill}' with the following structure:

{{
    "skill": "{skill}",
    "title": "Comprehensive {skill} Learning Module",
    "description": "Detailed description of what will be learned",
    "difficulty": "beginner/intermediate/advanced",
    "estimated_hours": 20,
    "prerequisites": ["prerequisite1", "prerequisite2"],
    "learning_objectives": [
        "objective1",
        "objective2",
        "objective3"
    ],
    "curriculum": [
        {{
            "week": 1,
            "topics": ["topic1", "topic2"],
            "resources": [
                {{
                    "type": "video/article/book/exercise",
                    "title": "Resource Title",
                    "url": "https://example.com/resource",
                    "description": "Brief description"
                }}
            ],
            "exercises": [
                {{
                    "title": "Exercise Title",
                    "description": "Exercise description",
                    "difficulty": "easy/medium/hard",
                    "estimated_time": "30 minutes"
                }}
            ]
        }}
    ],
    "assessment": [
        {{
            "type": "quiz/project/code_review",
            "title": "Assessment Title",
            "description": "Assessment description",
            "criteria": ["criterion1", "criterion2"]
        }}
    ],
    "real_world_applications": [
        "application1",
        "application2"
    ],
    "career_opportunities": [
        "opportunity1",
        "opportunity2"
    ]
}}

Focus on practical, hands-on learning with real-world applications.
"""
                
                response = model.generate_content(prompt)
                response_text = response.text
                
                # Extract JSON from response
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_str = response_text[json_start:json_end].strip()
                    module_data = json.loads(json_str)
                else:
                    module_data = json.loads(response_text)
                
                module_data["id"] = str(uuid.uuid4())
                modules.append(module_data)
                
            except Exception as e:
                print(f"Failed to generate module for {skill}: {e}")
                continue
        
        # Log module generation
        activity_tracker.log_activity(payload.user_id, "learning_modules_generated", {
            "skills": [m["skill"] for m in modules],
            "modules_count": len(modules)
        })
        
        return {"modules": modules}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate modules: {e}")

@router.get("/{user_id}/progress")
async def get_learning_progress(user_id: str):
    """Get user's learning progress"""
    try:
        user_profile = activity_tracker.get_user_profile(user_id)
        if "error" in user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get learning-related activities
        learning_activities = [
            activity for activity in activity_tracker.get_user_activities(user_id, 50)
            if activity["activity_type"] in ["learning_path_generated", "learning_modules_generated", "learning_progress"]
        ]
        
        return {
            "user_id": user_id,
            "learning_activities": learning_activities,
            "modules_completed": user_profile.get("learning_modules_completed", 0),
            "current_learning_path": user_profile.get("current_learning_path"),
            "profile": user_profile
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {e}")

@router.post("/{user_id}/complete-module")
async def complete_learning_module(user_id: str, module_id: str, completion_data: Dict):
    """Mark a learning module as completed"""
    try:
        # Log module completion
        activity_tracker.log_activity(user_id, "learning_module_completed", {
            "module_id": module_id,
            "completion_data": completion_data
        })
        
        return {
            "user_id": user_id,
            "module_id": module_id,
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete module: {e}")

# Import datetime for the last function
from datetime import datetime
