

from PyPDF2 import PdfReader
from transformers import pipeline
import re

# Load Hugging Face model
SKILL_NER_PIPE = pipeline(
    "ner",
    model="Nucha/Nucha_ITSkillNER_BERT",
    aggregation_strategy="simple",
    device=-1  # Use CPU; change to device=0 for GPU
)

def clean_skill(skill):
    return re.sub(r'[^a-zA-Z0-9\+\.#]+', ' ', skill.lower()).strip()

def load_known_skills():
    return {
        "python", "java", "javascript", "sql", "html", "css", "react", "node.js",
        "git", "github", "docker", "kubernetes", "api", "tensorflow", "pytorch",
        "data science", "machine learning", "ai", "nlp", "flask", "django"
    }

def extract_technical_skills(file_obj) -> list:
    reader = PdfReader(file_obj)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    ner_results = SKILL_NER_PIPE(text)
    raw_skills = {clean_skill(res["word"]) for res in ner_results}

    known_skills = load_known_skills()
    filtered_skills = sorted(skill for skill in raw_skills if skill in known_skills)

    return filtered_skills
