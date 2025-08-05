import re

# A basic keyword matcher — you can improve this with spaCy or Hugging Face later
TECH_KEYWORDS = [
    "python", "java", "c++", "javascript", "react", "node.js", "sql", "mongodb",
    "html", "css", "docker", "git", "aws", "firebase", "machine learning", "ai",
    "tensorflow", "pytorch", "express", "flask", "fastapi"
]

async def extract_skills(text: str, _client=None) -> list:
    found = set()
    lowered = text.lower()
    for keyword in TECH_KEYWORDS:
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, lowered):
            found.add(keyword.title())
    return sorted(list(found))
