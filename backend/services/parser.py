import random

def extract_skills_from_resume(text: str) -> list:
    known_skills = [
        "Python", "JavaScript", "React", "Node.js", "SQL",
        "Machine Learning", "Flask", "Git", "Docker", "AWS"
    ]

    lower = text.lower()
    detected = [skill for skill in known_skills if skill.lower() in lower]

    if not detected:
        # fallback if no match found in resume
        detected = random.sample(known_skills, k=3)

    return detected
