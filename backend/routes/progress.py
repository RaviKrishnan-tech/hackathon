from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from utils.user_activity_tracker import activity_tracker
from utils.ai_mentor import ai_mentor
import json

router = APIRouter(prefix="/progress", tags=["Progress Tracking"])

class ProgressUpdate(BaseModel):
    user_id: str
    skill: str
    progress_percentage: float
    completed_modules: List[str]
    current_module: Optional[str] = None
    time_spent: int  # in minutes

class LearningSession(BaseModel):
    user_id: str
    skill: str
    module: str
    start_time: str
    end_time: Optional[str] = None
    duration: Optional[int] = None  # in minutes

class SkillAchievement(BaseModel):
    user_id: str
    skill: str
    achievement_type: str  # milestone, completion, mastery
    description: str
    points_earned: int

@router.get("/{user_id}/overview")
async def get_user_progress_overview(user_id: str):
    """Get comprehensive progress overview for a user"""
    
    print(f"📊 Getting progress overview for user {user_id}")
    
    try:
        # Get user activities
        user_activities = activity_tracker.get_user_activities(user_id, 100)
        
        # Calculate progress metrics
        progress_metrics = calculate_progress_metrics(user_activities)
        
        # Get skill progress
        skill_progress = calculate_skill_progress(user_activities)
        
        # Get learning path progress
        learning_path_progress = calculate_learning_path_progress(user_activities)
        
        # Get achievements
        achievements = get_user_achievements(user_activities)
        
        # Get recent activity
        recent_activity = get_recent_activity(user_activities)
        
        return {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "progress_metrics": progress_metrics,
            "skill_progress": skill_progress,
            "learning_path_progress": learning_path_progress,
            "achievements": achievements,
            "recent_activity": recent_activity
        }
        
    except Exception as e:
        print(f"❌ Progress overview error: {e}")
        raise HTTPException(status_code=500, detail=f"Progress overview error: {e}")

def calculate_progress_metrics(activities: List[Dict]) -> Dict:
    """Calculate overall progress metrics"""
    
    # Count different types of activities
    activity_counts = {}
    for activity in activities:
        activity_type = activity.get("activity_type", "unknown")
        activity_counts[activity_type] = activity_counts.get(activity_type, 0) + 1
    
    # Calculate engagement score
    engagement_score = calculate_engagement_score(activities)
    
    # Calculate learning streak
    learning_streak = calculate_learning_streak(activities)
    
    # Calculate total time spent
    total_time_spent = calculate_total_time_spent(activities)
    
    return {
        "total_activities": len(activities),
        "activity_breakdown": activity_counts,
        "engagement_score": engagement_score,
        "learning_streak": learning_streak,
        "total_time_spent": total_time_spent,
        "average_session_length": calculate_average_session_length(activities),
        "completion_rate": calculate_completion_rate(activities)
    }

def calculate_skill_progress(activities: List[Dict]) -> Dict:
    """Calculate progress for each skill"""
    
    skill_progress = {}
    
    # Group activities by skill
    for activity in activities:
        activity_data = activity.get("activity_data", {})
        
        # Extract skill from different activity types
        skill = None
        if activity.get("activity_type") == "resume_upload":
            skills = activity_data.get("skills", [])
            for skill_name in skills:
                if skill_name not in skill_progress:
                    skill_progress[skill_name] = {
                        "skill": skill_name,
                        "progress_percentage": 0,
                        "completed_modules": [],
                        "current_module": None,
                        "time_spent": 0,
                        "last_activity": None,
                        "assessment_score": None
                    }
        
        elif activity.get("activity_type") == "assessment_completed":
            skill_scores = activity_data.get("skill_scores", {})
            for skill_name, score in skill_scores.items():
                if skill_name not in skill_progress:
                    skill_progress[skill_name] = {
                        "skill": skill_name,
                        "progress_percentage": 0,
                        "completed_modules": [],
                        "current_module": None,
                        "time_spent": 0,
                        "last_activity": activity.get("timestamp"),
                        "assessment_score": score
                    }
                else:
                    skill_progress[skill_name]["assessment_score"] = score
                    skill_progress[skill_name]["last_activity"] = activity.get("timestamp")
    
    # Calculate progress percentages based on activities
    for skill_name, progress in skill_progress.items():
        # Calculate progress based on assessment scores and activities
        assessment_score = progress.get("assessment_score", 0)
        if assessment_score:
            progress["progress_percentage"] = min(assessment_score * 10, 100)  # Convert score to percentage
        
        # Add completed modules based on activities
        skill_activities = [a for a in activities if skill_name in str(a.get("activity_data", {}))]
        progress["completed_modules"] = get_completed_modules(skill_activities)
        
        # Calculate time spent
        progress["time_spent"] = calculate_skill_time_spent(skill_activities)
    
    return list(skill_progress.values())

def calculate_learning_path_progress(activities: List[Dict]) -> Dict:
    """Calculate learning path progress"""
    
    # Find learning path generation activities
    learning_path_activities = [
        a for a in activities 
        if a.get("activity_type") == "learning_path_generated"
    ]
    
    if not learning_path_activities:
        return {
            "has_learning_path": False,
            "current_path": None,
            "completed_modules": 0,
            "total_modules": 0,
            "progress_percentage": 0
        }
    
    latest_path = learning_path_activities[-1]
    path_data = latest_path.get("activity_data", {})
    
    # Calculate progress through the learning path
    completed_modules = count_completed_modules(activities)
    total_modules = len(path_data.get("learning_path", []))
    
    progress_percentage = (completed_modules / total_modules * 100) if total_modules > 0 else 0
    
    return {
        "has_learning_path": True,
        "current_path": path_data.get("learning_path", []),
        "completed_modules": completed_modules,
        "total_modules": total_modules,
        "progress_percentage": round(progress_percentage, 2),
        "estimated_completion": calculate_estimated_completion(activities, total_modules - completed_modules)
    }

def get_user_achievements(activities: List[Dict]) -> List[Dict]:
    """Get user achievements based on activities"""
    
    achievements = []
    
    # Count different types of achievements
    total_activities = len(activities)
    assessment_count = len([a for a in activities if a.get("activity_type") == "assessment_completed"])
    mentor_questions = len([a for a in activities if a.get("activity_type") == "mentor_question"])
    hackathon_applications = len([a for a in activities if a.get("activity_type") == "hackathon_applied"])
    
    # Define achievement thresholds
    if total_activities >= 10:
        achievements.append({
            "id": "first_10_activities",
            "title": "Getting Started",
            "description": "Completed 10 activities",
            "type": "milestone",
            "points": 50,
            "earned_at": get_achievement_date(activities, 10)
        })
    
    if assessment_count >= 1:
        achievements.append({
            "id": "first_assessment",
            "title": "Skill Assessor",
            "description": "Completed your first skill assessment",
            "type": "milestone",
            "points": 100,
            "earned_at": get_achievement_date([a for a in activities if a.get("activity_type") == "assessment_completed"], 1)
        })
    
    if mentor_questions >= 5:
        achievements.append({
            "id": "mentor_learner",
            "title": "Mentor Seeker",
            "description": "Asked 5 questions to AI mentor",
            "type": "milestone",
            "points": 75,
            "earned_at": get_achievement_date([a for a in activities if a.get("activity_type") == "mentor_question"], 5)
        })
    
    if hackathon_applications >= 1:
        achievements.append({
            "id": "hackathon_participant",
            "title": "Hackathon Participant",
            "description": "Applied for your first hackathon",
            "type": "milestone",
            "points": 150,
            "earned_at": get_achievement_date([a for a in activities if a.get("activity_type") == "hackathon_applied"], 1)
        })
    
    return achievements

def get_recent_activity(activities: List[Dict], limit: int = 10) -> List[Dict]:
    """Get recent activity for progress tracking"""
    
    # Sort by timestamp and get recent activities
    sorted_activities = sorted(
        activities, 
        key=lambda x: x.get("timestamp", "2024-01-01T00:00:00"),
        reverse=True
    )
    
    recent_activities = []
    for activity in sorted_activities[:limit]:
        recent_activities.append({
            "activity_type": activity.get("activity_type"),
            "timestamp": activity.get("timestamp"),
            "description": get_activity_description(activity),
            "impact": get_activity_impact(activity)
        })
    
    return recent_activities

def calculate_engagement_score(activities: List[Dict]) -> float:
    """Calculate user engagement score"""
    
    # Weight different activity types
    activity_weights = {
        "resume_upload": 10,
        "assessment_completed": 15,
        "mentor_question": 5,
        "learning_path_generated": 8,
        "hackathon_applied": 12,
        "hackathon_project_submitted": 20,
        "daily_tip_requested": 2
    }
    
    score = 0
    for activity in activities:
        activity_type = activity.get("activity_type", "unknown")
        weight = activity_weights.get(activity_type, 1)
        score += weight
    
    return score

def calculate_learning_streak(activities: List[Dict]) -> int:
    """Calculate consecutive days of learning activity"""
    
    if not activities:
        return 0
    
    # Sort activities by date
    sorted_activities = sorted(
        activities, 
        key=lambda x: x.get("timestamp", "2024-01-01T00:00:00")
    )
    
    # Group by date
    daily_activities = {}
    for activity in sorted_activities:
        timestamp = datetime.fromisoformat(activity.get("timestamp", "2024-01-01T00:00:00"))
        date_key = timestamp.strftime("%Y-%m-%d")
        
        if date_key not in daily_activities:
            daily_activities[date_key] = []
        daily_activities[date_key].append(activity)
    
    # Calculate streak
    dates = sorted(daily_activities.keys())
    streak = 0
    current_date = datetime.now().date()
    
    for i in range(len(dates) - 1, -1, -1):
        activity_date = datetime.strptime(dates[i], "%Y-%m-%d").date()
        days_diff = (current_date - activity_date).days
        
        if days_diff == streak:
            streak += 1
        else:
            break
    
    return streak

def calculate_total_time_spent(activities: List[Dict]) -> int:
    """Calculate total time spent learning"""
    
    total_time = 0
    
    for activity in activities:
        activity_data = activity.get("activity_data", {})
        
        # Extract time from different activity types
        if activity.get("activity_type") == "assessment_completed":
            time_taken = activity_data.get("time_taken", 0)
            total_time += time_taken // 60  # Convert seconds to minutes
        
        elif activity.get("activity_type") == "learning_session":
            duration = activity_data.get("duration", 0)
            total_time += duration
    
    return total_time

def calculate_average_session_length(activities: List[Dict]) -> float:
    """Calculate average session length"""
    
    session_activities = [
        a for a in activities 
        if a.get("activity_type") in ["assessment_completed", "learning_session"]
    ]
    
    if not session_activities:
        return 0.0
    
    total_time = calculate_total_time_spent(session_activities)
    return round(total_time / len(session_activities), 2)

def calculate_completion_rate(activities: List[Dict]) -> float:
    """Calculate completion rate of started activities"""
    
    started_activities = len(activities)
    completed_activities = len([
        a for a in activities 
        if a.get("activity_type") in ["assessment_completed", "learning_path_generated"]
    ])
    
    if started_activities == 0:
        return 0.0
    
    return round((completed_activities / started_activities) * 100, 2)

def get_completed_modules(activities: List[Dict]) -> List[str]:
    """Get list of completed modules"""
    
    completed_modules = []
    
    for activity in activities:
        activity_data = activity.get("activity_data", {})
        
        if activity.get("activity_type") == "module_completed":
            module_name = activity_data.get("module_name")
            if module_name:
                completed_modules.append(module_name)
    
    return completed_modules

def calculate_skill_time_spent(activities: List[Dict]) -> int:
    """Calculate time spent on a specific skill"""
    
    total_time = 0
    
    for activity in activities:
        activity_data = activity.get("activity_data", {})
        
        if activity.get("activity_type") == "assessment_completed":
            time_taken = activity_data.get("time_taken", 0)
            total_time += time_taken // 60
    
    return total_time

def count_completed_modules(activities: List[Dict]) -> int:
    """Count completed modules"""
    
    return len([
        a for a in activities 
        if a.get("activity_type") == "module_completed"
    ])

def calculate_estimated_completion(activities: List[Dict], remaining_modules: int) -> str:
    """Calculate estimated completion time"""
    
    if remaining_modules == 0:
        return "Completed"
    
    # Calculate average time per module
    module_activities = [
        a for a in activities 
        if a.get("activity_type") == "module_completed"
    ]
    
    if not module_activities:
        return "Unknown"
    
    avg_time_per_module = calculate_average_session_length(module_activities)
    total_estimated_time = avg_time_per_module * remaining_modules
    
    if total_estimated_time < 60:
        return f"{int(total_estimated_time)} minutes"
    elif total_estimated_time < 1440:  # Less than 24 hours
        hours = total_estimated_time / 60
        return f"{round(hours, 1)} hours"
    else:
        days = total_estimated_time / 1440
        return f"{round(days, 1)} days"

def get_achievement_date(activities: List[Dict], threshold: int) -> str:
    """Get date when achievement was earned"""
    
    if len(activities) < threshold:
        return None
    
    # Sort by timestamp and get the threshold activity
    sorted_activities = sorted(
        activities, 
        key=lambda x: x.get("timestamp", "2024-01-01T00:00:00")
    )
    
    return sorted_activities[threshold - 1].get("timestamp")

def get_activity_description(activity: Dict) -> str:
    """Get human-readable description of activity"""
    
    activity_type = activity.get("activity_type", "unknown")
    activity_data = activity.get("activity_data", {})
    
    descriptions = {
        "resume_upload": f"Uploaded resume with {len(activity_data.get('skills', []))} skills",
        "assessment_completed": f"Completed assessment with {len(activity_data.get('skill_scores', {}))} skills",
        "mentor_question": "Asked AI mentor a question",
        "learning_path_generated": "Generated personalized learning path",
        "hackathon_applied": f"Applied for hackathon: {activity_data.get('hackathon_title', 'Unknown')}",
        "hackathon_project_submitted": f"Submitted project for hackathon",
        "daily_tip_requested": "Requested daily learning tip"
    }
    
    return descriptions.get(activity_type, f"Completed {activity_type}")

def get_activity_impact(activity: Dict) -> str:
    """Get impact level of activity"""
    
    activity_type = activity.get("activity_type", "unknown")
    
    high_impact = ["assessment_completed", "hackathon_project_submitted", "learning_path_generated"]
    medium_impact = ["resume_upload", "hackathon_applied"]
    low_impact = ["mentor_question", "daily_tip_requested"]
    
    if activity_type in high_impact:
        return "high"
    elif activity_type in medium_impact:
        return "medium"
    else:
        return "low"

@router.post("/update")
async def update_progress(payload: ProgressUpdate):
    """Update user progress for a specific skill"""
    
    print(f"📈 Updating progress for user {payload.user_id}, skill: {payload.skill}")
    
    try:
        # Log progress update
        activity_tracker.log_activity(payload.user_id, "progress_updated", {
            "skill": payload.skill,
            "progress_percentage": payload.progress_percentage,
            "completed_modules": payload.completed_modules,
            "current_module": payload.current_module,
            "time_spent": payload.time_spent,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "message": "Progress updated successfully",
            "user_id": payload.user_id,
            "skill": payload.skill,
            "progress_percentage": payload.progress_percentage,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Progress update error: {e}")
        raise HTTPException(status_code=500, detail=f"Progress update error: {e}")

@router.post("/session/start")
async def start_learning_session(payload: LearningSession):
    """Start a learning session"""
    
    print(f"🎯 Starting learning session for user {payload.user_id}")
    
    try:
        # Log session start
        activity_tracker.log_activity(payload.user_id, "learning_session_started", {
            "skill": payload.skill,
            "module": payload.module,
            "start_time": payload.start_time,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "message": "Learning session started",
            "session_id": f"session_{payload.user_id}_{datetime.utcnow().timestamp()}",
            "start_time": payload.start_time
        }
        
    except Exception as e:
        print(f"❌ Session start error: {e}")
        raise HTTPException(status_code=500, detail=f"Session start error: {e}")

@router.post("/session/end")
async def end_learning_session(payload: LearningSession):
    """End a learning session"""
    
    print(f"✅ Ending learning session for user {payload.user_id}")
    
    try:
        # Calculate session duration
        start_time = datetime.fromisoformat(payload.start_time)
        end_time = datetime.fromisoformat(payload.end_time) if payload.end_time else datetime.utcnow()
        duration = int((end_time - start_time).total_seconds() / 60)  # Convert to minutes
        
        # Log session end
        activity_tracker.log_activity(payload.user_id, "learning_session_ended", {
            "skill": payload.skill,
            "module": payload.module,
            "start_time": payload.start_time,
            "end_time": payload.end_time,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "message": "Learning session ended",
            "duration": duration,
            "end_time": payload.end_time
        }
        
    except Exception as e:
        print(f"❌ Session end error: {e}")
        raise HTTPException(status_code=500, detail=f"Session end error: {e}")

@router.get("/{user_id}/achievements")
async def get_user_achievements_detailed(user_id: str):
    """Get detailed achievements for a user"""
    
    try:
        user_activities = activity_tracker.get_user_activities(user_id, 1000)
        achievements = get_user_achievements(user_activities)
        
        return {
            "user_id": user_id,
            "achievements": achievements,
            "total_achievements": len(achievements),
            "total_points": sum(achievement.get("points", 0) for achievement in achievements)
        }
        
    except Exception as e:
        print(f"❌ Achievements error: {e}")
        raise HTTPException(status_code=500, detail=f"Achievements error: {e}")

@router.get("/{user_id}/streak")
async def get_learning_streak(user_id: str):
    """Get user's learning streak information"""
    
    try:
        user_activities = activity_tracker.get_user_activities(user_id, 1000)
        streak = calculate_learning_streak(user_activities)
        
        return {
            "user_id": user_id,
            "current_streak": streak,
            "longest_streak": streak,  # In a real app, you'd track this separately
            "streak_type": "daily",
            "last_activity": get_last_activity_date(user_activities)
        }
        
    except Exception as e:
        print(f"❌ Streak error: {e}")
        raise HTTPException(status_code=500, detail=f"Streak error: {e}")

def get_last_activity_date(activities: List[Dict]) -> str:
    """Get date of last activity"""
    
    if not activities:
        return None
    
    # Sort by timestamp and get the most recent
    sorted_activities = sorted(
        activities, 
        key=lambda x: x.get("timestamp", "2024-01-01T00:00:00"),
        reverse=True
    )
    
    return sorted_activities[0].get("timestamp")
