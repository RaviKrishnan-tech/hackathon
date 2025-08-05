import google.generativeai as genai
import os
from typing import Dict, List, Optional
from datetime import datetime
import json
from dotenv import load_dotenv

load_dotenv()

class AIMentor:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key and self.api_key != "your_gemini_api_key_here":
            genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel("gemini-pro")
        else:
            self.model = None
            print("⚠️ GEMINI_API_KEY not configured. AI Mentor will use fallback responses.")
    
    async def get_mentor_response(self, user_id: str, question: str, context: Dict = None) -> Dict:
        """Get AI mentor response to user questions"""
        
        print(f"🤖 AI Mentor: User {user_id} asked: {question[:100]}...")
        
        if not self.model:
            return self._get_fallback_response(question)
        
        try:
            # Build context-aware prompt
            prompt = self._build_mentor_prompt(question, context)
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Try to parse as JSON for structured response
            try:
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return {
                        "response": result.get("answer", response_text),
                        "resources": result.get("resources", []),
                        "next_steps": result.get("next_steps", []),
                        "confidence": result.get("confidence", "high"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
            except:
                pass
            
            # Return simple response if JSON parsing fails
            return {
                "response": response_text,
                "resources": [],
                "next_steps": [],
                "confidence": "medium",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ AI Mentor error: {e}")
            return self._get_fallback_response(question)
    
    def _build_mentor_prompt(self, question: str, context: Dict = None) -> str:
        """Build context-aware prompt for AI mentor"""
        
        base_prompt = f"""
        You are an expert AI mentor helping a student with programming and technology questions.
        
        Student Question: {question}
        
        Context: {json.dumps(context) if context else "No additional context provided"}
        
        Provide a helpful, detailed response in JSON format:
        {{
            "answer": "Your detailed answer to the question",
            "resources": ["resource1", "resource2", "resource3"],
            "next_steps": ["step1", "step2", "step3"],
            "confidence": "high/medium/low"
        }}
        
        Guidelines:
        - Be encouraging and supportive
        - Provide practical, actionable advice
        - Include relevant learning resources
        - Suggest next steps for improvement
        - Keep explanations clear and beginner-friendly when appropriate
        """
        
        return base_prompt
    
    def _get_fallback_response(self, question: str) -> Dict:
        """Fallback response when AI is not available"""
        
        # Simple keyword-based responses
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["python", "programming", "code"]):
            return {
                "response": "For Python programming questions, I recommend starting with the official Python documentation and practicing with small projects. What specific Python concept are you struggling with?",
                "resources": ["Python.org documentation", "Codecademy Python course", "Real Python tutorials"],
                "next_steps": ["Practice with small exercises", "Build a simple project", "Join Python communities"],
                "confidence": "medium",
                "timestamp": datetime.utcnow().isoformat()
            }
        elif any(word in question_lower for word in ["javascript", "js", "web"]):
            return {
                "response": "JavaScript is essential for web development. Start with the basics of DOM manipulation and gradually move to frameworks like React. What aspect of JavaScript would you like to learn?",
                "resources": ["MDN Web Docs", "JavaScript.info", "Eloquent JavaScript"],
                "next_steps": ["Learn DOM manipulation", "Practice with browser console", "Build a simple web app"],
                "confidence": "medium",
                "timestamp": datetime.utcnow().isoformat()
            }
        elif any(word in question_lower for word in ["sql", "database"]):
            return {
                "response": "SQL is fundamental for data management. Start with basic SELECT statements and gradually learn JOINs and complex queries. What database concept are you working on?",
                "resources": ["SQL Tutorial", "W3Schools SQL", "SQLite documentation"],
                "next_steps": ["Practice with sample databases", "Learn about normalization", "Build a simple database"],
                "confidence": "medium",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            return {
                "response": "I'm here to help with your programming and technology questions! Could you provide more details about what you're working on?",
                "resources": ["Stack Overflow", "GitHub", "Documentation"],
                "next_steps": ["Research the topic", "Practice with examples", "Ask in communities"],
                "confidence": "low",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def generate_learning_path(self, user_id: str, skills: List[str], skill_levels: Dict[str, str]) -> Dict:
        """Generate personalized learning path using AI"""
        
        print(f"🎯 Generating learning path for user {user_id} with skills: {skills}")
        
        if not self.model:
            return self._get_fallback_learning_path(skills, skill_levels)
        
        try:
            prompt = f"""
            Generate a personalized learning path for a user with the following skills and levels:
            
            Skills: {skills}
            Skill Levels: {json.dumps(skill_levels)}
            
            Create a comprehensive learning path in JSON format:
        {{
            "learning_path": [
                {{
                    "skill": "skill_name",
                        "current_level": "beginner/intermediate/advanced",
                        "target_level": "next_level",
                        "modules": [
                            {{
                                "title": "Module Title",
                                "description": "Module description",
                                "duration": "estimated_time",
                                "resources": ["resource1", "resource2"],
                                "projects": ["project1", "project2"],
                                "assessment": "assessment_type"
                            }}
                        ],
                        "estimated_completion": "total_time"
                    }}
                ],
                "overall_timeline": "total_estimated_time",
                "priority_order": ["skill1", "skill2", "skill3"],
                "success_metrics": ["metric1", "metric2", "metric3"]
        }}
        """
            
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._get_fallback_learning_path(skills, skill_levels)
                
        except Exception as e:
            print(f"❌ Failed to generate AI learning path: {e}")
            return self._get_fallback_learning_path(skills, skill_levels)
    
    def _get_fallback_learning_path(self, skills: List[str], skill_levels: Dict[str, str]) -> Dict:
        """Fallback learning path generation"""
        
        learning_path = []
        for skill in skills:
            level = skill_levels.get(skill, "beginner")
            
            if level == "beginner":
                modules = [
                    {
                        "title": f"Introduction to {skill}",
                        "description": f"Learn the basics of {skill}",
                        "duration": "1-2 weeks",
                        "resources": [f"{skill} documentation", "Online tutorials"],
                        "projects": [f"Simple {skill} project"],
                        "assessment": "Basic quiz"
                    }
                ]
                target_level = "intermediate"
            elif level == "intermediate":
                modules = [
                    {
                        "title": f"Advanced {skill} Concepts",
                        "description": f"Deep dive into {skill}",
                        "duration": "2-3 weeks",
                        "resources": [f"Advanced {skill} courses", "Practice platforms"],
                        "projects": [f"Complex {skill} project"],
                        "assessment": "Project-based assessment"
                    }
                ]
                target_level = "advanced"
            else:
                modules = [
                    {
                        "title": f"Expert {skill} Mastery",
                        "description": f"Master {skill} at expert level",
                        "duration": "3-4 weeks",
                        "resources": [f"Expert {skill} resources", "Industry best practices"],
                        "projects": [f"Expert-level {skill} project"],
                        "assessment": "Expert evaluation"
                    }
                ]
                target_level = "expert"
            
            learning_path.append({
                "skill": skill,
                "current_level": level,
                "target_level": target_level,
                "modules": modules,
                "estimated_completion": "4-6 weeks"
            })
        
        return {
            "learning_path": learning_path,
            "overall_timeline": "3-6 months",
            "priority_order": skills,
            "success_metrics": ["Skill assessments", "Project completion", "Real-world application"]
        }
    
    async def get_daily_tip(self, user_id: str, current_skills: List[str]) -> Dict:
        """Get daily learning tip based on user's skills"""
        
        if not self.model:
            return self._get_fallback_daily_tip(current_skills)
        
        try:
            prompt = f"""
            Generate a daily learning tip for a user with these skills: {current_skills}
            
            Provide the tip in JSON format:
            {{
                "tip": "The daily tip",
                "skill_focus": "skill_name",
                "difficulty": "beginner/intermediate/advanced",
                "practice_exercise": "A quick exercise to practice",
                "motivation": "Motivational message"
            }}
            """
            
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._get_fallback_daily_tip(current_skills)
                
        except Exception as e:
            print(f"❌ Failed to generate daily tip: {e}")
            return self._get_fallback_daily_tip(current_skills)
    
    def _get_fallback_daily_tip(self, current_skills: List[str]) -> Dict:
        """Fallback daily tip"""
        
        skill = current_skills[0] if current_skills else "programming"
        
        tips = [
            {
                "tip": f"Practice {skill} for at least 30 minutes today",
                "skill_focus": skill,
                "difficulty": "beginner",
                "practice_exercise": f"Write a simple {skill} program",
                "motivation": "Consistency is key to mastering any skill!"
            },
            {
                "tip": f"Review {skill} concepts you learned yesterday",
                "skill_focus": skill,
                "difficulty": "intermediate",
                "practice_exercise": f"Debug a {skill} code snippet",
                "motivation": "Repetition helps solidify your knowledge!"
            },
            {
                "tip": f"Teach someone else about {skill}",
                "skill_focus": skill,
                "difficulty": "advanced",
                "practice_exercise": f"Create a {skill} tutorial",
                "motivation": "Teaching is the best way to learn!"
            }
        ]
        
        import random
        return random.choice(tips)

# Global AI Mentor instance
ai_mentor = AIMentor() 