from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from utils.ai_mentor import ai_mentor
from utils.user_activity_tracker import activity_tracker
from datetime import datetime

router = APIRouter(prefix="/mentor", tags=["AI Mentor"])

class MentorQuestion(BaseModel):
    user_id: str
    question: str
    context: Optional[Dict] = None

class LearningPathRequest(BaseModel):
    user_id: str
    skills: List[str]
    skill_levels: Dict[str, str]

class DailyTipRequest(BaseModel):
    user_id: str
    current_skills: List[str]

@router.post("/ask")
async def ask_mentor(payload: MentorQuestion):
    """Ask AI mentor a question"""
    
    print(f"🤖 AI Mentor: User {payload.user_id} asking question")
    
    try:
        response = await ai_mentor.get_mentor_response(
            payload.user_id, 
            payload.question, 
            payload.context
        )
        
        # Log the interaction
        activity_tracker.log_activity(payload.user_id, "mentor_question", {
            "question": payload.question,
            "response_length": len(response.get("response", "")),
            "confidence": response.get("confidence", "medium"),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "user_id": payload.user_id,
            "question": payload.question,
            "mentor_response": response,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Mentor error: {e}")
        raise HTTPException(status_code=500, detail=f"Mentor service error: {e}")

@router.post("/learning-path")
async def generate_learning_path(payload: LearningPathRequest):
    """Generate personalized learning path"""
    
    print(f"🎯 Generating learning path for user {payload.user_id}")
    
    try:
        learning_path = await ai_mentor.generate_learning_path(
            payload.user_id,
            payload.skills,
            payload.skill_levels
        )
        
        # Log learning path generation
        activity_tracker.log_activity(payload.user_id, "learning_path_generated", {
            "skills": payload.skills,
            "skill_levels": payload.skill_levels,
            "path_length": len(learning_path.get("learning_path", [])),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "user_id": payload.user_id,
            "learning_path": learning_path,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Learning path error: {e}")
        raise HTTPException(status_code=500, detail=f"Learning path generation error: {e}")

@router.post("/daily-tip")
async def get_daily_tip(payload: DailyTipRequest):
    """Get daily learning tip"""
    
    print(f"💡 Getting daily tip for user {payload.user_id}")
    
    try:
        tip = await ai_mentor.get_daily_tip(payload.user_id, payload.current_skills)
        
        # Log daily tip request
        activity_tracker.log_activity(payload.user_id, "daily_tip_requested", {
            "current_skills": payload.current_skills,
            "tip_skill": tip.get("skill_focus", "general"),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "user_id": payload.user_id,
            "daily_tip": tip,
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        }
        
    except Exception as e:
        print(f"❌ Daily tip error: {e}")
        raise HTTPException(status_code=500, detail=f"Daily tip error: {e}")

@router.get("/{user_id}/history")
async def get_mentor_history(user_id: str, limit: int = 10):
    """Get user's mentor interaction history"""
    
    try:
        activities = activity_tracker.get_user_activities(user_id, limit)
        mentor_activities = [
            activity for activity in activities 
            if activity.get("activity_type") in ["mentor_question", "learning_path_generated", "daily_tip_requested"]
        ]
        
        return {
            "user_id": user_id,
            "mentor_history": mentor_activities,
            "total_interactions": len(mentor_activities)
        }
        
    except Exception as e:
        print(f"❌ Mentor history error: {e}")
        raise HTTPException(status_code=500, detail=f"Mentor history error: {e}")

@router.get("/stats")
async def get_mentor_stats():
    """Get overall mentor usage statistics"""
    
    try:
        # Get all mentor-related activities
        all_activities = activity_tracker.get_all_activities()
        mentor_activities = [
            activity for activity in all_activities 
            if activity.get("activity_type") in ["mentor_question", "learning_path_generated", "daily_tip_requested"]
        ]
        
        # Calculate statistics
        total_interactions = len(mentor_activities)
        unique_users = len(set(activity.get("user_id") for activity in mentor_activities))
        
        # Count by type
        question_count = len([a for a in mentor_activities if a.get("activity_type") == "mentor_question"])
        learning_path_count = len([a for a in mentor_activities if a.get("activity_type") == "learning_path_generated"])
        tip_count = len([a for a in mentor_activities if a.get("activity_type") == "daily_tip_requested"])
        
        return {
            "total_interactions": total_interactions,
            "unique_users": unique_users,
            "questions_asked": question_count,
            "learning_paths_generated": learning_path_count,
            "daily_tips_requested": tip_count,
            "average_confidence": "medium",  # This would be calculated from actual data
            "most_active_hours": "9 AM - 6 PM",  # This would be calculated from timestamps
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Mentor stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Mentor stats error: {e}") 