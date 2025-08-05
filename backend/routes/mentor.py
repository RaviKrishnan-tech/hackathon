from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, List, Optional
from utils.ai_mentor import ai_mentor
from utils.user_activity_tracker import activity_tracker
from utils.skill_analyzer import skill_analyzer
import json
from datetime import datetime

router = APIRouter(prefix="/mentor", tags=["AI Mentor"])

class MentorMessage(BaseModel):
    user_id: str
    message: str
    context: Optional[Dict] = None

class MentorSession(BaseModel):
    user_id: str
    session_id: str
    topic: str
    start_time: str
    messages: List[Dict]

@router.post("/chat")
async def chat_with_mentor(payload: MentorMessage):
    """Chat with AI mentor and get personalized guidance"""
    try:
        # Get user context for personalized responses
        user_profile = activity_tracker.get_user_profile(payload.user_id)
        user_context = {}
        
        if "error" not in user_profile:
            # Get recent assessment scores if available
            assessment_activities = [
                activity for activity in activity_tracker.get_user_activities(payload.user_id, 10)
                if activity["activity_type"] == "assessment_completed"
            ]
            
            if assessment_activities:
                latest_assessment = assessment_activities[0]
                if "scores" in latest_assessment["details"]:
                    user_context["recent_assessment_scores"] = latest_assessment["details"]["scores"]
            
            # Add learning progress context
            learning_progress = activity_tracker.learning_progress.get(payload.user_id, {})
            if learning_progress:
                user_context["current_learning_modules"] = list(learning_progress.keys())
        
        # Merge with provided context
        if payload.context:
            user_context.update(payload.context)
        
        # Get mentor response
        mentor_response = ai_mentor.get_mentor_response(
            payload.user_id,
            payload.message,
            user_context
        )
        
        # Log mentor session
        session_data = {
            "message": payload.message,
            "response": mentor_response["response"],
            "context": user_context,
            "suggestions": mentor_response.get("suggestions", [])
        }
        
        activity_tracker.log_mentor_session(payload.user_id, session_data)
        
        return {
            "user_id": payload.user_id,
            "mentor_response": mentor_response["response"],
            "suggestions": mentor_response.get("suggestions", []),
            "timestamp": mentor_response["timestamp"],
            "context_used": user_context
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get mentor response: {e}")

@router.get("/{user_id}/sessions")
async def get_mentor_sessions(user_id: str, limit: int = 20):
    """Get user's mentor session history"""
    try:
        sessions = activity_tracker.mentor_sessions.get(user_id, [])
        return {
            "user_id": user_id,
            "sessions": sessions[-limit:],
            "total_sessions": len(sessions),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sessions: {e}")

@router.get("/{user_id}/conversation-history")
async def get_conversation_history(user_id: str, limit: int = 10):
    """Get recent conversation history with AI mentor"""
    try:
        history = ai_mentor.get_conversation_history(user_id, limit)
        return {
            "user_id": user_id,
            "conversation_history": history,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation history: {e}")

@router.post("/{user_id}/learning-guidance")
async def get_learning_guidance(user_id: str, skill_gaps: List[str]):
    """Get personalized learning guidance for specific skill gaps"""
    try:
        # Get learning path suggestions
        learning_path = ai_mentor.get_learning_path_suggestions(user_id, skill_gaps)
        
        # Get additional mentor guidance
        guidance_prompt = f"I need help improving these skills: {', '.join(skill_gaps)}. " \
                         f"Please provide specific guidance on how to approach learning these skills effectively."
        
        mentor_guidance = ai_mentor.get_mentor_response(
            user_id,
            guidance_prompt,
            {"skill_gaps": skill_gaps}
        )
        
        return {
            "user_id": user_id,
            "skill_gaps": skill_gaps,
            "learning_path": learning_path,
            "mentor_guidance": mentor_guidance["response"],
            "suggestions": mentor_guidance.get("suggestions", []),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get learning guidance: {e}")

@router.post("/{user_id}/code-review")
async def get_code_review(user_id: str, code: str, language: str = "python"):
    """Get AI mentor code review and suggestions"""
    try:
        review_prompt = f"Please review this {language} code and provide feedback:\n\n{code}\n\n" \
                       f"Provide feedback on:\n1. Code quality and best practices\n" \
                       f"2. Potential improvements\n3. Common pitfalls to avoid\n" \
                       f"4. Alternative approaches"
        
        code_review = ai_mentor.get_mentor_response(
            user_id,
            review_prompt,
            {"code_review": True, "language": language}
        )
        
        # Log code review session
        session_data = {
            "type": "code_review",
            "language": language,
            "code_length": len(code),
            "response": code_review["response"]
        }
        
        activity_tracker.log_mentor_session(user_id, session_data)
        
        return {
            "user_id": user_id,
            "code_review": code_review["response"],
            "suggestions": code_review.get("suggestions", []),
            "language": language,
            "timestamp": code_review["timestamp"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get code review: {e}")

@router.post("/{user_id}/debug-help")
async def get_debug_help(user_id: str, error_message: str, code_context: str = ""):
    """Get AI mentor help with debugging"""
    try:
        debug_prompt = f"I'm getting this error: {error_message}\n\n" \
                      f"Code context: {code_context}\n\n" \
                      f"Please help me understand and fix this error."
        
        debug_help = ai_mentor.get_mentor_response(
            user_id,
            debug_prompt,
            {"debug_help": True, "error": error_message}
        )
        
        # Log debug session
        session_data = {
            "type": "debug_help",
            "error_message": error_message,
            "response": debug_help["response"]
        }
        
        activity_tracker.log_mentor_session(user_id, session_data)
        
        return {
            "user_id": user_id,
            "debug_help": debug_help["response"],
            "suggestions": debug_help.get("suggestions", []),
            "error_message": error_message,
            "timestamp": debug_help["timestamp"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get debug help: {e}")

@router.get("/{user_id}/recommendations")
async def get_personalized_recommendations(user_id: str):
    """Get personalized learning and career recommendations"""
    try:
        # Get user's skill analysis
        user_profile = activity_tracker.get_user_profile(user_id)
        if "error" in user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get recent assessment data
        assessment_activities = [
            activity for activity in activity_tracker.get_user_activities(user_id, 5)
            if activity["activity_type"] == "assessment_completed"
        ]
        
        recommendations = {
            "user_id": user_id,
            "learning_recommendations": [],
            "career_recommendations": [],
            "skill_development_plan": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if assessment_activities:
            latest_assessment = assessment_activities[0]
            if "scores" in latest_assessment["details"]:
                scores = latest_assessment["details"]["scores"]
                skill_analysis = skill_analyzer.analyze_skill_strengths(scores)
                
                # Generate recommendations based on skill analysis
                recommendations_prompt = f"Based on these assessment scores: {scores}, " \
                                       f"provide specific recommendations for:\n" \
                                       f"1. Learning priorities\n" \
                                       f"2. Career development\n" \
                                       f"3. Skill improvement strategies"
                
                ai_recommendations = ai_mentor.get_mentor_response(
                    user_id,
                    recommendations_prompt,
                    {"assessment_scores": scores, "skill_analysis": skill_analysis}
                )
                
                recommendations["ai_recommendations"] = ai_recommendations["response"]
                recommendations["skill_analysis"] = skill_analysis
        
        return recommendations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {e}")

# WebSocket endpoint for real-time chat
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Get mentor response
            mentor_response = ai_mentor.get_mentor_response(
                user_id,
                message_data["message"],
                message_data.get("context")
            )
            
            # Send response back
            response_data = {
                "type": "mentor_response",
                "response": mentor_response["response"],
                "suggestions": mentor_response.get("suggestions", []),
                "timestamp": mentor_response["timestamp"]
            }
            
            await manager.send_personal_message(json.dumps(response_data), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket) 