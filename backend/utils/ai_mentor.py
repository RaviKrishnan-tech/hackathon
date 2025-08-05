import google.generativeai as genai
import os
from typing import Dict, List, Optional
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class AIMentor:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-pro")
        self.conversation_history = {}
        
    def get_mentor_response(self, user_id: str, message: str, context: Dict = None) -> Dict:
        """Get AI mentor response with context awareness"""
        
        # Build context-aware prompt
        context_prompt = self._build_context_prompt(context)
        
        system_prompt = f"""You are an expert coding mentor with 10+ years of experience. 
        Your role is to help students learn programming concepts, debug code, and understand best practices.
        
        {context_prompt}
        
        Guidelines:
        - Provide clear, step-by-step explanations
        - Include code examples when relevant
        - Suggest additional resources for deeper learning
        - Be encouraging and supportive
        - Ask follow-up questions to ensure understanding
        - Provide practical examples and real-world applications
        
        Current user message: {message}
        """
        
        try:
            response = self.model.generate_content(system_prompt)
            
            # Store conversation history
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            self.conversation_history[user_id].append({
                "timestamp": datetime.utcnow().isoformat(),
                "user_message": message,
                "mentor_response": response.text,
                "context": context
            })
            
            return {
                "response": response.text,
                "timestamp": datetime.utcnow().isoformat(),
                "suggestions": self._generate_follow_up_suggestions(message, context)
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I'm having trouble processing your request. Please try again. Error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
                "suggestions": []
            }
    
    def _build_context_prompt(self, context: Dict = None) -> str:
        """Build context-aware prompt based on user's current learning state"""
        if not context:
            return ""
        
        context_parts = []
        
        if context.get("current_skill"):
            context_parts.append(f"User is currently learning: {context['current_skill']}")
        
        if context.get("skill_level"):
            context_parts.append(f"User's skill level: {context['skill_level']}")
        
        if context.get("recent_assessment_scores"):
            scores = context["recent_assessment_scores"]
            weak_skills = [skill for skill, score in scores.items() if score < 6.0]
            strong_skills = [skill for skill, score in scores.items() if score >= 8.0]
            
            if weak_skills:
                context_parts.append(f"Areas needing improvement: {', '.join(weak_skills)}")
            if strong_skills:
                context_parts.append(f"Strong areas: {', '.join(strong_skills)}")
        
        if context.get("learning_goals"):
            context_parts.append(f"Learning goals: {context['learning_goals']}")
        
        return "Context: " + ". ".join(context_parts) if context_parts else ""
    
    def _generate_follow_up_suggestions(self, message: str, context: Dict = None) -> List[str]:
        """Generate follow-up questions and suggestions"""
        suggestions = []
        
        # Add context-specific suggestions
        if context and context.get("current_skill"):
            skill = context["current_skill"]
            suggestions.extend([
                f"Would you like to practice {skill} with some coding exercises?",
                f"Should we explore advanced concepts in {skill}?",
                f"Would you like to see real-world applications of {skill}?"
            ])
        
        # Add general suggestions
        suggestions.extend([
            "Would you like me to explain this concept in more detail?",
            "Should we work through a practical example?",
            "Would you like to see some common mistakes to avoid?"
        ])
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def get_learning_path_suggestions(self, user_id: str, skill_gaps: List[str]) -> Dict:
        """Generate personalized learning path suggestions"""
        
        prompt = f"""Based on the following skill gaps: {', '.join(skill_gaps)}
        
        Generate a structured learning path with:
        1. Recommended learning order
        2. Estimated time for each skill
        3. Key concepts to focus on
        4. Practice exercises
        5. Resources and references
        
        Format as JSON with structure:
        {{
            "learning_path": [
                {{
                    "skill": "skill_name",
                    "estimated_hours": 10,
                    "key_concepts": ["concept1", "concept2"],
                    "exercises": ["exercise1", "exercise2"],
                    "resources": ["resource1", "resource2"]
                }}
            ]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Extract JSON from response
            response_text = response.text
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                return json.loads(json_str)
            else:
                # Try to parse as JSON directly
                return json.loads(response_text)
        except Exception as e:
            return {
                "learning_path": [],
                "error": f"Failed to generate learning path: {str(e)}"
            }
    
    def get_conversation_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent conversation history for a user"""
        if user_id not in self.conversation_history:
            return []
        
        return self.conversation_history[user_id][-limit:]

# Global mentor instance
ai_mentor = AIMentor() 