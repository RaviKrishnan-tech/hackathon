from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from utils.ai_mentor import ai_mentor
from utils.user_activity_tracker import activity_tracker
import json

router = APIRouter(prefix="/recommend", tags=["Learning Recommendations"])

class LearningPathRequest(BaseModel):
    user_id: str
    skills: List[str]
    skill_levels: Dict[str, str]
    goals: List[str]
    time_available: str  # "1-2 hours", "3-5 hours", "5+ hours"
    preferred_format: List[str]  # ["video", "text", "interactive", "project"]

class ModuleCompletion(BaseModel):
    user_id: str
    module_id: str
    skill: str
    completion_percentage: float
    time_spent: int  # in minutes
    feedback: Optional[str] = None

@router.post("/learning-path")
async def generate_learning_path(payload: LearningPathRequest):
    """Generate personalized learning path using AI"""
    
    print(f"🎯 Generating learning path for user {payload.user_id}")
    print(f"📋 Skills: {payload.skills}")
    print(f"🎯 Goals: {payload.goals}")
    
    try:
        # Generate learning path using AI mentor
        learning_path = await ai_mentor.generate_learning_path(
            payload.user_id,
            payload.skills,
            payload.skill_levels
        )
        
        # Enhance with user preferences
        enhanced_path = enhance_learning_path(learning_path, payload)
        
        # Log learning path generation
        activity_tracker.log_activity(payload.user_id, "learning_path_generated", {
            "skills": payload.skills,
            "skill_levels": payload.skill_levels,
            "goals": payload.goals,
            "time_available": payload.time_available,
            "preferred_format": payload.preferred_format,
            "path_length": len(enhanced_path.get("learning_path", [])),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "user_id": payload.user_id,
            "learning_path": enhanced_path,
            "generated_at": datetime.utcnow().isoformat(),
            "estimated_completion": enhanced_path.get("overall_timeline", "Unknown")
        }
        
    except Exception as e:
        print(f"❌ Learning path generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Learning path generation error: {e}")

def enhance_learning_path(learning_path: Dict, user_preferences: LearningPathRequest) -> Dict:
    """Enhance learning path with user preferences and additional details"""
    
    enhanced_modules = []
    
    for skill_path in learning_path.get("learning_path", []):
        skill = skill_path.get("skill", "")
        modules = skill_path.get("modules", [])
        
        enhanced_skill_modules = []
        for module in modules:
            enhanced_module = {
                **module,
                "module_id": f"{skill}_{len(enhanced_skill_modules)}",
                "difficulty": determine_difficulty(skill_path.get("current_level", "beginner")),
                "estimated_time": adjust_time_for_preferences(module.get("duration", "1 week"), user_preferences.time_available),
                "resources": filter_resources_by_preferences(module.get("resources", []), user_preferences.preferred_format),
                "prerequisites": get_prerequisites(skill, skill_path.get("current_level", "beginner")),
                "learning_objectives": generate_learning_objectives(skill, module.get("title", "")),
                "assessment_criteria": generate_assessment_criteria(skill, module.get("title", "")),
                "completion_status": "not_started"
            }
            enhanced_skill_modules.append(enhanced_module)
        
        enhanced_skill_path = {
            **skill_path,
            "modules": enhanced_skill_modules,
            "priority": calculate_priority(skill, user_preferences.goals),
            "estimated_skill_gain": calculate_skill_gain(skill_path.get("current_level", "beginner"))
        }
        enhanced_modules.append(enhanced_skill_path)
    
    return {
        **learning_path,
        "learning_path": enhanced_modules,
        "user_preferences": {
            "time_available": user_preferences.time_available,
            "preferred_format": user_preferences.preferred_format,
            "goals": user_preferences.goals
        },
        "adaptive_features": {
            "difficulty_adjustment": True,
            "pace_adjustment": True,
            "content_personalization": True
        }
    }

def determine_difficulty(current_level: str) -> str:
    """Determine module difficulty based on current skill level"""
    
    difficulty_mapping = {
        "beginner": "beginner",
        "intermediate": "intermediate", 
        "advanced": "advanced"
    }
    
    return difficulty_mapping.get(current_level, "intermediate")

def adjust_time_for_preferences(base_time: str, time_available: str) -> str:
    """Adjust estimated time based on user's available time"""
    
    # Parse base time
    if "week" in base_time:
        base_hours = 7 * 24  # Assume 7 days
    elif "day" in base_time:
        base_hours = 24
    elif "hour" in base_time:
        base_hours = 1
    else:
        base_hours = 5  # Default
    
    # Adjust based on user preference
    if time_available == "1-2 hours":
        adjusted_hours = min(base_hours, 2)
    elif time_available == "3-5 hours":
        adjusted_hours = min(base_hours, 5)
    else:  # 5+ hours
        adjusted_hours = base_hours
    
    if adjusted_hours < 1:
        return f"{int(adjusted_hours * 60)} minutes"
    elif adjusted_hours < 24:
        return f"{int(adjusted_hours)} hours"
    else:
        days = adjusted_hours / 24
        return f"{int(days)} days"

def filter_resources_by_preferences(resources: List[str], preferred_format: List[str]) -> List[str]:
    """Filter resources based on user's preferred format"""
    
    # Map resource types to formats
    resource_format_mapping = {
        "video": ["YouTube", "Udemy", "Coursera", "video", "tutorial"],
        "text": ["documentation", "book", "article", "blog", "text"],
        "interactive": ["Codecademy", "interactive", "practice", "exercise"],
        "project": ["GitHub", "project", "build", "create"]
    }
    
    filtered_resources = []
    
    for resource in resources:
        resource_lower = resource.lower()
        for format_type in preferred_format:
            if format_type in resource_format_mapping:
                format_keywords = resource_format_mapping[format_type]
                if any(keyword in resource_lower for keyword in format_keywords):
                    filtered_resources.append(resource)
                    break
    
    # If no resources match preferences, return original list
    return filtered_resources if filtered_resources else resources

def get_prerequisites(skill: str, current_level: str) -> List[str]:
    """Get prerequisites for a skill/module"""
    
    prerequisites = {
        "python": {
            "beginner": ["basic computer skills"],
            "intermediate": ["python basics", "programming fundamentals"],
            "advanced": ["python intermediate", "data structures", "algorithms"]
        },
        "javascript": {
            "beginner": ["basic computer skills"],
            "intermediate": ["javascript basics", "HTML/CSS"],
            "advanced": ["javascript intermediate", "DOM manipulation", "async programming"]
        },
        "react": {
            "beginner": ["javascript basics", "HTML/CSS"],
            "intermediate": ["react basics", "component lifecycle"],
            "advanced": ["react intermediate", "state management", "hooks"]
        },
        "sql": {
            "beginner": ["basic computer skills"],
            "intermediate": ["sql basics", "database concepts"],
            "advanced": ["sql intermediate", "database design", "optimization"]
        }
    }
    
    return prerequisites.get(skill, {}).get(current_level, [])

def generate_learning_objectives(skill: str, module_title: str) -> List[str]:
    """Generate learning objectives for a module"""
    
    objectives = {
        "python": [
            "Understand Python syntax and basic concepts",
            "Write simple Python programs",
            "Use Python data structures effectively",
            "Implement basic algorithms in Python"
        ],
        "javascript": [
            "Master JavaScript fundamentals",
            "Understand DOM manipulation",
            "Work with asynchronous programming",
            "Build interactive web applications"
        ],
        "react": [
            "Understand React component architecture",
            "Manage component state and props",
            "Implement React hooks effectively",
            "Build scalable React applications"
        ],
        "sql": [
            "Write basic SQL queries",
            "Understand database relationships",
            "Optimize database performance",
            "Design efficient database schemas"
        ]
    }
    
    return objectives.get(skill, [
        f"Master {skill} fundamentals",
        f"Apply {skill} in practical scenarios",
        f"Build projects using {skill}",
        f"Understand advanced {skill} concepts"
    ])

def generate_assessment_criteria(skill: str, module_title: str) -> List[str]:
    """Generate assessment criteria for a module"""
    
    return [
        "Complete all module exercises",
        "Build a practical project",
        "Pass the module assessment",
        "Demonstrate understanding through code review"
    ]

def calculate_priority(skill: str, goals: List[str]) -> str:
    """Calculate priority of a skill based on user goals"""
    
    # Simple priority calculation based on goal alignment
    goal_keywords = " ".join(goals).lower()
    skill_lower = skill.lower()
    
    if skill_lower in goal_keywords:
        return "high"
    elif any(keyword in goal_keywords for keyword in ["web", "frontend", "backend"]) and skill in ["javascript", "react", "python"]:
        return "medium"
                else:
        return "low"

def calculate_skill_gain(current_level: str) -> str:
    """Calculate expected skill gain from completing the path"""
    
    skill_gains = {
        "beginner": "Beginner to Intermediate",
        "intermediate": "Intermediate to Advanced", 
        "advanced": "Advanced to Expert"
    }
    
    return skill_gains.get(current_level, "Skill improvement")

@router.post("/module/complete")
async def complete_module(payload: ModuleCompletion):
    """Mark a module as completed"""
    
    print(f"✅ User {payload.user_id} completed module {payload.module_id}")
    
    try:
        # Log module completion
        activity_tracker.log_activity(payload.user_id, "module_completed", {
            "module_id": payload.module_id,
            "skill": payload.skill,
            "completion_percentage": payload.completion_percentage,
            "time_spent": payload.time_spent,
            "feedback": payload.feedback,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Check if this completes a skill path
        await check_skill_completion(payload.user_id, payload.skill)
        
        return {
            "message": "Module completed successfully",
            "module_id": payload.module_id,
            "completion_percentage": payload.completion_percentage,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Module completion error: {e}")
        raise HTTPException(status_code=500, detail=f"Module completion error: {e}")

async def check_skill_completion(user_id: str, skill: str):
    """Check if user has completed a skill path"""
    
    try:
        # Get user's module completions for this skill
        user_activities = activity_tracker.get_user_activities(user_id, 1000)
        skill_modules = [
            a for a in user_activities 
            if a.get("activity_type") == "module_completed" and 
            a.get("activity_data", {}).get("skill") == skill
        ]
        
        # Check if all modules for this skill are completed
        # This is a simplified check - in a real app, you'd have a proper module tracking system
        
        if len(skill_modules) >= 3:  # Assume 3 modules per skill
            # Log skill completion
            activity_tracker.log_activity(user_id, "skill_completed", {
                "skill": skill,
                "modules_completed": len(skill_modules),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            print(f"🎉 User {user_id} completed skill: {skill}")
        
    except Exception as e:
        print(f"❌ Skill completion check error: {e}")

@router.get("/{user_id}/recommendations")
async def get_personalized_recommendations(user_id: str):
    """Get personalized learning recommendations"""
    
    try:
        # Get user's current skills and progress
        user_activities = activity_tracker.get_user_activities(user_id, 100)
        
        # Extract current skills
        current_skills = extract_current_skills(user_activities)
        
        # Get skill levels
        skill_levels = assess_skill_levels(user_activities)
        
        # Generate recommendations
        recommendations = generate_recommendations(current_skills, skill_levels, user_activities)
        
        return {
            "user_id": user_id,
            "current_skills": current_skills,
            "skill_levels": skill_levels,
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Recommendations error: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendations error: {e}")

def extract_current_skills(activities: List[Dict]) -> List[str]:
    """Extract current skills from user activities"""
    
    skills = set()
    
    for activity in activities:
        activity_data = activity.get("activity_data", {})
        
        if activity.get("activity_type") == "resume_upload":
            skills.update(activity_data.get("skills", []))
        
        elif activity.get("activity_type") == "assessment_completed":
            skill_scores = activity_data.get("skill_scores", {})
            skills.update(skill_scores.keys())
    
    return list(skills)

def assess_skill_levels(activities: List[Dict]) -> Dict[str, str]:
    """Assess skill levels based on activities"""
    
    skill_levels = {}
    
    for activity in activities:
        if activity.get("activity_type") == "assessment_completed":
            skill_scores = activity.get("activity_data", {}).get("skill_scores", {})
            
            for skill, score in skill_scores.items():
                if score >= 8.0:
                    skill_levels[skill] = "advanced"
                elif score >= 5.0:
                    skill_levels[skill] = "intermediate"
                else:
                    skill_levels[skill] = "beginner"
    
    return skill_levels

def generate_recommendations(current_skills: List[str], skill_levels: Dict[str, str], activities: List[Dict]) -> Dict:
    """Generate personalized recommendations"""
    
    recommendations = {
        "next_skills": [],
        "improvement_areas": [],
        "project_suggestions": [],
        "resource_recommendations": []
    }
    
    # Suggest next skills based on current skills
    skill_ecosystem = {
        "python": ["django", "flask", "data science", "machine learning"],
        "javascript": ["react", "node.js", "typescript", "vue"],
        "react": ["redux", "next.js", "graphql", "testing"],
        "sql": ["database design", "optimization", "nosql", "data engineering"]
    }
    
    for skill in current_skills:
        if skill in skill_ecosystem:
            recommendations["next_skills"].extend(skill_ecosystem[skill])
    
    # Remove duplicates
    recommendations["next_skills"] = list(set(recommendations["next_skills"]))
    
    # Identify improvement areas
    for skill, level in skill_levels.items():
        if level == "beginner":
            recommendations["improvement_areas"].append(f"Advance {skill} to intermediate level")
        elif level == "intermediate":
            recommendations["improvement_areas"].append(f"Master {skill} at advanced level")
    
    # Suggest projects
    for skill in current_skills:
        if skill == "python":
            recommendations["project_suggestions"].append("Build a web scraper")
            recommendations["project_suggestions"].append("Create a REST API")
        elif skill == "javascript":
            recommendations["project_suggestions"].append("Build a todo app")
            recommendations["project_suggestions"].append("Create a weather app")
        elif skill == "react":
            recommendations["project_suggestions"].append("Build a portfolio website")
            recommendations["project_suggestions"].append("Create a social media clone")
    
    # Recommend resources
    recommendations["resource_recommendations"] = [
        "Practice on LeetCode/HackerRank",
        "Build projects for your portfolio",
        "Join coding communities",
        "Follow tech blogs and tutorials"
    ]
    
    return recommendations
