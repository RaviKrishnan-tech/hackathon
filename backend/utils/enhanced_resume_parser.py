import google.generativeai as genai
import os
from typing import Dict, List, Optional
from datetime import datetime
import json
from PyPDF2 import PdfReader
import re
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class EnhancedResumeParser:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-pro")
        
    def parse_resume(self, file_obj) -> Dict:
        """Enhanced resume parsing using Gemini AI"""
        
        # Extract text from PDF
        text = self._extract_text_from_pdf(file_obj)
        
        # Use Gemini AI to analyze the resume
        analysis = self._analyze_resume_with_ai(text)
        
        return {
            "extracted_skills": analysis.get("extracted_skills", []),
            "experience_level": analysis.get("experience_level", "entry"),
            "years_of_experience": analysis.get("years_of_experience", 0),
            "education": analysis.get("education", []),
            "projects": analysis.get("projects", []),
            "certifications": analysis.get("certifications", []),
            "skill_categories": analysis.get("skill_categories", {}),
            "career_summary": analysis.get("career_summary", ""),
            "recommended_learning_path": analysis.get("recommended_learning_path", []),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _extract_text_from_pdf(self, file_obj) -> str:
        """Extract text from PDF file"""
        try:
            reader = PdfReader(file_obj)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return text
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def _analyze_resume_with_ai(self, resume_text: str) -> Dict:
        """Use Gemini AI to analyze resume content"""
        
        # Check if API key is configured
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            print("⚠️ GEMINI_API_KEY not configured. Using fallback skill extraction.")
            return self._fallback_skill_extraction(resume_text)
        
        prompt = f"""Analyze the following resume and extract comprehensive information:

Resume Text:
{resume_text[:4000]}  # Limit text to avoid token limits

Please provide analysis in the following JSON format:
{{
    "extracted_skills": ["skill1", "skill2", "skill3"],
    "experience_level": "entry/mid/senior",
    "years_of_experience": 3,
    "education": [
        {{
            "degree": "Bachelor of Science",
            "field": "Computer Science",
            "institution": "University Name",
            "year": 2020
        }}
    ],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Brief description",
            "technologies": ["tech1", "tech2"],
            "impact": "What was accomplished"
        }}
    ],
    "certifications": ["cert1", "cert2"],
    "skill_categories": {{
        "programming_languages": ["Python", "JavaScript"],
        "frameworks": ["React", "Django"],
        "databases": ["PostgreSQL", "MongoDB"],
        "tools": ["Git", "Docker"],
        "soft_skills": ["Leadership", "Communication"]
    }},
    "career_summary": "Brief summary of career background and goals",
    "recommended_learning_path": [
        {{
            "skill": "skill_name",
            "priority": "high/medium/low",
            "reason": "Why this skill is recommended"
        }}
    ]
}}

Focus on:
1. Technical skills (programming languages, frameworks, tools)
2. Experience level and years of experience
3. Education and certifications
4. Notable projects and their impact
5. Skill categorization for better learning recommendations
6. Career summary and learning path suggestions

Be thorough but accurate. If information is not available, use empty arrays or appropriate defaults.
"""
        
        try:
            print("🤖 Using Gemini AI for resume analysis...")
            response = self.model.generate_content(prompt)
            response_text = response.text
            print(f"📄 AI Response: {response_text[:200]}...")
            
            # Extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                result = json.loads(json_str)
                print(f"✅ AI Analysis successful. Found {len(result.get('extracted_skills', []))} skills.")
                return result
            else:
                # Try to parse as JSON directly
                result = json.loads(response_text)
                print(f"✅ AI Analysis successful. Found {len(result.get('extracted_skills', []))} skills.")
                return result
                
        except Exception as e:
            print(f"❌ AI Analysis failed: {str(e)}. Using fallback extraction.")
            # Fallback to basic skill extraction
            return self._fallback_skill_extraction(resume_text)
    
    def _fallback_skill_extraction(self, text: str) -> Dict:
        """Fallback method for skill extraction if AI fails"""
        
        print("🔍 Using fallback skill extraction...")
        print(f"📄 Resume text length: {len(text)} characters")
        print(f"📄 First 200 characters: {text[:200]}...")
        
        # Common technical skills - expanded list
        known_skills = {
            # Programming Languages
            "python", "java", "javascript", "typescript", "c++", "c#", "php", "ruby", "go", "rust", "swift", "kotlin", "scala", "r", "matlab", "perl", "bash", "shell", "powershell",
            
            # Web Technologies
            "html", "css", "react", "angular", "vue", "node.js", "express", "django", "flask", "spring", "asp.net", "laravel", "rails", "jquery", "ajax", "rest", "graphql", "api", "webpack", "babel",
            
            # Databases
            "sql", "mongodb", "postgresql", "mysql", "redis", "oracle", "sqlite", "mariadb", "cassandra", "neo4j", "elasticsearch",
            
            # Cloud & DevOps
            "docker", "kubernetes", "aws", "azure", "gcp", "google cloud", "heroku", "jenkins", "gitlab", "github", "bitbucket", "ci/cd", "terraform", "ansible", "chef", "puppet",
            
            # Frameworks & Libraries
            "bootstrap", "tailwind", "material-ui", "ant design", "lodash", "moment", "axios", "fetch", "socket.io", "webpack", "vite", "rollup",
            
            # Data Science & AI
            "machine learning", "ai", "artificial intelligence", "data science", "pandas", "numpy", "tensorflow", "pytorch", "scikit-learn", "nlp", "natural language processing", "computer vision", "deep learning", "neural networks", "opencv", "matplotlib", "seaborn", "plotly",
            
            # Mobile Development
            "react native", "flutter", "xamarin", "ionic", "cordova", "android", "ios", "mobile development",
            
            # Other Technologies
            "git", "agile", "scrum", "microservices", "serverless", "blockchain", "ethereum", "solidity", "bitcoin", "web3", "metaverse", "ar", "vr", "augmented reality", "virtual reality",
            
            # Common abbreviations and variations
            "js", "ts", "py", "ml", "dl", "cv", "nlp", "api", "ui", "ux", "db", "devops", "fullstack", "frontend", "backend", "full-stack", "front-end", "back-end"
        }
        
        # Extract skills from text
        text_lower = text.lower()
        found_skills = []
        
        # First pass: exact matches
        for skill in known_skills:
            if skill in text_lower:
                found_skills.append(skill)
        
        # Second pass: look for common skill patterns
        skill_patterns = [
            r'\b(?:proficient in|experience with|skilled in|knowledge of|familiar with)\s+([a-zA-Z\s+#]+)',
            r'\b(?:worked with|used|developed|built|created|implemented)\s+([a-zA-Z\s+#]+)',
            r'\b(?:expertise in|specialized in|focused on)\s+([a-zA-Z\s+#]+)',
            r'\b([a-zA-Z]+(?:\s*[+#])?)\s+(?:developer|engineer|programmer|specialist)',
            r'\b(?:frontend|backend|fullstack|full-stack|front-end|back-end)\s+development',
            r'\b(?:web|mobile|desktop|cloud|devops|data)\s+development',
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                # Clean up the match
                skill_name = match.strip().lower()
                if len(skill_name) > 2 and skill_name not in found_skills:
                    # Check if it's a known skill or similar to one
                    for known_skill in known_skills:
                        if skill_name in known_skill or known_skill in skill_name:
                            if known_skill not in found_skills:
                                found_skills.append(known_skill)
                            break
                    else:
                        # If not found in known skills, add it if it looks like a technical term
                        if any(word in skill_name for word in ['script', 'scripting', 'language', 'framework', 'library', 'tool', 'platform', 'service']):
                            found_skills.append(skill_name)
        
        # Remove duplicates while preserving order
        found_skills = list(dict.fromkeys(found_skills))
        
        # If no skills found, provide some basic default skills
        if not found_skills:
            found_skills = ["general programming", "problem solving", "software development"]
            print("🔍 No specific skills found, using default skills")
        
        print(f"🔍 Found skills: {found_skills}")
        
        result = {
            "extracted_skills": found_skills,
            "experience_level": "entry",
            "years_of_experience": 0,
            "education": [],
            "projects": [],
            "certifications": [],
            "skill_categories": {
                "programming_languages": [s for s in found_skills if s in ["python", "java", "javascript", "typescript"]],
                "frameworks": [s for s in found_skills if s in ["react", "angular", "vue", "django", "flask", "spring"]],
                "databases": [s for s in found_skills if s in ["sql", "mongodb", "postgresql", "mysql", "redis"]],
                "tools": [s for s in found_skills if s in ["git", "docker", "aws", "jenkins"]]
            },
            "career_summary": "Resume analysis completed with basic skill extraction",
            "recommended_learning_path": []
        }
        
        print(f"📊 Fallback extraction result: {len(found_skills)} skills found")
        return result
    
    def generate_skill_assessment_plan(self, extracted_skills: List[str], experience_level: str) -> Dict:
        """Generate assessment plan based on extracted skills"""
        
        # Check if API key is configured
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            print("⚠️ GEMINI_API_KEY not configured. Using fallback assessment plan.")
            return self._fallback_assessment_plan(extracted_skills, experience_level)
        
        prompt = f"""Based on the following skills and experience level, generate an assessment plan:

Skills: {extracted_skills}
Experience Level: {experience_level}

Create an assessment plan in JSON format:
{{
    "assessment_plan": [
        {{
            "skill": "skill_name",
            "difficulty": "beginner/intermediate/advanced",
            "question_count": 5,
            "focus_areas": ["area1", "area2"],
            "estimated_duration": "15 minutes"
        }}
    ],
    "total_questions": 25,
    "estimated_total_duration": "75 minutes",
    "skill_priorities": ["priority1", "priority2"],
    "assessment_strategy": "Strategy description"
}}

Consider the experience level when determining question difficulty and focus areas.
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                return json.loads(json_str)
            else:
                return json.loads(response_text)
                
        except Exception as e:
            print(f"❌ AI Assessment plan generation failed: {str(e)}. Using fallback.")
            return self._fallback_assessment_plan(extracted_skills, experience_level)
    
    def _fallback_assessment_plan(self, extracted_skills: List[str], experience_level: str) -> Dict:
        """Fallback assessment plan generation"""
        return {
            "assessment_plan": [
                {
                    "skill": skill,
                    "difficulty": "intermediate",
                    "question_count": 3,
                    "focus_areas": ["fundamentals", "practical application"],
                    "estimated_duration": "10 minutes"
                } for skill in extracted_skills[:5]
            ],
            "total_questions": len(extracted_skills) * 3,
            "estimated_total_duration": f"{len(extracted_skills) * 10} minutes",
            "skill_priorities": extracted_skills[:3],
            "assessment_strategy": "Comprehensive skill assessment with practical questions"
        }

# Global parser instance
resume_parser = EnhancedResumeParser() 